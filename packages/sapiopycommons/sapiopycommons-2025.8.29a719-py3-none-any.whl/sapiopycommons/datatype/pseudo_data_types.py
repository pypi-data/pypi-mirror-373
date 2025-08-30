from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrapperField


class ActiveTaskPseudoDef:
    DATA_TYPE_NAME: str = "ActiveTask"
    ACTIVE_TASK_ID__FIELD_NAME = WrapperField("ActiveTaskId", FieldType.LONG, display_name="Active Task ID")
    ACTIVE_WORKFLOW_ID__FIELD_NAME = WrapperField("ActiveWorkflowId", FieldType.LONG, display_name="Active Workflow ID")
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE, display_name="Date Edited")
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING, display_name="Edited By")
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.ENUM, display_name="Status")
    TASK_USAGE_ID__FIELD_NAME = WrapperField("TaskUsageId", FieldType.LONG, display_name="Task Usage ID")


class ActiveWorkflowPseudoDef:
    DATA_TYPE_NAME: str = "ActiveWorkflow"
    ACTIVE_WORKFLOW_ID__FIELD_NAME = WrapperField("ActiveWorkflowId", FieldType.LONG, display_name="Active Workflow ID")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.STRING, display_name="Date Last Edited")
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING, display_name="Last Edited By")
    ESTIMATED_ATTACHMENTS__FIELD_NAME = WrapperField("EstimatedAttachments", FieldType.LONG, display_name="Estimated Attachments")
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING, display_name="Name")
    RELATED_RECORD_ID__FIELD_NAME = WrapperField("RelatedRecordId", FieldType.LONG, display_name="Related Record ID")
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.ENUM, display_name="Status")
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG, display_name="Workflow ID")


class AuditLogPseudoDef:
    DATA_TYPE_NAME: str = "AuditLog"
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING, display_name="Data Field Name")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data Type Name")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    EVENT_TYPE__FIELD_NAME = WrapperField("EventType", FieldType.ENUM, display_name="Event Type")
    FULL_NAME__FIELD_NAME = WrapperField("FullName", FieldType.STRING, display_name="User's Full Name")
    NEW_VALUE__FIELD_NAME = WrapperField("NewValue", FieldType.STRING, display_name="New Value")
    ORIGINAL_VALUE__FIELD_NAME = WrapperField("OriginalValue", FieldType.STRING, display_name="Original Value")
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG, display_name="Record ID")
    RECORD_NAME__FIELD_NAME = WrapperField("RecordName", FieldType.STRING, display_name="Data Record Name(ID)")
    TIME_STAMP__FIELD_NAME = WrapperField("TimeStamp", FieldType.DATE, display_name="Date")
    USER_COMMENT__FIELD_NAME = WrapperField("UserComment", FieldType.STRING, display_name="Comment")
    USER_NAME__FIELD_NAME = WrapperField("UserName", FieldType.STRING, display_name="User's Login Name")


class DataFieldDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "DataFieldDefinition"
    APPROVE_EDIT__FIELD_NAME = WrapperField("ApproveEdit", FieldType.BOOLEAN, display_name="Approve Edit")
    AUTO_CLEAR_FIELD_LIST__FIELD_NAME = WrapperField("AutoClearFieldList", FieldType.STRING, display_name="Auto Clear Field List")
    AUTO_SORT__FIELD_NAME = WrapperField("AutoSort", FieldType.BOOLEAN, display_name="Auto-Sort")
    BACKGROUND_COLOR__FIELD_NAME = WrapperField("BACKGROUND_COLOR", FieldType.STRING, display_name="Background Color")
    BOLD_FONT__FIELD_NAME = WrapperField("BOLDFONT", FieldType.BOOLEAN, display_name="Bold Font")
    COLOR_MAPPING_ID__FIELD_NAME = WrapperField("ColorMappingId", FieldType.LONG, display_name="Color Mapping ID")
    DATE_TIME_FORMAT__FIELD_NAME = WrapperField("DATETIMEFORMAT", FieldType.STRING, display_name="Date Time Format")
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING, display_name="Data Field Name")
    DATA_FIELD_TAG__FIELD_NAME = WrapperField("DataFieldTag", FieldType.STRING, display_name="Data Field Tag")
    DATA_FIELD_TYPE__FIELD_NAME = WrapperField("DataFieldType", FieldType.STRING, display_name="Data Field Type")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data TypeName")
    DECIMAL_DIGITS__FIELD_NAME = WrapperField("DecimalDigits", FieldType.INTEGER, display_name="Decimal Digits")
    DEFAULT_VALUE__FIELD_NAME = WrapperField("DefaultValue", FieldType.STRING, display_name="Default Value")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    DIRECT_EDIT__FIELD_NAME = WrapperField("DirectEdit", FieldType.BOOLEAN, display_name="Allow Direct Edit")
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING, display_name="Display Name")
    EDITABLE__FIELD_NAME = WrapperField("Editable", FieldType.BOOLEAN, display_name="Editable")
    ENUM_VALUES__FIELD_NAME = WrapperField("EnumValues", FieldType.STRING, display_name="Values")
    FIELD_VALIDATOR_ERROR__FIELD_NAME = WrapperField("FIELD_VALIDATOR_ERROR", FieldType.STRING, display_name="Field Validator Error")
    FIELD_VALIDATOR_REGEX__FIELD_NAME = WrapperField("FIELD_VALIDATOR_REGEX", FieldType.STRING, display_name="Field Validator Regex")
    FONT_SIZE__FIELD_NAME = WrapperField("FONTSIZE", FieldType.STRING, display_name="Font Size")
    FONT_COLOR__FIELD_NAME = WrapperField("FONT_COLOR", FieldType.STRING, display_name="Font Color")
    FORMAT_TYPE__FIELD_NAME = WrapperField("FORMATTYPE", FieldType.STRING, display_name="Format Type")
    HTML_EDITOR__FIELD_NAME = WrapperField("HtmlEditor", FieldType.BOOLEAN, display_name="HTML Editor")
    ICON_COLOR__FIELD_NAME = WrapperField("ICON_COLOR", FieldType.STRING, display_name="Icon Color")
    ICON_NAME__FIELD_NAME = WrapperField("ICON_NAME", FieldType.STRING, display_name="Icon Name")
    IDENTIFIER_ORDER__FIELD_NAME = WrapperField("IDENTIFIERORDER", FieldType.INTEGER, display_name="Identifier Order")
    IS_ACTIVE__FIELD_NAME = WrapperField("ISACTIVE", FieldType.BOOLEAN, display_name="Is Active")
    IS_AUDIT_LOGGED__FIELD_NAME = WrapperField("ISAUDITLOGGED", FieldType.BOOLEAN, display_name="Is Audit Logged")
    IS_HIDE_DISABLED_FIELDS__FIELD_NAME = WrapperField("ISHIDEDISABLEDFIELDS", FieldType.BOOLEAN, display_name="Is Hide Disabled Fields")
    IS_PROCESS_TODO_ITEM__FIELD_NAME = WrapperField("ISPROCESSTODOITEM", FieldType.BOOLEAN, display_name="Is Process Todo Item")
    IS_REMOVABLE__FIELD_NAME = WrapperField("ISREMOVABLE", FieldType.BOOLEAN, display_name="Is Removable")
    IS_RESTRICTED__FIELD_NAME = WrapperField("ISRESTRICTED", FieldType.BOOLEAN, display_name="Is Restricted")
    IS_SYSTEM_FIELD__FIELD_NAME = WrapperField("ISSYSTEMFIELD", FieldType.BOOLEAN, display_name="Is System Field")
    IS_AUTO_SIZE__FIELD_NAME = WrapperField("IS_AUTO_SIZE", FieldType.BOOLEAN, display_name="Is Auto Size")
    ITALIC_FONT__FIELD_NAME = WrapperField("ITALICFONT", FieldType.BOOLEAN, display_name="Italic Font")
    IDENTIFIER__FIELD_NAME = WrapperField("Identifier", FieldType.BOOLEAN, display_name="Identifier")
    INDEX_FOR_SEARCH__FIELD_NAME = WrapperField("IndexForSearch", FieldType.BOOLEAN, display_name="Index For Search")
    KEY_FIELD__FIELD_NAME = WrapperField("KEYFIELD", FieldType.BOOLEAN, display_name="Key Field")
    KEY_FIELD_ORDER__FIELD_NAME = WrapperField("KEYFIELDORDER", FieldType.INTEGER, display_name="Key Field Order")
    KNOWLEDGE_GRAPH_DISPLAY_NAME__FIELD_NAME = WrapperField("KNOWLEDGE_GRAPH_DISPLAY_NAME", FieldType.STRING, display_name="Knowledge Graph Display name")
    LINKED_DATA_TYPE_NAME__FIELD_NAME = WrapperField("LINKED_DATA_TYPE_NAME", FieldType.STRING, display_name="Linked Data Type Name")
    LINK_OUT__FIELD_NAME = WrapperField("LinkOut", FieldType.BOOLEAN, display_name="Link Out")
    LINK_OUT_URL__FIELD_NAME = WrapperField("LinkOutUrl", FieldType.STRING, display_name="Link Out URL")
    MAX_LENGTH__FIELD_NAME = WrapperField("MaxLength", FieldType.INTEGER, display_name="Maximum Length")
    MAXIMUM_VALUE__FIELD_NAME = WrapperField("MaximumValue", FieldType.DOUBLE, display_name="Maximum Value")
    MINIMUM_VALUE__FIELD_NAME = WrapperField("MinimumValue", FieldType.DOUBLE, display_name="Minimum Value")
    MULTI_SELECT__FIELD_NAME = WrapperField("MultiSelect", FieldType.BOOLEAN, display_name="Multi Select")
    NUMBER_OF_DIGITS__FIELD_NAME = WrapperField("NUMBEROFDIGITS", FieldType.INTEGER, display_name="Number Of Digits")
    NUM_LINES__FIELD_NAME = WrapperField("NumLines", FieldType.INTEGER, display_name="Number of Lines")
    PLUGIN_PATH__FIELD_NAME = WrapperField("PLUGIN_PATH", FieldType.STRING, display_name="Plugin path")
    PREFIX__FIELD_NAME = WrapperField("PREFIX", FieldType.STRING, display_name="Prefix")
    PRESERVE_PADDING__FIELD_NAME = WrapperField("PRESERVE_PADDING", FieldType.BOOLEAN, display_name="Preserve Padding")
    REQUIRED__FIELD_NAME = WrapperField("Required", FieldType.BOOLEAN, display_name="Required")
    SCI_MIN_NUM_DIGITS__FIELD_NAME = WrapperField("SCI_MIN_NUM_DIGITS", FieldType.INTEGER, display_name="Minimum Number of Digits")
    SEQUENCE_KEY__FIELD_NAME = WrapperField("SEQUENCE_KEY", FieldType.STRING, display_name="Sequence Key")
    SHOW_IN_KNOWLEDGE_GRAPH__FIELD_NAME = WrapperField("SHOW_IN_KNOWLEDGE_GRAPH", FieldType.BOOLEAN, display_name="Show In Knowledge Graph")
    SORT_DIRECTION__FIELD_NAME = WrapperField("SORTDIRECTION", FieldType.STRING, display_name="Sort Direction")
    SORT_ORDER__FIELD_NAME = WrapperField("SORTORDER", FieldType.INTEGER, display_name="Sort Order")
    STARTING_VALUE__FIELD_NAME = WrapperField("STARTINGVALUE", FieldType.LONG, display_name="Starting Value")
    SUFFIX__FIELD_NAME = WrapperField("SUFFIX", FieldType.STRING, display_name="Suffix")
    STATIC_DATE__FIELD_NAME = WrapperField("StaticDate", FieldType.BOOLEAN, display_name="Static Date")
    TABLE_COLUMN_WIDTH__FIELD_NAME = WrapperField("TABLE_COLUMN_WIDTH", FieldType.INTEGER, display_name="Table Column Width")
    TEXT_DECORATION__FIELD_NAME = WrapperField("TEXTDECORATION", FieldType.STRING, display_name="Text Decoration")
    UNIQUE_VALUE__FIELD_NAME = WrapperField("UniqueValue", FieldType.BOOLEAN, display_name="Unique Value")
    VISIBLE__FIELD_NAME = WrapperField("Visible", FieldType.BOOLEAN, display_name="Visible")
    WORKFLOW_ONLY_EDITING__FIELD_NAME = WrapperField("WorkflowOnlyEditing", FieldType.BOOLEAN, display_name="Workflow Only Editing")


class DataTypeDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "DataTypeDefinition"
    ADDABLE__FIELD_NAME = WrapperField("Addable", FieldType.BOOLEAN, display_name="Addable")
    ATTACHMENT__FIELD_NAME = WrapperField("Attachment", FieldType.BOOLEAN, display_name="Attachment Type")
    ATTACHMENT_TYPE__FIELD_NAME = WrapperField("AttachmentType", FieldType.STRING, display_name="Attachment Extension Types")
    DATA_TYPE_TAG__FIELD_NAME = WrapperField("DATA_TYPE_TAG", FieldType.STRING, display_name="Data Type Tag")
    DATA_TYPE_ID__FIELD_NAME = WrapperField("DataTypeId", FieldType.LONG, display_name="Data Type ID")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data Type Name")
    DELETABLE__FIELD_NAME = WrapperField("Deletable", FieldType.BOOLEAN, display_name="Deletable")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING, display_name="Display Name")
    EXTENSION_TYPE__FIELD_NAME = WrapperField("ExtensionType", FieldType.BOOLEAN, display_name="Extension Type")
    GROUP_ADDABLE__FIELD_NAME = WrapperField("GroupAddable", FieldType.BOOLEAN, display_name="Group Addable")
    HIDE_RECORD_SELECTION_ON_ADD__FIELD_NAME = WrapperField("HIDE_RECORD_SELECTION_ON_ADD", FieldType.BOOLEAN, display_name="Hide Record Selection On Add")
    HIDE_DATA_RECORDS__FIELD_NAME = WrapperField("HideDataRecords", FieldType.BOOLEAN, display_name="Hide Data Records")
    HIGH_VOLUME__FIELD_NAME = WrapperField("HighVolume", FieldType.BOOLEAN, display_name="High Volume")
    IS_HIDE_IN_MOBILE__FIELD_NAME = WrapperField("IS_HIDE_IN_MOBILE", FieldType.BOOLEAN, display_name="Is Hide In Mobile")
    IS_HVDT_ON_SAVE_ENABLED__FIELD_NAME = WrapperField("IS_HVDT_ON_SAVE_ENABLED", FieldType.BOOLEAN, display_name="Is HVDT On Save Enabled")
    IS_PUBLIC_ATTACHMENT__FIELD_NAME = WrapperField("IS_PUBLIC_ATTACHMENT", FieldType.BOOLEAN, display_name="Is Public Attachment")
    ICON_COLOR__FIELD_NAME = WrapperField("IconColor", FieldType.STRING, display_name="Icon Color")
    ICON_NAME__FIELD_NAME = WrapperField("IconName", FieldType.STRING, display_name="Icon Name")
    IMPORTABLE__FIELD_NAME = WrapperField("Importable", FieldType.BOOLEAN, display_name="Importable")
    IS_ACTIVE__FIELD_NAME = WrapperField("IsActive", FieldType.BOOLEAN, display_name="Is Active")
    IS_HIDDEN__FIELD_NAME = WrapperField("IsHidden", FieldType.BOOLEAN, display_name="Is Hidden")
    MAX_TABLE_ROW_COUNT__FIELD_NAME = WrapperField("MaxTableRowCount", FieldType.LONG, display_name="Max Table Row Count")
    PLURAL_DISPLAY_NAME__FIELD_NAME = WrapperField("PluralDisplayName", FieldType.STRING, display_name="Plural Display Name")
    RECORD_ASSIGNABLE__FIELD_NAME = WrapperField("RecordAssignable", FieldType.BOOLEAN, display_name="Record Assignable")
    RECORD_IMAGE_ASSIGNABLE__FIELD_NAME = WrapperField("RecordImageAssignable", FieldType.BOOLEAN, display_name="Record Image Assignable")
    RECORD_IMAGE_MANUALLY_ADDABLE__FIELD_NAME = WrapperField("RecordImageManuallyAddable", FieldType.BOOLEAN, display_name="Record Image Manually Addable")
    REMOVABLE__FIELD_NAME = WrapperField("Removable", FieldType.BOOLEAN, display_name="Removable")
    RESTRICTED__FIELD_NAME = WrapperField("Restricted", FieldType.BOOLEAN, display_name="Restricted")
    SHOW_IN_KNOWLEDGE_GRAPH__FIELD_NAME = WrapperField("SHOW_IN_KNOWLEDGE_GRAPH", FieldType.BOOLEAN, display_name="Show In Knowledge Graph")
    SHOW_ON_HOME_SCREEN__FIELD_NAME = WrapperField("ShowOnHomeScreen", FieldType.BOOLEAN, display_name="Show On Home Screen")
    SHOW_SUB_TABLES__FIELD_NAME = WrapperField("ShowSubTables", FieldType.BOOLEAN, display_name="Show Sub Tables")
    SHOW_TABS__FIELD_NAME = WrapperField("ShowTabs", FieldType.BOOLEAN, display_name="Show Tabs")
    SINGLE_PARENT__FIELD_NAME = WrapperField("SingleParent", FieldType.BOOLEAN, display_name="Single Parent")
    UNDER_CONTAINER__FIELD_NAME = WrapperField("UnderContainer", FieldType.BOOLEAN, display_name="Under Container")


