from __future__ import annotations

from collections.abc import Iterable
from typing import cast

from sapiopycommons.datatype.data_fields import SystemFields
from sapiopycommons.eln.step_creation import StepCreation, AttachmentStepCreation, GlobalDtFormStepCreation, \
    ELnDtFormStepCreation, PluginStepCreation, TextStepCreation, TempDataStepCreation, ELnDtTableStepCreation, \
    GlobalDtTableStepCreation, DashboardStepCreation
from sapiopycommons.eln.experiment_cache import ExperimentCacheManager
from sapiopycommons.eln.experiment_handler import ExperimentHandler, Step
from sapiopycommons.eln.experiment_tags import PLATE_DESIGNER_PLUGIN
from sapiopycommons.general.aliases import AliasUtil, SapioRecord, DataTypeIdentifier, FieldMap, \
    ExperimentEntryIdentifier
from sapiopycommons.general.exceptions import SapioException
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.TableColumn import TableColumn
from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition
from sapiopylib.rest.pojo.eln.ExperimentEntry import EntryAttachment, EntryRecordAttachment
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ExperimentEntryCriteriaUtil, AbstractElnEntryCriteria, \
    ElnAttachmentEntryCriteria, \
    ElnFormEntryCriteria, ElnPluginEntryCriteria, ElnTextEntryCriteria, ElnTempDataEntryCriteria, ElnTableEntryCriteria, \
    ElnDashboardEntryCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.pojo.eln.eln_headings import ElnExperimentTab
from sapiopylib.rest.pojo.eln.field_set import ElnFieldSetInfo
from sapiopylib.rest.utils.Protocols import ElnEntryStep
from sapiopylib.rest.utils.plates.MultiLayerPlating import MultiLayerPlateConfig, MultiLayerPlateLayer, \
    MultiLayerDataTypeConfig, MultiLayerReplicateConfig, MultiLayerDilutionConfig
from sapiopylib.rest.utils.plates.MultiLayerPlatingUtils import MultiLayerPlatingManager
from sapiopylib.rest.utils.plates.PlatingUtils import PlatingOrder


