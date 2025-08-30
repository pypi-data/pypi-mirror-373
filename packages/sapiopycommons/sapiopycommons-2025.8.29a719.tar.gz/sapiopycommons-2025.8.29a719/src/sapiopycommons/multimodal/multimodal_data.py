# Includes general Multimodal registration data structures for specific endpoints.
# Author: yqiao
import base64
from enum import Enum
from typing import Any

from databind.core import ExtraKeys
from databind.core.dataclasses import dataclass


@dataclass
class PySimpleMoleculePojo:
    imageSVG: str | None
    smiles: str
    molBlock: str


@dataclass
@ExtraKeys()
class PyMolecule:
    """
    Describes a deserialized molecule for Java.
    """
    imageSVG: str | None
    smiles: str
    clogP: float
    tpsa: float
    amw: float
    exactMass: float
    numHBondDonors: int
    numHBondAcceptors: int
    molFormula: str
    charge: int
    molBlock: str
    inchi: str
    inchiKey: str
    stereoisomers: list[PySimpleMoleculePojo] | None
    normError: str | None
    desaltError: str | None
    desaltedList: list[str] | None
    registrationHash: str | None
    hasOrGroup: bool
    CXSMILESHash: str | None


@dataclass
class PyCompound:
    """
    class PyCompound
    """

    # The original substance data.
    originalMol: PyMolecule  # since May 24, 2023

    # The normalized, desalted abstract compound data.
    canonicalMol: PyMolecule | None  # since May 24, 2023

    props: dict[str, object] | None


class ChemFileType(Enum):
    CSV = 0
    SDF = 1


class ChemLoadType(Enum):
    SMILES_LIST = 0
    INCHI_LIST = 1
    MOL_BLOCK_LIST = 2
    SDF_FILE = 3


class ChemSearchType(Enum):
    """
    All possible chemistry quicksearch types.
    """
    COMPOUND_SUBSTRUCTURE = 0
    COMPOUND_SIMILARITY = 1
    REACTION_SUBSTRUCTURE = 2


@dataclass
class ChemLoadingError:
    """
    Describes a single record of compound loading error, this will be produced by interactive loader of compounds.
    Attributes:
        original: The original data that makes up the molecule so user can find it in the file.
        errorMsg: Why the import has failed. (normalization/desalting/sanitization/kekulize)
        properties: The additional attributes in the import. (for mols in SDF)
    """
    original: str
    errorMsg: str
    properties: dict


@dataclass
class PyMoleculeLoaderResult:
    """
    The results of a loading operation.

    Attributes:
        compoundByStr: may be blank if irrelevant. The map of source data string to the compound loaded.
        compoundList: the compounds successfully loaded.
        errorList: an error record is added here for each one we failed to load in Sapio.
    """
    compoundByStr: dict[str, PyCompound] | None
    compoundList: list[PyCompound] | None
    errorList: list[ChemLoadingError] | None


@dataclass
class ChemCompleteImportPojo:
    # Variables declaration with type hints
    dataTypeName: str
    successPartRecordIdList: list[int] | None
    successSampleRecordIdList: list[int] | None
    errors: list[ChemLoadingError] | None
    registeredOriginalParts: list[int]
    allRegisteredPartsNoDuplicates: list[int]
    newPartList: list[int]
    numOldParts: int


@dataclass
class ChemInteractiveRegisterRequestPojo:
    dataType: str
    fileType: ChemFileType
    fileDataEncodedBase64: str | None
    addingItems: bool

    def __init__(self, data_type: str, file_type: ChemFileType, is_adding_items: bool, file_data: bytes):
        self.dataType = data_type
        self.fileType = file_type
        self.addingItems = is_adding_items
        self.fileDataEncodedBase64 = base64.b64encode(file_data).decode()


@dataclass
class CompoundLoadRequestPojo:
    """
    Describes a load request for the Load Compound Endpoint.

    Attributes:
        dataType: The data type of records to be registered in Sapio.
        loadType: The source data's type you are loading.
        dataList: If the source data is not a file, here you specify a list of string describing molecule for that src.
        fileDataBase64: If the source data is a file, the file's base64 data content.
    """
    dataType: str
    loadType: ChemLoadType
    dataList: list[str] | None
    fileDataBase64: str | None

    def __init__(self, data_type: str, load_type: ChemLoadType, data_list: list[str] | None = None,
                 file_data: bytes | None = None):
        self.dataType = data_type
        self.loadType = load_type
        if load_type is ChemLoadType.SDF_FILE:
            self.dataList = None
            if file_data is None:
                raise ValueError("The file data must be specify the the load type is of a file type.")
            self.fileDataBase64 = base64.b64encode(file_data).decode()
        else:
            self.dataList = data_list
            self.fileDataBase64 = None


