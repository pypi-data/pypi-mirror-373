import json
from typing import Any

from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext


class CustomWebhookContext(SapioWebhookContext):
    """
    CustomWebhookContext is a wrapper for the default SapioWebhookContext to be used by custom invocation types to
    convert the context_data that the server sends from a JSON string to usable parameters. This class works as a
    middleman to cleanly convert a SapioWebhookContext object into a CustomWebhookContext by copying all the parameters
    of the given context into the custom context.
    """
    def __init__(self, context: SapioWebhookContext):
        # Use __dict__ so that we don't need t maintain this class due to future changes to SapioWebhookContext.
        self.__dict__ = context.__dict__
        super().__init__(self.user, self.end_point_type)


class ProcessQueueContext(CustomWebhookContext):
    """
    When a custom process queue endpoint is invoked, the context from the queue is sent in a context_data parameter
    on the SapioWebhookContext object, stored as a JSON string. This class parses that JSON into fields for the
    caller to make use of.
    """
    process_name: str
    """The name of the process that the user invoked this webhook from."""
    step_name: str
    """The name of the step in the process that the user invoked this webhook from."""
    process_queue_item_record_ids: list[int]
    """The record IDs of the process queue items related to the records that were selected by the user when this
    webhook was invoked."""

    def __init__(self, context: SapioWebhookContext):
        super().__init__(context)
        context_data: dict[str, Any] = json.loads(self.context_data)
        self.process_name = context_data["processName"]
        self.step_name = context_data["workflowName"]
        self.process_queue_item_record_ids = context_data["processQueueItemRecordIds"]