class EnbDataTypeDefinitionPseudoDef:
    DATA_TYPE_NAME: str = "EnbDataTypeDefinition"
    DATA_TYPE_ID__FIELD_NAME = WrapperField("DataTypeId", FieldType.LONG, display_name="Data Type ID")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data Type Name")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    DISPLAY_NAME__FIELD_NAME = WrapperField("DisplayName", FieldType.STRING, display_name="Display Name")
    ENB_DATA_TYPE_NAME__FIELD_NAME = WrapperField("EnbDataTypeName", FieldType.STRING, display_name="ENB Base Data Type Name")
    ICON_COLOR__FIELD_NAME = WrapperField("IconColor", FieldType.STRING, display_name="Icon Color")
    ICON_NAME__FIELD_NAME = WrapperField("IconName", FieldType.STRING, display_name="Icon Name")
    NOTEBOOK_EXPERIMENT_ID__FIELD_NAME = WrapperField("Notebook_Experiment_ID", FieldType.LONG, display_name="Notebook Experiment ID")
    PLURAL_DISPLAY_NAME__FIELD_NAME = WrapperField("PluralDisplayName", FieldType.STRING, display_name="Plural Display Name")


class EnbEntryPseudoDef:
    DATA_TYPE_NAME: str = "EnbEntry"
    APPROVAL_DUE_DATE__FIELD_NAME = WrapperField("ApprovalDueDate", FieldType.DATE, display_name="Approval Due Date")
    COLUMN_ORDER__FIELD_NAME = WrapperField("ColumnOrder", FieldType.INTEGER, display_name="Column Order")
    COLUMN_SPAN__FIELD_NAME = WrapperField("ColumnSpan", FieldType.INTEGER, display_name="Column Span")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data Type Name")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    DEPENDENT_ENTRY_ID_LIST__FIELD_NAME = WrapperField("DependentEntryIdList", FieldType.STRING, display_name="Dependent Entry ID List")
    ENTRY_DESCRIPTION__FIELD_NAME = WrapperField("EntryDescription", FieldType.STRING, display_name="Entry Description")
    ENTRY_HEIGHT__FIELD_NAME = WrapperField("EntryHeight", FieldType.INTEGER, display_name="Entry Height")
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG, display_name="Entry ID")
    ENTRY_NAME__FIELD_NAME = WrapperField("EntryName", FieldType.STRING, display_name="Entry Name")
    ENTRY_ORDER__FIELD_NAME = WrapperField("EntryOrder", FieldType.INTEGER, display_name="Entry Order")
    ENTRY_REQUIRES_E_SIGN__FIELD_NAME = WrapperField("EntryRequiresESign", FieldType.BOOLEAN, display_name="Entry Requries Esign")
    ENTRY_SINGLETON_ID__FIELD_NAME = WrapperField("EntrySingletonId", FieldType.STRING, display_name="Entry Singleton ID")
    ENTRY_STATUS__FIELD_NAME = WrapperField("EntryStatus", FieldType.STRING, display_name="Entry Status")
    ENTRY_TYPE__FIELD_NAME = WrapperField("EntryType", FieldType.STRING, display_name="Entry Type")
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG, display_name="Experiment ID")
    HAS_COMMENTS__FIELD_NAME = WrapperField("HasComments", FieldType.BOOLEAN, display_name="Has Comments")
    IS_CREATED_FROM_TEMPLATE__FIELD_NAME = WrapperField("IsCreatedFromTemplate", FieldType.BOOLEAN, display_name="Is Created From Template")
    IS_REQUIRED_ENTRY__FIELD_NAME = WrapperField("IsRequiredEntry", FieldType.BOOLEAN, display_name="Is Required Entry")
    IS_SHOWN_IN_TEMPLATE__FIELD_NAME = WrapperField("IsShownInTemplate", FieldType.BOOLEAN, display_name="Is Shown In Template")
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING, display_name="Last Modified By")
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.DATE, display_name="Last Mdoified Date")
    RELATED_ENTRY_ID_LIST__FIELD_NAME = WrapperField("RelatedEntryIdList", FieldType.STRING, display_name="Related Entry ID List")
    REQUIRES_GRABBER_PLUGIN__FIELD_NAME = WrapperField("RequiresGrabberPlugin", FieldType.BOOLEAN, display_name="Requires Grabber Plugin")
    SOURCE_ENTRY_ID__FIELD_NAME = WrapperField("SourceEntryId", FieldType.LONG, display_name="Source Entry ID")
    SUBMITTED_BY__FIELD_NAME = WrapperField("SubmittedBy", FieldType.STRING, display_name="Submitted By")
    SUBMITTED_DATE__FIELD_NAME = WrapperField("SubmittedDate", FieldType.DATE, display_name="Submitted Date")
    TAB_ID__FIELD_NAME = WrapperField("TabId", FieldType.LONG, display_name="Tab ID")
    TEMPLATE_ITEM_FULFILLED_TIME_STAMP__FIELD_NAME = WrapperField("TemplateItemFulfilledTimeStamp", FieldType.LONG, display_name="Template Item Fulfilled Time Stamp")


class EnbEntryOptionsPseudoDef:
    DATA_TYPE_NAME: str = "EnbEntryOptions"
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG, display_name="Entry ID")
    ENTRY_OPTION_VALUE__FIELD_NAME = WrapperField("EntryOptionValue", FieldType.STRING, display_name="Entry Option Value")
    ENTRY_OPTION_KEY__FIELD_NAME = WrapperField("EntryOptionkey", FieldType.STRING, display_name="Entry Option Key")