@dataclass
class ChemRegisterRequestPojo:
    """
    Data payload to send to webservice to request registration in RegisterCompoundEndpoint

    Attributes:
        dataType: The data type of records to be registered in Sapio.
        registrationList: This list must be of correct data structure suitable for the type. For example, for CompoundPart data type the canonical form must be resolved by earlier call.
    """
    dataType: str
    registrationList: list[PyCompound]

    def __init__(self, data_type: str, registration_list: list[PyCompound]):
        self.dataType = data_type
        self.registrationList = registration_list


@dataclass
class ImageDataRequestPojo:
    """
    Payload to request in endpoint loading of image data of a compound or a reaction in Sapio's unified drawing format.

    Attributes:
        dataList: The list of data about the images of the molecules or reactions. This can be SMILES, MOL, or INCHI. SMILES is expected. INCHI can be ambiguous to chrality as well as tautomers.
        isReaction: true if the underlying data is of RxN format of reaction.
    """
    dataList: list[str]
    reaction: bool

    def __init__(self, data_list: list[str], is_reaction: bool):
        self.dataList = data_list
        self.reaction = is_reaction


@dataclass
class PyIndigoReactionPojo:
    """
    The result of loading a reaction.

    Attributes:
        products: products of the reaction.
        reactants: reactants of the reaction.
        reactionSmiles: the SMILES representation of this reaction.
        reactionRxn: the RxN of an arotmized reaction
        reactionRenderRxn: the RxN of no-automapping, DE-aromotized reaction, with 2D coordinates of atoms computed.
    """
    products: list[PyCompound]
    reactants: list[PyCompound]
    reactionSmiles: str
    reactionRxn: str
    reactionRenderRxn: str


@dataclass
class ChemQuickSearchContextData:
    """
    Do not directly make use of this class. The only use for this class is to pass in the "next page"
    produced by the endpoint.

    When obtaining the first page, this parameter argument should not be passed at all (not created with default values).
    """
    previousPageSearchAfterJsonStack: list[str] | None
    nextPageSearchAfter: str | None
    pitId: str | None
    query: str | None
    joinSapioPartType: str | None
    simUpperLimit: float | None


@dataclass
class ChemSearchRequestPojo:
    """
    Payload to send to endpoint to request a chemical search in Sapio.
    This can be a substructure search or similarity search.

    Attributes:
        searchStr: The search string of SMILES or SMARTS you are searching
        searchType: The type of search you are doing.
        joinMethod: The registry you are using to join with Sapio record. This is not relevant for reactions.
        contextData: The context data of the current page passed to you by result of previous page. If this is the first page you are querying, leave this as None.
        simSearchUpperLimit: similarity search upper limit, between 0.0 to 1.0, valid only to similarity searches.
    """
    searchStr: str
    searchType: ChemSearchType
    joinSapioType: str | None
    contextData: ChemQuickSearchContextData | None
    simSearchUpperLimit: float | None

    def __init__(self, search_str: str, search_type: ChemSearchType, join_sapio_type: str | None = None,
                 context_data: ChemQuickSearchContextData | None = None, sim_search_upper: float | None = None):
        self.searchStr = search_str
        self.searchType = search_type
        self.joinSapioType = join_sapio_type
        self.contextData = context_data
        self.simSearchUpperLimit = sim_search_upper


@dataclass
class ChemSearchResponsePojo:
    """
    A response object of a chemistry quick search.
    NOTE: It's possible to have next page while the current records list is blank (although without additional query conditions, this should be rare).

    Attributes:
         recordsOfPage: The records returned in this page.
         nextPageAvailable: Whether there is still a next page to query. If this is filled, then the context to query next page is on nextPageContext.

    """
    recordIdListOfPage: list[int]
    nextPageAvailable: bool
    nextPageContext: ChemQuickSearchContextData


class MAFFTStrategy(Enum):
    """
    Select one of the strategies for MAFFT multi sequence alignment.
    """
    # Accuracy-Orientated options
    L_INS_i = 0
    G_INS_i = 1
    E_INS_i = 2
    # Speed-Orientated options
    AUTO = 3
    FFT_NS_i = 4
    FFT_NS_2 = 5
    FFT_NS_1 = 6
    NW_NS_i = 7
    NW_NS_2 = 8
    NW_NS_PartTree_1 = 9


class MultiSequenceAlignmentTool(Enum):
    MAFFT = 0


class MultiSeqAlignemntSeqType(Enum):
    nucleic = 0
    amino = 1


@dataclass
class MultiSequenceAlignmentSeqPojo:
    seqId: str
    seqString: str | None
    hyphSeqString: str | None

    @staticmethod
    def create(id: str, seq: str):
        ret = MultiSequenceAlignmentSeqPojo(seqId=id, seqString=seq, hyphSeqString=None)
        return ret


