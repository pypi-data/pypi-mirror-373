from sapiopylib.rest.User import SapioUser

from sapiopycommons.general.aliases import RecordIdentifier, AliasUtil, ExperimentIdentifier, DataTypeIdentifier, \
    UserIdentifier


class ProcessTracking:
    """
    A class for calling the Foundations process tracking endpoints.

    IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
    processes that use ProcessQueueItem records, see the QueueItemHandler class.
    """
    @staticmethod
    def assign_to_process(context: UserIdentifier, data_type: DataTypeIdentifier, records: list[RecordIdentifier],
                          process_name: str, step_number: int | None = None, branch_id: int | None = None,
                          request: RecordIdentifier | None = None) -> None:
        """
        Assign the given tracked records to a new process at the specified step, settings its status to "Ready for -"
        at that step.
        Synonymous with what occurs during request creation or when using the assign to process button.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param process_name: The name of the process that the tracked records should start at.
        :param step_number: The step number that the tracked records should start at. If not provided, assumes step
            number 1.
        :param branch_id: The branch ID of the above step. Only necessary to provide if multiple steps in the process
            share the same step number.
        :param request: The request that the tracked records are a part of, to be used for the assigned process record's
            request record ID field. If none is provided, creates a new request with default fields.
        """
        sub_path = '/ext/process-tracking/assign-to-process'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "process-name": process_name,
            "step-number": step_number,
            "branch-id": branch_id,
            "request-record-id": AliasUtil.to_record_ids([request])[0] if request is not None else None
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def begin_protocol(context: UserIdentifier, data_type: DataTypeIdentifier, records: list[RecordIdentifier],
                       experiment: ExperimentIdentifier) -> None:
        """
        Begin the assigned processes of the given tracked records as the given experiment. This sets the status of the
        tracked records from "Ready for -" to "In Process -" for their current step.
        Synonymous with what occurs when starting a process step in the system.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param experiment: The experiment that the tracked records are beginning the process for. This must be the next
            step in the current process of the tracked records.
        """
        sub_path = '/ext/process-tracking/begin-protocol'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "experiment-id": AliasUtil.to_notebook_id(experiment),
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def complete_protocol(context: UserIdentifier, data_type: DataTypeIdentifier, records: list[RecordIdentifier],
                          experiment: ExperimentIdentifier) -> None:
        """
        Complete the current step that the given tracked records are at given the experiment.
        Moves the status to "Ready for -" for the next step in the process, or "Completed -" if this was the last
        step.
        Moves the status to "Failed -" if the failed flag for the tracked record is true.
        Moves the assigned process down to the descendant sample(s) if both samples are provided in the records list.
        Synonymous with what occurs when completing an experiment in the system.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param experiment: The experiment that the tracked records are currently in and completing.
        """
        sub_path = '/ext/process-tracking/complete-protocol'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "experiment-id": AliasUtil.to_notebook_id(experiment),
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def fail(context: UserIdentifier, data_type: DataTypeIdentifier, records: list[RecordIdentifier],
             experiment: ExperimentIdentifier) -> None:
        """
        Fail the assigned processes of the given tracked records, changing their statuses to "Failed -". The tracked
        records must be "In Process -" for the given step.
        Synonymous with what occurs when failing a sample due to a QC failure in a process in the system.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param experiment: The experiment that the tracked records are currently in.
        """
        sub_path = '/ext/process-tracking/fail'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "experiment-id": AliasUtil.to_notebook_id(experiment),
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def promote_to_next_by_experiment(context: UserIdentifier, data_type: DataTypeIdentifier,
                                      records: list[RecordIdentifier], experiment: ExperimentIdentifier) -> None:
        """
        Promote the status of the given tracked records to the next status in their process using an experiment.
        If the tracked records currently have a status of "Ready for -", then providing an experiment of the template
        they are ready for will move their status to "In Process -" for the experiment.
        If the tracked records currently have a status of "In Process -", then providing their current experiment
        will move their status to "Ready for -" for the next step in the process, or "Completed -" if this was the
        last step.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param experiment: The experiment that the tracked records are currently in.
        """
        sub_path = '/ext/process-tracking/promote-status-to-next'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "experiment-id": AliasUtil.to_notebook_id(experiment),
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def promote_to_next_by_step(context: UserIdentifier, data_type: DataTypeIdentifier,
                                records: list[RecordIdentifier], process_name: str, step_number: int,
                                branch_id: int | None = None) -> None:
        """
        Promote the status of the given tracked records to the next status in their process using step info.
        If the tracked records currently have a status of "Ready for -", then providing the step info for their current
        step will move their status to "In Process -" for that step.
        If the tracked records currently have a status of "In Process -", then providing the step info for their current
        step will move their status to "Ready for -" for the next step in the process, or "Completed -" if this was the
        last step.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param data_type: The data type of the tracked records.
        :param records: A list of the tracked records.
        :param process_name: The name of the process that the tracked records are currently in.
        :param step_number: The step number that the tracked records are currently in.
        :param branch_id: The branch ID of the above step. Only necessary to provide if multiple steps in the process
            share the same step number.
        """
        sub_path = '/ext/process-tracking/promote-status-to-next'
        payload = {
            "data-type-name": AliasUtil.to_data_type_name(data_type),
            "record-ids": AliasUtil.to_record_ids(records),
            "current-process-status": {
                "process-name": process_name,
                "step-number": step_number,
                "branch-id": branch_id
            }
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)

    @staticmethod
    def reprocess(context: UserIdentifier, records: list[RecordIdentifier]) -> None:
        """
        Reprocess tracked records to a previous step in their process. Reprocessing is controlled by ReturnPoint records
        which are children of the AssignedProcess on the tracked records. Creates a new AssignedProcess record for the
        effected tracked records. Any existing AssignedProcess records are untouched.
        Synonymous with what occurs when reprocessing records to a previous step due to QC failures in a process in the
        system.

        IMPORTANT NOTICE: This is only for experiment processes that make use of AssignedProcess records. For custom
        processes that use ProcessQueueItem records, see the QueueItemHandler class.

        :param context: The current webhook context or a user object to send requests from.
        :param records: A list of ReturnPoint records to reprocess to.
        """
        sub_path = '/ext/process-tracking/reprocess'
        payload = {
            "record-ids": AliasUtil.to_record_ids(records)
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, payload=payload)
        user.raise_for_status(response)