class ExperimentEntryRecordPseudoDef:
    DATA_TYPE_NAME: str = "ExperimentEntryRecord"
    ENTRY_ID__FIELD_NAME = WrapperField("EntryId", FieldType.LONG, display_name="Entry ID")
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG, display_name="Record ID")


class NotebookExperimentPseudoDef:
    DATA_TYPE_NAME: str = "NotebookExperiment"
    ACCESS_LEVEL__FIELD_NAME = WrapperField("AccessLevel", FieldType.STRING, display_name="Access Level")
    APPROVAL_DUE_DATE__FIELD_NAME = WrapperField("ApprovalDueDate", FieldType.DATE, display_name="Approval Due Date")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG, display_name="Notebook Experiment ID")
    EXPERIMENT_NAME__FIELD_NAME = WrapperField("ExperimentName", FieldType.STRING, display_name="Notebook Experiment Name")
    EXPERIMENT_OWNER__FIELD_NAME = WrapperField("ExperimentOwner", FieldType.STRING, display_name="Notebook Experiment Owner")
    EXPERIMENT_RECORD_ID__FIELD_NAME = WrapperField("ExperimentRecordId", FieldType.LONG, display_name="Experiment Record ID")
    EXPERIMENT_TYPE_NAME__FIELD_NAME = WrapperField("ExperimentTypeName", FieldType.STRING, display_name="ExperimentDataTypeName")
    IS_ACTIVE__FIELD_NAME = WrapperField("IsActive", FieldType.BOOLEAN, display_name="Is Active")
    IS_MODIFIABLE__FIELD_NAME = WrapperField("IsModifiable", FieldType.BOOLEAN, display_name="Is Modifiable")
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN, display_name="Is Template")
    IS_PROTOCOL_TEMPLATE__FIELD_NAME = WrapperField("Is_Protocol_Template", FieldType.BOOLEAN, display_name="Is Protocol Template")
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING, display_name="Last Modified By")
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.DATE, display_name="Last Modified Date")
    SOURCE_TEMPLATE_ID__FIELD_NAME = WrapperField("SourceTemplateId", FieldType.LONG, display_name="Source Template ID")
    STATUS__FIELD_NAME = WrapperField("Status", FieldType.STRING, display_name="Notebook Experiment Status")
    TEMPLATE_VERSION__FIELD_NAME = WrapperField("TemplateVersion", FieldType.LONG, display_name="Template Version")


class NotebookExperimentOptionPseudoDef:
    DATA_TYPE_NAME: str = "NotebookExperimentOption"
    EXPERIMENT_ID__FIELD_NAME = WrapperField("ExperimentId", FieldType.LONG, display_name="Experiment ID")
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING, display_name="Option Key")
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING, display_name="Option Value")


class SystemLogPseudoDef:
    DATA_TYPE_NAME: str = "SystemLog"
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("DataFieldName", FieldType.STRING, display_name="Data Field Name")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("DataTypeName", FieldType.STRING, display_name="Data Type Name")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    EVENT_ID__FIELD_NAME = WrapperField("EventId", FieldType.LONG, display_name="Event ID")
    EVENT_TYPE__FIELD_NAME = WrapperField("EventType", FieldType.STRING, display_name="Event Type")
    FULL_NAME__FIELD_NAME = WrapperField("FullName", FieldType.STRING, display_name="Full Name")
    NEW_VALUE__FIELD_NAME = WrapperField("NewValue", FieldType.STRING, display_name="New Value")
    ORIGINAL_VALUE__FIELD_NAME = WrapperField("OriginalValue", FieldType.STRING, display_name="Original Value")
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG, display_name="Record ID")
    RECORD_NAME__FIELD_NAME = WrapperField("RecordName", FieldType.STRING, display_name="Data Record Name")
    TIMESTAMP__FIELD_NAME = WrapperField("Timestamp", FieldType.DATE, display_name="Timestamp")
    USER_COMMENT__FIELD_NAME = WrapperField("UserComment", FieldType.STRING, display_name="User Comment")
    USERNAME__FIELD_NAME = WrapperField("Username", FieldType.STRING, display_name="Username")


class SystemObjectChangeLogPseudoDef:
    DATA_TYPE_NAME: str = "System_Object_Change_Log"
    ALT_ID__FIELD_NAME = WrapperField("Alt_Id", FieldType.STRING, display_name="Alternative ID")
    ATTRIBUTE_NAME__FIELD_NAME = WrapperField("Attribute_Name", FieldType.STRING, display_name="Attribute Name")
    CHANGE_TYPE__FIELD_NAME = WrapperField("Change_Type", FieldType.STRING, display_name="Change Type")
    DATA_FIELD_NAME__FIELD_NAME = WrapperField("Data_Field_Name", FieldType.STRING, display_name="Data Field Name")
    DATA_TYPE_NAME__FIELD_NAME = WrapperField("Data_Type_Name", FieldType.STRING, display_name="Data Type Name")
    EVENT_ID__FIELD_NAME = WrapperField("Event_Id", FieldType.STRING, display_name="Event ID")
    NEW_VALUE__FIELD_NAME = WrapperField("New_Value", FieldType.STRING, display_name="New Value")
    OBJECT_ID__FIELD_NAME = WrapperField("Object_Id", FieldType.STRING, display_name="Object ID")
    OBJECT_TYPE__FIELD_NAME = WrapperField("Object_Type", FieldType.STRING, display_name="Object Type")
    OLD_VALUE__FIELD_NAME = WrapperField("Old_Value", FieldType.STRING, display_name="Old Value")
    TIMESTAMP__FIELD_NAME = WrapperField("Timestamp", FieldType.DATE, display_name="Timestamp")
    USERNAME__FIELD_NAME = WrapperField("Username", FieldType.STRING, display_name="Username")


