from __future__ import annotations

import warnings
from collections.abc import Mapping, Iterable
from typing import TypeAlias
from weakref import WeakValueDictionary

from sapiopycommons.eln.experiment_cache import ExperimentCacheManager
from sapiopycommons.eln.experiment_report_util import ExperimentReportUtil
from sapiopycommons.general.aliases import AliasUtil, SapioRecord, ExperimentIdentifier, UserIdentifier, \
    DataTypeIdentifier, RecordModel, ExperimentEntryIdentifier
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnExperiment, TemplateExperimentQueryPojo, ElnTemplate, \
    InitializeNotebookExperimentPojo, ElnExperimentUpdateCriteria
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntry, ExperimentTableEntry, ExperimentFormEntry, \
    ExperimentAttachmentEntry, ExperimentPluginEntry, ExperimentDashboardEntry, ExperimentTextEntry, \
    ExperimentTempDataEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import AbstractElnEntryUpdateCriteria, \
    ElnTableEntryUpdateCriteria, ElnFormEntryUpdateCriteria, ElnAttachmentEntryUpdateCriteria, \
    ElnPluginEntryUpdateCriteria, ElnDashboardEntryUpdateCriteria, ElnTextEntryUpdateCriteria, \
    ElnTempDataEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ExperimentEntryStatus, ElnExperimentStatus, ElnEntryType, \
    ElnBaseDataType
from sapiopylib.rest.pojo.eln.eln_headings import ElnExperimentTab, ElnExperimentTabAddCriteria
from sapiopylib.rest.pojo.eln.protocol_template import ProtocolTemplateInfo
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookDirective import ElnExperimentDirective
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.Protocols import ElnEntryStep, ElnExperimentProtocol
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelInstanceManager, RecordModelManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType
from sapiopylib.rest.utils.recordmodel.properties import Child

