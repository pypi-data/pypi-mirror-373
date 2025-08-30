from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrapperField


class SystemFields:
    RECORD_ID__FIELD = WrapperField("RecordId", FieldType.LONG)
    DATA_RECORD_NAME__FIELD = WrapperField("DataRecordName", FieldType.IDENTIFIER)
    CREATED_BY__FIELD = WrapperField("CreatedBy", FieldType.STRING)
    DATE_CREATED__FIELD = WrapperField("DateCreated", FieldType.DATE)
    LAST_MODIFIED_BY__FIELD = WrapperField("VeloxLastModifiedBy", FieldType.STRING)
    LAST_MODIFIED_DATE__FIELD = WrapperField("VeloxLastModifiedDate", FieldType.DATE)


class ProcessQueueItemFields:
    DATA_TYPE_NAME: str = 'ProcessQueueItem'
    ASSIGNED_TO__FIELD = WrapperField('AssignedTo', FieldType.SELECTION)
    DATA_RECORD_ID__FIELD = WrapperField('DataRecordId', FieldType.LONG)
    DATA_TYPE_NAME__FIELD = WrapperField('DataTypeName', FieldType.STRING)
    DURATION_IN_QUEUE__FIELD = WrapperField('DurationInQueue', FieldType.LONG)
    EXPERIMENT__FIELD = WrapperField('Experiment', FieldType.SIDE_LINK)
    LAUNCHED_DATE__FIELD = WrapperField('LaunchedDate', FieldType.DATE)
    PROCESS_HEADER_NAME__FIELD = WrapperField('ProcessHeaderName', FieldType.STRING)
    SCHEDULED_DATE__FIELD = WrapperField('ScheduledDate', FieldType.DATE)
    SHOW_IN_QUEUE__FIELD = WrapperField('ShowInQueue', FieldType.BOOLEAN)
    WORKFLOW_HEADER_NAME__FIELD = WrapperField('WorkflowHeaderName', FieldType.STRING)


class ProcessWorkflowTrackingFields:
    DATA_TYPE_NAME: str = 'ProcessWorkflowTracking'
    ACTIVE_WORKFLOW_ID__FIELD = WrapperField("ActiveWorkflowId", FieldType.LONG)
    BRANCH_LONG_ID__FIELD = WrapperField("BranchLongId", FieldType.LONG)
    END_DATE__FIELD = WrapperField("EndDate", FieldType.DATE)
    END_HOUR__FIELD = WrapperField("EndHour", FieldType.LONG)
    END_MINUTE_TIME__FIELD = WrapperField("EndMinuteTime", FieldType.LONG)
    EXPECTED_QUEUE_TIME__FIELD = WrapperField("ExpectedQueueTime", FieldType.DOUBLE)
    EXPECTED_TAT__FIELD = WrapperField("ExpectedTAT", FieldType.DOUBLE)
    PROCESS_QUEUE_ITEM__FIELD = WrapperField("ProcessQueueItem", FieldType.SIDE_LINK)
    PROCESS_STEP_NUMBER__FIELD = WrapperField("ProcessStepNumber", FieldType.LONG)
    QUEUED_HOURS__FIELD = WrapperField("QueuedHours", FieldType.LONG)
    QUEUED_MINUTES__FIELD = WrapperField("QueuedMinutes", FieldType.LONG)
    QUEUED_TIME__FIELD = WrapperField("QueuedTime", FieldType.DOUBLE)
    QUEUE_START_DATE__FIELD = WrapperField("QueueStartDate", FieldType.DATE)
    QUEUE_START_HOUR__FIELD = WrapperField("QueueStartHour", FieldType.LONG)
    QUEUE_START_MINUTE_TIME__FIELD = WrapperField("QueueStartMinuteTime", FieldType.LONG)
    SAMPLE_RECORD_ID__FIELD = WrapperField("SampleRecordId", FieldType.LONG)
    START_DATE__FIELD = WrapperField("StartDate", FieldType.DATE)
    START_HOUR__FIELD = WrapperField("StartHour", FieldType.LONG)
    START_MINUTE_TIME__FIELD = WrapperField("StartMinuteTime", FieldType.LONG)
    STATUS__FIELD = WrapperField("Status", FieldType.PICKLIST)
    TURN_AROUND_HOURS__FIELD = WrapperField("TurnAroundHours", FieldType.LONG)
    TURN_AROUND_MINUTES__FIELD = WrapperField("TurnAroundMinutes", FieldType.LONG)
    WORKFLOW_END_USER_ID__FIELD = WrapperField("WorkflowEndUserId", FieldType.STRING)
    WORKFLOW_EXPECTED_QUEUE_TIME__FIELD = WrapperField("WorkflowExpectedQueueTime", FieldType.STRING)
    WORKFLOW_EXPECTED_TAT__FIELD = WrapperField("WorkflowExpectedTAT", FieldType.STRING)
    WORKFLOW_EXPECTED_TOTAL_TAT__FIELD = WrapperField("WorkflowExpectedTotalTAT", FieldType.DOUBLE)
    WORKFLOW_ID_NUMBER__FIELD = WrapperField("WorkflowIdNumber", FieldType.LONG)
    WORKFLOW_NAME__FIELD = WrapperField("WorkflowName", FieldType.STRING)
    WORKFLOW_PROCESS_TAT__FIELD = WrapperField("WorkflowProcessTAT", FieldType.DOUBLE)
    WORKFLOW_START_USER_ID__FIELD = WrapperField("WorkflowStartUserId", FieldType.STRING)
    WORKFLOW_TAT__FIELD = WrapperField("WorkflowTAT", FieldType.DOUBLE)
    WORKFLOW_VERSION__FIELD = WrapperField("WorkflowVersion", FieldType.LONG)

