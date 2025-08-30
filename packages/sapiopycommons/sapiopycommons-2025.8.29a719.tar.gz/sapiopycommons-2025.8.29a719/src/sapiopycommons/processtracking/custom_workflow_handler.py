from typing import Iterable

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.customreport.auto_pagers import CustomReportDictAutoPager, CustomReportRecordAutoPager
from sapiopycommons.customreport.custom_report_builder import CustomReportBuilder
from sapiopycommons.datatype.data_fields import ProcessQueueItemFields, SystemFields, ProcessWorkflowTrackingFields
from sapiopycommons.general.aliases import UserIdentifier, AliasUtil, SapioRecord
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler
from sapiopycommons.webhook.webhook_context import ProcessQueueContext


class QueueItemReportCriteria:
    """
    Queue item report criteria is used to restrict the results of searches for queue item records.
    """
    process_names: list[str] | None
    not_process_names: list[str] | None
    step_names: list[str] | None
    not_step_names: list[str] | None
    data_type_names: list[str] | None
    not_data_type_names: list[str] | None
    data_record_ids: list[int] | None
    not_data_record_ids: list[int] | None
    assigned_to: list[str] | None
    not_assigned_to: list[str] | None
    launched_after: int | None
    launched_before: int | None
    scheduled_after: int | None
    scheduled_before: int | None
    shown_in_queue: bool | None
    has_experiment: bool | None

    def __init__(self, *,
                 process_names: list[str] | None = None,
                 not_process_names: list[str] | None = None,
                 step_names: list[str] | None = None,
                 not_step_names: list[str] | None = None,
                 data_type_names: list[str] | None = None,
                 not_data_type_names: list[str] | None = None,
                 data_record_ids: list[int] | None = None,
                 not_data_record_ids: list[int] | None = None,
                 assigned_to: list[str] | None = None,
                 not_assigned_to: list[str] | None = None,
                 launched_after: int | None = None,
                 launched_before: int | None = None,
                 scheduled_after: int | None = None,
                 scheduled_before: int | None = None,
                 shown_in_queue: bool | None = None,
                 has_experiment: bool | None = None):
        """
        :param process_names: The allowed process name(s).
        :param not_process_names: The disallowed process name(s).
        :param step_names: The allowed step name(s).
        :param not_step_names: The disallowed step name(s).
        :param data_type_names: The allowed data type name(s).
        :param not_data_type_names: The disallowed dta type name(s).
        :param data_record_ids: The allowed record ID(s).
        :param not_data_record_ids: The disallowed record ID(s).
        :param assigned_to: The allowed username(s) of the user(s) that the queue items are assigned to.
        :param not_assigned_to: The disallowed username(s) of the user(s) that the queue items are assigned to.
        :param launched_after: A timestamp after which the queue item was launched.
        :param launched_before: A timestamp before which the queue item was launched.
        :param scheduled_after: A timestamp after which the queue item was scheduled.
        :param scheduled_before: A timestamp before which the queue item was scheduled.
        :param shown_in_queue: Whether the queue item is currently being shown in a queue.
        :param has_experiment: Whether the queue item is linked to an experiment record.
        """
        self.process_names = process_names
        self.not_process_names = not_process_names
        self.step_names = step_names
        self.not_step_names = not_step_names
        self.data_type_names = data_type_names
        self.not_data_type_names = not_data_type_names
        self.data_record_ids = data_record_ids
        self.not_data_record_ids = not_data_record_ids
        self.assigned_to = assigned_to
        self.not_assigned_to = not_assigned_to
        self.launched_after = launched_after
        self.launched_before = launched_before
        self.scheduled_after = scheduled_after
        self.scheduled_before = scheduled_before
        self.shown_in_queue = shown_in_queue
        self.has_experiment = has_experiment