# CR-47564: Moved the entry creation functions to their own class.
class ExperimentStepFactory:
    user: SapioUser
    _exp_handler: ExperimentHandler

    _exp_id: int

    _eln_man: ElnManager
    _exp_cache: ExperimentCacheManager

    def __init__(self, exp_handler: ExperimentHandler):
        self.user = exp_handler.user
        self._exp_handler = exp_handler
        self._exp_id = exp_handler.protocol.get_id()
        self._eln_man = ElnManager(self.user)
        self._exp_cache = ExperimentCacheManager(self.user)

    # FR-47468: Add functions for creating new entries in the experiment.
    def create_attachment_step(self, entry_name: str, data_type: DataTypeIdentifier,
                               attachments: Iterable[EntryAttachment] | Iterable[SapioRecord] | None = None,
                               criteria: AttachmentStepCreation = AttachmentStepCreation(),
                               position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new attachment entry in the experiment.

        :param entry_name: The name of the entry.
        :param data_type: The data type of the entry.
        :param attachments: The list of attachments to initially populate the entry with.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created attachment entry.
        """
        entry_criteria = cast(ElnAttachmentEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))

        if attachments:
            entry_attachments: list[EntryAttachment] = []
            for entry in attachments:
                if isinstance(entry, EntryAttachment):
                    entry_attachments.append(entry)
                elif isinstance(entry, SapioRecord):
                    entry: SapioRecord
                    file_name: str = entry.get_field_value("FilePath")
                    if not file_name:
                        file_name = entry.get_field_value(SystemFields.DATA_RECORD_NAME__FIELD.field_name)
                    rec_id: int = AliasUtil.to_record_id(entry)
                    entry_attachments.append(EntryRecordAttachment(file_name, rec_id))
                else:
                    raise SapioException("Attachments must be of type EntryAttachment or SapioRecord.")
            entry_criteria.entry_attachment_list = entry_attachments

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_dashboard_step(self, entry_name, data_type: DataTypeIdentifier,
                              criteria: DashboardStepCreation = DashboardStepCreation(),
                              position: ElnEntryPosition | None = None) -> ElnEntryStep:
        entry_criteria = cast(ElnDashboardEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))

        if criteria:
            if entry_criteria.source_entry_id:
                entry_criteria.source_entry_id = self.__to_entry_ids([criteria.source_entry])[0]
            if criteria.dashboard_guids:
                entry_criteria.dashboard_guid_list = list(criteria.dashboard_guids)

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_form_step(self, entry_name: str,
                         data_type: DataTypeIdentifier,
                         record: SapioRecord | None = None,
                         criteria: GlobalDtFormStepCreation = GlobalDtFormStepCreation(),
                         position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new form entry in the experiment.

        :param entry_name: The name of the entry.
        :param data_type: The data type of the entry.
        :param record: The record to initially populate the entry with.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created form entry.
        """
        if record:
            rdt: str = AliasUtil.to_data_type_name(record)
            sdt: str = AliasUtil.to_data_type_name(data_type)
            if rdt != sdt:
                raise SapioException(f"Cannot set {rdt} records for entry {entry_name} of type "
                                     f"{sdt}.")

        entry_criteria = cast(ElnFormEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))
        if record:
            entry_criteria.record_id = AliasUtil.to_record_id(record)
        if criteria:
            entry_criteria.data_type_layout_name = criteria.layout_name
            if entry_criteria.form_name_list:
                entry_criteria.form_name_list = list(criteria.form_names)
            if criteria.extension_types:
                entry_criteria.extension_type_list = AliasUtil.to_data_type_names(criteria.extension_types)
            if criteria.field_names:
                entry_criteria.data_field_name_list = AliasUtil.to_data_field_names(criteria.field_names)

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_experiment_detail_form_step(self, entry_name: str,
                                           field_map: FieldMap | None = None,
                                           criteria: ELnDtFormStepCreation = ELnDtFormStepCreation(),
                                           position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new ELN experiment details form entry in the experiment.

        :param entry_name: The name of the entry.
        :param field_map: A field map that will be used to populate the entry. The data field names in
            the map must match the field names of the provided field definitions.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created form entry.
        """
        dt = ElnBaseDataType.EXPERIMENT_DETAIL
        return self._create_eln_dt_form_step(entry_name, dt, field_map, criteria, position)

    def create_sample_detail_form_step(self, entry_name: str,
                                       field_map: FieldMap | None = None,
                                       criteria: ELnDtFormStepCreation = ELnDtFormStepCreation(),
                                       position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new ELN sample details form entry in the experiment.

        :param entry_name: The name of the entry.
        :param field_map: A field map that will be used to populate the entry. The data field names in
            the map must match the field names of the provided field definitions.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created form entry.
        """
        dt = ElnBaseDataType.SAMPLE_DETAIL
        return self._create_eln_dt_form_step(entry_name, dt, field_map, criteria, position)

    def _create_eln_dt_form_step(self, entry_name: str,
                                 dt: ElnBaseDataType,
                                 field_map: FieldMap | None = None,
                                 criteria: ELnDtFormStepCreation = ELnDtFormStepCreation(),
                                 position: ElnEntryPosition | None = None) -> ElnEntryStep:
        entry_criteria = cast(ElnFormEntryCriteria,
                              self._create_step_criteria(entry_name, dt.data_type_name, criteria, position))

        if field_map:
            entry_criteria.field_map = field_map
        if criteria:
            entry_criteria.is_field_addable = criteria.is_field_addable
            entry_criteria.is_existing_field_removable = criteria.is_existing_field_removable
            if criteria.field_sets:
                field_sets: set[int] = set()
                for field_set in criteria.field_sets:
                    if isinstance(field_set, int):
                        field_sets.add(field_set)
                    elif isinstance(field_set, ElnFieldSetInfo):
                        field_sets.add(field_set.field_set_id)
                    elif isinstance(field_set, str):
                        field_sets.add(self._exp_cache.get_field_set(field_set).field_set_id)
                entry_criteria.field_set_id_list = list(field_sets)
            if criteria.field_definitions:
                entry_criteria.field_definition_list = list(criteria.field_definitions)
            if criteria.predefined_field_names:
                if entry_criteria.field_definition_list is None:
                    entry_criteria.field_definition_list = []
                for field_name in criteria.predefined_field_names:
                    entry_criteria.field_definition_list.append(self._exp_cache.get_predefined_field(field_name, dt))

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_plugin_step(self, entry_name: str,
                           data_type: DataTypeIdentifier,
                           criteria: PluginStepCreation | None,
                           position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new plugin entry in the experiment.

        :param entry_name: The name of the entry.
        :param data_type: The data type of the entry.
        :param criteria: Additional criteria for creating the entry, such as plugin name and whether it provides
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created plugin entry.
        """
        entry_criteria = cast(ElnPluginEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))

        if criteria:
            entry_criteria.csp_plugin_name = criteria.plugin_name
            entry_criteria.using_template_data = criteria.using_template_data
            entry_criteria.provides_template_data = criteria.provides_template_data

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_table_step(self, entry_name: str, data_type: DataTypeIdentifier,
                          records: list[SapioRecord] | None = None,
                          criteria: GlobalDtTableStepCreation = GlobalDtTableStepCreation(),
                          position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new table entry in the experiment.

        :param entry_name: The name of the entry.
        :param data_type: The data type of the entry.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :param records: The list of records to initially populate the entry with.
        :return: The newly created table entry.
        """
        entry_criteria = cast(ElnTableEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))
        if criteria:
            entry_criteria.data_type_layout_name = criteria.layout_name
            entry_criteria.show_key_fields = criteria.show_key_fields
            if criteria.extension_types:
                entry_criteria.extension_type_list = list(criteria.extension_types)
            if criteria.table_columns:
                entry_criteria.table_column_list = list(criteria.table_columns)
            if criteria.field_names:
                if entry_criteria.table_column_list is None:
                    entry_criteria.table_column_list = []
                for field in AliasUtil.to_data_field_names(criteria.field_names):
                    entry_criteria.table_column_list.append(TableColumn(data_type, field))

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        if records:
            self._exp_handler.set_step_records(step, records)
        return step

    def create_experiment_detail_table_step(self, entry_name: str,
                                            field_maps: list[FieldMap] | None = None,
                                            criteria: ELnDtTableStepCreation = ELnDtTableStepCreation(),
                                            position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new ELN experiment details table entry in the experiment.

        :param entry_name: The name of the entry.
        :param field_maps: A field maps list that will be used to populate the entry. The data field names in
            the maps must match the field names of the provided field definitions.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created table entry.
        """
        dt = ElnBaseDataType.EXPERIMENT_DETAIL
        return self._create_eln_dt_table_step(entry_name, dt, field_maps, criteria, position)

    def create_sample_detail_table_step(self, entry_name: str,
                                        field_maps: list[FieldMap] | None = None,
                                        criteria: ELnDtTableStepCreation = ELnDtTableStepCreation(),
                                        position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new ELN sample details table entry in the experiment.

        :param entry_name: The name of the entry.
        :param field_maps: A field maps list that will be used to populate the entry. The data field names in
            the maps must match the field names of the provided field definitions.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created table entry.
        """
        dt = ElnBaseDataType.SAMPLE_DETAIL
        return self._create_eln_dt_table_step(entry_name, dt, field_maps, criteria, position)

    def _create_eln_dt_table_step(self, entry_name: str,
                                  dt: ElnBaseDataType,
                                  field_maps: list[FieldMap] | None = None,
                                  criteria: ELnDtTableStepCreation = ELnDtTableStepCreation(),
                                  position: ElnEntryPosition | None = None) -> ElnEntryStep:
        entry_criteria = cast(ElnTableEntryCriteria,
                              self._create_step_criteria(entry_name, dt.data_type_name, criteria,  position))

        if field_maps:
            entry_criteria.field_map_list = field_maps
        if criteria:
            entry_criteria.is_field_addable = criteria.is_field_addable
            entry_criteria.is_existing_field_removable = criteria.is_existing_field_removable
            if criteria.field_sets:
                field_sets: set[int] = set()
                for field_set in criteria.field_sets:
                    if isinstance(field_set, int):
                        field_sets.add(field_set)
                    elif isinstance(field_set, ElnFieldSetInfo):
                        field_sets.add(field_set.field_set_id)
                    elif isinstance(field_set, str):
                        field_sets.add(self._exp_cache.get_field_set(field_set).field_set_id)
                entry_criteria.field_set_id_list = list(field_sets)
            if criteria.field_definitions:
                entry_criteria.field_definition_list = list(criteria.field_definitions)
            if criteria.predefined_field_names:
                if entry_criteria.field_definition_list is None:
                    entry_criteria.field_definition_list = []
                for field_name in criteria.predefined_field_names:
                    entry_criteria.field_definition_list.append(self._exp_cache.get_predefined_field(field_name, dt))
            if criteria.table_columns:
                entry_criteria.table_column_list = list(criteria.table_columns)

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_temp_data_step(self, entry_name: str,
                              data_type: DataTypeIdentifier,
                              criteria: TempDataStepCreation = TempDataStepCreation(),
                              position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new temp data entry in the experiment.

        :param entry_name: The name of the entry.
        :param data_type: The data type of the entry.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created temp data entry.
        """
        entry_criteria = cast(ElnTempDataEntryCriteria,
                              self._create_step_criteria(entry_name, data_type, criteria, position))

        if criteria:
            entry_criteria.temp_data_plugin_path = criteria.plugin_path

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))
        return step

    def create_text_step(self, entry_name: str,
                         text: str | None = None,
                         criteria: TextStepCreation = TextStepCreation(),
                         position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new text entry in the experiment.

        :param entry_name: The name of the entry.
        :param text: The text to populate the entry with.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created text entry.
        """
        dt = ElnBaseDataType.TEXT_ENTRY_DETAIL.data_type_name
        entry_criteria = cast(ElnTextEntryCriteria,
                              self._create_step_criteria(entry_name, dt, criteria, position))

        step = self._exp_handler.add_entry_to_caches(self._eln_man.add_experiment_entry(self._exp_id, entry_criteria))

        if text:
            text_record: DataRecord = step.get_records()[0]
            text_record.set_field_value(ElnBaseDataType.get_text_entry_data_field_name(), text)
            DataRecordManager(self.user).commit_data_records([text_record])

        return step

    def create_plate_designer_step(self, entry_name: str,
                                   source_entry: Step | None = None,
                                   criteria: PluginStepCreation = PluginStepCreation(),
                                   position: ElnEntryPosition | None = None) -> ElnEntryStep:
        """
        Create a new 3D plate designer entry in the experiment.

        :param entry_name: The name of the entry.
        :param source_entry: The entry that the plate designer will source its samples from.
        :param criteria: Additional criteria for creating the entry.
        :param position: Information about where to place the entry in the experiment.
        :return: The newly created plate designer entry.
        """
        criteria.plugin_name = PLATE_DESIGNER_PLUGIN
        if criteria.entry_height is None:
            criteria.entry_height = 600
        if source_entry is not None:
            criteria.related_entry_set = [source_entry]
        default_layer = MultiLayerPlateLayer(
            MultiLayerDataTypeConfig("Sample"),
            PlatingOrder.FillBy.BY_COLUMN,
            MultiLayerReplicateConfig(),
            MultiLayerDilutionConfig()
        )
        initial_step_options: dict[str, str] = {
            "MultiLayerPlating_Plate_RecordIdList": "",
            "MultiLayerPlating_Entry_Prefs": MultiLayerPlatingManager.get_entry_prefs_json([default_layer]),
            "MultiLayerPlating_Entry_PrePlating_Prefs": MultiLayerPlatingManager.get_plate_configs_json(MultiLayerPlateConfig())
        }
        if criteria.entry_options is None:
            criteria.entry_options = initial_step_options
        else:
            criteria.entry_options.update(initial_step_options)
        return self.create_plugin_step(entry_name, "Sample", criteria, position)

    def _create_step_criteria(self, name: str, dt: DataTypeIdentifier,
                              criteria: StepCreation, position: ElnEntryPosition | None) \
            -> AbstractElnEntryCriteria:
        """
        Create the criteria for a new entry in the experiment of the given type.
        """
        if position is not None:
            order: int = position.order
            tab_id: int = position.tab_id
            column_order: int = position.column_order
            column_span: int = position.column_span
        else:
            last_tab: ElnExperimentTab = self._exp_handler.get_last_tab()
            order: int = self._exp_handler.get_next_entry_order_in_tab(last_tab)
            tab_id: int = last_tab.tab_id
            column_order: int = 0
            column_span: int = last_tab.max_number_of_columns

        dt: str = AliasUtil.to_data_type_name(dt)
        et = criteria.entry_type
        entry_criteria = ExperimentEntryCriteriaUtil.get_entry_creation_criteria(et, name, dt, order)
        entry_criteria.notebook_experiment_tab_id = tab_id
        entry_criteria.column_order = column_order
        entry_criteria.column_span = column_span
        if criteria:
            entry_criteria.is_shown_in_template = criteria.is_shown_in_template
            entry_criteria.is_removable = criteria.is_removable
            entry_criteria.is_renamable = criteria.is_renamable
            entry_criteria.is_static_view = criteria.is_static_view
            if criteria.related_entry_set:
                entry_criteria.related_entry_set = self.__to_entry_ids(criteria.related_entry_set)
            if criteria.dependency_set:
                entry_criteria.dependency_set = self.__to_entry_ids(criteria.dependency_set)
            entry_criteria.requires_grabber_plugin = criteria.requires_grabber_plugin
            entry_criteria.entry_singleton_id = criteria.entry_singleton_id
            entry_criteria.is_hidden = criteria.is_hidden
            entry_criteria.entry_height = criteria.entry_height
            entry_criteria.description = criteria.description
            entry_criteria.is_initialization_required = criteria.is_initialization_required
            entry_criteria.collapse_entry = criteria.collapse_entry
            entry_criteria.entry_status = criteria.entry_status
            entry_criteria.template_item_fulfilled_timestamp = criteria.template_item_fulfilled_timestamp
            entry_criteria.entry_options = criteria.entry_options

        return entry_criteria

    def __to_entry_ids(self, entries: Iterable[ExperimentEntryIdentifier | str]) -> list[int] | None:
        entry_ids: set[int] = set()
        for entry in entries:
            if isinstance(entry, str):
                entry_ids.add(self._exp_handler.get_step(entry).get_id())
            else:
                entry_ids.add(AliasUtil.to_entry_id(entry))
        return list(entry_ids)