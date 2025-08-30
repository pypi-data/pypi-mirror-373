from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, AbstractReportTerm, RawReportTerm
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment, ElnExperimentQueryCriteria, ElnTemplate
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnExperimentStatus, ElnBaseDataType
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.customreport.auto_pagers import CustomReportDictAutoPager
from sapiopycommons.customreport.custom_report_builder import CustomReportBuilder
from sapiopycommons.customreport.term_builder import TermBuilder
from sapiopycommons.datatype.pseudo_data_types import EnbEntryOptionsPseudoDef, NotebookExperimentOptionPseudoDef, \
    NotebookExperimentPseudoDef, ExperimentEntryRecordPseudoDef, EnbEntryPseudoDef
from sapiopycommons.general.aliases import SapioRecord, UserIdentifier, AliasUtil, FieldValue, \
    ExperimentEntryIdentifier, ExperimentIdentifier
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler


# FR-47234: Create an ExperimentReportCriteria class for finer experiment searching
# and create/update ExperimentReportUtil functions to use it.
class ExperimentReportCriteria:
    """
    Experiment report criteria is used to restrict the results of searches for experiments.
    """
    notebook_ids: list[int] | None
    not_notebook_ids: list[int] | None
    names: list[str] | None
    not_names: list[str] | None
    created_by: list[str] | None
    not_created_by: list[str] | None
    last_modified_by: list[str] | None
    not_last_modified_by: list[str] | None
    owners: list[str] | None
    not_owners: list[str] | None
    statuses: list[str] | None
    not_statuses: list[str] | None
    templates: str | None
    not_templates: str | None
    is_from_template: bool | None
    is_from_protocol_template: bool | None
    is_modifiable: bool | None
    is_active: bool | None
    created_before: int | None
    created_after: int | None
    due_before: int | None
    due_after: int | None
    last_modified_before: int | None
    last_modified_after: int | None

    def __init__(self, *,
                 notebook_ids: list[ExperimentIdentifier] | None = None,
                 not_notebook_ids: list[ExperimentIdentifier] | None = None,
                 names: list[str] | None = None,
                 not_names: list[str] | None = None,
                 created_by: list[str] | None = None,
                 not_created_by: list[str] | None = None,
                 last_modified_by: list[str] | None = None,
                 not_last_modified_by: list[str] | None = None,
                 owners: list[str] | None = None,
                 not_owners: list[str] | None = None,
                 statuses: list[ElnExperimentStatus | str] | None = None,
                 not_statuses: list[ElnExperimentStatus | str] | None = None,
                 templates: list[str] | None = None,
                 not_templates: list[str] | None = None,
                 is_from_template: bool | None = None,
                 is_from_protocol_template: bool | None = None,
                 is_modifiable: bool | None = None,
                 is_active: bool | None = None,
                 created_after: int | None = None,
                 created_before: int | None = None,
                 due_after: int | None = None,
                 due_before: int | None = None,
                 last_modified_after: int | None = None,
                 last_modified_before: int | None = None):
        """
        Restrict searches using the following criteria.

        :param notebook_ids: The allowed notebook ID(s) of the experiment.
        :param not_notebook_ids: The disallowed notebook ID(s) of the experiment.
        :param names: The allowed name(s) of the experiment.
        :param not_names: The disallowed name(s) of the experiment.
        :param created_by: The allowed username(s) of the user who created the experiment.
        :param not_created_by: The disallowed username(s) of the user who created the experiment.
        :param last_modified_by: The allowed username(s) of the user who last modified the experiment.
        :param not_last_modified_by: The disallowed username(s) of the user who last modified the experiment.
        :param owners: The allowed username(s) of the user who owns the experiment.
        :param not_owners: The disallowed username(s) of the user who owns the experiment.
        :param statuses: The allowed status(es) of the experiment.
        :param not_statuses: The disallowed status(es) of the experiment.
        :param templates: The allowed template name(s) that the experiment was created from.
        :param not_templates: The disallowed template name(s) that the experiment was created from.
        :param is_from_template: Whether the experiment was created from a template.
        :param is_from_protocol_template: Whether the experiment was created from a protocol template.
        :param is_modifiable: Whether the experiment is modifiable.
        :param is_active: Whether the experiment is from an active template.
        :param created_after: A timestamp after which the experiment was created.
        :param created_before: A timestamp before which the experiment was created.
        :param due_after: A timestamp after which the experiment's approval is due.
        :param due_before: A timestamp before which the experiment's approval is due.
        :param last_modified_after: A timestamp after which the experiment last modified.
        :param last_modified_before: A timestamp before which the experiment last modified.
        """
        self.notebook_ids = notebook_ids
        self.not_notebook_ids = not_notebook_ids
        self.names = names
        self.not_names = not_names
        self.created_by = created_by
        self.not_created_by = not_created_by
        self.last_modified_by = last_modified_by
        self.not_last_modified_by = not_last_modified_by
        self.owners = owners
        self.not_owners = not_owners
        self.statuses = statuses
        self.not_statuses = not_statuses
        self.templates = templates
        self.not_templates = not_templates

        self.is_from_template = is_from_template
        self.is_from_protocol_template = is_from_protocol_template
        self.is_modifiable = is_modifiable
        self.is_active = is_active

        self.created_before = created_before
        self.created_after = created_after
        self.due_before = due_before
        self.due_after = due_after
        self.last_modified_before = last_modified_before
        self.last_modified_after = last_modified_after

        if self.notebook_ids is not None:
            self.notebook_ids = AliasUtil.to_notebook_ids(self.notebook_ids)
        if self.not_notebook_ids is not None:
            self.not_notebook_ids = AliasUtil.to_notebook_ids(self.not_notebook_ids)
        if self.statuses is not None:
            self.statuses = [x.description if isinstance(x, ElnExperimentStatus) else x for x in self.statuses]
        if self.not_statuses is not None:
            self.not_statuses = [x.description if isinstance(x, ElnExperimentStatus) else x for x in self.not_statuses]