class QueueItemHandler:
    """
    A class used for handling the display of records in custom process queues, which are controlled in the system by
    ProcessQueueItem data types.

    IMPORTANT NOTICE: This is only for custom processes that make use of ProcessQueueItem records. For experiment
    processes that use AssignedProcess records, see the ProcessTracking class.
    """
    user: SapioUser
    context: ProcessQueueContext | None
    rec_handler: RecordHandler

    def __init__(self, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        self.user = AliasUtil.to_sapio_user(context)
        self.rec_handler = RecordHandler(self.user)
        # PR-47565: Only initialize a ProcessQueueContext if the given context object has context_data.
        if isinstance(context, SapioWebhookContext) and context.context_data:
            self.context = ProcessQueueContext(context)
        else:
            self.context = None

    # CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
    def get_process_queue_items_from_context(self, wrapper: type[WrappedType] | str,
                                             context: SapioWebhookContext | ProcessQueueContext | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        When you launch records from a custom process queue, the process queue items related to the selected records
        are provided as record IDs to the process queue context. Using these record IDs, query for the queue item
        records and wrap them as record models.

        :param wrapper: The record model wrapper or data type name for the process queue items.
        :param context: If this handler was not initialized with a context object, or you wish to retrieve
            data from a different context object than the initializing context, then provide the context to retrieve the
            record IDs from.
        :return: The process queue items corresponding to the record IDs from the context wrapped as record models.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        """
        if context is None and self.context is not None:
            record_ids: list[int] = self.context.process_queue_item_record_ids
        elif context is not None:
            if isinstance(context, SapioWebhookContext):
                record_ids: list[int] = ProcessQueueContext(context).process_queue_item_record_ids
            else:
                record_ids: list[int] = context.process_queue_item_record_ids
        else:
            raise SapioException("A context object must be provided to this function call, as the handler "
                                 "was not initialized with one.")
        return self.rec_handler.query_models_by_id(wrapper, record_ids)

    def map_records_to_queue_items(self, records: Iterable[SapioRecord], queue_items: Iterable[SapioRecord]) \
            -> dict[SapioRecord, list[SapioRecord]]:
        """
        Given a list of records and a list of queue items, create a dictionary mapping the records to the queue items
        that refer to them.

        :param records: The records to map to the queue items.
        :param queue_items: The queue items to map to the records.
        :return: A dictionary of record to the queue items that refer to them. Input queue items that don't refer to
            any provided records will not be in this dictionary.
        """
        ret_val: dict[SapioRecord, list[SapioRecord]] = {}
        id_to_queue_items: dict[int, list[SapioRecord]] = self.rec_handler.map_by_field(queue_items,
                                                                                        ProcessQueueItemFields.DATA_RECORD_ID__FIELD)
        id_to_record: dict[int, SapioRecord] = self.rec_handler.map_by_id(records)
        for record_id, record in id_to_record.items():
            ret_val[record] = id_to_queue_items[record_id]
        return ret_val

    def map_queue_items_to_records(self, queue_items: Iterable[SapioRecord], records: Iterable[SapioRecord]) \
            -> dict[SapioRecord, SapioRecord]:
        """
        Given a list of queue items and a list of records, create a dictionary mapping the queue items to the record
        that they refer to.

        :param queue_items: The queue items to map to the records.
        :param records: The records to map to the queue items.
        :return: A dictionary of queue items to the records that the refer to. Input record that aren't referred to by
            any provided queue items will not be in this dictionary.
        """
        ret_val: dict[SapioRecord, SapioRecord] = {}
        id_to_queue_items: dict[int, list[SapioRecord]] = self.rec_handler.map_by_field(queue_items,
                                                                                        ProcessQueueItemFields.DATA_RECORD_ID__FIELD)
        id_to_record: dict[int, SapioRecord] = self.rec_handler.map_by_id(records)
        for record_id, queue_items in id_to_queue_items.items():
            record: SapioRecord = id_to_record[record_id]
            for queue_item in queue_items:
                ret_val[queue_item] = record
        return ret_val

    def get_queue_items_from_report(self, wrapper: type[WrappedType] | None, criteria: QueueItemReportCriteria) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Run a custom report that retrieves every queue item in the system for the given search criteria.

        :param wrapper: The record model wrapper for the process queue items. If not provided, the returned records will
            be PyRecordModels instead of WrappedRecordModels.
        :param criteria: The search criteria to query for queue items with.
        :return: A list of every queue item in the system that matches the search criteria.
        """
        report = self.build_queue_item_report(criteria)
        dt: type[WrappedType] | str = wrapper if wrapper else ProcessQueueItemFields.DATA_TYPE_NAME
        return CustomReportRecordAutoPager(self.user, report, dt).get_all_at_once()

    def get_records_from_item_report(self, wrapper: type[WrappedType] | str,
                                     criteria: QueueItemReportCriteria = QueueItemReportCriteria()) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Run a custom report that retrieves for queue items that match the given search criteria, then query for the
        data records that those queue items refer to.

        :param wrapper: The record model wrapper or data type name for the records being queried for.
        :param criteria: Additional search criteria to filter the results. This function forces the data_type_names
            parameter of the criteria to match the data type of the given record model wrapper.
        :return: A list of all records related to the queue items in the system that match the search criteria.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        """
        # Don't try to query for process queue items that don't match the data type of this wrapper.
        criteria.data_type_names = [AliasUtil.to_data_type_name(wrapper)]
        criteria.not_data_type_names = None
        report = self.build_queue_item_report(criteria)
        record_ids: list[int] = [x[ProcessQueueItemFields.DATA_RECORD_ID__FIELD.field_name]
                                 for x in CustomReportDictAutoPager(self.user, report)]
        return self.rec_handler.query_models_by_id(wrapper, record_ids)

    def get_queue_items_for_records(self, records: Iterable[SapioRecord], wrapper: type[WrappedType] | None = None,
                                    criteria: QueueItemReportCriteria = QueueItemReportCriteria()) \
            -> dict[SapioRecord, list[WrappedType] | list[PyRecordModel]]:
        """
        Given a list of records, query the system for every process queue item that refers to those records and matches
        the provided search criteria.

        :param records: The queued records to query for the process queue items of.
        :param wrapper: The record model wrapper for the returned process queue item records. If not provided, the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        :param criteria: Additional search criteria to filter the results. This function forces the data_record_ids and
            data_type_names parameters on the criteria to match the given records.
        :return: A dictionary mapping the input records to a list of the process queue items that refer to them. If a
            record does not have any queue items that refer to it that match the given search criteria, then it will
            map to an empty list.
        """
        # Query for only those process queue items that have a record ID from the provided records.
        criteria.data_record_ids = AliasUtil.to_record_ids(records)
        criteria.not_data_record_ids = None
        criteria.data_type_names = AliasUtil.to_data_type_names(records)
        criteria.not_data_type_names = None
        items: list[WrappedType] | list[PyRecordModel] = self.get_queue_items_from_report(wrapper, criteria)
        return self.map_records_to_queue_items(records, items)

    def get_records_for_queue_items(self, queue_items: Iterable[SapioRecord], wrapper: type[WrappedType] | str) \
            -> dict[SapioRecord, WrappedType | PyRecordModel]:
        """
        Given a list of process queue items, query the system for the records that those queue items refer to.

        :param queue_items: The process queue items to query for the referenced records of.
        :param wrapper: The record model wrapper or data type name for the records being queried.
        :return: A dictionary mapping the input process queue items to the record tht they refer to. If a data type
            name was used instead of a model wrapper, then the returned records will be PyRecordModels instead of
            WrappedRecordModels.
        """
        record_ids: set[int] = {x.get_field_value(ProcessQueueItemFields.DATA_RECORD_ID__FIELD) for x in queue_items}
        records: list[WrappedType] | list[PyRecordModel] = self.rec_handler.query_models_by_id(wrapper, record_ids)
        return self.map_queue_items_to_records(queue_items, records)

    def queue_records_for_process(self, records: Iterable[SapioRecord], process: str, step: str,
                                  wrapper: type[WrappedType] | None = None) -> dict[SapioRecord, WrappedType | PyRecordModel]:
        """
        Given a list of records, create process queue item records for them at the provided process and step names.
        You must store and commit using the record model manager in order for these changes to take effect.

        IMPORTANT NOTICE: This is only for custom processes that make use of ProcessQueueItem records. For experiment
        processes that use AssignedProcess records, see the ProcessTracking class.

        :param records: The records to create process queue items for.
        :param process: The name of the process to queue for.
        :param step: The name of the step in the above process to queue for. This is the "Workflow Name" field of the
            Process Workflow record corresponding to the step you want to assign these records to. For steps that
            launch an experiment, this is the name of the template that will be launched. For the other types of custom
            process steps, this is the "Workflow Name" as defined in the process manager config.
        :param wrapper: The record model wrapper for the process queue items being created. If not provided, the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dictionary mapping each input record to the newly created process queue item for that record.
        """
        ret_val: dict[SapioRecord, WrappedType] = {}
        for record in records:
            item = self.rec_handler.add_model(wrapper if wrapper else ProcessQueueItemFields.DATA_TYPE_NAME)
            item.set_field_values({
                ProcessQueueItemFields.PROCESS_HEADER_NAME__FIELD.field_name: process,
                ProcessQueueItemFields.WORKFLOW_HEADER_NAME__FIELD.field_name: step,
                ProcessQueueItemFields.SHOW_IN_QUEUE__FIELD.field_name: True,
                ProcessQueueItemFields.SCHEDULED_DATE__FIELD.field_name: TimeUtil.now_in_millis(),
                ProcessQueueItemFields.DATA_RECORD_ID__FIELD.field_name: AliasUtil.to_record_id(record),
                ProcessQueueItemFields.DATA_TYPE_NAME__FIELD.field_name: AliasUtil.to_data_type_name(record)
            })
            ret_val[record] = item
        return ret_val

    def dequeue_records_for_process(self, records: Iterable[SapioRecord], wrapper: type[WrappedType] | None = None,
                                    criteria: QueueItemReportCriteria = QueueItemReportCriteria()) \
            -> dict[SapioRecord, list[WrappedType] | list[PyRecordModel]]:
        """
        Given a list of records, locate the process queue items that refer to them and that match the given search
        criteria and remove them from the queue by setting the ShowInQueue field on the process queue items to false.
        You must store and commit using the record model manager in order for these changes to take effect.

        IMPORTANT NOTICE: This is only for custom processes that make use of ProcessQueueItem records. For experiment
        processes that use AssignedProcess records, see the ProcessTracking class.

        :param records: The records to remove from the queue.
        :param wrapper: The record model wrapper for the process queue items being updated. If not provided, the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        :param criteria: Additional search criteria to filter the results. This function forces the show_in_queue
            parameter on the criteria to True.
        :return: A dictionary mapping each input record to the queue item records that refer to that record and were
            updated. If a record does not have any queue items that refer to it that match the given search criteria,
            then it will map to an empty list.
        """
        # Only locate queue items that are currently visible in the queue.
        criteria.shown_in_queue = True
        dequeue: dict[SapioRecord, list[WrappedType] | list[PyRecordModel]]
        dequeue = self.get_queue_items_for_records(records, wrapper, criteria)
        for record, items in dequeue.items():
            for item in items:
                item.set_field_value(ProcessQueueItemFields.SHOW_IN_QUEUE__FIELD.field_name, False)
        return dequeue

    @staticmethod
    def assigned_queue_items(queue_items: Iterable[SapioRecord], assign_to: list[str]) -> None:
        """
        Given a collection of queue items, assign them to a list of usernames or group names. Only those users in the
        listed groups or those users with the matching username will be able to see these related records in the process
        queue.
        You must store and commit using the record model manager in order for these changes to take effect.

        :param queue_items: The queue items to assign.
        :param assign_to: A list of usernames and/or group names to assign these items to.
        """
        for item in queue_items:
            item.set_field_value(ProcessQueueItemFields.ASSIGNED_TO__FIELD, ",".join(assign_to))

    def get_queue_item_workflow_trackers(self, items: Iterable[SapioRecord], wrapper: type[WrappedType]) \
            -> dict[SapioRecord, list[WrappedType]]:
        """
        When a queue item is launched into a process step, a ProcessWorkflowTracking record is created by the system
        with a side link to the process queue item. This record records information about how long the record ws in
        the queue, among other details.

        Retrieve the workflow tracker records for the input queue items.

        :param items: The queue items to load the workflow trackers of.
        :param wrapper: The record model wrapper for the ProcessWorkflowTracking records.
        :return: A dictionary mapping each queue item to the workflow trackers that side link to that item. If an input
            queue item doesn't have any workflow trackers, then it will map to an empty list.
        """
        field: str = ProcessWorkflowTrackingFields.PROCESS_QUEUE_ITEM__FIELD.field_name
        self.rec_handler.rel_man.load_reverse_side_links_of_type(list(items), wrapper, field)
        return self.rec_handler.map_to_reverse_side_links(items, field, wrapper)

    @staticmethod
    def build_queue_item_report(criteria: QueueItemReportCriteria) -> CustomReportCriteria:
        """
        Construct a custom report using the provided QueueItemReportCriteria.

        :param criteria: The criteria to construct a custom report from.
        :return: A custom report that can be used to search for queue items that match the given criteria.
        """
        dt: str = ProcessQueueItemFields.DATA_TYPE_NAME
        report_builder = CustomReportBuilder(dt)
        tb = report_builder.get_term_builder()
        report_builder.add_column(SystemFields.RECORD_ID__FIELD)
        report_builder.add_column(ProcessQueueItemFields.DATA_RECORD_ID__FIELD)

        root = tb.all_records_term()

        if criteria.process_names is not None:
            term = tb.is_term(ProcessQueueItemFields.PROCESS_HEADER_NAME__FIELD, criteria.process_names)
            root = tb.and_terms(root, term)
        if criteria.not_process_names is not None:
            term = tb.not_term(ProcessQueueItemFields.PROCESS_HEADER_NAME__FIELD, criteria.not_process_names)
            root = tb.and_terms(root, term)

        if criteria.step_names is not None:
            term = tb.is_term(ProcessQueueItemFields.WORKFLOW_HEADER_NAME__FIELD, criteria.step_names)
            root = tb.and_terms(root, term)
        if criteria.not_step_names is not None:
            term = tb.not_term(ProcessQueueItemFields.WORKFLOW_HEADER_NAME__FIELD, criteria.not_step_names)
            root = tb.and_terms(root, term)

        if criteria.data_type_names is not None:
            term = tb.is_term(ProcessQueueItemFields.DATA_TYPE_NAME__FIELD, criteria.data_type_names)
            root = tb.and_terms(root, term)
        if criteria.not_data_type_names is not None:
            term = tb.not_term(ProcessQueueItemFields.DATA_TYPE_NAME__FIELD, criteria.not_data_type_names)
            root = tb.and_terms(root, term)

        if criteria.data_record_ids is not None:
            term = tb.is_term(ProcessQueueItemFields.DATA_RECORD_ID__FIELD, criteria.data_record_ids)
            root = tb.and_terms(root, term)
        if criteria.not_data_record_ids is not None:
            term = tb.not_term(ProcessQueueItemFields.DATA_RECORD_ID__FIELD, criteria.not_data_record_ids)
            root = tb.and_terms(root, term)

        if criteria.assigned_to is not None:
            term = tb.is_term(ProcessQueueItemFields.ASSIGNED_TO__FIELD, criteria.assigned_to)
            root = tb.and_terms(root, term)
        if criteria.not_assigned_to is not None:
            term = tb.not_term(ProcessQueueItemFields.ASSIGNED_TO__FIELD, criteria.not_assigned_to)
            root = tb.and_terms(root, term)

        if criteria.launched_after is not None:
            term = tb.gte_term(ProcessQueueItemFields.LAUNCHED_DATE__FIELD, criteria.launched_after)
            root = tb.and_terms(root, term)
        if criteria.launched_before is not None:
            term = tb.lte_term(ProcessQueueItemFields.LAUNCHED_DATE__FIELD, criteria.launched_before)
            root = tb.and_terms(root, term)

        if criteria.scheduled_after is not None:
            term = tb.gte_term(ProcessQueueItemFields.LAUNCHED_DATE__FIELD, criteria.scheduled_after)
            root = tb.and_terms(root, term)
        if criteria.scheduled_before is not None:
            term = tb.lte_term(ProcessQueueItemFields.LAUNCHED_DATE__FIELD, criteria.scheduled_before)
            root = tb.and_terms(root, term)

        if criteria.shown_in_queue is not None:
            term = tb.is_term(ProcessQueueItemFields.SHOW_IN_QUEUE__FIELD, criteria.shown_in_queue)
            root = tb.and_terms(root, term)
        if criteria.has_experiment is not None:
            if criteria.has_experiment:
                term = tb.not_term(ProcessQueueItemFields.EXPERIMENT__FIELD, None)
            else:
                term = tb.is_term(ProcessQueueItemFields.EXPERIMENT__FIELD, None)
            root = tb.and_terms(root, term)

        report_builder.set_root_term(root)
        return report_builder.build_report_criteria()
