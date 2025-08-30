import unittest

from sapiopylib.rest.User import SapioUser

from sapiopycommons.general.accession_service import AccessionService
from data_type_models import SampleModel

user = SapioUser(url="https://linux-vm:8443/webservice/api", verify_ssl_cert=False,
                 guid="3c232543-f407-4828-aae5-b33d4cd31fa7",
                 username="yqiao_api", password="Password1!")

accession_service = AccessionService(user)

# This test needs to be run together with accessioning happening separately inside Sapio for creating samples/plates in 3D plater.
# Set plate to auto accession mode and ensure plate ID is non-unique to trigger global accessioning logic.
class AccessionServiceTest(unittest.TestCase):

    def test_sample_accession_with_config(self):
        """
        This is how platform accessions new samples that isn't an aliquot or pool.
        """
        id_list = accession_service.accession_with_config(SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name, 5)
        print("New Sample IDs: " + str(id_list) +
              ". Accession some more samples in ELN grabber and run this again and check continuity.")
        self.assertEqual(len(id_list), 5)

    def test_plate_id_nonunique_accession(self):
        """
        This will test the platform accessioning plate IDs.
        """
        # This is from MultiLayerPlatingConfigManager
        id_list = accession_service.get_global_affixed_id_in_batch(5, "", "", 4, 1000)
        print("New Plate IDs: " + str(id_list) + ". Check continuty in ELN using 3d plating auto accession plate ID, then make sure the plate ID is non-unique.")
        self.assertEqual(len(id_list), 5)

    def test_accession_pool_ids(self):
        # This is from CreateBoolBase, and MultiLayerPlatingRecordManager
        id_list = accession_service.get_affixed_id_in_batch(SampleModel.DATA_TYPE_NAME, SampleModel.SAMPLEID__FIELD_NAME.field_name,
                                                            10, "Pool-", "", None, 1000)
        print("New Pool IDs: " + str(id_list))
        self.assertEqual(len(id_list), 10)