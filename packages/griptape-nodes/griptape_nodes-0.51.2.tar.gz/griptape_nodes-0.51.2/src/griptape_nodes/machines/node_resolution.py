from __future__ import annotations

import logging
from collections.abc import Generator
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

from griptape.events import EventBus
from griptape.utils import with_contextvars

from griptape_nodes.exe_types.core_types import ParameterType, ParameterTypeBuiltin
from griptape_nodes.exe_types.node_types import BaseNode, NodeResolutionState
from griptape_nodes.exe_types.type_validator import TypeValidator
from griptape_nodes.machines.fsm import FSM, State
from griptape_nodes.node_library.library_registry import LibraryRegistry
from griptape_nodes.retained_mode.events.base_events import (
    ExecutionEvent,
    ExecutionGriptapeNodeEvent,
)
from griptape_nodes.retained_mode.events.execution_events import (
    CurrentDataNodeEvent,
    NodeFinishProcessEvent,
    NodeResolvedEvent,
    NodeStartProcessEvent,
    ParameterSpotlightEvent,
    ParameterValueUpdateEvent,
    ResumeNodeProcessingEvent,
)
from griptape_nodes.retained_mode.events.parameter_events import (
    SetParameterValueRequest,
)

logger = logging.getLogger("griptape_nodes")


@dataclass
class Focus:
    node: BaseNode
    scheduled_value: Any | None = None
    process_generator: Generator | None = None


# This is on a per-node basis
class ResolutionContext:
    focus_stack: list[Focus]
    paused: bool

    def __init__(self) -> None:
        self.focus_stack = []
        self.paused = False

    def reset(self) -> None:
        if self.focus_stack:
            node = self.focus_stack[-1].node
            # clear the data node being resolved.
            node.clear_node()
            self.focus_stack[-1].process_generator = None
            self.focus_stack[-1].scheduled_value = None
        self.focus_stack.clear()
        self.paused = False


class InitializeSpotlightState(State):
    @staticmethod
    def on_enter(context: ResolutionContext) -> type[State] | None:
        # If the focus stack is empty
        current_node = context.focus_stack[-1].node
        EventBus.publish_event(
            ExecutionGriptapeNodeEvent(
                wrapped_event=ExecutionEvent(payload=CurrentDataNodeEvent(node_name=current_node.name))
            )
        )
        if not context.paused:
            return InitializeSpotlightState
        return None

    @staticmethod
    def on_update(context: ResolutionContext) -> type[State] | None:
        # If the focus stack is empty
        if not len(context.focus_stack):
            return CompleteState
        current_node = context.focus_stack[-1].node
        if current_node.state == NodeResolutionState.UNRESOLVED:
            # Mark all future nodes unresolved.
            # TODO: https://github.com/griptape-ai/griptape-nodes/issues/862
            from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

            GriptapeNodes.FlowManager().get_connections().unresolve_future_nodes(current_node)
            current_node.initialize_spotlight()
        # Set node to resolving - we are now resolving this node.
        current_node.state = NodeResolutionState.RESOLVING
        # Advance to next port if we do not have one ATM!
        if current_node.get_current_parameter() is None:
            # Advance to next port
            if current_node.advance_parameter():
                # if true, we advanced the port!
                return EvaluateParameterState
            # if not true, we have no ports left to advance to or none at all
            return ExecuteNodeState
        # We are already set here
        return EvaluateParameterState  # TODO: https://github.com/griptape-ai/griptape-nodes/issues/863


class EvaluateParameterState(State):
    @staticmethod
    def on_enter(context: ResolutionContext) -> type[State] | None:
        current_node = context.focus_stack[-1].node
        current_parameter = current_node.get_current_parameter()
        if current_parameter is None:
            return ExecuteNodeState
        # if not in debug mode - keep going!
        EventBus.publish_event(
            ExecutionGriptapeNodeEvent(
                wrapped_event=ExecutionEvent(
                    payload=ParameterSpotlightEvent(
                        node_name=current_node.name,
                        parameter_name=current_parameter.name,
                    )
                )
            )
        )
        if not context.paused:
            return EvaluateParameterState
        return None

    @staticmethod
    def on_update(context: ResolutionContext) -> type[State] | None:
        current_node = context.focus_stack[-1].node
        current_parameter = current_node.get_current_parameter()
        from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

        connections = GriptapeNodes.FlowManager().get_connections()
        if current_parameter is None:
            msg = "No current parameter set."
            raise ValueError(msg)
        # Get the next node
        next_node = connections.get_connected_node(current_node, current_parameter)
        if next_node:
            next_node, _ = next_node
        if next_node and next_node.state == NodeResolutionState.UNRESOLVED:
            focus_stack_names = {focus.node.name for focus in context.focus_stack}
            if next_node.name in focus_stack_names:
                msg = f"Cycle detected between node '{current_node.name}' and '{next_node.name}'."
                raise RuntimeError(msg)

            context.focus_stack.append(Focus(node=next_node))
            return InitializeSpotlightState

        if current_node.advance_parameter():
            return InitializeSpotlightState
        return ExecuteNodeState


