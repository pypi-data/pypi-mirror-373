from typing import Iterable

from sapiopycommons.general.aliases import DataTypeIdentifier, FieldIdentifier, ExperimentEntryIdentifier
from sapiopylib.rest.pojo.TableColumn import TableColumn
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.eln.SapioELNEnums import ExperimentEntryStatus, ElnEntryType
from sapiopylib.rest.pojo.eln.field_set import ElnFieldSetInfo


# CR-47564: Created these classes to streamline entry creation using the ExperimentEntryFactory.
class StepCreation:
    """
    An object that contains the criteria for creating a new entry in the experiment.
    """
    _entry_type: ElnEntryType
    """The type of the entry to be created."""
    is_shown_in_template: bool | None
    """Whether the entry will appear in the template if the experiment this entry is in is saved to a new template."""
    is_removable: bool | None
    """Whether the entry can be removed by users."""
    is_renamable: bool | None
    """Whether the entry can be renamed by users."""
    is_static_view: bool | None
    """Whether the entry's attachment is static. For attachment entries only. Static attachment entries will store
    their attachment data in the template."""
    related_entry_set: Iterable[ExperimentEntryIdentifier | str] | None
    """The IDs of the entries this entry is implicitly dependent on. If any of the entries are deleted then this entry
    is also deleted."""
    dependency_set: Iterable[ExperimentEntryIdentifier | str] | None
    """The IDs of the entries this entry is dependent on. Requires the entries to be completed before this entry will
    be enabled."""
    requires_grabber_plugin: bool
    """Whether to run a grabber plugin when this entry is initialized."""
    entry_singleton_id: str | None
    """When this field is present (i.e. not null or blank) it will enforce that only one entry with this singleton
    value is present in the experiment. If you attempt to create an entry with the singletonId of an entry already
    present in the experiment it will return the existing entry instead of creating a new one. If an entry isn't
    present in the Notebook Experiment with a matching singletonId it will create a new entry like normal."""
    is_hidden: bool | None
    """Whether the user is able to visibly see this entry within the experiment."""
    entry_height: int | None
    """The height of this entry in pixels. Setting the height to 0 will cause the entry to auto-size to its contents."""
    description: str | None
    """The description of the entry."""
    is_initialization_required: bool | None
    """Whether the user must manually initialize this entry by clicking on it."""
    collapse_entry: bool | None
    """Whether the entry should be collapsed by default."""
    entry_status: ExperimentEntryStatus | None
    """The current status of the entry."""
    template_item_fulfilled_timestamp: int | None
    """The time in milliseconds since the epoch that this entry became initialized."""
    entry_options: dict[str, str] | None
    """The entry options of the entry."""

    def __init__(self, entry_type: ElnEntryType):
        self._entry_type = entry_type
        self.is_shown_in_template = None
        self.is_removable = None
        self.is_renamable = None
        self.is_static_view = None
        self.related_entry_set = None
        self.dependency_set = None
        self.requires_grabber_plugin = False
        self.entry_singleton_id = None
        self.is_hidden = None
        self.entry_height = None
        self.description = None
        self.is_initialization_required = None
        self.collapse_entry = None
        self.entry_status = None
        self.template_item_fulfilled_timestamp = None
        self.entry_options = None

    @property
    def entry_type(self) -> ElnEntryType:
        return self._entry_type

class AttachmentStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new attachment entry in an experiment.
    """
    def __init__(self):
        super().__init__(ElnEntryType.Attachment)


class DashboardStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new dashboard entry in an experiment.
    """
    source_entry: ExperimentEntryIdentifier | str | None
    """The entry that contains the source data for this entry's dashboard(s)."""
    dashboard_guids: Iterable[str] | None
    """The GUIDs of the dashboards to display in this entry."""

    def __init__(self):
        super().__init__(ElnEntryType.Dashboard)
        self.source_entry = None
        self.dashboard_guids = None


class GlobalDtFormStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new global data type form entry in an experiment.
    """
    layout_name: str | None
    """The name of the data type layout to be displayed in this form. The layout must be for the data type for this
    entry."""
    form_names: Iterable[str] | None
    """The names of the components in the chosen data type layout to display in this form."""
    extension_types: Iterable[DataTypeIdentifier] | None
    """The names of the extension data types to display fields from within the form."""
    field_names: Iterable[FieldIdentifier] | None
    """A list of data field names for the fields to be displayed in the form."""

    def __init__(self):
        super().__init__(ElnEntryType.Form)
        self.form_names = None
        self.layout_name = None
        self.extension_types = None
        self.field_names = None


class ELnDtFormStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new ELN data type form entry in an experiment.
    """
    is_field_addable: bool | None
    """Whether new fields can be added to the entry by users."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the entry can be removed by users."""
    field_sets: Iterable[int | str | ElnFieldSetInfo] | None
    """The predefined field sets to display in this form."""
    field_definitions: Iterable[AbstractVeloxFieldDefinition] | None
    """New field definitions to be created for this entry."""
    predefined_field_names: Iterable[str] | None
    """The names of the predefined fields to display in this form."""

    def __init__(self):
        super().__init__(ElnEntryType.Form)
        self.is_field_addable = None
        self.is_existing_field_removable = None
        self.field_sets = None
        self.field_definitions = None
        self.predefined_field_names = None
        self.table_columns = None


class PluginStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new plugin entry in an experiment.
    """
    plugin_name: str | None
    """The client side plugin name to render this entry with."""
    using_template_data: bool | None
    """Whether this entry will use the data from the template."""
    provides_template_data: bool | None
    """Whether this entry can provide data to copy into a new template."""

    def __init__(self):
        super().__init__(ElnEntryType.Plugin)
        self.plugin_name = None
        self.using_template_data = None
        self.provides_template_data = None


class GlobalDtTableStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new global data type table entry in an experiment.
    """
    layout_name: str | None
    """The name of the data type layout to display in this table."""
    extension_types: Iterable[str] | None
    """The names of the extension data types to display fields from within the table."""
    table_columns: Iterable[TableColumn] | None
    """The columns to display in the table. This can be used to change the sort order and direction of columns."""
    field_names: Iterable[FieldIdentifier] | None
    """A list of data field names for the fields to be displayed in the table. These will be added as TableColumns and
    placed after any of the existing columns specified in the table_columns parameter without any sorting."""
    show_key_fields: bool | None
    """Whether the key fields of the data type should be shown in the entry."""

    def __init__(self):
        super().__init__(ElnEntryType.Table)
        self.layout_name = None
        self.extension_types = None
        self.table_columns = None
        self.field_names = None
        self.show_key_fields = None


class ELnDtTableStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new ELN data type table entry in an experiment.
    """
    is_field_addable: bool | None
    """Whether new fields can be added to the entry by users."""
    is_existing_field_removable: bool | None
    """Whether existing fields on the entry can be removed by users."""
    field_sets: Iterable[int | str | ElnFieldSetInfo] | None
    """The predefined field sets to display in this form."""
    field_definitions: Iterable[AbstractVeloxFieldDefinition] | None
    """New field definitions to be created for this entry."""
    predefined_field_names: Iterable[str] | None
    """The names of the predefined fields to display in this form."""
    table_columns: Iterable[TableColumn] | None
    """The columns to display in the table."""

    def __init__(self):
        super().__init__(ElnEntryType.Table)
        self.is_field_addable = None
        self.is_existing_field_removable = None
        self.field_sets = None
        self.field_definitions = None
        self.predefined_field_names = None
        self.table_columns = None


class TempDataStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new temp data entry in an experiment.
    """
    plugin_path: str | None
    """The temp data plugin path to run to populate the entry."""

    def __init__(self):
        super().__init__(ElnEntryType.TempData)
        self.plugin_path = None


class TextStepCreation(StepCreation):
    """
    An object that contains criteria for creating a new text entry in an experiment.
    """
    def __init__(self):
        super().__init__(ElnEntryType.Text)
