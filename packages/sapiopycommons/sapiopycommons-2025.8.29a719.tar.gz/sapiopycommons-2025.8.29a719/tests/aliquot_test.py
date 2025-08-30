import unittest

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.properties import Children

from sapiopycommons.samples.aliquot import create_aliquot_for_samples
from sapiopycommons.general.accession_service import AccessionService
from data_type_models import *

# FR-47421 Added module

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="66c2bea5-7cb2-4bfc-a413-304a3f4c3f33",
                 username="yqiao_api", password="Password1!")
data_record_manager: DataRecordManager = DataMgmtServer.get_data_record_manager(user)
rec_man: RecordModelManager = RecordModelManager(user)
inst_man: RecordModelInstanceManager = rec_man.instance_manager
relationship_man: RecordModelRelationshipManager = rec_man.relationship_manager
accession_service = AccessionService(user)

class AliquotTest(unittest.TestCase):
    def test_aliquot_samples(self):
        parent_sample_1 = inst_man.add_new_record_of_type(SampleModel)
        parent_sample_2 = inst_man.add_new_record_of_type(SampleModel)
        id_list = accession_service.accession_with_config(SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name, 2)
        parent_sample_1.set_SampleId_field(id_list[0])
        parent_sample_2.set_SampleId_field(id_list[1])
        aliquot_request = {parent_sample_1: 2, parent_sample_2: 3}
        rec_man.store_and_commit()
        aliquot_map = create_aliquot_for_samples(aliquot_request, user)
        self.assertTrue(len(aliquot_map) == 2)
        self.assertTrue(parent_sample_1 in aliquot_map and parent_sample_2 in aliquot_map)
        self.assertTrue(len(aliquot_map.get(parent_sample_1)) == 2)
        self.assertTrue(len(aliquot_map.get(parent_sample_2)) == 3)

        relationship_man.load_children_of_type([parent_sample_1, parent_sample_2], SampleModel)
        child_id_list_sample_1 = [child.get_SampleId_field() for child in parent_sample_1.get(Children.of_type(SampleModel))]
        child_id_list_sample_2 = [child.get_SampleId_field() for child in parent_sample_2.get(Children.of_type(SampleModel))]
        # Check the format of all ids of parent sample id "_" number is in the child list.
        for i in range(2):
            self.assertTrue(f"{parent_sample_1.get_SampleId_field()}_{i+1}" in child_id_list_sample_1)
        for i in range(3):
            self.assertTrue(f"{parent_sample_2.get_SampleId_field()}_{i+1}" in child_id_list_sample_2)