class TaskPseudoDef:
    DATA_TYPE_NAME: str = "Task"
    ATTACHMENT_REQUIRED__FIELD_NAME = WrapperField("AttachmentRequired", FieldType.BOOLEAN, display_name="Attachment Required")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    CUSTOM_ACTION__FIELD_NAME = WrapperField("CustomAction", FieldType.STRING, display_name="Custom Action")
    DATA_TYPE_NAME_LIST__FIELD_NAME = WrapperField("DataTypeNameList", FieldType.STRING, display_name="Date Type Name List")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE, display_name="Date Edited")
    DISPLAY_TYPE__FIELD_NAME = WrapperField("DisplayType", FieldType.ENUM, display_name="Display Type")
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING, display_name="Edited By")
    INPUT_DATA_TYPE_NAME__FIELD_NAME = WrapperField("InputDataTypeName", FieldType.STRING, display_name="Input Data Type Name")
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN, display_name="Is Template")
    LONG_DESC__FIELD_NAME = WrapperField("LongDesc", FieldType.STRING, display_name="Long Description")
    MENU_TASK_ID__FIELD_NAME = WrapperField("MenuTaskId", FieldType.ENUM, display_name="Action Task Type")
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING, display_name="Name")
    SHORT_DESC__FIELD_NAME = WrapperField("ShortDesc", FieldType.STRING, display_name="Short Description")
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG, display_name="Task ID")
    TASK_VERSION__FIELD_NAME = WrapperField("TaskVersion", FieldType.LONG, display_name="Task Version")
    TEMPLATE_TASK_ID__FIELD_NAME = WrapperField("TemplateTaskId", FieldType.LONG, display_name="Template Task ID")
    TYPE__FIELD_NAME = WrapperField("Type", FieldType.ENUM, display_name="Type")


class TaskAttachmentPseudoDef:
    DATA_TYPE_NAME: str = "TaskAttachment"
    ACTIVE_TASK_ID__FIELD_NAME = WrapperField("ActiveTaskId", FieldType.LONG, display_name="Active Task ID")
    RECORD_ID__FIELD_NAME = WrapperField("RecordId", FieldType.LONG, display_name="Record ID")


class TaskOptionPseudoDef:
    DATA_TYPE_NAME: str = "TaskOption"
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING, display_name="Option Key")
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING, display_name="Option Value")
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG, display_name="Task ID")


class TaskUsagePseudoDef:
    DATA_TYPE_NAME: str = "TaskUsage"
    FORCE_ATTACH__FIELD_NAME = WrapperField("ForceAttach", FieldType.BOOLEAN, display_name="Force Attach")
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN, display_name="Is Template")
    TASK_ID__FIELD_NAME = WrapperField("TaskId", FieldType.LONG, display_name="Task ID")
    TASK_ORDER__FIELD_NAME = WrapperField("TaskOrder", FieldType.INTEGER, display_name="Task Order")
    TASK_USAGE_ID__FIELD_NAME = WrapperField("TaskUsageId", FieldType.LONG, display_name="Task Usage ID")
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG, display_name="Workflow ID")


class VeloxWebhookPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK"
    CUSTOM_PLUGIN_POINT__FIELD_NAME = WrapperField("CUSTOM_PLUGIN_POINT", FieldType.STRING, display_name="Custom Plugin Point")
    DATA_TYPE_NAME_SET__FIELD_NAME = WrapperField("DATA_TYPE_NAME_SET", FieldType.STRING, display_name="Data Type Name Set")
    DESCRIPTION__FIELD_NAME = WrapperField("DESCRIPTION", FieldType.STRING, display_name="Description")
    ENB_ENTRY_TYPE__FIELD_NAME = WrapperField("ENB_ENTRY_TYPE", FieldType.STRING, display_name="ENB Entry Type")
    EXPERIMENT_ENTRY_NAME_SET__FIELD_NAME = WrapperField("EXPERIMENT_ENTRY_NAME_SET", FieldType.STRING, display_name="Experiment Entry Name Set")
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING, display_name="Guid")
    ICON_COLOR__FIELD_NAME = WrapperField("ICON_COLOR", FieldType.STRING, display_name="Icon Color")
    ICON_GUID__FIELD_NAME = WrapperField("ICON_GUID", FieldType.STRING, display_name="Icon Guid")
    IS_RETRY_ON_FAILURE__FIELD_NAME = WrapperField("IS_RETRY_ON_FAILURE", FieldType.BOOLEAN, display_name="Is Retry On Failure")
    IS_TRANSACTIONAL__FIELD_NAME = WrapperField("IS_TRANSACTIONAL", FieldType.BOOLEAN, display_name="Is Transactional")
    LINE_1_TEXT__FIELD_NAME = WrapperField("LINE_1_TEXT", FieldType.STRING, display_name="Line 1 Text")
    LINE_2_TEXT__FIELD_NAME = WrapperField("LINE_2_TEXT", FieldType.STRING, display_name="Line 2 Text")
    PLUGIN_ORDER__FIELD_NAME = WrapperField("PLUGIN_ORDER", FieldType.INTEGER, display_name="Plugin Order")
    PLUGIN_POINT__FIELD_NAME = WrapperField("PLUGIN_POINT", FieldType.STRING, display_name="Plugin Point")
    SECTION_NAME_PATH__FIELD_NAME = WrapperField("SECTION_NAME_PATH", FieldType.STRING, display_name="Section Name Path")
    TEMPLATE_NAME_SET__FIELD_NAME = WrapperField("TEMPLATE_NAME_SET", FieldType.STRING, display_name="Template Name Set")
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING, display_name="Webhook URL")


class VeloxWebhookExecutionPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION"
    EXECUTION_TIMESTAMP__FIELD_NAME = WrapperField("EXECUTION_TIMESTAMP", FieldType.DATE, display_name="Execution Timestamp")
    EXECUTION_USERNAME__FIELD_NAME = WrapperField("EXECUTION_USERNAME", FieldType.STRING, display_name="Execution Username")
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING, display_name="Guid")
    LAST_ATTEMPT_NUMBER__FIELD_NAME = WrapperField("LAST_ATTEMPT_NUMBER", FieldType.INTEGER, display_name="Last Attempt Number")
    LAST_ATTEMPT_RESULT__FIELD_NAME = WrapperField("LAST_ATTEMPT_RESULT", FieldType.STRING, display_name="Last Attempt Result")
    REQUEST_BODY__FIELD_NAME = WrapperField("REQUEST_BODY", FieldType.STRING, display_name="Request Body")
    WEBHOOK_GUID__FIELD_NAME = WrapperField("WEBHOOK_GUID", FieldType.STRING, display_name="Webhook Guid")
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING, display_name="Webhook Url")


class VeloxWebhookExecutionAttemptPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION_ATTEMPT"
    ATTEMPT_DURATION__FIELD_NAME = WrapperField("ATTEMPT_DURATION", FieldType.INTEGER, display_name="Attempt Duration")
    ATTEMPT_NUMBER__FIELD_NAME = WrapperField("ATTEMPT_NUMBER", FieldType.INTEGER, display_name="Attempt Number")
    ATTEMPT_RESULT__FIELD_NAME = WrapperField("ATTEMPT_RESULT", FieldType.STRING, display_name="Attempt Result")
    ATTEMPT_TIMESTAMP__FIELD_NAME = WrapperField("ATTEMPT_TIMESTAMP", FieldType.DATE, display_name="Attempt Timestamp")
    EXECUTION_GUID__FIELD_NAME = WrapperField("EXECUTION_GUID", FieldType.STRING, display_name="Execution Guid")
    GUID__FIELD_NAME = WrapperField("GUID", FieldType.STRING, display_name="Guid")
    RESPONSE_BODY__FIELD_NAME = WrapperField("RESPONSE_BODY", FieldType.STRING, display_name="Response Body")
    RESPONSE_CODE__FIELD_NAME = WrapperField("RESPONSE_CODE", FieldType.INTEGER, display_name="Response Code")
    WEBHOOK_GUID__FIELD_NAME = WrapperField("WEBHOOK_GUID", FieldType.STRING, display_name="Webhook Guid")
    WEBHOOK_URL__FIELD_NAME = WrapperField("WEBHOOK_URL", FieldType.STRING, display_name="Webhook Url")


class VeloxWebhookExecutionLogPseudoDef:
    DATA_TYPE_NAME: str = "VELOXWEBHOOK_EXECUTION_LOG"
    ATTEMPT_GUID__FIELD_NAME = WrapperField("ATTEMPT_GUID", FieldType.STRING, display_name="Attempt Guid")
    LOG_LEVEL__FIELD_NAME = WrapperField("LOG_LEVEL", FieldType.STRING, display_name="Log Level")
    LOG_LINE_NUM__FIELD_NAME = WrapperField("LOG_LINE_NUM", FieldType.INTEGER, display_name="Log Line Num")
    LOG_MESSAGE__FIELD_NAME = WrapperField("LOG_MESSAGE", FieldType.STRING, display_name="Log Message")
    LOG_TIMESTAMP__FIELD_NAME = WrapperField("LOG_TIMESTAMP", FieldType.DATE, display_name="Log Timestamp")


class VeloxRuleCostPseudoDef:
    DATA_TYPE_NAME: str = "VELOX_RULE_COST"
    ACTION_COST__FIELD_NAME = WrapperField("ACTION_COST", FieldType.LONG, display_name="Action Cost")
    ACTION_COUNT__FIELD_NAME = WrapperField("ACTION_COUNT", FieldType.LONG, display_name="Action Count")
    ANCESTOR_DESCENDANT_COUNT__FIELD_NAME = WrapperField("ANCESTOR_DESCENDANT_COUNT", FieldType.LONG, display_name="Ancestor/ Descendant Count")
    PARENT_CHILD_COUNT__FIELD_NAME = WrapperField("PARENT_CHILD_COUNT", FieldType.LONG, display_name="Parent/ Child Count")
    PROCESSING_TIME__FIELD_NAME = WrapperField("PROCESSING_TIME", FieldType.LONG, display_name="Processing Time (MS)")
    RULE_GUID__FIELD_NAME = WrapperField("RULE_GUID", FieldType.STRING, display_name="Rule GUID")
    SOURCE_RECORD_COUNT__FIELD_NAME = WrapperField("SOURCE_RECORD_COUNT", FieldType.LONG, display_name="Source Record Count")
    TIMESTAMP__FIELD_NAME = WrapperField("TIMESTAMP", FieldType.DATE, display_name="Timestamp")
    TOTAL_COST__FIELD_NAME = WrapperField("TOTAL_COST", FieldType.LONG, display_name="Total Cost")
    TRANSACTION_GUID__FIELD_NAME = WrapperField("TRANSACTION_GUID", FieldType.STRING, display_name="Transaction GUID")
    USERNAME__FIELD_NAME = WrapperField("USERNAME", FieldType.STRING, display_name="Username")


class VeloxConversationPseudoDef:
    DATA_TYPE_NAME: str = "VeloxConversation"
    CONVERSATION_DESCRIPTION__FIELD_NAME = WrapperField("ConversationDescription", FieldType.STRING, display_name="Conversation Description")
    CONVERSATION_GUID__FIELD_NAME = WrapperField("ConversationGuid", FieldType.STRING, display_name="Conversation GUID")
    CONVERSATION_NAME__FIELD_NAME = WrapperField("ConversationName", FieldType.STRING, display_name="Conversation Name")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    SERVER_PLUGIN_PATH__FIELD_NAME = WrapperField("Server_Plugin_Path", FieldType.STRING, display_name="Server Plugin Path")


