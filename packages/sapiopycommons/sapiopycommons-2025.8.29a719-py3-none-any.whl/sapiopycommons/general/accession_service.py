from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser

_STR_JAVA_TYPE = "java.lang.String"
_INT_JAVA_TYPE = "java.lang.Integer"
_BOOL_JAVA_TYPE = "java.lang.Boolean"


class AbstractAccessionServiceOperator(ABC):
    """
    Abstract class to define an accession service operator.
    The default one in sapiopycommon only includes the out of box operators.
    More can be added via java plugins for global operators.
    """

    @property
    @abstractmethod
    def op_class_name(self) -> str:
        pass

    @property
    @abstractmethod
    def op_param_value_list(self) -> list[Any] | None:
        pass

    @property
    @abstractmethod
    def op_param_class_name_list(self) -> list[str] | None:
        pass

    @property
    @abstractmethod
    def default_accessor_name(self) -> str:
        pass


class AccessionWithPrefixSuffix(AbstractAccessionServiceOperator):
    """
    Local operator for accessioning prefix and suffix format.
    """
    _prefix: str | None
    _suffix: str | None
    _num_of_digits: int | None
    _start_num: int
    _strict_mode: bool

    @property
    def prefix(self):
        return self._prefix

    @property
    def suffix(self):
        return self._suffix

    @property
    def num_of_digits(self):
        return self._num_of_digits

    @property
    def start_num(self):
        return self._start_num

    @property
    def strict_mode(self):
        return self._strict_mode

    def __init__(self, prefix: str | None, suffix: str | None, num_of_digits: int | None = None,
                 start_num: int = 1, strict_mode: bool = False):
        if prefix is None:
            prefix = ""
        if suffix is None:
            suffix = ""
        self._prefix = prefix
        self._suffix = suffix
        self._num_of_digits = num_of_digits
        self._start_num = start_num
        self._strict_mode = strict_mode

    @property
    def op_param_value_list(self):
        return [self._prefix, self._suffix, self._num_of_digits, self._start_num, self._strict_mode]

    @property
    def op_param_class_name_list(self):
        return [_STR_JAVA_TYPE, _STR_JAVA_TYPE, _INT_JAVA_TYPE, _INT_JAVA_TYPE, _BOOL_JAVA_TYPE]

    @property
    def op_class_name(self):
        return "com.velox.accessionservice.operators.AccessionWithPrefixSuffix"

    @property
    def default_accessor_name(self):
        return "PREFIX_AND_SUFFIX" + "(" + self.prefix + "," + self.suffix + ")"


class AccessionGlobalPrefixSuffix(AbstractAccessionServiceOperator):
    """
    Global operator for accessioning prefix and suffix format.
    """
    _prefix: str | None
    _suffix: str | None
    _num_of_digits: int | None
    _start_num: int
    _strict_mode: bool

    @property
    def prefix(self):
        return self._prefix

    @property
    def suffix(self):
        return self._suffix

    @property
    def num_of_digits(self):
        return self._num_of_digits

    @property
    def start_num(self):
        return self._start_num

    @property
    def strict_mode(self):
        return self._strict_mode

    def __init__(self, prefix: str | None, suffix: str | None, num_of_digits: int | None = None,
                 start_num: int = 1, strict_mode: bool = False):
        if prefix is None:
            prefix = ""
        if suffix is None:
            suffix = ""
        self._prefix = prefix
        self._suffix = suffix
        self._num_of_digits = num_of_digits
        self._start_num = start_num
        self._strict_mode = strict_mode

    @property
    def op_param_value_list(self):
        return [self._prefix, self._suffix, self._num_of_digits, self._start_num, self._strict_mode]

    @property
    def op_param_class_name_list(self):
        return [_STR_JAVA_TYPE, _STR_JAVA_TYPE, _INT_JAVA_TYPE, _INT_JAVA_TYPE, _BOOL_JAVA_TYPE]

    @property
    def op_class_name(self):
        return "com.velox.accessionservice.operators.sapio.AccessionGlobalPrefixSuffix"

    @property
    def default_accessor_name(self):
        return "PREFIX_AND_SUFFIX" + "(" + self._prefix + "," + self._suffix + ")"


