# Multimodal registration client
from __future__ import annotations

import io
from weakref import WeakValueDictionary

from databind.json import dumps, loads
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord

from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.multimodal.multimodal_data import *


class MultiModalManager:
    _user: SapioUser

    __instances: WeakValueDictionary[SapioUser, MultiModalManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user:SapioUser):
        if self.__initialized:
            return
        self._user = user
        self.__initialized = True

    def load_image_data(self, request: ImageDataRequestPojo) -> list[str]:
        """
        Loading of image data of a compound or a reaction in Sapio's unified drawing format.
        :param request:
        :return:
        """
        payload = dumps(request, ImageDataRequestPojo)
        response = self._user.plugin_post("chemistry/request_image_data",
                                          payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return response.json()

    def load_compounds(self, request: CompoundLoadRequestPojo):
        """
        Load compounds from the provided data here.
        The compounds will not be registered but returned to you "the script".
        To complete registration, you need to call register_compounds method after obtaining result.
        """
        payload = dumps(request, CompoundLoadRequestPojo)
        response = self._user.plugin_post("chemistry/load",
                                          payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, PyMoleculeLoaderResult)

    def register_compounds(self, request: ChemRegisterRequestPojo) -> ChemCompleteImportPojo:
        """
        Register the filled compounds that are previously loaded via load_compounds operation.
        """
        payload = dumps(request, ChemRegisterRequestPojo)
        response = self._user.plugin_post("chemistry/register",
                                          payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, ChemCompleteImportPojo)

    def load_reactions(self, reaction_str: str) -> PyIndigoReactionPojo:
        """
        Load a reaction and return the loaded reaction result.
        :param reaction_str: A reaction string, in format of mrv, rxn, or smiles.
        """
        response = self._user.plugin_post("chemistry/reaction/load",
                                          payload=reaction_str, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, PyIndigoReactionPojo)

    def register_reactions(self, reaction_str: str) -> DataRecord:
        """
        Register a single reaction provided.
        Note: if the rxn has already specified a 2D coordinate, it may not be recomputed when generating record image.
        :param reaction_str: The rxn of a reaction.
        :return: The registered data record. This can be a record that already exists or new.
        """
        response = self._user.plugin_post("chemistry/reaction/register",
                                          payload=reaction_str, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, DataRecord)

    def search_structures(self, request: ChemSearchRequestPojo) -> ChemSearchResponsePojo:
        """
        Perform structure search against the Sapio registries.
        An error can be thrown as exception if search is structurally invalid.
        :param request: The request object containing the detailed context of this search.
        :return: The response object of the result.
        """
        payload = dumps(request, ChemSearchRequestPojo)
        response = self._user.plugin_post("chemistry/search",
                                          payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, ChemSearchResponsePojo)

    def run_multi_sequence_alignment(self, request: MultiSequenceAlignmentRequestPojo) -> list[MultiSequenceAlignmentSeqPojo]:
        """
        Run a multi-sequence alignment using the specified tool and strategy.
        :param request: The request object containing the sequences and alignment parameters. The parameters inside it can be the pojo dict of one of the options.
        :return: The result of the multi-sequence alignment.
        """
        payload = dumps(request, MultiSequenceAlignmentRequestPojo)
        response = self._user.plugin_post("bio/multisequencealignment",
                                          payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, list[MultiSequenceAlignmentSeqPojo])

    def register_bio(self, request: BioFileRegistrationRequest) -> BioFileRegistrationResponse:
        """
        Register to bioregistry of a file.
        """
        payload = dumps(request, BioFileRegistrationRequest)
        response = self._user.plugin_post("bio/register/file", payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        return loads(response.text, BioFileRegistrationResponse)

    def export_to_sdf(self, request: ChemExportSDFRequest) -> str:
        """
        Export the SDF files
        :param request: The request for exporting SDF file.
        :return: the SDF plain text data.
        """
        payload = dumps(request, ChemExportSDFRequest)
        response = self._user.plugin_post("chemistry/export_sdf", payload=payload, is_payload_plain_text=True)
        self._user.raise_for_status(response)
        gzip_base64: str = response.text
        if not gzip_base64:
            raise SapioException("Returning data from server is blank for export SDF.")
        decoded_bytes = base64.b64decode(gzip_base64)
        with io.BytesIO(decoded_bytes) as bytes_io:
            import gzip
            with gzip.GzipFile(fileobj=bytes_io, mode='rb') as f:
                ret: str = f.read().decode()
                return ret