class ExecuteNodeState(State):
    executor: ThreadPoolExecutor = ThreadPoolExecutor()

    # TODO: https://github.com/griptape-ai/griptape-nodes/issues/864
    @staticmethod
    def clear_parameter_output_values(context: ResolutionContext) -> None:
        """Clears all parameter output values for the currently focused node in the resolution context.

        This method iterates through each parameter output value stored in the current node,
        removes it from the node's parameter_output_values dictionary, and publishes an event
        to notify the system about the parameter value being set to None.

        Args:
            context (ResolutionContext): The resolution context containing the focus stack
                with the current node being processed.

        Raises:
            ValueError: If a parameter name in parameter_output_values doesn't correspond
                to an actual parameter in the node.

        Note:
            - Uses a copy of parameter_output_values to safely modify the dictionary during iteration
            - For each parameter, publishes a ParameterValueUpdateEvent with value=None
            - Events are wrapped in ExecutionGriptapeNodeEvent before publishing
        """
        current_node = context.focus_stack[-1].node
        for parameter_name in current_node.parameter_output_values.copy():
            parameter = current_node.get_parameter_by_name(parameter_name)
            if parameter is None:
                err = f"Attempted to execute node '{current_node.name}' but could not find parameter '{parameter_name}' that was indicated as having a value."
                raise ValueError(err)
            parameter_type = parameter.type
            if parameter_type is None:
                parameter_type = ParameterTypeBuiltin.NONE.value
            payload = ParameterValueUpdateEvent(
                node_name=current_node.name,
                parameter_name=parameter_name,
                data_type=parameter_type,
                value=None,
            )
            EventBus.publish_event(ExecutionGriptapeNodeEvent(wrapped_event=ExecutionEvent(payload=payload)))
        current_node.parameter_output_values.clear()

    @staticmethod
    def collect_values_from_upstream_nodes(context: ResolutionContext) -> None:
        """Collect output values from resolved upstream nodes and pass them to the current node.

        This method iterates through all input parameters of the current node, finds their
        connected upstream nodes, and if those nodes are resolved, retrieves their output
        values and passes them through using SetParameterValueRequest.

        Args:
            context (ResolutionContext): The resolution context containing the focus stack
                with the current node being processed.
        """
        from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

        current_node = context.focus_stack[-1].node
        connections = GriptapeNodes.FlowManager().get_connections()

        for parameter in current_node.parameters:
            # Skip control type parameters
            if ParameterTypeBuiltin.CONTROL_TYPE.value.lower() == parameter.output_type:
                continue

            # Get the connected upstream node for this parameter
            upstream_connection = connections.get_connected_node(current_node, parameter)
            if upstream_connection:
                upstream_node, upstream_parameter = upstream_connection

                # If the upstream node is resolved, collect its output value
                if upstream_parameter.name in upstream_node.parameter_output_values:
                    output_value = upstream_node.parameter_output_values[upstream_parameter.name]
                else:
                    output_value = upstream_node.get_parameter_value(upstream_parameter.name)

                # Pass the value through using the same mechanism as normal resolution
                # Skip propagation for Control Parameters as they should not receive values
                if (
                    ParameterType.attempt_get_builtin(upstream_parameter.output_type)
                    != ParameterTypeBuiltin.CONTROL_TYPE
                ):
                    GriptapeNodes.get_instance().handle_request(
                        SetParameterValueRequest(
                            parameter_name=parameter.name,
                            node_name=current_node.name,
                            value=output_value,
                            data_type=upstream_parameter.output_type,
                        )
                    )

    @staticmethod
    def on_enter(context: ResolutionContext) -> type[State] | None:
        current_node = context.focus_stack[-1].node

        # Clear all of the current output values
        # if node is locked, don't clear anything. skip all of this.
        if current_node.lock:
            return ExecuteNodeState
        ExecuteNodeState.collect_values_from_upstream_nodes(context)
        ExecuteNodeState.clear_parameter_output_values(context)
        for parameter in current_node.parameters:
            if ParameterTypeBuiltin.CONTROL_TYPE.value.lower() == parameter.output_type:
                continue
            if parameter.name not in current_node.parameter_values:
                # If a parameter value is not already set
                value = current_node.get_parameter_value(parameter.name)
                if value is not None:
                    current_node.set_parameter_value(parameter.name, value)

            if parameter.name in current_node.parameter_values:
                parameter_value = current_node.get_parameter_value(parameter.name)
                data_type = parameter.type
                if data_type is None:
                    data_type = ParameterTypeBuiltin.NONE.value
                EventBus.publish_event(
                    ExecutionGriptapeNodeEvent(
                        wrapped_event=ExecutionEvent(
                            payload=ParameterValueUpdateEvent(
                                node_name=current_node.name,
                                parameter_name=parameter.name,
                                # this is because the type is currently IN the parameter.
                                data_type=data_type,
                                value=TypeValidator.safe_serialize(parameter_value),
                            )
                        )
                    )
                )

        exceptions = current_node.validate_before_node_run()
        if exceptions:
            msg = f"Canceling flow run. Node '{current_node.name}' encountered problems: {exceptions}"
            # Mark the node as unresolved, broadcasting to everyone.
            raise RuntimeError(msg)
        if not context.paused:
            return ExecuteNodeState
        return None

    @staticmethod
    def on_update(context: ResolutionContext) -> type[State] | None:
        from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

        # Once everything has been set
        current_focus = context.focus_stack[-1]
        current_node = current_focus.node
        # If the node is not locked, execute all of this.
        if not current_node.lock:
            # To set the event manager without circular import errors
            EventBus.publish_event(
                ExecutionGriptapeNodeEvent(
                    wrapped_event=ExecutionEvent(payload=NodeStartProcessEvent(node_name=current_node.name))
                )
            )
            logger.info("Node '%s' is processing.", current_node.name)

            try:
                work_is_scheduled = ExecuteNodeState._process_node(current_focus)
                if work_is_scheduled:
                    logger.debug("Pausing Node '%s' to run background work", current_node.name)
                    return None
            except Exception as e:
                logger.exception("Error processing node '%s", current_node.name)
                msg = f"Canceling flow run. Node '{current_node.name}' encountered a problem: {e}"
                # Mark the node as unresolved, broadcasting to everyone.
                current_node.make_node_unresolved(
                    current_states_to_trigger_change_event=set(
                        {NodeResolutionState.UNRESOLVED, NodeResolutionState.RESOLVED, NodeResolutionState.RESOLVING}
                    )
                )
                current_focus.process_generator = None
                current_focus.scheduled_value = None

                from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

                GriptapeNodes.FlowManager().cancel_flow_run()

                EventBus.publish_event(
                    ExecutionGriptapeNodeEvent(
                        wrapped_event=ExecutionEvent(payload=NodeFinishProcessEvent(node_name=current_node.name))
                    )
                )
                raise RuntimeError(msg) from e

            logger.info("Node '%s' finished processing.", current_node.name)

            EventBus.publish_event(
                ExecutionGriptapeNodeEvent(
                    wrapped_event=ExecutionEvent(payload=NodeFinishProcessEvent(node_name=current_node.name))
                )
            )
            current_node.state = NodeResolutionState.RESOLVED
            details = f"'{current_node.name}' resolved."

            logger.info(details)

            # Serialization can be slow so only do it if the user wants debug details.
            if logger.level <= logging.DEBUG:
                logger.debug(
                    "INPUTS: %s\nOUTPUTS: %s",
                    TypeValidator.safe_serialize(current_node.parameter_values),
                    TypeValidator.safe_serialize(current_node.parameter_output_values),
                )

            for parameter_name, value in current_node.parameter_output_values.items():
                parameter = current_node.get_parameter_by_name(parameter_name)
                if parameter is None:
                    err = f"Canceling flow run. Node '{current_node.name}' specified a Parameter '{parameter_name}', but no such Parameter could be found on that Node."
                    raise KeyError(err)
                data_type = parameter.type
                if data_type is None:
                    data_type = ParameterTypeBuiltin.NONE.value
                EventBus.publish_event(
                    ExecutionGriptapeNodeEvent(
                        wrapped_event=ExecutionEvent(
                            payload=ParameterValueUpdateEvent(
                                node_name=current_node.name,
                                parameter_name=parameter_name,
                                data_type=data_type,
                                value=TypeValidator.safe_serialize(value),
                            )
                        ),
                    )
                )
            # Output values should already be saved!
        library = LibraryRegistry.get_libraries_with_node_type(current_node.__class__.__name__)
        if len(library) == 1:
            library_name = library[0]
        else:
            library_name = None
        EventBus.publish_event(
            ExecutionGriptapeNodeEvent(
                wrapped_event=ExecutionEvent(
                    payload=NodeResolvedEvent(
                        node_name=current_node.name,
                        parameter_output_values=TypeValidator.safe_serialize(current_node.parameter_output_values),
                        node_type=current_node.__class__.__name__,
                        specific_library_name=library_name,
                    )
                )
            )
        )
        context.focus_stack.pop()
        if len(context.focus_stack):
            return EvaluateParameterState

        return CompleteState

    @staticmethod
    def _process_node(current_focus: Focus) -> bool:
        """Run the process method of the node.

        If the node's process method returns a generator, take the next value from the generator (a callable) and run
        that in a thread pool executor. The result of that callable will be passed to the generator when it is resumed.

        This has the effect of pausing at a yield expression, running the expression in a thread, and resuming when the thread pool is done.

        Args:
            current_focus (Focus): The current focus.

        Returns:
            bool: True if work has been scheduled, False if the node is done processing.
        """

        def on_future_done(future: Future) -> None:
            """Called when the future is done.

            Stores the result of the future in the node's context, and publishes an event to resume the flow.
            """
            try:
                current_focus.scheduled_value = future.result()
            except Exception as e:
                logger.debug("Error in future: %s", e)
                current_focus.scheduled_value = e
            finally:
                # If it hasn't been cancelled.
                if current_focus.process_generator:
                    EventBus.publish_event(
                        ExecutionGriptapeNodeEvent(
                            wrapped_event=ExecutionEvent(payload=ResumeNodeProcessingEvent(node_name=current_node.name))
                        )
                    )

        current_node = current_focus.node
        # Only start the processing if we don't already have a generator
        logger.debug("Node '%s' process generator: %s", current_node.name, current_focus.process_generator)
        if current_focus.process_generator is None:
            result = current_node.process()

            # If the process returned a generator, we need to store it for later
            if isinstance(result, Generator):
                current_focus.process_generator = result
                logger.debug("Node '%s' returned a generator.", current_node.name)

        # We now have a generator, so we need to run it
        if current_focus.process_generator is not None:
            try:
                logger.debug(
                    "Node '%s' has an active generator, sending scheduled value of type: %s",
                    current_node.name,
                    type(current_focus.scheduled_value),
                )
                if isinstance(current_focus.scheduled_value, Exception):
                    func = current_focus.process_generator.throw(current_focus.scheduled_value)
                else:
                    func = current_focus.process_generator.send(current_focus.scheduled_value)

                # Once we've passed on the scheduled value, we should clear it out just in case
                current_focus.scheduled_value = None

                future = ExecuteNodeState.executor.submit(with_contextvars(func))
                future.add_done_callback(with_contextvars(on_future_done))
            except StopIteration:
                logger.debug("Node '%s' generator is done.", current_node.name)
                # If that was the last generator, clear out the generator and indicate that there is no more work scheduled
                current_focus.process_generator = None
                current_focus.scheduled_value = None
                return False
            else:
                # If the generator is not done, indicate that there is work scheduled
                logger.debug("Node '%s' generator is not done.", current_node.name)
                return True
        logger.debug("Node '%s' did not return a generator.", current_node.name)
        return False


class CompleteState(State):
    @staticmethod
    def on_enter(context: ResolutionContext) -> type[State] | None:  # noqa: ARG004
        return None

    @staticmethod
    def on_update(context: ResolutionContext) -> type[State] | None:  # noqa: ARG004
        return None


class NodeResolutionMachine(FSM[ResolutionContext]):
    """State machine for resolving node dependencies."""

    def __init__(self) -> None:
        resolution_context = ResolutionContext()
        super().__init__(resolution_context)

    def resolve_node(self, node: BaseNode) -> None:
        self._context.focus_stack.append(Focus(node=node))
        self.start(InitializeSpotlightState)

    def change_debug_mode(self, debug_mode: bool) -> None:  # noqa: FBT001
        self._context.paused = debug_mode

    def is_complete(self) -> bool:
        return self._current_state is CompleteState

    def is_started(self) -> bool:
        return self._current_state is not None

    def reset_machine(self) -> None:
        self._context.reset()
        self._current_state = None
