from collections import defaultdict
from collections.abc import Callable
from dataclasses import fields
from typing import TYPE_CHECKING

from griptape.events import EventBus
from typing_extensions import TypeVar

from griptape_nodes.retained_mode.events.base_events import (
    AppPayload,
    EventRequest,
    EventResultFailure,
    EventResultSuccess,
    FlushParameterChangesRequest,
    GriptapeNodeEvent,
    RequestPayload,
    ResultPayload,
    WorkflowAlteredMixin,
)

if TYPE_CHECKING:
    from griptape_nodes.retained_mode.griptape_nodes import WorkflowManager
    from griptape_nodes.retained_mode.managers.operation_manager import OperationDepthManager

RP = TypeVar("RP", bound=RequestPayload, default=RequestPayload)
AP = TypeVar("AP", bound=AppPayload, default=AppPayload)


class EventManager:
    def __init__(self) -> None:
        # Dictionary to store the SPECIFIC manager for each request type
        self._request_type_to_manager: dict[type[RequestPayload], Callable] = defaultdict(list)  # pyright: ignore[reportAttributeAccessIssue]
        # Dictionary to store ALL SUBSCRIBERS to app events.
        self._app_event_listeners: dict[type[AppPayload], set[Callable]] = {}
        self.current_active_node: str | None = None
        # Boolean that lets us know if there is currently a FlushParameterChangesRequest in the event queue.
        self._flush_in_queue: bool = False

    def clear_flush_in_queue(self) -> None:
        self._flush_in_queue = False

    def assign_manager_to_request_type(
        self,
        request_type: type[RP],
        callback: Callable[[RP], ResultPayload],
    ) -> None:
        """Assign a manager to handle a request.

        Args:
            request_type: The type of request to assign the manager to
            callback: Function to be called when event occurs
        """
        existing_manager = self._request_type_to_manager.get(request_type)
        if existing_manager is not None:
            msg = f"Attempted to assign an event of type {request_type} to manager {callback.__name__}, but that request is already assigned to manager {existing_manager.__name__}."
            raise ValueError(msg)
        self._request_type_to_manager[request_type] = callback

    def remove_manager_from_request_type(self, request_type: type[RP]) -> None:
        """Unsubscribe the manager from the request of a specific type.

        Args:
            request_type: The type of request to unsubscribe from
        """
        if request_type in self._request_type_to_manager:
            del self._request_type_to_manager[request_type]

    def handle_request(
        self,
        request: RP,
        *,
        operation_depth_mgr: "OperationDepthManager",
        workflow_mgr: "WorkflowManager",
        response_topic: str | None = None,
        request_id: str | None = None,
    ) -> ResultPayload:
        """Publish an event to the manager assigned to its type.

        Args:
            request: The request to handle
            operation_depth_mgr: The operation depth manager to use
            workflow_mgr: The workflow manager to use
            response_topic: The topic to send the response to (optional)
            request_id: The ID of the request to correlate with the response (optional)
        """
        # Notify the manager of the event type
        with operation_depth_mgr as depth_manager:
            request_type = type(request)
            callback = self._request_type_to_manager.get(request_type)
            if callback:
                # Actually make the handler callback:
                result_payload = callback(request)

                # Now see if the WorkflowManager was asking us to squelch altered_workflow_state commands
                # This prevents situations like loading a workflow (which naturally alters the workflow state)
                # from coming in and immediately being flagged as being dirty.
                if workflow_mgr.should_squelch_workflow_altered():
                    result_payload.altered_workflow_state = False

                retained_mode_str = None
                # If request_id exists, that means it's a direct request from the GUI (not internal), and should be echoed by retained mode.
                if depth_manager.is_top_level() and request_id is not None:
                    retained_mode_str = depth_manager.request_retained_mode_translation(request)

                # Some requests have fields marked as "omit_from_result" which should be removed from the request
                for field in fields(request):
                    if field.metadata.get("omit_from_result", False):
                        setattr(request, field.name, None)
                if result_payload.succeeded():
                    result_event = EventResultSuccess(
                        request=request,
                        request_id=request_id,
                        result=result_payload,
                        retained_mode=retained_mode_str,
                        response_topic=response_topic,
                    )
                    # If the result is a success, and the WorkflowAlteredMixin is present, that means the flow has been changed in some way.
                    # In that case, we need to flush the element changes, so we add one to the event queue.
                    if isinstance(result_event.result, WorkflowAlteredMixin) and not self._flush_in_queue:
                        from griptape_nodes.app.app import event_queue

                        event_queue.put(EventRequest(request=FlushParameterChangesRequest()))
                        self._flush_in_queue = True
                else:
                    result_event = EventResultFailure(
                        request=request,
                        request_id=request_id,
                        result=result_payload,
                        retained_mode=retained_mode_str,
                        response_topic=response_topic,
                    )
                wrapped_event = GriptapeNodeEvent(wrapped_event=result_event)
                EventBus.publish_event(wrapped_event)
            else:
                msg = f"No manager found to handle request of type '{request_type.__name__}."
                raise TypeError(msg)

        return result_payload

    def add_listener_to_app_event(self, app_event_type: type[AP], callback: Callable[[AP], None]) -> None:
        listener_set = self._app_event_listeners.get(app_event_type)
        if listener_set is None:
            listener_set = set()
            self._app_event_listeners[app_event_type] = listener_set

        listener_set.add(callback)

    def remove_listener_for_app_event(self, app_event_type: type[AP], callback: Callable[[AP], None]) -> None:
        listener_set = self._app_event_listeners[app_event_type]
        listener_set.remove(callback)

    def broadcast_app_event(self, app_event: AP) -> None:
        app_event_type = type(app_event)
        if app_event_type in self._app_event_listeners:
            listener_set = self._app_event_listeners[app_event_type]
            for listener_callback in listener_set:
                listener_callback(app_event)