Step: TypeAlias = str | ExperimentEntryIdentifier
"""An object representing an identifier to an entry in a particular experiment. This may be the name of the experiment,
or a typical experiment entry identifier."""
Tab: TypeAlias = int | str | ElnExperimentTab
"""An object representing an identifier to a tab in a particular experiment. This may be the tab's order, its name,
or the tab object itself."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class ExperimentHandler:
    user: SapioUser
    context: SapioWebhookContext | None
    """The context that this handler is working from, if any."""

    # CR-47485: Made variables protected instead of private.
    # Basic experiment info from the context.
    _eln_exp: ElnExperiment
    """The ELN experiment from the context."""
    _protocol: ElnExperimentProtocol
    """The ELN experiment as a protocol."""
    _exp_id: int
    """The ID of this experiment's notebook. Used for making update webservice calls."""

    # Managers.
    _eln_man: ElnManager
    """The ELN manager. Used for updating the experiment and its steps."""
    _exp_cache: ExperimentCacheManager
    """The experiment cache manager. Used for caching experiment-related information."""
    _inst_man: RecordModelInstanceManager
    """The record model instance manager. Used for wrapping the data records of a step as record models."""
    _rec_handler: RecordHandler
    """The record handler. Also used for wrapping the data records of a step as record models."""

    # Only a fraction of the information about the current experiment exists in the context. Much information requires
    # additional queries to obtain, but may also be repeatedly accessed. In such cases, cache the information after it
    # has been requested so that the user doesn't need to worry about caching it themselves.
    # CR-46341: Replace class variables with instance variables.
    _exp_record: DataRecord | None
    """The data record for this experiment. Only cached when first accessed."""
    _exp_template: ElnTemplate | None
    """The template for this experiment. Only cached when first accessed."""
    _exp_options: dict[str, str]
    """Experiment options for this experiment. Only cached when first accessed."""

    _queried_all_steps: bool
    """Whether this ExperimentHandler has queried the system for all steps in the experiment."""
    _steps: list[ElnEntryStep]
    """The sorted list of steps for this experiment. All steps are cached the first time any individual step is accessed."""
    _steps_by_name: dict[str, ElnEntryStep]
    """Steps from this experiment by their name. All steps are cached the first time any individual step is accessed."""
    _steps_by_id: dict[int, ElnEntryStep]
    """Steps from this experiment by their ID. All steps are cached the first time any individual step is accessed."""
    _step_options: dict[int, dict[str, str]]
    """Entry options for each step in this experiment. All entry options are cached the first time any individual step's
    options are queried. The cache is updated whenever the entry options for a step are changed by this handler."""

    _step_updates: dict[int, AbstractElnEntryUpdateCriteria]
    """A dictionary of entry updates that have been made by this handler. Used to batch update entries."""

    _queried_all_tabs: bool
    """Whether this ExperimentHandler has queried the system for all tabs in the experiment."""
    _tabs: list[ElnExperimentTab]
    """The sorted tabs for this experiment. Only cached when first accessed."""
    _tabs_by_id: dict[int, ElnExperimentTab]
    """The tabs for this experiment by their ID. Only cached when first accessed."""
    _tabs_by_name: dict[str, ElnExperimentTab]
    """The tabs for this experiment by their name. Only cached when first accessed."""

    # Constants
    _ENTRY_COMPLETE_STATUSES = [ExperimentEntryStatus.Completed, ExperimentEntryStatus.CompletedApproved]
    """The set of statuses that an ELN entry could have and be considered completed/submitted."""
    _ENTRY_LOCKED_STATUSES = [ExperimentEntryStatus.Completed, ExperimentEntryStatus.CompletedApproved,
                              ExperimentEntryStatus.Disabled, ExperimentEntryStatus.LockedAwaitingApproval,
                              ExperimentEntryStatus.LockedRejected]
    """The set of statuses that an ELN entry could have and be considered locked."""
    _EXPERIMENT_COMPLETE_STATUSES = [ElnExperimentStatus.Completed, ElnExperimentStatus.CompletedApproved]
    """The set of statuses that an ELN experiment could have and be considered completed."""
    _EXPERIMENT_LOCKED_STATUSES = [ElnExperimentStatus.Completed, ElnExperimentStatus.CompletedApproved,
                                   ElnExperimentStatus.LockedRejected, ElnExperimentStatus.LockedAwaitingApproval,
                                   ElnExperimentStatus.Canceled]
    """The set of statuses that an ELN experiment could have and be considered locked."""

    __instances: WeakValueDictionary[str, ExperimentHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None):
        """
        :param context: The current webhook context or a user object to send requests from.
        :param experiment: If an experiment is provided that is separate from the experiment that is in the context,
            that experiment will be used by this ExperimentHandler instead. An experiment can be provided in various
            forms, including an ElnExperiment, ElnExperimentProtocol, an experiment record, or a notebook experiment ID.
        """
        param_results = cls.__parse_params(context, experiment)
        user = param_results[0]
        experiment = param_results[2]
        key = f"{user.__hash__()}:{experiment.notebook_experiment_id}"
        obj = cls.__instances.get(key)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[key] = obj
        return obj

    def __init__(self, context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None):
        """
        Initialization will throw an exception if there is no ELN Experiment in the provided context and no experiment
        is provided.

        :param context: The current webhook context or a user object to send requests from.
        :param experiment: If an experiment is provided that is separate from the experiment that is in the context,
            that experiment will be used by this ExperimentHandler instead. An experiment can be provided in various
            forms, including an ElnExperiment, ElnExperimentProtocol, an experiment record, or a notebook experiment ID.
        """
        param_results = self.__parse_params(context, experiment)
        self.user = param_results[0]
        self.context = param_results[1]
        experiment = param_results[2]

        # Get the basic information about this experiment that already exists in the context and is often used.
        self._eln_exp = experiment
        self._protocol = ElnExperimentProtocol(experiment, self.user)
        self._exp_id = self._protocol.get_id()

        # Grab various managers that may be used.
        self._eln_man = DataMgmtServer.get_eln_manager(self.user)
        self._exp_cache = ExperimentCacheManager(self.user)
        self._inst_man = RecordModelManager(self.user).instance_manager
        self._rec_handler = RecordHandler(self.user)

        # Create empty caches to fill when necessary.
        self._queried_all_steps = False
        self._steps_by_name = {}
        self._steps_by_id = {}
        self._steps = []
        self._step_options = {}
        self._step_updates = {}

        self._tabs = []
        self._tabs_by_id = {}
        self._tabs_by_name = {}

        self._queried_all_tabs = False

        # CR-46330: Cache any experiment entry information that might already exist in the context.
        # We can only trust the entries in the context if the experiment that this handler is for is the same as the
        # one from the context.
        if self.context is not None and self.context.eln_experiment == experiment:
            cache_steps: list[ElnEntryStep] = []
            if self.context.experiment_entry is not None:
                cache_steps.append(ElnEntryStep(self._protocol, self.context.experiment_entry))
            if self.context.experiment_entry_list is not None:
                for entry in self.context.experiment_entry_list:
                    cache_steps.append(ElnEntryStep(self._protocol, entry))
            for step in cache_steps:
                self._steps.append(step)
                self._steps_by_name.update({step.get_name(): step})
                self._steps_by_id.update({step.get_id(): step})

    @staticmethod
    def __parse_params(context: UserIdentifier, experiment: ExperimentIdentifier | SapioRecord | None = None) \
            -> tuple[SapioUser, SapioWebhookContext | None, ElnExperiment]:
        if isinstance(context, SapioWebhookContext):
            user = context.user
            context = context
        else:
            user = context
            context = None
        if context is not None and context.eln_experiment is not None and experiment is None:
            experiment = context.eln_experiment
        # FR-46495 - Allow the init function of ExperimentHandler to take in an ElnExperiment that is separate from the
        # context.
        # CR-37038 - Allow other experiment object types to be provided. Convert them all down to ElnExperiment.
        if (context is None or context.eln_experiment is None) and experiment is not None:
            eln_manager = DataMgmtServer.get_eln_manager(user)
            # If this object is already an ElnExperiment, do nothing.
            if isinstance(experiment, ElnExperiment):
                pass
            # If this object is an ElnExperimentProtocol, then we can get the ElnExperiment from the object.
            elif isinstance(experiment, ElnExperimentProtocol):
                experiment: ElnExperiment = experiment.eln_experiment
            # If this object is an integer, assume it is a notebook ID that we can query the system with.
            elif isinstance(experiment, int):
                notebook_id: int = experiment
                experiment: ElnExperiment = eln_manager.get_eln_experiment_by_id(notebook_id)
                if not experiment:
                    raise SapioException(f"No experiment with notebook ID {notebook_id} located in the system.")
            # If this object is a record, assume it is an experiment record that we can query the system with.
            else:
                record_id: int = AliasUtil.to_record_ids([experiment])[0]
                experiment: ElnExperiment = eln_manager.get_eln_experiment_by_record_id(record_id)
                if not experiment:
                    raise SapioException(f"No experiment with record ID {record_id} located in the system.")
        if experiment is None:
            raise SapioException("Cannot initialize ExperimentHandler. No ELN Experiment found in the provided "
                                 "parameters.")

        return user, context, experiment

    @property
    def protocol(self) -> ElnExperimentProtocol:
        """
        The ELN experiment that this handler is for as a protocol object.
        """
        return self._protocol

    # CR-47485: Add methods for clearing and updating the caches of this ExperimentHandler.
    def clear_all_caches(self) -> None:
        """
        Clear all caches that this ExperimentHandler uses.
        """
        self.clear_step_caches()
        self.clear_experiment_caches()
        self.clear_tab_caches()

    def clear_step_caches(self) -> None:
        """
        Clear the step caches that this ExperimentHandler uses.
        """
        self._queried_all_steps = False
        self._steps.clear()
        self._steps_by_name.clear()
        self._steps_by_id.clear()
        self._step_options.clear()
        self._step_updates.clear()

    def clear_experiment_caches(self) -> None:
        """
        Clear the experiment information caches that this ExperimentHandler uses.
        """
        self._exp_record = None
        self._exp_template = None
        self._exp_options = {}

    def clear_tab_caches(self) -> None:
        """
        Clear the tab caches that this ExperimentHandler uses.
        """
        self._queried_all_tabs = False
        self._tabs.clear()
        self._tabs_by_id.clear()
        self._tabs_by_name.clear()

    def add_entry_to_caches(self, entry: ExperimentEntry | ElnEntryStep) -> ElnEntryStep:
        """
        Add the given entry to the cache of steps for this experiment. This is necessary in order for certain methods to
        work. You should only need to do this if you have created a new entry in your code using a method outside
        of this ExperimentHandler.

        :param entry: The entry to add to the cache.
        :return: The entry that was added to the cache as an ElnEntryStep.
        """
        # ExperimentEntries are stored as ElnEntrySteps in the cache.
        if isinstance(entry, ExperimentEntry):
            entry = ElnEntryStep(self._protocol, entry)
        # PR-47699: Confirm that this entry is part of the experiment that this handler is for.
        if entry.eln_entry.parent_experiment_id != self._exp_id:
            raise SapioException(f"Entry with ID {entry.get_id()} is not part of the experiment with ID "
                                 f"{self._exp_id}.")
        # PR-47699: Don't add the entry if it is already in the cache.
        if entry.get_id() not in self._steps_by_id:
            self._steps.append(entry)
            self._steps_by_name.update({entry.get_name(): entry})
            self._steps_by_id.update({entry.get_id(): entry})
            # Skipping the options cache. The get_step_options method will update that cache when necessary.
        return entry

    def add_entries_to_caches(self, entries: list[ExperimentEntry | ElnEntryStep]) -> list[ElnEntryStep]:
        """
        Add the given entries to the cache of steps for this experiment. This is necessary in order for certain methods
        to work. You should only need to do this if you have created a new entry in your code using a method outside
        of this ExperimentHandler.

        :param entries: The entries to add to the cache.
        :return: The entries that were added to the cache as ElnEntrySteps.
        """
        new_entries: list[ElnEntryStep] = []
        for entry in entries:
            new_entries.append(self.add_entry_to_caches(entry))
        return new_entries

    def add_tab_to_cache(self, tab: ElnExperimentTab) -> None:
        """
        Add the given tab to the cache of tabs for this experiment. This is necessary in order for certain methods
        to work properly. You should only need to do this if you have created a new tab in your code using a method
        outside of this ExperimentHandler.

        :param tab: The tab to add to the cache.
        """
        self._tabs.append(tab)
        self._tabs.sort(key=lambda t: t.tab_order)
        self._tabs_by_id[tab.tab_id] = tab
        self._tabs_by_name[tab.tab_name] = tab

    # FR-46495: Split the creation of the experiment in launch_experiment into a create_experiment function.
    # CR-47703: Allow create_experiment and launch_experiment to accept None as a template_name to create a blank
    # experiment. Also allow a SapioUser object to be provided as context instead of a full SapioWebhookContext object.
    @staticmethod
    def create_experiment(context: UserIdentifier,
                          template_name: str | None = None,
                          experiment_name: str | None = None,
                          parent_record: SapioRecord | None = None, *,
                          template_version: int | None = None, active_templates_only: bool = True) -> ElnExperiment:
        """
        Create an ElnExperiment from the given template name.

        Makes a webservice request to query for all the templates matching the provided criteria. Note that if multiple
        templates match the same criteria, the first template that is encountered in the query is used. Throws an
        exception if no template is found. Also makes a webservice request to create the experiment.

        :param context: The current webhook context or a user object to send requests from.
        :param template_name: The name of the template to create the experiment from. If None, a blank experiment
            is created.
        :param experiment_name: The name to give to the experiment after it is created. If not provided, defaults to the
            display name of the template.
        :param parent_record: The parent record to attach this experiment under. This record must be an eligible
            parent type to ELNExperiment. If not provided, the experiment is stored in the aether.
        :param template_version: The version number of the template to use. If not provided, the latest version of the
            template is used. NOTICE: Template version numbers aren't necessarily the same between environments, so
            be careful with using the same webhook across multiple environments if you are searching for a specific
            version number.
        :param active_templates_only: Whether only active templates should be queried for.
        :return: The newly created experiment.
        """
        user = AliasUtil.to_sapio_user(context)
        cache = ExperimentCacheManager(user)
        eln_manager: ElnManager = DataMgmtServer.get_eln_manager(user)

        template_id: int | None = None
        if template_name:
            launch_template: ElnTemplate = cache.get_experiment_template(template_name, active_templates_only,
                                                                         template_version, first_match=True)
            template_id = launch_template.template_id
            if experiment_name is None:
                experiment_name: str = launch_template.display_name
        elif experiment_name is None:
            experiment_name = f"{user.username}'s Experiment"
        if parent_record is not None:
            parent_record: DataRecord = AliasUtil.to_data_record(parent_record)
        notebook_init = InitializeNotebookExperimentPojo(experiment_name, template_id, parent_record)
        return eln_manager.create_notebook_experiment(notebook_init)

    @staticmethod
    def launch_experiment(context: UserIdentifier,
                          template_name: str | None = None,
                          experiment_name: str | None = None,
                          parent_record: SapioRecord | None = None, *,
                          template_version: int | None = None,
                          active_templates_only: bool = True) -> SapioWebhookResult:
        """
        Create a SapioWebhookResult that, when returned by a webhook handler, sends the user to a new experiment of the
        input template name.

        Makes a webservice request to query for all the templates matching the provided criteria. Note that if multiple
        templates match the same criteria, the first template that is encountered in the query is used. Throws an
        exception if no template is found. Also makes a webservice request to create the experiment.

        :param context: The current webhook context or a user object to send requests from.
        :param template_name: The name of the template to create the experiment from. If None, a blank experiment
            is created.
        :param experiment_name: The name to give to the experiment after it is created. If not provided, defaults to the
            display name of the template.
        :param parent_record: The parent record to attach this experiment under. This record must be an eligible
            parent type to ELNExperiment. If not provided, the experiment is stored in the aether.
        :param template_version: The version number of the template to use. If not provided, the latest version of the
            template is used. NOTICE: Template version numbers aren't necessarily the same between environments, so
            be careful with using the same webhook across multiple environments if you are searching for a specific
            version number.
        :param active_templates_only: Whether only active templates should be queried for.
        :return: A SapioWebhookResult that directs the user to the newly created experiment.
        """
        experiment = ExperimentHandler.create_experiment(context, template_name, experiment_name, parent_record,
                                                         template_version=template_version,
                                                         active_templates_only=active_templates_only)
        return SapioWebhookResult(True, directive=ElnExperimentDirective(experiment.notebook_experiment_id))

    def get_experiment_template(self, exception_on_none: bool = True) -> ElnTemplate | None:
        """
        Query for the experiment template for the current experiment. The returned template is cached by the
        ExperimentHandler.

        :param exception_on_none: If false, returns None if there is no experiment template. If true, raises an exception
            when the experiment template doesn't exist.
        :return: This experiment's template. None if it has no template.
        """
        template_id: int | None = self._eln_exp.template_id
        if template_id is None:
            self._exp_template = None
            if exception_on_none:
                raise SapioException(f"Experiment with ID {self._exp_id} has no template ID.")
            return None

        if not hasattr(self, "_exp_template"):
            # PR-46504: Allow inactive and non-latest version templates to be queried.
            query = TemplateExperimentQueryPojo(template_id_white_list=[template_id],
                                                active_templates_only=False,
                                                latest_version_only=False)
            templates: list[ElnTemplate] = self._eln_man.get_template_experiment_list(query)
            # PR-46504: Set the exp_template to None if there are no results.
            self._exp_template = templates[0] if templates else None
        if self._exp_template is None and exception_on_none:
            raise SapioException(f"Experiment template not found for experiment with ID {self._exp_id}.")
        return self._exp_template

    # CR-46104: Change get_template_name to behave like NotebookProtocolImpl.getTemplateName (i.e. first see if the
    # experiment template exists, and if not, see if the experiment record exists, instead of only checking the
    # template).
    def get_template_name(self, exception_on_none: bool = True) -> str | None:
        """
        Get the template name for the current experiment.

        The template name is determined by either the experiment template or the experiment record, whichever is
        already cached. If neither are cached, queries for the experiment template. If no experiment template exists,
        queries for the experiment record.

        :param exception_on_none: If false, returns None if there is no template name. If true, raises an exception
            when the template name doesn't exist.
        :return: The template name of the current experiment. None if it has no template name.
        """
        if not hasattr(self, "_exp_template"):
            self.get_experiment_template(False)
        if self._exp_template is None and not hasattr(self, "_exp_record"):
            self.get_experiment_record(False)

        name: str | None = None
        if self._exp_template is not None:
            name = self._exp_template.template_name
        elif self._exp_record is not None:
            name = self._exp_record.get_field_value("TemplateExperimentName")
        if name is None and exception_on_none:
            raise SapioException(f"Template name not found for experiment with ID {self._exp_id}.")
        return name

    def get_experiment_record(self, exception_on_none: bool = True) -> DataRecord | None:
        """
        Query for the data record of this experiment. The returned record is cached by the ExperimentHandler.

        :param exception_on_none: If false, returns None if there is no experiment record. If true, raises an exception
            when the experiment record doesn't exist.
        :return: The data record for this experiment. None if it has no record.
        """
        if not hasattr(self, "_exp_record"):
            self._exp_record = self._protocol.get_record()
        if self._exp_record is None and exception_on_none:
            raise SapioException(f"Experiment record not found for experiment with ID {self._exp_id}.")
        return self._exp_record

    # CR-47491: Support not providing a wrapper type to receive PyRecordModels instead of WrappedRecordModels.
    def get_experiment_model(self, wrapper_type: type[WrappedType] | None = None) -> WrappedType | PyRecordModel:
        """
        Query for the data record of this experiment and wrap it as a record model with the given wrapper.
        The returned record is cached by the ExperimentHandler.

        :param wrapper_type: The record model wrapper to use. If not provided, the record is returned as a
            PyRecordModel instead of a WrappedRecordModel.
        :return: The record model for this experiment.
        """
        return self._rec_handler.wrap_model(self.get_experiment_record(), wrapper_type)

    def update_experiment(self,
                          experiment_name: str | None = None,
                          experiment_status: ElnExperimentStatus | None = None,
                          experiment_option_map: dict[str, str] | None = None) -> None:
        """
        Make a webservice call to update the experiment for this ExperimentHandler.  If any parameter is not provided,
        then no change is made to it.

        :param experiment_name: The new name of the experiment.
        :param experiment_status: The new status of this experiment.
        :param experiment_option_map:
            The new map of options for this experiment. Completely overwrites the existing options map.
            Any changes to the experiment options will update this ExperimentHandler's cache of the experiment options.
            If you wish to add options to the existing map of options that an experiment has, use the
            add_experiment_options method.
        """
        criteria = ElnExperimentUpdateCriteria()
        criteria.new_experiment_name = experiment_name
        criteria.new_experiment_status = experiment_status
        criteria.experiment_option_map = experiment_option_map
        self._eln_man.update_notebook_experiment(self._exp_id, criteria)

        if experiment_name is not None:
            self._eln_exp.notebook_experiment_name = experiment_name
        if experiment_status is not None:
            self._eln_exp.notebook_experiment_status = experiment_status
        if experiment_option_map is not None:
            self._exp_options = experiment_option_map

    def get_experiment_option(self, option: str) -> str:
        """
        Get the value of a specific experiment option.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param option: The experiment option to search for.
        :return: The value of the input experiment options.
        """
        return self.get_experiment_options().get(option)

    def get_experiment_options(self) -> dict[str, str]:
        """
        Get the entire map of options for this experiment.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :return: The map of options for this experiment.
        """
        if hasattr(self, "_exp_options"):
            return self._exp_options
        self._exp_options = self._eln_man.get_notebook_experiment_options(self._exp_id)
        return self._exp_options

    def add_experiment_options(self, mapping: Mapping[str, str]) -> None:
        """
        Add to the existing map of options for this experiment. Makes a webservice call to update the experiment. Also
        updates the cache of the experiment options.

        Getting the experiment options requires a webservice query, which is made the first time any experiment option
        method is called by this ExperimentHandler. The experiment options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param mapping: The new options and values to add to the existing experiment options, provided as some Mapping
            (e.g. a Dict). If an option key already exists and is provided in the mapping, overwrites the existing value
            for that key.
        """
        options: dict[str, str] = self.get_experiment_options()
        options.update(mapping)
        self.update_experiment(experiment_option_map=options)

    def experiment_is_complete(self) -> bool:
        """
        Determine if the experiment has been completed.

        :return: True if the experiment's status is Completed or CompletedApproved. False otherwise.
        """
        return self._eln_exp.notebook_experiment_status in self._EXPERIMENT_COMPLETE_STATUSES

    def experiment_is_canceled(self) -> bool:
        """
        Determine if the experiment has been canceled.

        :return: True if the experiment's status is Canceled. False otherwise.
        """
        return self._eln_exp.notebook_experiment_status == ElnExperimentStatus.Canceled

    def experiment_is_locked(self) -> bool:
        """
        Determine if the experiment has been locked in any way.

        :return: True if the experiment's status is Completed, CompletedApproved, Canceled, LockedAwaitingApproval,
            or LockedRejected. False otherwise.
        """
        return self._eln_exp.notebook_experiment_status in self._EXPERIMENT_LOCKED_STATUSES

    def complete_experiment(self) -> None:
        """
        Set the experiment's status to Completed. Makes a webservice call to update the experiment. Checks if the
        experiment is already completed, and does nothing if so.

        NOTE: This will cause the usual process tracking logic to run as if you'd clicked the "Complete Experiment"
        toolbar button. This includes moving the in process samples forward to the next step in the process.
        """
        if not self.experiment_is_complete():
            self._protocol.complete_protocol()
            self._eln_exp.notebook_experiment_status = ElnExperimentStatus.Completed

    def cancel_experiment(self) -> None:
        """
        Set the experiment's status to Canceled. Makes a webservice call to update the experiment. Checks if the
        experiment is already canceled, and does nothing if so.

        NOTE: This will cause the usual process tracking logic to run as if you'd clicked the "Cancel Experiment"
        toolbar button. This includes moving the in process samples back into the process queue for the current step.

        On version 24.12 and earlier, this was not the case, as the process tracking logic was tied to the button
        instead of being on the experiment status change.
        """
        if not self.experiment_is_canceled():
            self._protocol.cancel_protocol()
            self._eln_exp.notebook_experiment_status = ElnExperimentStatus.Canceled

    def step_exists(self, step_name: str) -> bool:
        """
        Determine if a step by the given name exists in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_name: The name of the step to search for.
        :return: True if the step exists, false otherwise.
        """
        return self.get_step(step_name, False) is not None

    def steps_exist(self, step_names: Iterable[str]) -> bool:
        """
        Determine if all the steps by the given names exist in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_names: The names of the steps to search for.
        :return: True if every step exists, false if at least one does not exist.
        """
        return all([x is not None for x in self.get_steps(step_names, False)])

    def get_step(self, step_name: Step, exception_on_none: bool = True) -> ElnEntryStep | None:
        """
        Get the step of the given name from the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_name: The identifier for the step to return.
        :param exception_on_none: If false, returns None if the entry can't be found. If true, raises an exception
            when the named entry doesn't exist in the experiment.
        :return: An ElnEntrySteps matching the provided name. If there is no match and no exception is to be thrown,
            returns None.
        """
        return self.get_steps([step_name], exception_on_none)[0]

    def get_steps(self, step_names: Iterable[Step], exception_on_none: bool = True) -> list[ElnEntryStep | None]:
        """
        Get a list of steps of the given names from the experiment, sorted in the same order as the names are provided.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step_names: A list of identifiers for the entries to return and the order to return them in.
        :param exception_on_none: If false, returns None for entries that can't be found. If true, raises an exception
            when the named entry doesn't exist in the experiment.
        :return: A list of ElnEntrySteps matching the provided names in the order they were provided in. If there is no
            match for a given step and no exception is to be thrown, returns None for that step.
        """
        # CR-47700: Support getting steps from entry objects.
        step_ids: list[str | int] = []
        for step in step_names:
            # Convert any ElnEntrySteps into ExperimentEntries.
            if isinstance(step, ElnEntryStep):
                step: ExperimentEntry = step.eln_entry
            # If an ExperimentEntry is provided, then add its ID to the list of steps to return.
            if isinstance(step, ExperimentEntry):
                step_ids.append(step.entry_id)
                # Add this entry to the caches so that it doesn't need to be queried for. This will also verify that
                # this entry belongs to the experiment that this handler is for.
                self.add_entry_to_caches(step)
            elif isinstance(step, (str, int)):
                step_ids.append(step)

        ret_list: list[ElnEntryStep | None] = []
        for step_id in step_ids:
            # If we haven't queried the system for all steps in the experiment yet, then the reason that a step is
            # missing may be because it wasn't in the webhook context. Therefore, query all steps and then check
            # if the step name is still missing from the experiment before potentially throwing an exception.
            if not self._queried_all_steps:
                if ((isinstance(step_id, str) and step_id not in self._steps_by_name)
                        or (isinstance(step_id, int) and step_id not in self._steps_by_id)):
                    self._query_all_steps()
            if isinstance(step_id, str):
                step: ElnEntryStep = self._steps_by_name.get(step_id)
            else:
                step: ElnEntryStep = self._steps_by_id.get(step_id)
            if step is None and exception_on_none is True:
                raise SapioException(f"ElnEntryStep of name \"{step_id}\" not found in experiment with ID {self._exp_id}.")
            ret_list.append(step)
        return ret_list

    def get_all_steps(self, data_type: DataTypeIdentifier | None = None) -> list[ElnEntryStep]:
        """
        Get a list of every entry in the experiment. Optionally filter the returned entries by a data type.

        Makes a webservice call to retrieve every entry in the experiment if they were not already previously cached.

        :param data_type: A data type used to filter the returned entries. If None is given, returns all entries. If
            a data type name or wrapper is given, only returns entries that match that data type name or wrapper.
        :return: Every entry in the experiment in order of appearance that match the provided data type, if any.
        """
        if self._queried_all_steps is False:
            self._query_all_steps()
        else:
            # Re-sort the steps in case any new steps were added before the last time that this was called.
            def sort_steps(step: ElnEntryStep) -> tuple:
                entry = step.eln_entry
                tab_order: int = self.get_tab_for_step(step).tab_order
                entry_order: int = entry.order
                column_order: int = entry.column_order
                return tab_order, entry_order, column_order

            self._steps.sort(key=sort_steps)
        all_steps: list[ElnEntryStep] = self._steps
        if data_type is None:
            return all_steps
        data_type: str = AliasUtil.to_data_type_name(data_type)
        return [x for x in all_steps if data_type in x.get_data_type_names()]

    def _query_all_steps(self) -> None:
        """
        Query the system for every step in the experiment and cache them.
        """
        self._queried_all_steps = True
        self._protocol.invalidate()
        self._steps = self._protocol.get_sorted_step_list()
        for step in self._steps:
            self._steps_by_name[step.get_name()] = step
            self._steps_by_id[step.get_id()] = step

    def get_step_by_option(self, key: str, value: str | None = None) -> ElnEntryStep:
        """
        Retrieve the step in this experiment that contains an entry option with the provided key and value.
        Throws an exception if no entries or multiple entries in the experiment match.

        :param key: The key of the entry option to match on.
        :param value: The value of the entry option to match on. If not provided, then only matches on key.
        :return: The entry in this experiment that matches the provided entry option key and value.
        """
        steps: list[ElnEntryStep] = self.get_steps_by_option(key, value)
        count: int = len(steps)
        if count != 1:
            option = key + ("::" + value if value is not None else "")
            raise SapioException(f"{('No' if count == 0 else 'Multiple')} entries in this experiment match the "
                                 f"provided option: {option}")
        return steps[0]

    def get_steps_by_option(self, key: str, value: str | None = None) -> list[ElnEntryStep]:
        """
        Retrieve every step in this experiment that contains an entry option with the provided key and value.

        :param key: The key of the entry option to match on.
        :param value: The value of the entry option to match on. If not provided, then only matches on key.
        :return: The entries in this experiment that match the provided entry option key and value.
        """
        ret_list: list[ElnEntryStep] = []
        for step in self.get_all_steps():
            options: dict[str, str] = self.get_step_options(step)
            if key in options:
                if value is None or options[key] == value:
                    ret_list.append(step)
        return ret_list

    def get_step_records(self, step: Step) -> list[DataRecord]:
        """
        Query for the data records for the given step. The returned records are not cached by the ExperimentHandler.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to get the data records for.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The data records for the given step.
        """
        return self.get_step(step).get_records()

    def get_step_models(self, step: Step, wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Query for the data records for the given step and wrap them as record models with the given type. The returned
        records are not cached by the ExperimentHandler.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to get the data records for.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param wrapper_type: The record model wrapper to use. If not provided, the records are returned as
            PyRecordModels instead of WrappedRecordModels.
        :return: The record models for the given step.
        """
        return self._rec_handler.wrap_models(self.get_step_records(step), wrapper_type)

    def add_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Make a webservice call to add a list of records to a step. Only functions for global data type table entries.
        For adding to an ELN data type table entry, see add_eln_rows.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to add the records to.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to add to the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step: ElnEntryStep = self.get_step(step)
        if not records:
            return
        dt: str = AliasUtil.to_singular_data_type_name(records)
        if ElnBaseDataType.is_base_data_type(dt):
            raise SapioException(f"{dt} is an ELN data type. This function call has no effect on ELN data types. ELN "
                                 f"records that are committed to the system will automatically appear in the ELN entry "
                                 f"with the matching data type name.")
        if dt != step.get_data_type_names()[0]:
            raise SapioException(f"Cannot add {dt} records to entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        step.add_records(AliasUtil.to_data_records(records))

    def remove_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Make a webservice call to remove a list of records from a step.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to remove from the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step: ElnEntryStep = self.get_step(step)
        if not records:
            return
        dt: str = AliasUtil.to_singular_data_type_name(records)
        if ElnBaseDataType.is_base_data_type(dt):
            # CR-47532: Add remove_step_records support for Experiment Detail and Sample Detail entries.
            self.remove_eln_rows(step, records)
            return
        if dt != step.get_data_type_names()[0]:
            raise SapioException(f"Cannot remove {dt} records from entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        step.remove_records(AliasUtil.to_data_records(records))

    def set_step_records(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Sets the records in the given step to be equal to the input list of records. If a record is already on the step,
        it remains. If a record is missing from the step, it gets added. If a record is on the step but not in the
        provided record list, it gets removed. Makes one webservice call to get what is currently on the step and
        one additional webservice call for each of either adding or removing, if necessary.

        Functions for table, form, and attachment entries. For form and attachment entries, only a single record should
        be provided.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to set for the given step,
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step: ElnEntryStep = self.get_step(step)
        if records:
            dt: str = AliasUtil.to_singular_data_type_name(records)
            # CR-47532: Add set_step_records support for Experiment Detail and Sample Detail entries.
            if ElnBaseDataType.is_base_data_type(dt):
                remove_rows: list[PyRecordModel] = []
                for record in self.get_step_models(step):
                    if record not in records:
                        remove_rows.append(record)
                self.remove_eln_rows(step, remove_rows)
                return
            if dt != step.get_data_type_names()[0]:
                raise SapioException(f"Cannot set {dt} records for entry {step.get_name()} of type "
                                     f"{step.get_data_type_names()[0]}.")
        step.set_records(AliasUtil.to_data_records(records))

    # FR-46496 - Provide alias of set_step_records for use with form entries.
    def set_form_record(self, step: Step, record: SapioRecord) -> None:
        """
        Sets the record for a form entry.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param record:
            A record to set for the given step,
            The record may be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel.
        """
        self.set_step_records(step, [record])
        step: ElnEntryStep = self.get_step(step)
        if isinstance(step.eln_entry, ExperimentFormEntry):
            step.eln_entry.record_id = AliasUtil.to_data_record(record).record_id

    # FR-46496 - Provide functions for adding and removing rows from an ELN data type entry.
    def add_eln_row(self, step: Step, wrapper_type: type[WrappedType] | None = None) -> WrappedType | PyRecordModel:
        """
        Add a row to an ELNExperimentDetail or ELNSampleDetail table entry. The row will not appear in the system
        until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param wrapper_type: Optionally wrap the ELN data type in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: The newly created row.
        """
        return self.add_eln_rows(step, 1, wrapper_type)[0]

    def add_eln_rows(self, step: Step, count: int, wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Add rows to an ELNExperimentDetail or ELNSampleDetail table entry. The rows will not appear in the system
        until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param count: The number of new rows to add to the entry.
        :param wrapper_type: Optionally wrap the ELN data type in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: A list of the newly created rows.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_type != ElnEntryType.Table:
            raise SapioException("The provided step is not a table entry.")
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt):
            raise SapioException("The provided step is not an ELN data type entry.")
        records: list[PyRecordModel] = self._inst_man.add_new_records(dt, count)
        if wrapper_type:
            return self._inst_man.wrap_list(records, wrapper_type)
        return records

    def add_sample_detail(self, step: Step, sample: RecordModel,
                           wrapper_type: type[WrappedType] | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Add a sample detail to a sample detail entry while relating it to the input sample record.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param sample: The sample record to add the sample detail to.
        :param wrapper_type: Optionally wrap the sample detail in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: The newly created sample detail.
        """
        return self.add_sample_details(step, [sample], wrapper_type)[0]

    def add_sample_details(self, step: Step, samples: Iterable[RecordModel],
                           wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Add sample details to a sample details entry while relating them to the input sample records.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param samples: The sample records to add the sample details to.
        :param wrapper_type: Optionally wrap the sample details in a record model wrapper. If not provided, returns
            an unwrapped PyRecordModel.
        :return: The newly created sample details. The indices of the samples in the input list match the index of the
            sample details in this list that they are related to.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_type != ElnEntryType.Table:
            raise SapioException("The provided step is not a table entry.")
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt) or ElnBaseDataType.get_base_type(dt) != ElnBaseDataType.SAMPLE_DETAIL:
            raise SapioException("The provided step is not an ELNSampleDetail entry.")
        records: list[PyRecordModel] = []
        for sample in samples:
            if sample.data_type_name != "Sample":
                raise SapioException(f"Received a {sample.data_type_name} record when Sample records were expected.")
            detail: PyRecordModel = sample.add(Child.create_by_name(dt))
            detail.set_field_values({
                "SampleId": sample.get_field_value("SampleId"),
                "OtherSampleId": sample.get_field_value("OtherSampleId")
            })
            records.append(detail)
        if wrapper_type:
            return self._inst_man.wrap_list(records, wrapper_type)
        return records

    def remove_eln_row(self, step: Step, record: SapioRecord) -> None:
        """
        Remove a row from an ELNExperimentDetail or ELNSampleDetail table entry. ELN data type table entries display all
        records in the system that match the entry's data type. This means that removing rows from an ELN data type
        table entry is equivalent to deleting the records for the rows.

        The row will not be deleted in the system until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param record:
            The record to remove from the given step.
            The record may be provided as either a DataRecord, PyRecordModel, or WrappedRecordModel.
        """
        self.remove_eln_rows(step, [record])

    def remove_eln_rows(self, step: Step, records: Iterable[SapioRecord]) -> None:
        """
        Remove rows from an ELNExperimentDetail or ELNSampleDetail table entry. ELN data type table entries display all
        records in the system that match the entry's data type. This means that removing rows from an ELN data type
        table entry is equivalent to deleting the records for the rows.

        The rows will not be deleted in the system until a record manager store and commit has occurred.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param records:
            A list of records to remove from the given step.
            The records may be provided as either DataRecords, PyRecordModels, or WrappedRecordModels.
        """
        step: ElnEntryStep = self.get_step(step)
        dt: str = step.get_data_type_names()[0]
        if not ElnBaseDataType.is_eln_type(dt):
            raise SapioException("The provided step is not an ELN data type entry.")
        if not records:
            return
        record_dt: str = AliasUtil.to_singular_data_type_name(records, False)
        if record_dt != dt:
            raise SapioException(f"Cannot remove {dt} records from entry {step.get_name()} of type "
                                 f"{step.get_data_type_names()[0]}.")
        # If any rows were provided as data records, turn them into record models before deleting them, as otherwise
        # this function would need to make a webservice call to do the deletion.
        data_records: list[DataRecord] = []
        for record in records:
            if isinstance(record, DataRecord):
                data_records.append(record)
            else:
                record.delete()
        if data_records:
            record_models: list[PyRecordModel] = self._inst_man.add_existing_records(data_records)
            for record in record_models:
                record.delete()

    # noinspection PyPep8Naming
    def update_step(self, step: Step,
                    entry_name: str | None = None,
                    related_entry_set: Iterable[int] | None = None,
                    dependency_set: Iterable[int] | None = None,
                    entry_status: ExperimentEntryStatus | None = None,
                    order: int | None = None,
                    description: str | None = None,
                    requires_grabber_plugin: bool | None = None,
                    is_initialization_required: bool | None = None,
                    notebook_experiment_tab_id: int | None = None,
                    entry_height: int | None = None,
                    column_order: int | None = None,
                    column_span: int | None = None,
                    is_removable: bool | None = None,
                    is_renamable: bool | None = None,
                    source_entry_id: int | None = None,
                    clear_source_entry_id: bool | None = None,
                    is_hidden: bool | None = None,
                    is_static_View: bool | None = None,
                    is_shown_in_template: bool | None = None,
                    template_item_fulfilled_timestamp: int | None = None,
                    clear_template_item_fulfilled_timestamp: bool | None = None,
                    entry_options_map: dict[str, str] | None = None) -> None:
        """
        Make a webservice call to update an abstract step. If any parameter is not provided, then no change is made
        to it. All changes will be reflected by the ExperimentEntry of the Step that is being updated.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The entry step to update.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param entry_name: The new name of this entry.
        :param related_entry_set: The new set of entry IDs for the entries that are related (implicitly dependent) to
            this entry. Completely overwrites the existing related entries.
        :param dependency_set: The new set of entry IDs for the entries that are dependent (explicitly dependent) on
            this entry. Completely overwrites the existing dependent entries.
        :param entry_status: The new status of this entry.
        :param order: The row order of this entry in its tab.
        :param description: The new description of this entry.
        :param requires_grabber_plugin: Whether this entry's initialization is handled by a grabber plugin. If true,
            then is_initialization_required is forced to true by the server.
        :param is_initialization_required: Whether the user is required to manually initialize this entry.
        :param notebook_experiment_tab_id: The ID of the tab that this entry should appear on.
        :param entry_height: The height of this entry.
        :param column_order: The column order of this entry.
        :param column_span: How many columns this entry spans.
        :param is_removable: Whether this entry can be removed by the user.
        :param is_renamable: Whether this entry can be renamed by the user.
        :param source_entry_id: The ID of this entry from its template.
        :param clear_source_entry_id: True if the source entry ID should be cleared.
        :param is_hidden: Whether this entry is hidden from the user.
        :param is_static_View: Whether this entry is static. Static entries are uneditable and shared across all
            experiments of the same template.
        :param is_shown_in_template: Whether this entry is saved to and shown in the experiment's template.
        :param template_item_fulfilled_timestamp: A timestamp in milliseconds for when this entry was initialized.
        :param clear_template_item_fulfilled_timestamp: True if the template item fulfilled timestamp should be cleared,
            uninitializing the entry.
        :param entry_options_map:
            The new map of options for this entry. Completely overwrites the existing options map.
            Any changes to the entry options will update this ExperimentHandler's cache of entry options.
            If you wish to add options to the existing map of options that an entry has, use the
            add_step_options method.
        """
        # FR-47468: Deprecating this since the entry-specific update criteria should be used instead.
        warnings.warn("Update step is deprecated. Use force_entry_update instead.",
                      DeprecationWarning)
        step: ElnEntryStep = self.get_step(step)
        update = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)

        # These two variables could be iterables that aren't lists. Convert them to plain
        # lists, since that's what the update criteria is expecting.
        if related_entry_set is not None:
            related_entry_set = list(related_entry_set)
        if dependency_set is not None:
            dependency_set = list(dependency_set)

        update.entry_name = entry_name
        update.related_entry_set = related_entry_set
        update.dependency_set = dependency_set
        update.entry_status = entry_status
        update.order = order
        update.description = description
        update.requires_grabber_plugin = requires_grabber_plugin
        update.is_initialization_required = is_initialization_required
        update.notebook_experiment_tab_id = notebook_experiment_tab_id
        update.entry_height = entry_height
        update.column_order = column_order
        update.column_span = column_span
        update.is_removable = is_removable
        update.is_renamable = is_renamable
        update.source_entry_id = source_entry_id
        update.clear_source_entry_id = clear_source_entry_id
        update.is_hidden = is_hidden
        update.is_static_View = is_static_View
        update.is_shown_in_template = is_shown_in_template
        update.template_item_fulfilled_timestamp = template_item_fulfilled_timestamp
        update.clear_template_item_fulfilled_timestamp = clear_template_item_fulfilled_timestamp
        update.entry_options_map = entry_options_map

        self.force_step_update(step, update)

    # FR-47468: Some functions that can help with entry updates.
    def force_step_update(self, step: Step, update: AbstractElnEntryUpdateCriteria) -> None:
        """
        Immediately sent an update to an entry in this experiment. All changes will be reflected by the ExperimentEntry
        of the Step that is being updated.

        Consider using store_step_update and commit_step_updates instead if the update does not need to be immediate.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step: The step to update.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param update: The update to make to the step.
        """
        step: ElnEntryStep = self.get_step(step)
        self._eln_man.update_experiment_entry(self._exp_id, step.get_id(), update)
        self._update_entry_details(step, update)

    def store_step_update(self, step: Step, update: AbstractElnEntryUpdateCriteria) -> None:
        """
        Store updates to be made to an entry in this experiment. The updates are not committed until
        commit_entry_updates is called.

        If the same entry is updated multiple times before committing, the latest update will be merged on top of the
        previous updates; where the new update and old update conflict, the new update will take precedence.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step: The step to update.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param update: The update to make to the step.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_type != update.entry_type:
            raise SapioException(f"The provided step and update criteria are not of the same entry type. "
                                 f"The step is of type {step.eln_entry.entry_type} and the update criteria is of type "
                                 f"{update.entry_type}.")
        if step.get_id() in self._step_updates:
            self._merge_updates(update, self._step_updates[step.get_id()])
        else:
            self._step_updates[step.get_id()] = update

    def store_step_updates(self, updates: dict[Step, AbstractElnEntryUpdateCriteria]) -> None:
        """
        Store updates to be made to multiple entries in this experiment. The updates are not committed until
        commit_entry_updates is called.

        If the same entry is updated multiple times before committing, the latest update will be merged on top of the
        previous updates; where the new update and old update conflict, the new update will take precedence.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param updates: A dictionary of steps and their respective updates.
        """
        for step, update in updates.items():
            self.store_step_update(step, update)

    def commit_step_updates(self) -> None:
        """
        Commit all the stored updates to the entries in this experiment. The updates are made in the order that they
        were stored.
        """
        if not self._step_updates:
            return
        self._eln_man.update_experiment_entries(self._exp_id, self._step_updates)
        for step_id, criteria in self._step_updates.items():
            self._update_entry_details(self._steps_by_id[step_id], criteria)
        self._step_updates.clear()

    @staticmethod
    def _merge_updates(new_update: AbstractElnEntryUpdateCriteria, old_update: AbstractElnEntryUpdateCriteria) -> None:
        """
        Merge the new update criteria onto the old update criteria. The new update will take precedence where there
        are conflicts.
        """
        for key, value in new_update.__dict__.items():
            if value is not None:
                old_update.__dict__[key] = value

    def _update_entry_details(self, step: Step, update: AbstractElnEntryUpdateCriteria) -> None:
        """
        Update the cached information for this entry in case it's needed by the caller after updating.
        """
        entry: ExperimentEntry = step.eln_entry
        if update.entry_name is not None:
            # PR-46477 - Ensure that the previous name of the updated entry already existed in the cache.
            if entry.entry_name in self._steps_by_name:
                self._steps_by_name.pop(entry.entry_name)
            entry.entry_name = update.entry_name
            self._steps_by_name.update({update.entry_name: step})
        if update.related_entry_set is not None:
            entry.related_entry_id_set = update.related_entry_set
        if update.dependency_set is not None:
            entry.dependency_set = update.dependency_set
        if update.entry_status is not None:
            entry.entry_status = update.entry_status
        if update.order is not None:
            entry.order = update.order
        if update.description is not None:
            entry.description = update.description
        if update.requires_grabber_plugin is not None:
            entry.requires_grabber_plugin = update.requires_grabber_plugin
        if update.is_initialization_required is not None:
            entry.is_initialization_required = update.is_initialization_required
        if update.notebook_experiment_tab_id is not None:
            entry.notebook_experiment_tab_id = update.notebook_experiment_tab_id
        if update.entry_height is not None:
            entry.entry_height = update.entry_height
        if update.column_order is not None:
            entry.column_order = update.column_order
        if update.column_span is not None:
            entry.column_span = update.column_span
        if update.is_removable is not None:
            entry.is_removable = update.is_removable
        if update.is_renamable is not None:
            entry.is_renamable = update.is_renamable
        if update.source_entry_id is not None:
            entry.source_entry_id = update.source_entry_id
        if update.clear_source_entry_id is True:
            entry.source_entry_id = None
        if update.is_hidden is not None:
            entry.is_hidden = update.is_hidden
        if update.is_static_View is not None:
            entry.is_static_View = update.is_static_View
        if update.is_shown_in_template is not None:
            entry.is_shown_in_template = update.is_shown_in_template
        if update.template_item_fulfilled_timestamp is not None:
            entry.template_item_fulfilled_timestamp = update.template_item_fulfilled_timestamp
        if update.clear_template_item_fulfilled_timestamp is True:
            entry.template_item_fulfilled_timestamp = None
        if update.entry_options_map is not None:
            self._step_options.update({step.get_id(): update.entry_options_map})

        if isinstance(entry, ExperimentAttachmentEntry) and isinstance(update, ElnAttachmentEntryUpdateCriteria):
            if update.entry_attachment_list is not None:
                entry.entry_attachment_list = update.entry_attachment_list
            if update.record_id is not None:
                entry.record_id = update.record_id
            if update.attachment_name is not None:
                entry.attachment_name = update.attachment_name
        elif isinstance(entry, ExperimentDashboardEntry) and isinstance(update, ElnDashboardEntryUpdateCriteria):
            if update.dashboard_guid is not None:
                entry.dashboard_guid = update.dashboard_guid
            if update.dashboard_guid_list is not None:
                entry.dashboard_guid_list = update.dashboard_guid_list
            if update.data_source_entry_id is not None:
                entry.data_source_entry_id = update.data_source_entry_id
        elif isinstance(entry, ExperimentFormEntry) and isinstance(update, ElnFormEntryUpdateCriteria):
            if update.record_id is not None:
                entry.record_id = update.record_id
            if update.form_name_list is not None:
                entry.form_name_list = update.form_name_list
            if update.data_type_layout_name is not None:
                entry.data_type_layout_name = update.data_type_layout_name
            if update.field_set_id_list is not None:
                entry.field_set_id_list = update.field_set_id_list
            if update.extension_type_list is not None:
                entry.extension_type_list = update.extension_type_list
            if update.data_field_name_list is not None:
                entry.data_field_name_list = update.data_field_name_list
            if update.is_existing_field_removable is not None:
                entry.is_existing_field_removable = update.is_existing_field_removable
            if update.is_field_addable is not None:
                entry.is_field_addable = update.is_field_addable
        elif isinstance(entry, ExperimentPluginEntry) and isinstance(update, ElnPluginEntryUpdateCriteria):
            if update.plugin_name is not None:
                entry.plugin_name = update.plugin_name
            if update.provides_template_data is not None:
                entry.provides_template_data = update.provides_template_data
            if update.using_template_data is not None:
                entry.using_template_data = update.using_template_data
        if isinstance(entry, ExperimentTableEntry) and isinstance(update, ElnTableEntryUpdateCriteria):
            if update.data_type_layout_name is not None:
                entry.data_type_layout_name = update.data_type_layout_name
            if update.extension_type_list is not None:
                entry.extension_type_list = update.extension_type_list
            if update.field_set_id_list is not None:
                entry.field_set_id_list = update.field_set_id_list
            if update.is_existing_field_removable is not None:
                entry.is_existing_field_removable = update.is_existing_field_removable
            if update.is_field_addable is not None:
                entry.is_field_addable = update.is_field_addable
            if update.show_key_fields is not None:
                entry.show_key_fields = update.show_key_fields
            if update.table_column_list is not None:
                entry.table_column_list = update.table_column_list
        elif isinstance(entry, ExperimentTempDataEntry) and isinstance(update, ElnTempDataEntryUpdateCriteria):
            if update.plugin_path is not None:
                entry.plugin_path = update.plugin_path
        elif isinstance(entry, ExperimentTextEntry) and isinstance(update, ElnTextEntryUpdateCriteria):
            # Text update criteria has no additional fields.
            pass

    def get_step_option(self, step: Step, option: str) -> str:
        """
        Get the value of a specific entry option for the given step.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for a specific step. The step options are cached so that subsequent calls of this
        method for that step don't make a webservice call.

        :param step:
            The step to check the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param option: The entry option to search for.
        :return: The value of the input entry option for the input step.
        """
        return self.get_step_options(step).get(option)

    def get_step_options(self, step: Step) -> dict[str, str]:
        """
        Get the entire map of options for the input step.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for any step in this experiment. The step options are cached so that subsequent calls of this
        method don't make a webservice call.

        :param step:
            The step to get the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The map of options for the input step.
        """
        step: ElnEntryStep = self.get_step(step)
        if step not in self._step_options:
            self._step_options.update(ExperimentReportUtil.get_experiment_entry_options(self.user,
                                                                                        self.get_all_steps()))
        return self._step_options[step.get_id()]

    def add_step_options(self, step: Step, mapping: Mapping[str, str]):
        """
        Add to the existing map of options for the input step. Makes a webservice call to update the step. Also
        updates the cache of the step's options.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        Getting the step options requires a webservice query, which is made the first time any step option
        method is called for a specific step. The step options are cached so that subsequent calls of this
        method for that step don't make a webservice call.

        :param step:
            The step to update the options of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :param mapping: The new options and values to add to the existing step options, provided as some Mapping
            (e.g. a dictionary). If an option key already exists and is provided in the mapping, overwrites the existing
            value for that key.
        """
        # PR-47698: Convert the given step to an ElnEntryStep if it is not already one.
        step: ElnEntryStep = self.get_step(step)
        options: dict[str, str] = self.get_step_options(step)
        options.update(mapping)
        update = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)
        update.entry_options_map = options
        self.force_step_update(step, update)

    def initialize_step(self, step: Step) -> None:
        """
        Initialize the input step by setting its template item fulfilled timestamp to now. Makes a webservice call to
        update the step. Checks if the step already has a timestamp, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to initialize.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        # Avoid unnecessary calls if the step is already initialized.
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.template_item_fulfilled_timestamp is None:
            update = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)
            update.template_item_fulfilled_timestamp = TimeUtil.now_in_millis()
            self.force_step_update(step, update)

    def uninitialize_step(self, step: Step) -> None:
        """
        Uninitialize the input step by clearing its template item fulfilled timestamp to now. Makes a webservice call to
        update the step. Checks if the step already doesn't have a timestamp, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to uninitialize.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        # Avoid unnecessary calls if the step is already uninitialized.
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.template_item_fulfilled_timestamp is not None:
            update = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)
            update.clear_template_item_fulfilled_timestamp = True
            self.force_step_update(step, update)

    def complete_step(self, step: Step) -> None:
        """
        Submit the input step. Makes a webservice call to update the step. Checks if the step is already completed, and
        does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to complete.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_status not in self._ENTRY_COMPLETE_STATUSES:
            step.complete_step()
            step.eln_entry.entry_status = ExperimentEntryStatus.Completed

    def unlock_step(self, step: Step) -> None:
        """
        Set the status of the input step to UnlockedChangesRequired. Makes a webservice call to update the step. Checks
        if the step is already unlocked, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to unlock.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_status in self._ENTRY_LOCKED_STATUSES:
            step.unlock_step()
            step.eln_entry.entry_status = ExperimentEntryStatus.UnlockedChangesRequired

    def disable_step(self, step: Step) -> None:
        """
        Set the status of the input step to Disabled. This is the state that entries are in when they are waiting for
        entries that they are dependent upon to be submitted before they can be enabled. If you have unsubmitted an
        entry and want its dependent entries to be locked again, then you would use this to set their status to
        disabled.

        Makes a webservice call to update the step. Checks if the step is already unlocked, and does nothing if so.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to disable.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        """
        step: ElnEntryStep = self.get_step(step)
        if step.eln_entry.entry_status in self._ENTRY_LOCKED_STATUSES:
            update = AbstractElnEntryUpdateCriteria(step.eln_entry.entry_type)
            update.entry_status = ExperimentEntryStatus.Disabled
            self.force_step_update(step, update)

    def step_is_submitted(self, step: Step) -> bool:
        """
        Determine if the input step has already been submitted.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to check.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: True if the step's status is Completed or CompletedApproved. False otherwise.
        """
        return self.get_step(step).eln_entry.entry_status in self._ENTRY_COMPLETE_STATUSES

    def step_is_locked(self, step: Step) -> bool:
        """
        Determine if the input step has been locked in any way.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to check.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: True if the step's status is Completed, CompletedApproved, Disabled, LockedAwaitingApproval,
            or LockedRejected. False otherwise.
        """
        return self.get_step(step).eln_entry.entry_status in self._ENTRY_LOCKED_STATUSES

    # FR-47464: Some functions that can help with entry placement.
    def get_all_tabs(self) -> list[ElnExperimentTab]:
        """
        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        :return: A list of all the tabs in the experiment in order of appearance.
        """
        if not self._queried_all_tabs:
            self._tabs = self._eln_man.get_tabs_for_experiment(self._exp_id)
            self._tabs.sort(key=lambda t: t.tab_order)
            self._tabs_by_id = {tab.tab_id: tab for tab in self._tabs}
            self._tabs_by_name = {tab.tab_name: tab for tab in self._tabs}
        return self._tabs

    def get_first_tab(self) -> ElnExperimentTab:
        """
        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        :return: The first tab in the experiment.
        """
        return self.get_all_tabs()[0]

    def get_last_tab(self) -> ElnExperimentTab:
        """
        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        :return: The last tab in the experiment.
        """
        return self.get_all_tabs()[-1]

    def create_tab(self, tab_name: str) -> ElnExperimentTab:
        """
        Create a new tab in the experiment with the input name.

        :param tab_name: The name of the tab to create.
        :return: The newly created tab.
        """
        crit = ElnExperimentTabAddCriteria(tab_name, [])
        tab: ElnExperimentTab = self._eln_man.add_tab_for_experiment(self._exp_id, crit)
        self.add_tab_to_cache(tab)
        return tab

    def get_tab(self, tab: str | int, exception_on_none: bool = True) -> ElnExperimentTab:
        """
        Return the tab with the input name.

        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        :param tab: The name or order of the tab to get. The order is 1-indexed.
        :param exception_on_none: If True, raises an exception if no tab with the given name exists.
        :return: The tab with the input name, or None if no such tab exists.
        """
        if isinstance(tab, str):
            if tab not in self._tabs_by_name:
                self.get_all_tabs()
            eln_tab = self._tabs_by_name.get(tab)
        elif isinstance(tab, int):
            # The given integer is expected to be 1-indexed, but we read from the list with a 0-index.
            tab -= 1
            tabs = self.get_all_tabs()
            eln_tab = tabs[tab] if len(tabs) > tab else None
        else:
            raise SapioException(f"Tab must be a string or an integer, not {type(tab)}.")
        if eln_tab is None and exception_on_none:
            raise SapioException(f"No tab with the name\\order \"{tab}\" exists in this experiment.")
        return eln_tab

    def get_steps_in_tab(self, tab: Tab, data_type: DataTypeIdentifier | None = None) \
            -> list[ElnEntryStep]:
        """
        Get all the steps in the input tab sorted in order of appearance.

        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        If the steps in the experiment have not been queried before, queries for the list of steps in the experiment
        and caches them.

        :param tab: The tab to get the steps of. This can be the tab's order, name, or the tab object itself.
            The order is 1-indexed.
        :param data_type: The data type to filter the steps by. If None, all steps are returned.
        :return: A list of all the steps in the input tab sorted in order of appearance.
        """
        tab: ElnExperimentTab = self.__to_eln_tab(tab)
        steps: list[ElnEntryStep] = []
        for step in self.get_all_steps(data_type):
            if step.eln_entry.notebook_experiment_tab_id == tab.tab_id:
                steps.append(step)
        return steps

    def get_tab_for_step(self, step: Step) -> ElnExperimentTab:
        """
        Get the tab that a particular step is located in.

        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        If the steps in the experiment have not been queried before, queries for the list of steps in the experiment
        and caches them.

        :param step:
            The step to get the position of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The tab that the input step is located in.
        """
        step: ElnEntryStep = self.get_step(step)
        tab_id = step.eln_entry.notebook_experiment_tab_id
        if tab_id not in self._tabs_by_id:
            self.get_all_tabs()
        return self._tabs_by_id.get(tab_id)

    def get_next_entry_order_in_tab(self, tab: Tab) -> int:
        """
        Get the next available order for a new entry in the input tab.

        If no tab functions have been called before and a tab is being searched for by name, queries for the
        list of tabs in the experiment and caches them.

        If the steps in the experiment have not been queried before, queries for the list of steps in the experiment
        and caches them.

        :param tab: The tab to get the steps of. This can be the tab's order, name, or the tab object itself.
            The order is 1-indexed.
        :return: The next available order for a new entry in the input tab.
        """
        steps = self.get_steps_in_tab(tab)
        return steps[-1].eln_entry.order + 1 if steps else 0

    # FR-47530: Add functions for dealing with entry positioning.
    def step_to_position(self, step: Step) -> ElnEntryPosition:
        """
        Get the position of the input step in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param step:
            The step to get the position of.
            The step may be provided as either a string for the name of the step or an ElnEntryStep.
            If given a name, throws an exception if no step of the given name exists in the experiment.
        :return: The position of the input step in the experiment.
        """
        step: ElnEntryStep = self.get_step(step)
        entry: ExperimentEntry = step.eln_entry
        return ElnEntryPosition(entry.notebook_experiment_tab_id,
                                entry.order,
                                entry.column_span,
                                entry.column_order)

    def step_at_position(self, position: ElnEntryPosition) -> Step | None:
        """
        Get the step at the input position in the experiment.

        If no step functions have been called before and a step is being searched for by name, queries for the
        list of steps in the experiment and caches them.

        :param position: The position to get the step at.
        :return: The step at the input position in the experiment, or None if no step exists at that position.
        """
        if position.tab_id is None or position.order is None:
            raise SapioException("The provided position must at least have a tab ID and order.")
        for step in self.get_steps_in_tab(position.tab_id):
            entry: ExperimentEntry = step.eln_entry
            if entry.order != position.order:
                continue
            if position.column_span is not None and entry.column_span != position.column_span:
                continue
            if position.column_order is not None and entry.column_order != position.column_order:
                continue
            return step
        return None

    # FR-47530: Create a function for adding protocol templates to the experiment.
    def add_protocol(self, protocol: ProtocolTemplateInfo | int, position: ElnEntryPosition) -> list[ElnEntryStep]:
        """
        Add a protocol to the experiment. Updates the handler cache with the newly created entries.

        :param protocol: The protocol to add. This can be either a ProtocolTemplateInfo object or the ID of the
            protocol template.
        :param position: The position that the protocol's first entry will be placed at.
        :return: The newly created protocol entries.
        """
        protocol = protocol if isinstance(protocol, int) else protocol.template_id
        new_entries: list[ExperimentEntry] = self._eln_man.add_protocol_template(self._exp_id, protocol, position)
        return self.add_entries_to_caches(new_entries)

    # CR-47700: Deleted __to_eln_step since it became redundant with the get_step method.

    def __to_eln_tab(self, tab: Tab) -> ElnExperimentTab:
        """
        Convert a variable that could be either a tab name, tab order, or ElnExperimentTab to just a tab object.
        This will query and cache the tabs for the experiment if the input tab is a name and the tabs have not been
        cached before.

        :return: The input tab as an ElnExperimentTab.
        """
        if not isinstance(tab, ElnExperimentTab):
            return self.get_tab(tab)
        return tab