class VeloxConversationMessagePseudoDef:
    DATA_TYPE_NAME: str = "VeloxConversationMessage"
    CONVERSATION_GUID__FIELD_NAME = WrapperField("ConversationGuid", FieldType.STRING, display_name="Conversation GUID")
    MESSAGE__FIELD_NAME = WrapperField("Message", FieldType.STRING, display_name="Message")
    MESSAGE_GUID__FIELD_NAME = WrapperField("MessageGuid", FieldType.STRING, display_name="Message GUID")
    MESSAGE_SENDER__FIELD_NAME = WrapperField("MessageSender", FieldType.STRING, display_name="Message Sender")
    MESSAGE_TIMESTAMP__FIELD_NAME = WrapperField("MessageTimestamp", FieldType.DATE, display_name="Message Timestamp")


class VeloxScriptPseudoDef:
    DATA_TYPE_NAME: str = "VeloxScript"
    CODE__FIELD_NAME = WrapperField("Code", FieldType.STRING, display_name="Script Code")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.LONG, display_name="Date Created")
    LAST_MODIFIED_BY__FIELD_NAME = WrapperField("LastModifiedBy", FieldType.STRING, display_name="Last Modified By")
    LAST_MODIFIED_DATE__FIELD_NAME = WrapperField("LastModifiedDate", FieldType.LONG, display_name="Last Modified Date")
    PATH__FIELD_NAME = WrapperField("Path", FieldType.STRING, display_name="Script Path")
    PLUGIN_DESCRIPTION__FIELD_NAME = WrapperField("PluginDescription", FieldType.STRING, display_name="Plugin Description")
    PLUGIN_LINE1_TEXT__FIELD_NAME = WrapperField("PluginLine1Text", FieldType.STRING, display_name="Plugin Line 1 Text")
    PLUGIN_LINE2_TEXT__FIELD_NAME = WrapperField("PluginLine2Text", FieldType.STRING, display_name="Plugin Line 2 Text")
    PLUGIN_ORDER__FIELD_NAME = WrapperField("PluginOrder", FieldType.INTEGER, display_name="Plugin Order")
    PLUGIN_POINT__FIELD_NAME = WrapperField("PluginPoint", FieldType.STRING, display_name="Plugin Point")
    PROJECT_GUID__FIELD_NAME = WrapperField("ProjectGuid", FieldType.STRING, display_name="Project GUID")
    SCRIPT_GUID__FIELD_NAME = WrapperField("ScriptGuid", FieldType.STRING, display_name="Script GUID")


class VeloxScriptProjectPseudoDef:
    DATA_TYPE_NAME: str = "VeloxScriptProject"
    CLASS_PATH__FIELD_NAME = WrapperField("ClassPath", FieldType.STRING, display_name="Class Path")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.LONG, display_name="Date Created")
    DEPLOYMENT_OUT_OF_DATE__FIELD_NAME = WrapperField("DeploymentOutOfDate", FieldType.BOOLEAN, display_name="Deployment Out of Date?")
    DESCRIPTION__FIELD_NAME = WrapperField("Description", FieldType.STRING, display_name="Description")
    PROJECT_GUID__FIELD_NAME = WrapperField("ProjectGuid", FieldType.STRING, display_name="Project GUID")
    PROJECT_NAME__FIELD_NAME = WrapperField("ProjectName", FieldType.STRING, display_name="Project Name")
    SCRIPT_LANGUAGE__FIELD_NAME = WrapperField("ScriptLanguage", FieldType.STRING, display_name="Script Language")


class WorkflowPseudoDef:
    DATA_TYPE_NAME: str = "Workflow"
    ALL_ACCESS__FIELD_NAME = WrapperField("AllAccess", FieldType.BOOLEAN, display_name="All Access")
    CATEGORY__FIELD_NAME = WrapperField("Category", FieldType.STRING, display_name="Category")
    CREATED_BY__FIELD_NAME = WrapperField("CreatedBy", FieldType.STRING, display_name="Created By")
    DATE_CREATED__FIELD_NAME = WrapperField("DateCreated", FieldType.DATE, display_name="Date Created")
    DATE_EDITED__FIELD_NAME = WrapperField("DateEdited", FieldType.DATE, display_name="Date Edited")
    DIRECT_LAUNCH__FIELD_NAME = WrapperField("DirectLaunch", FieldType.BOOLEAN, display_name="Direct Launch")
    EDITED_BY__FIELD_NAME = WrapperField("EditedBy", FieldType.STRING, display_name="Edited By")
    IS_TEMPLATE__FIELD_NAME = WrapperField("IsTemplate", FieldType.BOOLEAN, display_name="Is Template")
    LONG_DESC__FIELD_NAME = WrapperField("LongDesc", FieldType.STRING, display_name="Long Description")
    NAME__FIELD_NAME = WrapperField("Name", FieldType.STRING, display_name="Name")
    SHORT_DESC__FIELD_NAME = WrapperField("ShortDesc", FieldType.STRING, display_name="Short Description")
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG, display_name="Workflow ID")
    WORKFLOW_VERSION__FIELD_NAME = WrapperField("WorkflowVersion", FieldType.LONG, display_name="Workflow Version")


class WorkflowOptionPseudoDef:
    DATA_TYPE_NAME: str = "WorkflowOption"
    OPTION_KEY__FIELD_NAME = WrapperField("OptionKey", FieldType.STRING, display_name="Option Key")
    OPTION_VALUE__FIELD_NAME = WrapperField("OptionValue", FieldType.STRING, display_name="Option Value")
    WORKFLOW_ID__FIELD_NAME = WrapperField("WorkflowId", FieldType.LONG, display_name="Workflow ID")