class PlateDesignerWellElementFields:
    DATA_TYPE_NAME = 'PlateDesignerWellElement'
    ACTUAL_VOLUME_REMOVED__FIELD = WrapperField("ActualVolumeRemoved", FieldType.DOUBLE)
    ALIQUOT_SAMPLE_RECORD_ID__FIELD = WrapperField("AliquotSampleRecordId", FieldType.LONG)
    COL_POSITION__FIELD = WrapperField("ColPosition", FieldType.SELECTION)
    CONCENTRATION__FIELD = WrapperField("Concentration", FieldType.DOUBLE)
    CONCENTRATION_UNITS__FIELD = WrapperField("ConcentrationUnits", FieldType.STRING)
    CONTROL_TYPE__FIELD = WrapperField("ControlType", FieldType.STRING)
    DILUTION_SCHEME__FIELD = WrapperField("DilutionScheme", FieldType.DOUBLE)
    IS_CONTROL__FIELD = WrapperField("IsControl", FieldType.BOOLEAN)
    LAYER__FIELD = WrapperField("Layer", FieldType.INTEGER)
    PLATE_RECORD_ID__FIELD = WrapperField("PlateRecordId", FieldType.LONG)
    ROW_POSITION__FIELD = WrapperField("RowPosition", FieldType.SELECTION)
    SOURCE_DATA_TYPE_NAME__FIELD = WrapperField("SourceDataTypeName", FieldType.STRING)
    SOURCE_RECORD_ID__FIELD = WrapperField("SourceRecordId", FieldType.LONG)
    SOURCE_SAMPLE_CONCENTRATION__FIELD = WrapperField("SourceSampleConcentration", FieldType.DOUBLE)
    SOURCE_SAMPLE_MASS__FIELD = WrapperField("SourceSampleMass", FieldType.DOUBLE)
    SOURCE_SAMPLE_VOLUME__FIELD = WrapperField("SourceSampleVolume", FieldType.DOUBLE)
    SOURCE_VOLUME_TO_REMOVE__FIELD = WrapperField("SourceVolumeToRemove", FieldType.DOUBLE)
    TARGET_MASS__FIELD = WrapperField("TargetMass", FieldType.DOUBLE)
    VOLUME__FIELD = WrapperField("Volume", FieldType.DOUBLE)