class AccessionNextBarcode(AbstractAccessionServiceOperator):
    """
    From Java description:
    This will start accessioning at the getNextBarcode() when there's no system preference to be backward compatible.
    However, once it completes setting the first ID, it will start increment by its own preference and disregards getNextBarcode().

    Recommend using AccessionServiceBasicManager to accession next barcode.
    To avoid ambiguity in preference cache.

    This should not be used unless we are using something legacy such as plate mapping template record creation
    (Note: not 3D plating, I'm talking about the older aliquoter).
    """

    @property
    def op_param_value_list(self):
        return []

    @property
    def op_param_class_name_list(self):
        return []

    @property
    def op_class_name(self):
        return "com.velox.accessionservice.operators.sapio.AccessionNextBarcode"

    @property
    def default_accessor_name(self):
        return "Barcode"


class AccessionRequestId(AbstractAccessionServiceOperator):
    """
    This class implements the accessioning operator for com.velox.sapioutils.shared.managers.DataRecordUtilManager.getNextRequestId()
    and getNextRequestId(int numberOfCharacters).

    Operation: For 4 characters start with A001, increment by 1 until A999. Then We use B001.
    After Z999 we start with AA01 until we get to AA99, etc.

    Exception: Skips I and O to prevent confusions with 1 and 0 when incrementing letters.

    Properties:
        numberOfCharacters: Number of characters maximum in the request ID.
        accessorName: This is a legacy variable from drum.getNextIdListByMapName(), which allows setting different "accessorName" from old system. We need this for compatibility patch for converting these to the new preference format.
    """
    _num_of_characters: int
    _accessor_name: str

    @property
    def num_of_characters(self):
        return self._num_of_characters

    @property
    def accessor_name(self):
        return self._accessor_name

    def __init__(self, num_of_characters: int = 4, accessor_name: str = None):
        self._num_of_characters = num_of_characters
        if not accessor_name:
            accessor_name = self.default_accessor_name
        self._accessor_name = accessor_name

    @property
    def op_class_name(self):
        return "com.velox.accessionservice.operators.sapio.AccessionRequestId"

    @property
    def op_param_value_list(self):
        return [self._num_of_characters, self._accessor_name]

    @property
    def op_param_class_name_list(self):
        return [_INT_JAVA_TYPE, _STR_JAVA_TYPE]

    @property
    def default_accessor_name(self):
        return "SapioNextRequestIdMap"


class AccessionServiceDescriptor:
    """
    Describes a single accession service's accessioning request

    Attributes:
        opClassName: The accession service operator class name as in Java
        opParamValueList: Ordered list of parameter values to construct the accession service operator.
        opParamClassNameList: Ordered list of FQCN of java classes in order of parameter value list.
        dataTypeName: The data type to accession. Should be blank if opClassName resolves to a global operator.
        dataFieldName: The data field to accession. Should be blank if opClassName resolves to a global operator.
        accessorName: The accessor cache name to be used for accessioning.
        numIds: The number of IDs to accession.
    """
    op: AbstractAccessionServiceOperator
    dataTypeName: str | None
    dataFieldName: str | None
    accessorName: str
    numIds: int

    def __init__(self, accessor_name: str, op: AbstractAccessionServiceOperator, num_ids: int,
                 data_type_name: str | None, data_field_name: str | None):
        self.accessorName = accessor_name
        self.op = op
        self.dataTypeName = data_type_name
        self.dataFieldName = data_field_name
        self.numIds = num_ids

    def to_json(self):
        return {
            "opClassName": self.op.op_class_name,
            "opParamValueList": self.op.op_param_value_list,
            "opParamClassNameList": self.op.op_param_class_name_list,
            "accessorName": self.accessorName,
            "numIds": self.numIds,
            "dataTypeName": self.dataTypeName,
            "dataFieldName": self.dataFieldName
        }


