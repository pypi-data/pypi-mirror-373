import unittest

from sapiopycommons.multimodal.multimodal import MultiModalManager
from sapiopycommons.multimodal.multimodal_data import *
from data_type_models import *

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="ae4e92e1-34c6-4336-8d80-7f6804d3e51c",
                 username="yqiao_api", password="Password1!")

multi_modal_manager = MultiModalManager(user)


class ChemCurationTest(unittest.TestCase):
    def test_curation_reg(self):
        with open("curation_queue_test.sdf", "rb") as f:
            file_data: bytes = f.read()
            loader_result = multi_modal_manager.load_compounds(
                CompoundLoadRequestPojo(ChemicalReagentPartModel.DATA_TYPE_NAME, ChemLoadType.SDF_FILE,
                                        file_data=file_data))
            compound_list = loader_result.compoundList
            for compound in compound_list:
                self.assertTrue(compound.originalMol.CXSMILESHash)
                self.assertTrue(compound.originalMol.registrationHash)
            multi_modal_manager.register_compounds(ChemRegisterRequestPojo(
                ChemicalReagentPartModel.DATA_TYPE_NAME, compound_list))
            # User manually log in and resolve the curation queue.
            print("Loaded! Now play with curation queue inside Sapio!")
