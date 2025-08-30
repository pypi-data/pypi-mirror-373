import base64
from enum import Enum

from databind.core.dataclasses import dataclass


class ChannelStatisticType(Enum):
    """
    All supported channel statistics type.
    """
    MEAN = "(Mean) MFI"
    MEDIAN = "(Median) MFI"
    STD_EV = "Std. Dev."
    COEFFICIENT_OF_VARIATION = "CV"

    display_name: str

    def __init__(self, display_name: str):
        self.display_name = display_name


@dataclass
class ChannelStatisticsParameterJSON:
    channelNameList: list[str]
    statisticsType: ChannelStatisticType

    def __init__(self, channel_name_list: list[str], stat_type: ChannelStatisticType):
        self.channelNameList = channel_name_list
        self.statisticsType = stat_type


@dataclass
class ComputeFlowStatisticsInputJson:
    fcsFileRecordIdList: list[int]
    statisticsParameterList: list[ChannelStatisticsParameterJSON]

    def __init__(self, fcs_file_record_id_list: list[int], statistics_parameter_list: list[ChannelStatisticsParameterJSON]):
        self.fcsFileRecordIdList = fcs_file_record_id_list
        self.statisticsParameterList = statistics_parameter_list


@dataclass
class FlowJoWorkspaceInputJson:
    filePath: str
    base64Data: str

    def __init__(self, filePath: str, file_data: bytes):
        self.filePath = filePath
        self.base64Data = base64.b64encode(file_data).decode('utf-8')


@dataclass
class UploadFCSInputJson:
    """
    Request to upload new FCS file
    Attributes:
        filePath: The file name of the FCS file to be uploaded. For FlowJo workspace, this is important to match the file in group (via file names).
        attachmentDataType: the attachment data type that contains already-uploaded FCS data.
        attachmentRecordId: the attachment record ID that contains already-uploaded FCS data.
        associatedRecordDataType: the "parent" association for the FCS. Can either be a workspace or a sample record.
        associatedRecordId: the "parent" association for the FCS. Can either be a workspace or a sample record.
    """
    filePath: str
    attachmentDataType: str
    attachmentRecordId: int
    associatedRecordDataType: str
    associatedRecordId: int

    def __init__(self, associated_record_data_type: str, associated_record_id: int,
                 file_path: str, attachment_data_type: str, attachment_record_id: int):
        self.filePath = file_path
        self.attachmentDataType = attachment_data_type
        self.attachmentRecordId = attachment_record_id
        self.associatedRecordDataType = associated_record_data_type
        self.associatedRecordId = associated_record_id