class AccessionService:
    """
    Provides Sapio Foundations Accession Service functionalities.
    """
    _user: SapioUser

    __instances: WeakValueDictionary[SapioUser, AccessionService] = WeakValueDictionary()
    __initialized: bool

    @property
    def user(self) -> SapioUser:
        return self._user

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

    def __init__(self, user: SapioUser):
        if self.__initialized:
            return
        self._user = user
        self.__initialized = True

    def accession_with_config(self, data_type_name: str, data_field_name: str, num_ids: int) -> list[str]:
        """
        Accession with Configuration Manager => Accession Service configuration (This is not visible to regular users in SaaS)
        """
        payload = {
            "dataTypeName": data_type_name,
            "dataFieldName": data_field_name,
            "numIds": num_ids
        }
        response = self.user.plugin_post("accessionservice/accession_with_config", payload=payload)
        self.user.raise_for_status(response)
        return list(response.json())

    def accession_in_batch(self, descriptor: AccessionServiceDescriptor) -> list[str]:
        """
        This is the most flexible way to make use of accession service: directly via a descriptor object.
        """
        payload = descriptor.to_json()
        response = self.user.plugin_post("accessionservice/accession", payload=payload)
        self.user.raise_for_status(response)
        return list(response.json())

    def accession_next_request_id_list(self, num_of_characters: int, num_ids: int) -> list[str]:
        """
        Accession Request ID by old LIMS format. This is usually deprecated today.
        :param num_of_characters: Number of characters minimum in request ID.
        :param num_ids: Number of request IDs to accession.
        """
        op = AccessionRequestId(num_of_characters)
        descriptor = AccessionServiceDescriptor(op.default_accessor_name, op, num_ids, None, None)
        return self.accession_in_batch(descriptor)

    def get_affixed_id_in_batch(self, data_type_name: str, data_field_name: str, num_ids: int, prefix: str | None,
                                suffix: str | None, num_digits: int | None, start_num: int = 1) -> list[str]:
        """
        Get the batch affixed IDs that are maximal in cache and contiguous for a particular datatype.datafield under a given format.
        :param data_type_name: The datatype name to look for max ID
        :param data_field_name: The datafield name to look for max ID
        :param num_ids: The number of IDs to accession.
        :param prefix: leave it empty string "" if no prefix. Otherwise, specifies the prefix of ID.
        :param suffix: leave it empty string "" if no suffix. Otherwise, specifies the suffix of ID.
        :param num_digits: None if unlimited with no leading zeros.
        :param start_num The number to begin accessioning if this is the first time.
        :return:
        """
        op = AccessionWithPrefixSuffix(prefix, suffix, num_digits, start_num)
        descriptor = AccessionServiceDescriptor(op.default_accessor_name, op, num_ids, data_type_name, data_field_name)
        return self.accession_in_batch(descriptor)

    def get_global_affixed_id_in_batch(
            self, num_ids: int, prefix: str | None, suffix: str | None, num_digits: int | None, start_num: int = 1) -> list[str]:
        """
        Get the next numOfIds affixed IDs using system preference cache that's maximum across all datatype and datafields and maximal for the format.
        This method allows users to customize a start number instead of always starting at 1.
        :param num_ids: The number of IDs to accession.
        :param prefix: leave it empty string "" if no prefix. Otherwise, specifies the prefix of ID.
        :param suffix: leave it empty string "" if no suffix. Otherwise, specifies the suffix of ID.
        :param num_digits: None if unlimited with no leading zeros.
        :param start_num The number to begin accessioning if this is the first time.
        """
        op: AbstractAccessionServiceOperator
        if not prefix and not suffix:
            op = AccessionNextBarcode()
        else:
            op = AccessionGlobalPrefixSuffix(prefix, suffix, num_digits, start_num)
        descriptor = AccessionServiceDescriptor(op.default_accessor_name, op, num_ids, None, None)
        return self.accession_in_batch(descriptor)