class MAFFTRunOptions:
    strategy: MAFFTStrategy
    noScore: bool
    op: float
    lop: float
    lep: float
    lexp: float
    LOP: float
    LEXP: float
    fmodel: bool

    def __init__(self, strategy: MAFFTStrategy = MAFFTStrategy.AUTO, noScore: bool = True,
                 op: float = 1.53, lop: float = -2.0, lep: float = 0.1, lexp: float = -0.1,
                 LOP: float = -6.0, LEXP: float = 0.00, fmodel: bool = False):
        self.strategy = strategy
        self.noScore = noScore
        self.op = op
        self.lop = lop
        self.lep = lep
        self.lexp = lexp
        self.LOP = LOP
        self.LEXP = LEXP
        self.fmodel = fmodel

    def to_json(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy.name,
            "noScore": self.noScore,
            "op": self.op,
            "lop": self.lop,
            "lep": self.lep,
            "lexp": self.lexp,
            "LOP": self.LOP,
            "LEXP": self.LEXP,
            "fmodel": self.fmodel
        }


class ClustalOOptions:
    dealign: bool
    numCombinedIterations: int | None
    numGuideTreeIterations: int | None
    numHMMIterations: int | None

    def __init__(self, dealign: bool = False, numCombinedIterations: int | None = None,
                 numGuideTreeIterations: int | None = None, numHMMIterations: int | None = None):
        self.dealign = dealign
        self.numCombinedIterations = numCombinedIterations
        self.numGuideTreeIterations = numGuideTreeIterations
        self.numHMMIterations = numHMMIterations

    def to_json(self) -> dict[str, Any]:
        return {
            "dealign": self.dealign,
            "numCombinedIterations": self.numCombinedIterations,
            "numGuideTreeIterations": self.numGuideTreeIterations,
            "numHMMIterations": self.numHMMIterations
        }


class KAlignOptions:
    gapOpenPenalty: float | None
    gapExtensionPenalty: float | None
    terminalGapPenalty: float | None

    def __init__(self, gapOpenPenalty: float | None = None, gapExtensionPenalty: float | None = None,
                 terminalGapPenalty: float | None = None):
        self.gapOpenPenalty = gapOpenPenalty
        self.gapExtensionPenalty = gapExtensionPenalty
        self.terminalGapPenalty = terminalGapPenalty

    def to_json(self) -> dict[str, Any]:
        return {
            "gapOpenPenalty": self.gapOpenPenalty,
            "gapExtensionPenalty": self.gapExtensionPenalty,
            "terminalGapPenalty": self.terminalGapPenalty
        }


class MuscleOptions:
    consiters: int
    refineiters: int

    def __init__(self, consiters: int = 2, refineiters: int = 100):
        self.consiters = consiters
        self.refineiters = refineiters

    def to_json(self) -> dict[str, Any]:
        return {
            "consiters": self.consiters,
            "refineiters": self.refineiters
        }


@dataclass
class MultiSequenceAlignmentRequestPojo:
    tool: MultiSequenceAlignmentTool
    seqType: MultiSeqAlignemntSeqType
    inputSeqs: list[MultiSequenceAlignmentSeqPojo]
    parameters: dict[str, Any] | None

    def __init__(self, tool: MultiSequenceAlignmentTool, seq_type: MultiSeqAlignemntSeqType,
                 input_sequences: list[MultiSequenceAlignmentSeqPojo],
                 parameters: dict[str, Any]):
        self.tool = tool
        self.seqType = seq_type
        self.inputSeqs = input_sequences
        self.parameters = parameters


class BioFileType(Enum):
    """
    Different bio registry supported file types.
    """
    FASTA = 0
    GENBANK = 1
    PDB = 2
    CIF = 3


@dataclass
class BioFileRegistrationRequest:
    """
    A request object for a single bio-registration request on parts.
    """
    dataTypeName: str
    fileType: BioFileType
    prefilledFieldMapList: list[dict[str, Any]] | None
    overwriteExisting: bool
    fileContent: str

    def __init__(self, data_type_name: str, file_type: BioFileType, file_content: str,
                 prefilled_field_map_list: list[dict[str, Any]] | None = None, overwrite: bool = False):
        self.dataTypeName = data_type_name
        self.fileType = file_type
        self.fileContent = file_content
        self.prefilledFieldMapList = prefilled_field_map_list
        self.overwriteExisting = overwrite


@dataclass
class BioFileRegistrationResponse:
    """
    A response object for a single bio-registration request on parts.
    """
    newRecordIdList: list[int]
    oldRecordIdList: list[int]


@dataclass
class ChemExportSDFRequest:
    """
    A request to export SDF data from Sapio to Python REST client.
    """
    partDataTypeName: str
    partRecordIdList: list[int]

    forceV3000: bool
    fieldNameList: list[str] | None
    assayNameList: list[str] | None
    additionalPropertiesByRecordId: dict[int, dict[str, Any]] | None

    def __init__(self, partDataTypeName: str, partRecordIdList: list[int], forceV3000: bool = True,
                 fieldNameList: list[str] | None = None, assayNameList: list[str] | None = None,
                 additionalPropertiesByRecordId: dict[int, dict[str, Any]] | None = None):
        self.partDataTypeName = partDataTypeName
        self.partRecordIdList = partRecordIdList
        self.forceV3000 = forceV3000
        self.fieldNameList = fieldNameList
        self.assayNameList = assayNameList
        self.additionalPropertiesByRecordId = additionalPropertiesByRecordId