# FR-46908 - Provide a utility class that holds experiment related custom reports e.g. getting all the experiments
# that given records were used in or getting all records of a datatype used in given experiments.
class ExperimentReportUtil:
    @staticmethod
    def map_records_to_experiment_ids(context: UserIdentifier, records: list[SapioRecord]) \
            -> dict[SapioRecord, list[int]]:
        """
        Return a dictionary mapping each record to a list of ids of experiments that they were used in.
        If a record wasn't used in any experiments then it will be mapped to an empty list.

        :param context: The current webhook context or a user object to send requests from.
        :param records: A list of records of the same data type.
        :return: A dictionary mapping each record to a list of ids of each experiment it was used in.
        """
        if not records:
            return {}

        user: SapioUser = AliasUtil.to_sapio_user(context)
        data_type_name: str = AliasUtil.to_singular_data_type_name(records)

        record_ids: list[int] = AliasUtil.to_record_ids(records)
        rows = ExperimentReportUtil.__get_record_experiment_relation_rows(user, data_type_name, record_ids=record_ids)

        id_to_record: dict[int, SapioRecord] = RecordHandler.map_by_id(records)
        record_to_exps: dict[SapioRecord, set[int]] = {record: set() for record in records}
        for row in rows:
            record_id: int = row["RecordId"]
            exp_id: int = row[NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name]
            record = id_to_record[record_id]
            record_to_exps[record].add(exp_id)

        return {record: list(exps) for record, exps in record_to_exps.items()}

    @staticmethod
    def map_eln_records_to_experiment_ids(context: UserIdentifier, records: list[SapioRecord]) \
            -> dict[SapioRecord, int]:
        """
        Return a dictionary mapping each ELN record to the ID of the experiments that each were used in.

        :param context: The current webhook context or a user object to send requests from.
        :param records: A list of ELN data type records. They are permitted to be of mixed data type names.
        :return: A dictionary mapping each record to the ID of the experiment it was used in.
        """
        if not records:
            return {}

        data_types: set[str] = AliasUtil.to_data_type_names(records, True, False)
        for data_type in data_types:
            if not ElnBaseDataType.is_eln_type(data_type):
                raise SapioException(f"Data type {data_type} is not an ELN data type.")

        dt_to_record: dict[str, list[SapioRecord]] = {}
        for record in records:
            dt_to_record.setdefault(AliasUtil.to_data_type_name(record, False), []).append(record)

        report_builder = CustomReportBuilder(EnbEntryPseudoDef.DATA_TYPE_NAME)
        tb = report_builder.get_term_builder()
        report_builder.add_column(EnbEntryPseudoDef.DATA_TYPE_NAME__FIELD_NAME)
        report_builder.add_column(EnbEntryPseudoDef.EXPERIMENT_ID__FIELD_NAME)
        report_builder.set_root_term(tb.is_term(EnbEntryPseudoDef.DATA_TYPE_NAME__FIELD_NAME, data_types))
        criteria = report_builder.build_report_criteria()

        ret_val: dict[SapioRecord, int] = {}
        rows: list[dict[str, FieldValue]] = CustomReportDictAutoPager(context, criteria).get_all_at_once()
        for row in rows:
            dt: str = row[EnbEntryPseudoDef.DATA_TYPE_NAME__FIELD_NAME.field_name]
            exp_id: int = row[EnbEntryPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name]
            for record in dt_to_record[dt]:
                ret_val[record] = exp_id
        return ret_val

    # CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
    @staticmethod
    def map_experiments_to_records_of_type(context: UserIdentifier, exp_ids: list[ExperimentIdentifier],
                                           wrapper_type: type[WrappedType] | str) \
            -> dict[int, list[WrappedType] | list[PyRecordModel]]:
        """
        Return a dictionary mapping each experiment id to a list of records of the given type that were used in each
        experiment. If an experiment didn't use any records of the given type then it will be mapped to an empty list.

        :param context: The current webhook context or a user object to send requests from.
        :param exp_ids: A list of experiment identifiers.
        :param wrapper_type: The record model wrapper or data type name to use, corresponds to which data type we will
            query for. If a data type name is provided, the returned records will be PyRecordModels instead of
            WrappedRecordModels.
        :return: A dictionary mapping each experiment id to a list of records of the given type that were used in that
            experiment.
        """
        if not exp_ids:
            return {}

        user = AliasUtil.to_sapio_user(context)
        record_handler = RecordHandler(user)
        data_type_name: str = AliasUtil.to_data_type_name(wrapper_type)

        exp_ids: list[int] = AliasUtil.to_notebook_ids(exp_ids)
        rows = ExperimentReportUtil.__get_record_experiment_relation_rows(user, data_type_name, exp_ids=exp_ids)
        record_ids: set[int] = {row["RecordId"] for row in rows}
        records = record_handler.query_models_by_id(wrapper_type, record_ids)

        id_to_record: dict[int, WrappedType] = RecordHandler.map_by_id(records)
        exp_to_records: dict[int, set[SapioRecord]] = {exp: set() for exp in exp_ids}
        for row in rows:
            record_id: int = row["RecordId"]
            exp_id: int = row[NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name]
            record = id_to_record[record_id]
            exp_to_records[exp_id].add(record)

        return {exp: list(records) for exp, records in exp_to_records.items()}

    @staticmethod
    def get_experiment_options(context: UserIdentifier, experiments: list[ExperimentIdentifier | ElnTemplate]) \
            -> dict[int, dict[str, str]]:
        """
        Run a custom report to retrieve the experiment options for all the provided experiments or experiment templates.
        Effectively a batched version of the get_notebook_experiment_options function of ElnManager.

        :param context: The current webhook context or a user object to send requests from.
        :param experiments: The experiment/template identifiers to retrieve the experiment options for.
        :return: A dictionary mapping the notebook experiment ID to the options for that experiment.
        """
        exp_ids: list[int] = []
        for exp in experiments:
            if isinstance(exp, ElnTemplate):
                exp_ids.append(exp.template_id)
            else:
                exp_ids.append(AliasUtil.to_notebook_id(exp))

        report_builder = CustomReportBuilder(NotebookExperimentOptionPseudoDef.DATA_TYPE_NAME)
        tb = report_builder.get_term_builder()
        root = tb.is_term(NotebookExperimentOptionPseudoDef.EXPERIMENT_ID__FIELD_NAME, exp_ids)
        report_builder.set_root_term(root)
        report_builder.add_column(NotebookExperimentOptionPseudoDef.EXPERIMENT_ID__FIELD_NAME)
        report_builder.add_column(NotebookExperimentOptionPseudoDef.OPTION_KEY__FIELD_NAME)
        report_builder.add_column(NotebookExperimentOptionPseudoDef.OPTION_VALUE__FIELD_NAME)
        report = report_builder.build_report_criteria()

        # Ensure that each experiment appears in the dictionary, even if it has no experiment options.
        options: dict[int, dict[str, str]] = {x: {} for x in exp_ids}
        results: list[dict[str, FieldValue]] = CustomReportDictAutoPager(context, report).get_all_at_once()
        for row in results:
            exp_id: int = row[NotebookExperimentOptionPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name]
            key: str = row[NotebookExperimentOptionPseudoDef.OPTION_KEY__FIELD_NAME.field_name]
            value: str = row[NotebookExperimentOptionPseudoDef.OPTION_VALUE__FIELD_NAME.field_name]
            options[exp_id][key] = value
        return options

    @staticmethod
    def get_experiment_entry_options(context: UserIdentifier, entries: list[ExperimentEntryIdentifier]) \
            -> dict[int, dict[str, str]]:
        """
        Run a custom report to retrieve the entry options for all the provided entries. Effectively a batched
        version of the get_experiment_entry_options function of ElnManager.

        :param context: The current webhook context or a user object to send requests from.
        :param entries: The experiment entry identifiers to retrieve the entry options for.
        :return: A dictionary mapping the entry ID to the options for that entry.
        """
        entries: list[int] = AliasUtil.to_entry_ids(entries)
        report_builder = CustomReportBuilder(EnbEntryOptionsPseudoDef.DATA_TYPE_NAME)
        tb = report_builder.get_term_builder()
        root = tb.is_term(EnbEntryOptionsPseudoDef.ENTRY_ID__FIELD_NAME, entries)
        report_builder.set_root_term(root)
        report_builder.add_column(EnbEntryOptionsPseudoDef.ENTRY_ID__FIELD_NAME)
        report_builder.add_column(EnbEntryOptionsPseudoDef.ENTRY_OPTION_KEY__FIELD_NAME)
        report_builder.add_column(EnbEntryOptionsPseudoDef.ENTRY_OPTION_VALUE__FIELD_NAME)
        report = report_builder.build_report_criteria()

        # Ensure that each entry appears in the dictionary, even if it has no entry options.
        options: dict[int, dict[str, str]] = {x: {} for x in entries}
        results: list[dict[str, FieldValue]] = CustomReportDictAutoPager(context, report).get_all_at_once()
        for row in results:
            entry_id: int = row[EnbEntryOptionsPseudoDef.ENTRY_ID__FIELD_NAME.field_name]
            key: str = row[EnbEntryOptionsPseudoDef.ENTRY_OPTION_KEY__FIELD_NAME.field_name]
            value: str = row[EnbEntryOptionsPseudoDef.ENTRY_OPTION_VALUE__FIELD_NAME.field_name]
            options[entry_id][key] = value
        return options

    @staticmethod
    def get_template_names_for_experiments(context: UserIdentifier, experiments: list[ExperimentIdentifier]) \
            -> dict[int, str]:
        """
        Run a custom report to retrieve the template names for all the provided experiments.

        :param context: The current webhook context or a user object to send requests from.
        :param experiments: The experiment identifiers to retrieve the template names for.
        :return: A dictionary mapping the notebook experiment ID to the template name that the experiment was created from.
        """
        exp_ids: list[int] = AliasUtil.to_notebook_ids(experiments)

        report_builder = CustomReportBuilder(NotebookExperimentPseudoDef.DATA_TYPE_NAME)
        tb = report_builder.get_term_builder()
        root = tb.is_term(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME, exp_ids)
        report_builder.add_join(tb.compare_is_term("ELNExperiment",
                                                   "RecordId",
                                                   NotebookExperimentPseudoDef.DATA_TYPE_NAME,
                                                   NotebookExperimentPseudoDef.EXPERIMENT_RECORD_ID__FIELD_NAME))
        report_builder.set_root_term(root)
        report_builder.add_column(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME)
        report_builder.add_column("TemplateExperimentName", FieldType.STRING, data_type="ELNExperiment")
        report = report_builder.build_report_criteria()

        ret_val: dict[int, str] = {}
        results: list[dict[str, FieldValue]] = CustomReportDictAutoPager(context, report).get_all_at_once()
        for row in results:
            exp_id: int = row[NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name]
            name: str = row["TemplateExperimentName"]
            ret_val[exp_id] = name
        return ret_val

    @staticmethod
    def get_experiments_for_criteria(context: UserIdentifier, criteria: ExperimentReportCriteria) -> list[ElnExperiment]:
        """
        Run a custom report that retrieves every experiment in the system for the given search criteria.

        :param context: The current webhook context or a user object to send requests from.
        :param criteria: The search criteria to query for experiments with.
        :return: A list of every experiment in the system that matches the search criteria.
        """
        report: CustomReportCriteria = ExperimentReportUtil.build_experiment_id_report(criteria)
        return ExperimentReportUtil.get_experiments_for_report(context, report)

    @staticmethod
    def get_experiments_by_name(context: UserIdentifier, name: str,
                                criteria: ExperimentReportCriteria = ExperimentReportCriteria()) -> list[ElnExperiment]:
        """
        Run a custom report that retrieves every experiment in the system with a given name.

        :param context: The current webhook context or a user object to send requests from.
        :param name: The name of the experiment to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A list of every experiment in the system with a name that matches the input
            that matches the given criteria.
        """
        return ExperimentReportUtil.get_experiments_by_names(context, [name], criteria)[name]

    @staticmethod
    def get_experiments_by_names(context: UserIdentifier, names: list[str],
                                 criteria: ExperimentReportCriteria = ExperimentReportCriteria()) -> dict[str, list[ElnExperiment]]:
        """
        Run a custom report that retrieves every experiment in the system with a name from a list of names.

        :param context: The current webhook context or a user object to send requests from.
        :param names: The names of the experiment to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A dictionary mapping the experiment name to a list of every experiment in the system with that name
            that matches the given criteria.
        """
        criteria.names = names
        experiments: list[ElnExperiment] = ExperimentReportUtil.get_experiments_for_criteria(context, criteria)

        # Ensure that each name appears in the dictionary, even if it has no experiments.
        ret_val: dict[str, list[ElnExperiment]] = {x: [] for x in names}
        for experiment in experiments:
            ret_val.get(experiment.notebook_experiment_name).append(experiment)
        return ret_val

    @staticmethod
    def get_experiments_by_owner(context: UserIdentifier, owner: str,
                                 criteria: ExperimentReportCriteria = ExperimentReportCriteria()) -> list[ElnExperiment]:
        """
        Run a custom report that retrieves every experiment in the system with a given owner.

        :param context: The current webhook context or a user object to send requests from.
        :param owner: The username of the owner of the experiments to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A list of every experiment in the system with the owner that matches the input
            that matches the given criteria.
        """
        return ExperimentReportUtil.get_experiments_by_owners(context, [owner], criteria)[owner]

    @staticmethod
    def get_experiments_by_owners(context: UserIdentifier, owners: list[str],
                                  criteria: ExperimentReportCriteria = ExperimentReportCriteria) \
            -> dict[str, list[ElnExperiment]]:
        """
        Run a custom report that retrieves every experiment in the system with a given list of owners.

        :param context: The current webhook context or a user object to send requests from.
        :param owners: The usernames of the owner of the experiments to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A dictionary mapping the owner username to a list of every experiment in the system from that owner
            that matches the given criteria.
        """
        criteria.owners = owners
        experiments: list[ElnExperiment] = ExperimentReportUtil.get_experiments_for_criteria(context, criteria)

        # Ensure that each name appears in the dictionary, even if it has no experiments.
        ret_val: dict[str, list[ElnExperiment]] = {x: [] for x in owners}
        for experiment in experiments:
            ret_val.get(experiment.owner).append(experiment)
        return ret_val

    @staticmethod
    def get_experiments_by_creator(context: UserIdentifier, created_by: str,
                                   criteria: ExperimentReportCriteria = ExperimentReportCriteria()) \
            -> list[ElnExperiment]:
        """
        Run a custom report that retrieves every experiment in the system with a given creator.

        :param context: The current webhook context or a user object to send requests from.
        :param created_by: The username of the creator of the experiments to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A list of every experiment in the system with the creator that matches the input
            that matches the given criteria.
        """
        return ExperimentReportUtil.get_experiments_by_creators(context, [created_by], criteria=criteria)[created_by]

    @staticmethod
    def get_experiments_by_creators(context: UserIdentifier, created_by: list[str],
                                    criteria: ExperimentReportCriteria = ExperimentReportCriteria()) \
            -> dict[str, list[ElnExperiment]]:
        """
        Run a custom report that retrieves every experiment in the system with a given list of creators.

        :param context: The current webhook context or a user object to send requests from.
        :param created_by: The usernames of the creator of the experiments to query for.
        :param criteria: Additional search criteria to filter the results.
        :return: A dictionary mapping the owner username to a list of every experiment in the system from that creator
            that matches the given criteria.
        """
        criteria.created_by = created_by
        experiments: list[ElnExperiment] = ExperimentReportUtil.get_experiments_for_criteria(context, criteria)

        # Ensure that each name appears in the dictionary, even if it has no experiments.
        ret_val: dict[str, list[ElnExperiment]] = {x: [] for x in created_by}
        for experiment in experiments:
            ret_val.get(experiment.created_by).append(experiment)
        return ret_val

    @staticmethod
    def build_experiment_id_report(criteria: ExperimentReportCriteria = ExperimentReportCriteria()) \
            -> CustomReportCriteria:
        """
        Construct a custom report using the provided ExperimentReportCriteria.

        :param criteria: The criteria to construct a custom report from.
        :return: A custom report that can be used to search for experiment IDs that match the given criteria.
        """
        dt: str = NotebookExperimentPseudoDef.DATA_TYPE_NAME
        report_builder = CustomReportBuilder(dt)
        tb = report_builder.get_term_builder()
        report_builder.add_column(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME)

        root: AbstractReportTerm | None = None
        if criteria.notebook_ids is not None:
            root = tb.is_term(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME, criteria.notebook_ids)
        if criteria.not_notebook_ids is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME, criteria.not_notebook_ids)
            if root is not None:
                root = tb.and_terms(root, term)
        if root is None:
            root = ExperimentReportUtil.all_notebook_experiments_term()

        if criteria.names is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.EXPERIMENT_NAME__FIELD_NAME, criteria.names)
            root = tb.and_terms(root, term)
        if criteria.not_names is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.EXPERIMENT_NAME__FIELD_NAME, criteria.not_names)
            root = tb.and_terms(root, term)

        if criteria.created_by is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.CREATED_BY__FIELD_NAME, criteria.created_by)
            root = tb.and_terms(root, term)
        if criteria.not_created_by is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.CREATED_BY__FIELD_NAME, criteria.not_created_by)
            root = tb.and_terms(root, term)

        if criteria.last_modified_by is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.LAST_MODIFIED_BY__FIELD_NAME, criteria.last_modified_by)
            root = tb.and_terms(root, term)
        if criteria.not_last_modified_by is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.LAST_MODIFIED_BY__FIELD_NAME, criteria.not_last_modified_by)
            root = tb.and_terms(root, term)

        if criteria.owners is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.EXPERIMENT_OWNER__FIELD_NAME, criteria.owners)
            root = tb.and_terms(root, term)
        if criteria.not_owners is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.EXPERIMENT_OWNER__FIELD_NAME, criteria.not_owners)
            root = tb.and_terms(root, term)

        if criteria.statuses is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.STATUS__FIELD_NAME, criteria.statuses)
            root = tb.and_terms(root, term)
        if criteria.not_statuses is not None:
            term = tb.not_term(NotebookExperimentPseudoDef.STATUS__FIELD_NAME, criteria.not_statuses)
            root = tb.and_terms(root, term)

        # For the template name term, we need to join on the experiment record.
        if criteria.templates is not None or criteria.not_templates is not None:
            join = tb.compare_is_term("ELNExperiment",
                                      "RecordId",
                                      NotebookExperimentPseudoDef.DATA_TYPE_NAME,
                                      NotebookExperimentPseudoDef.EXPERIMENT_RECORD_ID__FIELD_NAME)
            report_builder.add_join(join)
        if criteria.templates is not None:
            term = tb.is_term("TemplateExperimentName", criteria.templates, data_type="ELNExperiment")
            root = tb.and_terms(root, term)
        if criteria.not_templates is not None:
            term = tb.not_term("TemplateExperimentName", criteria.not_templates, data_type="ELNExperiment")
            root = tb.and_terms(root, term)

        if criteria.is_from_template is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.IS_TEMPLATE__FIELD_NAME, criteria.is_from_template)
            root = tb.and_terms(root, term)
        if criteria.is_from_protocol_template is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.IS_PROTOCOL_TEMPLATE__FIELD_NAME, criteria.is_from_protocol_template)
            root = tb.and_terms(root, term)
        if criteria.is_modifiable is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.IS_MODIFIABLE__FIELD_NAME, criteria.is_modifiable)
            root = tb.and_terms(root, term)
        if criteria.is_active is not None:
            term = tb.is_term(NotebookExperimentPseudoDef.IS_ACTIVE__FIELD_NAME, criteria.is_active)
            root = tb.and_terms(root, term)

        if criteria.created_after is not None:
            term = tb.gte_term(NotebookExperimentPseudoDef.DATE_CREATED__FIELD_NAME, criteria.created_after)
            root = tb.and_terms(root, term)
        if criteria.created_before is not None:
            term = tb.lte_term(NotebookExperimentPseudoDef.DATE_CREATED__FIELD_NAME, criteria.created_before)
            root = tb.and_terms(root, term)

        if criteria.last_modified_after is not None:
            term = tb.gte_term(NotebookExperimentPseudoDef.LAST_MODIFIED_DATE__FIELD_NAME, criteria.last_modified_after)
            root = tb.and_terms(root, term)
        if criteria.last_modified_before is not None:
            term = tb.lte_term(NotebookExperimentPseudoDef.LAST_MODIFIED_DATE__FIELD_NAME, criteria.last_modified_before)
            root = tb.and_terms(root, term)

        if criteria.due_after is not None:
            term = tb.gte_term(NotebookExperimentPseudoDef.APPROVAL_DUE_DATE__FIELD_NAME, criteria.due_after)
            root = tb.and_terms(root, term)
        if criteria.due_before is not None:
            term = tb.lte_term(NotebookExperimentPseudoDef.APPROVAL_DUE_DATE__FIELD_NAME, criteria.due_before)
            root = tb.and_terms(root, term)

        report_builder.set_root_term(root)
        return report_builder.build_report_criteria()

    @staticmethod
    def get_experiments_for_report(context: UserIdentifier, report: CustomReportCriteria) -> list[ElnExperiment]:
        """
        Retrieve the ELN experiment objects for experiments whose notebook IDs appear in a custom report.

        :param context: The current webhook context or a user object to send requests from.
        :param report: A custom report that searches for ELN experiments, containing an "Experiment ID" column to
            query for the experiments of.
        :return: The ELN experiments that match the provided report.
        """
        user = AliasUtil.to_sapio_user(context)
        exp_ids: list[int] = []
        for row in CustomReportDictAutoPager(user, report):
            exp_ids.append(row[NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME.field_name])
        if not exp_ids:
            return []

        criteria = ElnExperimentQueryCriteria(notebook_experiment_id_white_list=exp_ids)
        return ElnManager(user).get_eln_experiment_by_criteria(criteria)

    @staticmethod
    def all_notebook_experiments_term() -> RawReportTerm:
        """
        :return: A report term searching for all notebook experiments.
        """
        tb = TermBuilder(NotebookExperimentPseudoDef.DATA_TYPE_NAME)
        return tb.gte_term(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME, 0)

    @staticmethod
    def __get_record_experiment_relation_rows(user: SapioUser, data_type_name: str, record_ids: list[int] | None = None,
                                              exp_ids: list[int] | None = None) -> list[dict[str, FieldValue]]:
        """
        Return a list of dicts mapping \"RECORDID\" to the record id and \"EXPERIMENTID\" to the experiment id.
        At least one of record_ids and exp_ids should be provided.
        """
        assert (record_ids or exp_ids)

        report_builder = CustomReportBuilder(data_type_name)
        tb = report_builder.get_term_builder()
        if record_ids:
            records_term = tb.is_term("RecordId", record_ids)
        else:
            # Get all records of the given type
            records_term = tb.all_records_term()

        if exp_ids:
            exp_term = tb.is_term(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME, exp_ids,
                                  data_type=NotebookExperimentPseudoDef.DATA_TYPE_NAME)
        else:
            # Get all experiments
            exp_term = ExperimentReportUtil.all_notebook_experiments_term()

        root_term = tb.and_terms(records_term, exp_term)

        # Join records on the experiment entry records that correspond to them.
        records_entry_join = tb.compare_is_term(data_type_name,
                                                "RecordId",
                                                ExperimentEntryRecordPseudoDef.DATA_TYPE_NAME,
                                                ExperimentEntryRecordPseudoDef.RECORD_ID__FIELD_NAME)
        # Join entry records on the experiment entries they are in.
        experiment_entry_enb_entry_join = tb.compare_is_term(EnbEntryPseudoDef.DATA_TYPE_NAME,
                                                             EnbEntryPseudoDef.ENTRY_ID__FIELD_NAME,
                                                             ExperimentEntryRecordPseudoDef.DATA_TYPE_NAME,
                                                             ExperimentEntryRecordPseudoDef.ENTRY_ID__FIELD_NAME)
        # Join entries on the experiments they are in.
        enb_entry_experiment_join = tb.compare_is_term(NotebookExperimentPseudoDef.DATA_TYPE_NAME,
                                                       NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME,
                                                       EnbEntryPseudoDef.DATA_TYPE_NAME,
                                                       EnbEntryPseudoDef.EXPERIMENT_ID__FIELD_NAME)

        report_builder.set_root_term(root_term)
        report_builder.add_column("RecordId", FieldType.LONG)
        report_builder.add_column(NotebookExperimentPseudoDef.EXPERIMENT_ID__FIELD_NAME,
                                  data_type=NotebookExperimentPseudoDef.DATA_TYPE_NAME)
        report_builder.add_join(records_entry_join, ExperimentEntryRecordPseudoDef.DATA_TYPE_NAME)
        report_builder.add_join(experiment_entry_enb_entry_join, EnbEntryPseudoDef.DATA_TYPE_NAME)
        report_builder.add_join(enb_entry_experiment_join, NotebookExperimentPseudoDef.DATA_TYPE_NAME)
        return CustomReportDictAutoPager(user, report_builder.build_report_criteria()).get_all_at_once()
