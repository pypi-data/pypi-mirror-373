import os
import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager

from sapiopycommons.flowcyto.flow_cyto import FlowCytoManager
from data_type_models import *

from sapiopycommons.flowcyto.flowcyto_data import UploadFCSInputJson, FlowJoWorkspaceInputJson, \
    ComputeFlowStatisticsInputJson, ChannelStatisticsParameterJSON, ChannelStatisticType

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
flow_man = FlowCytoManager(user)
data_record_manager = DataMgmtServer.get_data_record_manager(user)
rec_man = RecordModelManager(user)
inst_man = rec_man.instance_manager
data_dir = "flowcyto"

def _create_attachment_record_of_content(file_path: str) -> DataRecord:
    record = data_record_manager.add_data_record(AttachmentModel.DATA_TYPE_NAME)
    file_name: str = os.path.basename(file_path)
    with open(file_path, "rb") as file_content:
        data_record_manager.set_attachment_data(record, file_name, file_content)
    return record

# NOTE: This unit test will run for a few minutes...

class FlowCytoTest(unittest.TestCase):

    def test_sample_import_and_stats(self):
        file_name = "COVID19_W_001_O.fcs"
        file_path = data_dir + "/" + file_name
        sample_rec: DataRecord = data_record_manager.add_data_record(SampleModel.DATA_TYPE_NAME)
        fcs_attachment_rec = _create_attachment_record_of_content(file_path)
        response_record_id = flow_man.upload_fcs_for_sample(
            UploadFCSInputJson(sample_rec.data_type_name, sample_rec.record_id, file_name,
                               fcs_attachment_rec.data_type_name, fcs_attachment_rec.record_id))
        self.assertTrue(response_record_id == sample_rec.record_id)
        children_fcs_recs = data_record_manager.get_children(sample_rec.record_id, FCSFileModel.DATA_TYPE_NAME)
        input_json = ComputeFlowStatisticsInputJson([x.record_id for x in children_fcs_recs], [
            ChannelStatisticsParameterJSON(['FSC-H', 'FSC-W'], ChannelStatisticType.MEDIAN)])
        stat_rec_id_list = flow_man.compute_statistics(input_json)
        self.assertIsNotNone(stat_rec_id_list)
        self.assertTrue(2 == len(stat_rec_id_list))

    def test_flowjo_workspace(self):
        workspace_file_name = "8_color_ICS.wsp"
        sample_file_name_list = ["101_DEN084Y5_15_E01_008_clean.fcs", "101_DEN084Y5_15_E03_009_clean.fcs",
                                 "101_DEN084Y5_15_E05_010_clean.fcs"]
        file_path = data_dir + "/" + workspace_file_name
        workspace_record_id: int
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            workspace_record_id = flow_man.create_flowjo_workspace(
                FlowJoWorkspaceInputJson(workspace_file_name, file_bytes))
        workspace_record: DataRecord = data_record_manager.query_system_for_record(FlowJoWorkspaceRootModel.DATA_TYPE_NAME,
                                                                                   workspace_record_id)
        self.assertIsNotNone(workspace_record)
        for sample_file_name in sample_file_name_list:
            response_record_id: int
            file_path = data_dir + "/" + sample_file_name
            fcs_attachment_rec = _create_attachment_record_of_content(file_path)
            response_record_id = flow_man.upload_fcs_for_sample(UploadFCSInputJson(
                workspace_record.data_type_name, workspace_record.record_id, sample_file_name,
                fcs_attachment_rec.data_type_name, fcs_attachment_rec.record_id))
            self.assertTrue(response_record_id == workspace_record_id)
