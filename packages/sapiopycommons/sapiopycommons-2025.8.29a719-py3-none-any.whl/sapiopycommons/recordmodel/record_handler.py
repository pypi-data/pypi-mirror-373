from __future__ import annotations

import io
import warnings
from collections.abc import Iterable
from typing import Collection, TypeVar, TypeAlias
from weakref import WeakValueDictionary

from sapiopycommons.general.aliases import RecordModel, SapioRecord, FieldMap, FieldIdentifier, AliasUtil, \
    FieldIdentifierMap, FieldValue, UserIdentifier, FieldIdentifierKey, DataTypeIdentifier
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.general.exceptions import SapioException
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, RawReportTerm, ReportColumn
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.DataRecordPaging import DataRecordPojoPageCriteria
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.utils.autopaging import QueryDataRecordsAutoPager, QueryDataRecordByIdListAutoPager, \
    QueryAllRecordsOfTypeAutoPager
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel, AbstractRecordModelPropertyGetter, \
    RecordModelPropertyType, AbstractRecordModelPropertyAdder, AbstractRecordModelPropertySetter, \
    AbstractRecordModelPropertyRemover
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType, WrappedRecordModel
from sapiopylib.rest.utils.recordmodel.RelationshipPath import RelationshipPath, RelationshipNode, \
    RelationshipNodeType
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager
from sapiopylib.rest.utils.recordmodel.properties import Parents, Parent, Children, Child, ForwardSideLink, \
    ReverseSideLink

# Aliases for longer name.
_PropertyGetter: TypeAlias = AbstractRecordModelPropertyGetter
_PropertyAdder: TypeAlias = AbstractRecordModelPropertyAdder
_PropertyRemover: TypeAlias = AbstractRecordModelPropertyRemover
_PropertySetter: TypeAlias = AbstractRecordModelPropertySetter
_PropertyType: TypeAlias = RecordModelPropertyType

# CR-47717: Use TypeVars in the type hints of certain functions to prevent PyCharm from erroneously flagging certain
# return type hints as incorrect.
IsRecordModel = TypeVar('IsRecordModel', bound=RecordModel)
"""A PyRecordModel or AbstractRecordModel."""
IsSapioRecord = TypeVar('IsSapioRecord', bound=SapioRecord)
"""A DataRecord, PyRecordModel, or AbstractRecordModel."""


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
# FR-47575 - Reordered functions so that the Java and Python versions are as close to each other as possible.
class RecordHandler:
    """
    A collection of shorthand methods for dealing with the various record managers.
    """
    user: SapioUser
    dr_man: DataRecordManager
    rec_man: RecordModelManager
    inst_man: RecordModelInstanceManager
    rel_man: RecordModelRelationshipManager
    an_man: RecordModelAncestorManager

    __instances: WeakValueDictionary[SapioUser, RecordHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        user = AliasUtil.to_sapio_user(context)
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        if self.__initialized:
            return
        self.__initialized = True

        self.user = AliasUtil.to_sapio_user(context)
        self.dr_man = DataRecordManager(self.user)
        self.rec_man = RecordModelManager(self.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = RecordModelAncestorManager(self.rec_man)

    # CR-47491: Support not providing a wrapper type to receive PyRecordModels instead of WrappedRecordModels.
    def wrap_model(self, record: DataRecord | PyRecordModel, wrapper_type: type[WrappedType] | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Shorthand for adding a single data record or PyRecordModel as a WrappedRecordModel.

        :param record: The data record or PyRecordModel to wrap.
        :param wrapper_type: The record model wrapper to use. If not provided, the record is returned as a
            PyRecordModel instead of a WrappedRecordModel.
        :return: The record model for the input.
        """
        if wrapper_type is not None:
            self.__verify_data_type(record, wrapper_type)
            if isinstance(record, PyRecordModel):
                return self.inst_man.wrap(record, wrapper_type)
            return self.inst_man.add_existing_record_of_type(record, wrapper_type)
        if isinstance(record, PyRecordModel):
            return record
        return self.inst_man.add_existing_record(record)

    def wrap_models(self, records: Iterable[DataRecord | PyRecordModel],
                    wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for adding a list of data records or PyRecordModels as a WrappedRecordModels.

        :param records: The data records to wrap.
        :param wrapper_type: The record model wrapper to use. If not provided, the records are returned as
            PyRecordModels instead of WrappedRecordModels.
        :return: The record models for the input.
        """
        return [self.wrap_model(x, wrapper_type) for x in records]

    def add_model(self, wrapper_type: type[WrappedType] | str) -> WrappedType | PyRecordModel:
        """
        Shorthand for using the instance manager to add a new record model of the given type.

        :param wrapper_type: The record model wrapper to use, or the data type name of the record.
        :return: The newly added record model. If a data type name was used instead of a model wrapper, then the
            returned record will be a PyRecordModel instead of a WrappedRecordModel.
        """
        return self.add_models(wrapper_type, 1)[0]

    def add_models(self, wrapper_type: type[WrappedType] | str, num: int) -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for using the instance manager to add new record models of the given type.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param num: The number of models to create.
        :return: The newly added record models. If a data type name was used instead of a model wrapper, then the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        if isinstance(wrapper_type, str):
            return self.inst_man.add_new_records(wrapper_type, num)
        return self.inst_man.add_new_records_of_type(num, wrapper_type)

    def add_models_with_data(self, wrapper_type: type[WrappedType] | str, fields: list[FieldIdentifierMap]) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for using the instance manager to add new models of the given type, and then initializing all those
        models with the given fields.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param fields: A list of field maps to initialize the record models with.
        :return: The newly added record models with the provided fields set. The records will be in the same order as
            the fields in the fields list. If a data type name was used instead of a model wrapper, then the returned
            records will be PyRecordModels instead of WrappedRecordModels.
        """
        fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(fields)
        models: list[WrappedType] = self.add_models(wrapper_type, len(fields))
        for model, field_list in zip(models, fields):
            model.set_field_values(field_list)
        return models

    def find_or_add_model(self, wrapper_type: type[WrappedType] | str, primary_identifier: FieldIdentifier,
                          id_value: FieldValue, secondary_identifiers: FieldIdentifierMap | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Find a unique record that matches the given field values. If no such records exist, add a record model to the
        cache with the identifying fields set to the desired values. This record will be created in the system when
        you store and commit changes. If more than one record with the identifying values exists, throws an exception.

        The record is searched for using the primary identifier field name and value. If multiple records are returned
        by the query on this primary identifier, then the secondary identifiers are used to filter the results.

        Makes a webservice call to query for the existing record.

        :param wrapper_type: The record model wrapper to use, or the data type name of the record.
        :param primary_identifier: The data field name of the field to search on.
        :param id_value: The value of the identifying field to search for.
        :param secondary_identifiers: Optional fields used to filter the records that are returned after searching on
            the primary identifier.
        :return: The record model with the identifying field value, either pulled from the system or newly created.
            If a data type name was used instead of a model wrapper, then the returned record will be a PyRecordModel
            instead of a WrappedRecordModel.
        """
        # PR-46335: Initialize the secondary identifiers parameter if None is provided to avoid an exception.
        # If no secondary identifiers were provided, use an empty dictionary.
        if secondary_identifiers is None:
            secondary_identifiers = {}

        primary_identifier: str = AliasUtil.to_data_field_name(primary_identifier)
        secondary_identifiers: FieldMap = AliasUtil.to_data_field_names_dict(secondary_identifiers)
        unique_record: WrappedType | None = self.__find_model(wrapper_type, primary_identifier, id_value,
                                                              secondary_identifiers)
        # If a unique record matched the identifiers, return it.
        if unique_record is not None:
            return unique_record

        # If none of the results matched the identifiers, create a new record with all identifiers set.
        # Put the primary identifier and value into the secondary identifiers list and use that as the fields map
        # for this new record.
        secondary_identifiers.update({primary_identifier: id_value})
        return self.add_models_with_data(wrapper_type, [secondary_identifiers])[0]

    def create_models(self, wrapper_type: type[WrappedType] | str, num: int) -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for creating new records via the data record manager and then returning them as wrapped
        record models. Useful in cases where your record model needs to have a valid record ID.

        Makes a webservice call to create the data records.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param num: The number of new records to create.
        :return: The newly created record models. If a data type name was used instead of a model wrapper, then the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        if isinstance(wrapper_type, str):
            wrapper_type = None
        return self.wrap_models(self.dr_man.add_data_records(dt, num), wrapper_type)

    def create_models_with_data(self, wrapper_type: type[WrappedType] | str, fields: list[FieldIdentifierMap]) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for creating new records via the data record manager with field data to initialize the records with
        and then returning them as wrapped record models. Useful in cases where your record model needs to have a valid
        record ID.

        Makes a webservice call to create the data records.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param fields: The field map list to initialize the new data records with.
        :return: The newly created record models. If a data type name was used instead of a model wrapper, then the
            returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        if isinstance(wrapper_type, str):
            wrapper_type = None
        fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(fields)
        return self.wrap_models(self.dr_man.add_data_records_with_data(dt, fields), wrapper_type)

    def find_or_create_model(self, wrapper_type: type[WrappedType] | str, primary_identifier: FieldIdentifier,
                             id_value: FieldValue, secondary_identifiers: FieldIdentifierMap | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Find a unique record that matches the given field values. If no such records exist, create one with the
        identifying fields set to the desired values. If more than one record with the identifying values exists,
        throws an exception.

        The record is searched for using the primary identifier field name and value. If multiple records are returned
        by the query on this primary identifier, then the secondary identifiers are used to filter the results.

        Makes a webservice call to query for the existing record. Makes an additional webservice call if the record
        needs to be created.

        :param wrapper_type: The record model wrapper to use, or the data type name of the record.
        :param primary_identifier: The data field name of the field to search on.
        :param id_value: The value of the identifying field to search for.
        :param secondary_identifiers: Optional fields used to filter the records that are returned after searching on
            the primary identifier.
        :return: The record model with the identifying field value, either pulled from the system or newly created.
            If a data type name was used instead of a model wrapper, then the returned record will be a PyRecordModel
            instead of a WrappedRecordModel.
        """
        # PR-46335: Initialize the secondary identifiers parameter if None is provided to avoid an exception.
        # If no secondary identifiers were provided, use an empty dictionary.
        if secondary_identifiers is None:
            secondary_identifiers = {}

        primary_identifier: str = AliasUtil.to_data_field_name(primary_identifier)
        secondary_identifiers: FieldMap = AliasUtil.to_data_field_names_dict(secondary_identifiers)
        unique_record: WrappedType | None = self.__find_model(wrapper_type, primary_identifier, id_value,
                                                              secondary_identifiers)
        # If a unique record matched the identifiers, return it.
        if unique_record is not None:
            return unique_record

        # If none of the results matched the identifiers, create a new record with all identifiers set.
        # Put the primary identifier and value into the secondary identifiers list and use that as the fields map
        # for this new record.
        secondary_identifiers.update({primary_identifier: id_value})
        return self.create_models_with_data(wrapper_type, [secondary_identifiers])[0]

    # CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
    # CR-47523: Support a singular field value being provided for the value_list parameter.
    def query_models(self, wrapper_type: type[WrappedType] | str, field: FieldIdentifier,
                     value_list: Iterable[FieldValue] | FieldValue,
                     page_limit: int | None = None, page_size: int | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for using the data record manager to query for a list of data records by field value
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param field: The field to query on.
        :param value_list: The values of the field to query on, or a singular field value that will be automatically
            converted to a singleton list. Note that field values of None are not supported by this method and will be
            ignored. If you need to query for records with a null field value, use a custom report.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records. If a data type name was used instead of a model wrapper,
            then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_models_with_criteria(wrapper_type, field, value_list, criteria, page_limit)[0]

    def query_and_map_models(self, wrapper_type: type[WrappedType] | str, field: FieldIdentifier,
                             value_list: Iterable[FieldValue] | FieldValue,
                             page_limit: int | None = None, page_size: int | None = None,
                             *,
                             mapping_field: FieldIdentifier | None = None) \
            -> dict[FieldValue, list[WrappedType] | list[PyRecordModel]]:
        """
        Shorthand for using query_models to search for records given values on a specific field and then using
        map_by_field to turn the returned list into a dictionary mapping field values to records.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param field: The field to query and map on.
        :param value_list: The values of the field to query on, or a singular field value that will be automatically
            converted to a singleton list. Note that field values of None are not supported by this method and will be
            ignored. If you need to query for records with a null field value, use a custom report.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :param mapping_field: If provided, use this field to map against instead of the field that was queried on.
        :return: The record models for the queried records mapped by field values to the records with that value.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        """
        if mapping_field is None:
            mapping_field = field
        return self.map_by_field(self.query_models(wrapper_type, field, value_list, page_limit, page_size),
                                 mapping_field)

    def query_and_unique_map_models(self, wrapper_type: type[WrappedType] | str, field: FieldIdentifier,
                                    value_list: Iterable[FieldValue] | FieldValue,
                                    page_limit: int | None = None, page_size: int | None = None,
                                    *,
                                    mapping_field: FieldIdentifier | None = None) \
            -> dict[FieldValue, WrappedType | PyRecordModel]:
        """
        Shorthand for using query_models to search for records given values on a specific field and then using
        map_by_unique_field to turn the returned list into a dictionary mapping field values to records.
        If any two records share the same field value, throws an exception.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param field: The field to query and map on.
        :param value_list: The values of the field to query on, or a singular field value that will be automatically
            converted to a singleton list. Note that field values of None are not supported by this method and will be
            ignored. If you need to query for records with a null field value, use a custom report.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :param mapping_field: If provided, use this field to map against instead of the field that was queried on.
        :return: The record models for the queried records mapped by field values to the record with that value.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        """
        if mapping_field is None:
            mapping_field = field
        return self.map_by_unique_field(self.query_models(wrapper_type, field, value_list, page_limit, page_size),
                                        mapping_field)

    def query_models_with_criteria(self, wrapper_type: type[WrappedType] | str, field: FieldIdentifier,
                                   value_list: Iterable[FieldValue] | FieldValue,
                                   paging_criteria: DataRecordPojoPageCriteria | None = None,
                                   page_limit: int | None = None) \
            -> tuple[list[WrappedType] | list[PyRecordModel], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for a list of data records by field value
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param field: The field to query on.
        :param value_list: The values of the field to query on, or a singular field value that will be automatically
            converted to a singleton list. Note that field values of None are not supported by this method and will be
            ignored. If you need to query for records with a null field value, use a custom report.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria. If a data type name was used
            instead of a model wrapper, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        if isinstance(wrapper_type, str):
            wrapper_type = None
        field: str = AliasUtil.to_data_field_name(field)
        if isinstance(value_list, FieldValue):
            value_list: list[FieldValue] = [value_list]
        pager = QueryDataRecordsAutoPager(dt, field, list(value_list), self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_id(self, wrapper_type: type[WrappedType] | str, ids: Iterable[int],
                           page_limit: int | None = None, page_size: int | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param ids: The list of record IDs to query.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records. If a data type name was used instead of a model wrapper,
            then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_models_by_id_with_criteria(wrapper_type, ids, criteria, page_limit)[0]

    def query_models_by_id_with_criteria(self, wrapper_type: type[WrappedType] | str, ids: Iterable[int],
                                         paging_criteria: DataRecordPojoPageCriteria | None = None,
                                         page_limit: int | None = None) \
            -> tuple[list[WrappedType] | list[PyRecordModel], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param ids: The list of record IDs to query.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria. If a data type name was used
            instead of a model wrapper, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        if isinstance(wrapper_type, str):
            wrapper_type = None
        pager = QueryDataRecordByIdListAutoPager(dt, list(ids), self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_id_and_map(self, wrapper_type: type[WrappedType] | str, ids: Iterable[int],
                                   page_limit: int | None = None, page_size: int | None = None) \
            -> dict[int, WrappedType | PyRecordModel]:
        """
        Shorthand for using the data record manager to query for a list of data records by record ID
        and then converting the results into a dictionary of record ID to the record model for that ID.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param ids: The list of record IDs to query.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records mapped in a dictionary by their record ID.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        """
        return {AliasUtil.to_record_id(x): x for x in self.query_models_by_id(wrapper_type, ids, page_limit, page_size)}

    def query_all_models(self, wrapper_type: type[WrappedType] | str, page_limit: int | None = None,
                         page_size: int | None = None) -> list[WrappedType] | list[PyRecordModel]:
        """
        Shorthand for using the data record manager to query for all data records of a given type
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages. This parameter
            only functions if you set a page size or the platform enforces a page size.
        :param page_size: The size of the pages to query. If None, the page size may be limited by the platform.
        :return: The record models for the queried records. If a data type name was used instead of a model wrapper,
            then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        criteria: DataRecordPojoPageCriteria | None = None
        if page_size is not None:
            criteria = DataRecordPojoPageCriteria(page_size=page_size)
        return self.query_all_models_with_criteria(wrapper_type, criteria, page_limit)[0]

    def query_all_models_with_criteria(self, wrapper_type: type[WrappedType] | str,
                                       paging_criteria: DataRecordPojoPageCriteria | None = None,
                                       page_limit: int | None = None) \
            -> tuple[list[WrappedType] | list[PyRecordModel], DataRecordPojoPageCriteria]:
        """
        Shorthand for using the data record manager to query for all data records of a given type
        and then converting the results into a list of record models.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param paging_criteria: The paging criteria to start the query with.
        :param page_limit: The maximum number of pages to query from the starting criteria. If None, exhausts all
            possible pages. This parameter only functions if you set a page size in the paging criteria or the platform
            enforces a page size.
        :return: The record models for the queried records and the final paging criteria. If a data type name was used
            instead of a model wrapper, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        if isinstance(wrapper_type, str):
            wrapper_type = None
        pager = QueryAllRecordsOfTypeAutoPager(dt, self.user, paging_criteria)
        pager.max_page = page_limit
        return self.wrap_models(pager.get_all_at_once(), wrapper_type), pager.next_page_criteria

    def query_models_by_report(self, wrapper_type: type[WrappedType] | str,
                               report_name: str | RawReportTerm | CustomReportCriteria,
                               filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None = None,
                               page_limit: int | None = None,
                               page_size: int | None = None,
                               page_number: int | None = None) -> list[WrappedType] | list[PyRecordModel]:
        """
        Run a report and use the results of that report to query for and return the records in the report results.
        First runs the report, then runs a data record manager query on the results of the custom report.

        Will throw an exception if given the name of a system report that does not have a RecordId column.
        Quick and custom reports are guaranteed to have a record ID column.

        Any given custom report criteria should only have columns from a single data type.

        :param wrapper_type: The record model wrapper to use, or the data type name of the records.
        :param report_name: The name of a system report, or a raw report term for a quick report, or custom report
            criteria for a custom report.
        :param filters: If provided, filter the results of the report using the given mapping of headers to values to
            filter on. This filtering is done before the records are queried.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages.
        :param page_size: The size of each page of results in the search. If None, the page size is set by the server.
            If the input report is a custom report criteria, uses the value from the criteria, unless this value is
            not None, in which case it overwrites the given report's value.
        :param page_number: The page number to start the search from, If None, starts on the first page.
            If the input report is a custom report criteria, uses the value from the criteria, unless this value is
            not None, in which case it overwrites the given report's value. Note that the number of the first page is 0.
        :return: The record models for the queried records that matched the given report. If a data type name was used
            instead of a model wrapper, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        warnings.warn("Deprecated in favor of the [System/Custom/Quick]ReportRecordAutoPager classes.", DeprecationWarning)
        if isinstance(report_name, str):
            # noinspection PyDeprecation
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_system_report(self.user, report_name, filters,
                                                                                      page_limit, page_size, page_number)
        elif isinstance(report_name, RawReportTerm):
            # noinspection PyDeprecation
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_quick_report(self.user, report_name, filters,
                                                                                     page_limit, page_size, page_number)
        elif isinstance(report_name, CustomReportCriteria):
            dt: str = AliasUtil.to_data_type_name(wrapper_type)
            # Ensure that the root data type is the one we're looking for.
            report_name.root_data_type = dt
            # Raise an exception if any column in the report doesn't match the given data type.
            if any([x.data_type_name != dt for x in report_name.column_list]):
                raise SapioException("You may only query records from a report containing columns from that data type.")
            # Enforce that the given custom report has a record ID column.
            if not any([x.data_type_name == dt and x.data_field_name == "RecordId" for x in report_name.column_list]):
                report_name.column_list.append(ReportColumn(dt, "RecordId", FieldType.LONG))
            # noinspection PyDeprecation
            results: list[dict[str, FieldValue]] = CustomReportUtil.run_custom_report(self.user, report_name, filters,
                                                                                      page_limit, page_size, page_number)
        else:
            raise SapioException("Unrecognized report object.")

        # Using the bracket accessor because we want to throw an exception if RecordId doesn't exist in the report.
        # This should only possibly be the case with system reports, as quick reports will include the record ID, and
        # we forced any given custom report to have a record ID column.
        ids: list[int] = [row["RecordId"] for row in results]
        return self.query_models_by_id(wrapper_type, ids)

    @staticmethod
    def map_by_id(models: Iterable[IsSapioRecord]) -> dict[int, IsSapioRecord]:
        """
        Map the given records their record IDs.

        :param models: The records to map.
        :return: A dict mapping the record ID to each record.
        """
        ret_dict: dict[int, SapioRecord] = {}
        for model in models:
            ret_dict.update({AliasUtil.to_record_id(model): model})
        return ret_dict

    @staticmethod
    def map_by_field(models: Iterable[IsSapioRecord], field_name: FieldIdentifier) \
            -> dict[FieldValue, list[IsSapioRecord]]:
        """
        Map the given records by one of their fields. If any two records share the same field value, they'll appear in
        the same value list.

        :param models: The records to map.
        :param field_name: The field name to map against.
        :return: A dict mapping field values to the records with that value.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        ret_dict: dict[FieldValue, list[SapioRecord]] = {}
        for model in models:
            val: FieldValue = model.get_field_value(field_name)
            ret_dict.setdefault(val, []).append(model)
        return ret_dict

    @staticmethod
    def map_by_unique_field(models: Iterable[IsSapioRecord], field_name: FieldIdentifier) \
            -> dict[FieldValue, IsSapioRecord]:
        """
        Uniquely map the given records by one of their fields. If any two records share the same field value, throws
        an exception.

        :param models: The records to map.
        :param field_name: The field name to map against.
        :return: A dict mapping field values to the record with that value.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        ret_dict: dict[FieldValue, SapioRecord] = {}
        for model in models:
            val: FieldValue = model.get_field_value(field_name)
            if val in ret_dict:
                raise SapioException(f"Value {val} encountered more than once in models list.")
            ret_dict.update({val: model})
        return ret_dict

    # FR-47525: Add functions for getting and setting record image bytes.
    def get_record_image(self, record: SapioRecord) -> bytes:
        """
        Retrieve the record image for a given record.

        :param record: The record model to retrieve the image of.
        :return: The file bytes of the given record's image.
        """
        record: DataRecord = AliasUtil.to_data_record(record)
        with io.BytesIO() as data_sink:
            def consume_data(chunk: bytes):
                data_sink.write(chunk)

            self.dr_man.get_record_image(record, consume_data)
            data_sink.flush()
            data_sink.seek(0)
            file_bytes = data_sink.read()
        return file_bytes

    def set_record_image(self, record: SapioRecord, file_data: str | bytes) -> None:
        """
        Set the record image for a given record.

        :param record: The record model to set the image of.
        :param file_data: The file data of the image to set on the record.
        """
        record: DataRecord = AliasUtil.to_data_record(record)
        with io.BytesIO(file_data.encode() if isinstance(file_data, str) else file_data) as stream:
            self.dr_man.set_record_image(record, stream)

    @staticmethod
    def sum_of_field(models: Iterable[SapioRecord], field_name: FieldIdentifier) -> float:
        """
        Sum up the numeric value of a given field across all input models. Excepts that all given models have a value.
        If the field is an integer field, the value will be converted to a float.

        :param models: The models to calculate the sum of.
        :param field_name: The name of the numeric field to sum.
        :return: The sum of the field values for the collection of models.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        field_sum: float = 0
        for model in models:
            val = model.get_field_value(field_name)
            if isinstance(val, (int, float)):
                field_sum += float(model.get_field_value(field_name))
        return field_sum

    @staticmethod
    def mean_of_field(models: Collection[SapioRecord], field_name: FieldIdentifier) -> float:
        """
        Calculate the average (arithmetic mean) of the numeric value of a given field across all input models. Excepts
        that all given models have a value. If the field is an integer field, the value will be converted to a float.

        :param models: The models to calculate the mean of.
        :param field_name: The name of the numeric field to mean.
        :return: The mean of the field values for the collection of models.
        """
        return RecordHandler.sum_of_field(models, field_name) / len(models)

    @staticmethod
    def get_newest_record(records: Iterable[IsSapioRecord]) -> IsSapioRecord:
        """
        Get the newest record from a list of records.

        :param records: The list of records.
        :return: The input record with the highest record ID. None if the input list is empty.
        """
        return max(records, key=lambda x: x.record_id)

    # FR-46696: Add a function for getting the oldest record in a list, just like we have one for the newest record.
    @staticmethod
    def get_oldest_record(records: Iterable[IsSapioRecord]) -> IsSapioRecord:
        """
        Get the oldest record from a list of records.

        :param records: The list of records.
        :return: The input record with the lowest record ID. None if the input list is empty.
        """
        return min(records, key=lambda x: x.record_id)

    @staticmethod
    def get_min_record(records: list[IsSapioRecord], field: FieldIdentifier) -> IsSapioRecord:
        """
        Get the record model with the minimum value of a given field from a list of record models.

        :param records: The list of record models to search through.
        :param field: The field to find the minimum value of.
        :return: The record model with the minimum value of the given field.
        """
        field: str = AliasUtil.to_data_field_name(field)
        return min(records, key=lambda x: x.get_field_value(field))

    @staticmethod
    def get_max_record(records: list[IsSapioRecord], field: FieldIdentifier) -> IsSapioRecord:
        """
        Get the record model with the maximum value of a given field from a list of record models.

        :param records: The list of record models to search through.
        :param field: The field to find the maximum value of.
        :return: The record model with the maximum value of the given field.
        """
        field: str = AliasUtil.to_data_field_name(field)
        return max(records, key=lambda x: x.get_field_value(field))

    # FR-47522: Add RecordHandler functions that copy from the RecordModelUtil class in our Java utilities.
    @staticmethod
    def get_values_list(records: list[RecordModel], field: FieldIdentifier) -> list[FieldValue]:
        """
        Get a list of field values from a list of record models.

        :param records: The list of record models to get the field values from.
        :param field: The field to get the values of.
        :return: A list of field values from the input record models. The values are in the same order as the input
            record models.
        """
        field: str = AliasUtil.to_data_field_name(field)
        return [x.get_field_value(field) for x in records]

    @staticmethod
    def get_values_set(records: list[RecordModel], field: FieldIdentifier) -> set[FieldValue]:
        """
        Get a set of field values from a list of record models.

        :param records: The list of record models to get the field values from.
        :param field: The field to get the values of.
        :return: A set of field values from the input record models.
        """
        field: str = AliasUtil.to_data_field_name(field)
        return {x.get_field_value(field) for x in records}

    @staticmethod
    def set_values(records: list[RecordModel], field: FieldIdentifier, value: FieldValue) -> None:
        """
        Set the value of a field on a list of record models.

        :param records: The list of record models to set the field value on.
        :param field: The field to set the value of.
        :param value: The value to set the field to for all input records.
        """
        field: str = AliasUtil.to_data_field_name(field)
        for record in records:
            record.set_field_value(field, value)

    @staticmethod
    def values_to_field_maps(field_name: FieldIdentifier, values: Iterable[FieldValue],
                             existing_fields: list[FieldMap] | None = None) -> list[FieldMap]:
        """
        Add a list of values for a specific field to a list of dictionaries pairing each value to that field name.

        :param field_name: The name of the field that the values are from.
        :param values: A list of field values.
        :param existing_fields: An optional existing fields map list to add the new values to. Values are added in the
            list in the same order that they appear. If no existing fields are provided, returns a new fields map list.
        :return: A fields map list that contains the given values mapped by the given field name.
        """
        # Update the existing fields map list if one is given.
        field_name: str = AliasUtil.to_data_field_name(field_name)
        existing_fields: list[FieldMap] = AliasUtil.to_data_field_names_list_dict(existing_fields)
        if existing_fields:
            values = list(values)
            # The number of new values must match the length of the existing fields list.
            if len(values) != len(existing_fields):
                raise SapioException(f"Length of \"{field_name}\" values does not match the existing fields length.")
            for field, value in zip(existing_fields, values):
                field.update({field_name: value})
            return existing_fields
        # Otherwise, create a new fields map list.
        return [{field_name: value} for value in values]

    @staticmethod
    def get_from_all(records: Iterable[RecordModel], getter: _PropertyGetter[_PropertyType]) \
            -> list[RecordModelPropertyType]:
        """
        Use a getter property on all records in a list of record models. For example, you can iterate over a list of
        record models using a getter of Ancestors.of_type(SampleModel) to get all the SampleModel ancestors from each
        record.

        :param records: The list of record models to get the property from.
        :param getter: The getter to use to get the property from each record.
        :return: A list of the property values from the input record models. The value at the matching index of the
            input records is the results of using the getter on that record.
        """
        return [x.get(getter) for x in records]

    @staticmethod
    def set_on_all(records: Iterable[RecordModel], setter: _PropertySetter[_PropertyType]) \
            -> list[RecordModelPropertyType]:
        """
        Use a setter property on all records in a list of record models. For example, you can iterate over a list of
        record models user a setter of ForwardSideLink.ref(field_name, record) to set a forward side link on each
        record.

        :param records: The list of record models to set the property on.
        :param setter: The setter to use to set the property on each record.
        :return: A list of the property values that were set on the input record models. The value at the matching index
            of the input records is the results of using the setter on that record.
        """
        return [x.set(setter) for x in records]

    @staticmethod
    def add_to_all(records: Iterable[RecordModel], adder: _PropertyAdder[_PropertyType]) \
            -> list[RecordModelPropertyType]:
        """
        Use an adder property on all records in a list of record models. For example, you can iterate over a list of
        record models using an adder of Child.create(SampleModel) to create a new SampleModel child on each record.

        :param records: The list of record models to add the property to.
        :param adder: The adder to use to add the property to each record.
        :return: A list of the property values that were added to the input record models. The value at the matching
            index of the input records is the results of using the adder on that record.
        """
        return [x.add(adder) for x in records]

    @staticmethod
    def remove_from_all(records: Iterable[RecordModel], remover: _PropertyRemover[_PropertyType]) \
            -> list[RecordModelPropertyType]:
        """
        Use a remover property on all records in a list of record models. For example, you can iterate over a list of
        record models using a remover of Parents.ref(records) to remove a list of parents from each record.

        :param records: The list of record models to remove the property from.
        :param remover: The remover to use to remove the property from each record.
        :return: A list of the property values that were removed from the input record models. The value at the matching
            index of the input records is the results of using the remover on that record.
        """
        return [x.remove(remover) for x in records]

    # FR-47527: Created functions for manipulating relationships between records,
    def get_extension(self, model: RecordModel, wrapper_type: type[WrappedType] | str) \
            -> WrappedType | PyRecordModel | None:
        """
        Given a record with an extension record related to it, return the extension record as a record model.
        This will retrieve an extension record without doing a webservice request to the server. The input record and
        extension record will be considered related to one another if you later use load_child or load_parent on the
        input record or extension record respectively.

        :param model: The record model to get the extension for.
        :param wrapper_type: The record model wrapper to use, or the data type name of the extension record. If a data
            type name is provided, the returned record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: The extension record model for the input record model, or None if no extension record exists.
        """
        ext_dt: str = AliasUtil.to_data_type_name(wrapper_type)
        ext_fields: FieldMap = {}
        for field, value in AliasUtil.to_field_map(model).items():
            if field.startswith(ext_dt + "."):
                ext_fields[field.removeprefix(ext_dt + ".")] = value
        if not ext_fields or ext_fields.get("RecordId") is None:
            return None
        ext_rec: DataRecord = DataRecord(ext_dt, ext_fields.get("RecordId"), ext_fields)
        ext_model: WrappedType | PyRecordModel = self.wrap_model(ext_rec, wrapper_type)
        self._spoof_child_load(model, ext_model)
        self._spoof_parent_load(ext_model, model)
        return ext_model

    def get_or_add_parent(self, record: RecordModel, parent_type: type[WrappedType] | str) \
            -> WrappedType | PyRecordModel:
        """
        Given a record model, retrieve the singular parent record model of a given type. If a parent of the given type
        does not exist, a new one will be created. The parents of the given data type must already be loaded.

        :param record: The record model to get the parent of.
        :param parent_type: The record model wrapper of the parent, or the data type name of the parent. If a data type
            name is provided, the returned record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: The parent record model of the given type.
        """
        parent_dt: str = AliasUtil.to_data_type_name(parent_type)
        wrapper: type[WrappedType] | None = parent_type if isinstance(parent_type, type) else None
        record: PyRecordModel = RecordModelInstanceManager.unwrap(record)
        parent: PyRecordModel | None = record.get(Parent.of_type_name(parent_dt))
        if parent is not None:
            return self.wrap_model(parent, wrapper) if wrapper else parent
        return record.add(Parent.create(wrapper)) if wrapper else record.add(Parent.create_by_name(parent_dt))

    def get_or_add_child(self, record: RecordModel, child_type: type[WrappedType] | str) -> WrappedType | PyRecordModel:
        """
        Given a record model, retrieve the singular child record model of a given type. If a child of the given type
        does not exist, a new one will be created. The children of the given data type must already be loaded.

        :param record: The record model to get the child of.
        :param child_type: The record model wrapper of the child, or the data type name of the child. If a data type
            name is provided, the returned record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: The child record model of the given type.
        """
        child_dt: str = AliasUtil.to_data_type_name(child_type)
        wrapper: type[WrappedType] | None = child_type if isinstance(child_type, type) else None
        record: PyRecordModel = RecordModelInstanceManager.unwrap(record)
        child: PyRecordModel | None = record.get(Child.of_type_name(child_dt))
        if child is not None:
            return self.wrap_model(child, wrapper) if wrapper else child
        return record.add(Child.create(wrapper)) if wrapper else record.add(Child.create_by_name(child_dt))

    def get_or_add_side_link(self, record: RecordModel, side_link_field: FieldIdentifier,
                             side_link_type: type[WrappedType] | str) -> WrappedType | PyRecordModel:
        """
        Given a record model, retrieve the singular side link record model of a given type. If a side link of the given
        type does not exist, a new one will be created. The side links of the given data type must already be loaded.

        :param record: The record model to get the side link of.
        :param side_link_field: The field name of the side link to get.
        :param side_link_type: The record model wrapper of the side link, or the data type name of the side link. If a
            data type name is provided, the returned record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: The side link record model of the given type.
        """
        side_link_field: str = AliasUtil.to_data_field_name(side_link_field)
        wrapper: type[WrappedType] | None = side_link_type if isinstance(side_link_type, type) else None
        record: PyRecordModel = RecordModelInstanceManager.unwrap(record)
        side_link: PyRecordModel | None = record.get(ForwardSideLink.of(side_link_field))
        if side_link is not None:
            return self.wrap_model(side_link, wrapper) if wrapper else side_link
        side_link: WrappedType | PyRecordModel = self.add_model(side_link_type)
        record.set(ForwardSideLink.ref(side_link_field, side_link))
        return side_link

    @staticmethod
    def set_parents(record: RecordModel, parents: Iterable[RecordModel], parent_type: DataTypeIdentifier) -> None:
        """
        Set the parents of a record model to a list of parent record models of a given type. The parents of the given
        data type must already be loaded. This method will add the parents to the record model if they are not already
        parents, and remove any existing parents that are not in the input list.

        :param record: The record model to set the parents of.
        :param parents: The list of parent record models to set as the parents of the input record model.
        :param parent_type: The data type identifier of the parent record models.
        """
        parent_dt: str = AliasUtil.to_data_type_name(parent_type)
        existing_parents: list[PyRecordModel] = record.get(Parents.of_type_name(parent_dt))
        for parent in parents:
            if parent not in existing_parents:
                record.add(Parent.ref(parent))
        for parent in existing_parents:
            if parent not in parents:
                record.remove(Parent.ref(parent))

    @staticmethod
    def set_children(record: RecordModel, children: Iterable[RecordModel], child_type: DataTypeIdentifier) -> None:
        """
        Set the children of a record model to a list of child record models of a given type. The children of the given
        data type must already be loaded. This method will add the children to the record model if they are not already
        children, and remove any existing children that are not in the input list.

        :param record: The record model to set the children of.
        :param children: The list of child record models to set as the children of the input record model.
        :param child_type: The data type identifier of the child record models.
        """
        child_dt: str = AliasUtil.to_data_type_name(child_type)
        existing_children: list[PyRecordModel] = record.get(Children.of_type_name(child_dt))
        for child in children:
            if child not in existing_children:
                record.add(Child.ref(child))
        for child in existing_children:
            if child not in children:
                record.remove(Child.ref(child))

    # CR-47717: Update the map_[to/by]_[relationship] functions to allow PyRecordModels to be provided and returned
    # instead of only using WrappedRecordModels and wrapper types.
    @staticmethod
    def map_to_parent(models: Iterable[IsRecordModel], parent_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel]:
        """
        Map a list of record models to a single parent of a given type. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper or data type name of the parents. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, ParentType]. If an input model doesn't have a parent of the given parent type, then
            it will map to None.
        """
        return_dict: dict[RecordModel, WrappedType | PyRecordModel] = {}
        for model in models:
            if isinstance(parent_type, str):
                return_dict[model] = model.get(Parent.of_type_name(parent_type))
            else:
                return_dict[model] = model.get(Parent.of_type(parent_type))
        return return_dict

    @staticmethod
    def map_to_parents(models: Iterable[IsRecordModel], parent_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, list[WrappedType] | list[PyRecordModel]]:
        """
        Map a list of record models to a list parents of a given type. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper or data type name of the parents. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, list[ParentType]]. If an input model doesn't have a parent of the given parent type,
            then it will map to an empty list.
        """
        return_dict: dict[WrappedRecordModel, list[WrappedType] | list[PyRecordModel]] = {}
        for model in models:
            if isinstance(parent_type, str):
                return_dict[model] = model.get(Parents.of_type_name(parent_type))
            else:
                return_dict[model] = model.get(Parents.of_type(parent_type))
        return return_dict

    @staticmethod
    def map_by_parent(models: Iterable[IsRecordModel], parent_type: type[WrappedType] | str) \
            -> dict[WrappedType | PyRecordModel, IsRecordModel]:
        """
        Take a list of record models and map them by their parent. Essentially an inversion of map_to_parent.
        If two records share the same parent, an exception will be thrown. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper or data type name of the parents. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ParentType, ModelType]. If an input model doesn't have a parent of the given parent type,
            then it will not be in the resulting dictionary.
        """
        to_parent: dict[RecordModel, WrappedType | PyRecordModel] = RecordHandler.map_to_parent(models, parent_type)
        by_parent: dict[WrappedType | PyRecordModel, RecordModel] = {}
        for record, parent in to_parent.items():
            if parent is None:
                continue
            if parent in by_parent:
                raise SapioException(f"Parent {parent.data_type_name} {parent.record_id} encountered more than once "
                                     f"in models list.")
            by_parent[parent] = record
        return by_parent

    @staticmethod
    def map_by_parents(models: Iterable[IsRecordModel], parent_type: type[WrappedType] | str) \
            -> dict[WrappedType | PyRecordModel, list[IsRecordModel]]:
        """
        Take a list of record models and map them by their parents. Essentially an inversion of map_to_parents. Input
        models that share a parent will end up in the same list. The parents must already be loaded.

        :param models: A list of record models.
        :param parent_type: The record model wrapper or data type name of the parents. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ParentType, list[ModelType]]. If an input model doesn't have a parent of the given parent type,
            then it will not be in the resulting dictionary.
        """
        to_parents: dict[RecordModel, list[WrappedType] | list[PyRecordModel]] = RecordHandler\
            .map_to_parents(models, parent_type)
        by_parents: dict[WrappedType | PyRecordModel, list[RecordModel]] = {}
        for record, parents in to_parents.items():
            for parent in parents:
                by_parents.setdefault(parent, []).append(record)
        return by_parents

    @staticmethod
    def map_to_child(models: Iterable[IsRecordModel], child_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel]:
        """
        Map a list of record models to a single child of a given type. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper or data type name of the children. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, ChildType]. If an input model doesn't have a child of the given child type, then
            it will map to None.
        """
        return_dict: dict[RecordModel, WrappedType | PyRecordModel] = {}
        for model in models:
            if isinstance(child_type, str):
                return_dict[model] = model.get(Child.of_type_name(child_type))
            else:
                return_dict[model] = model.get(Child.of_type(child_type))
        return return_dict

    @staticmethod
    def map_to_children(models: Iterable[IsRecordModel], child_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, list[WrappedType] | PyRecordModel]:
        """
        Map a list of record models to a list children of a given type. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper or data type name of the children. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, list[ChildType]]. If an input model doesn't have children of the given child type,
            then it will map to an empty list.
        """
        return_dict: dict[RecordModel, list[WrappedType] | list[PyRecordModel]] = {}
        for model in models:
            if isinstance(child_type, str):
                return_dict[model] = model.get(Children.of_type_name(child_type))
            else:
                return_dict[model] = model.get(Children.of_type(child_type))
        return return_dict

    @staticmethod
    def map_by_child(models: Iterable[IsRecordModel], child_type: type[WrappedType] | str) \
            -> dict[WrappedType | str, IsRecordModel]:
        """
        Take a list of record models and map them by their children. Essentially an inversion of map_to_child.
        If two records share the same child, an exception will be thrown. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper or data type name of the children. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ChildType, ModelType]. If an input model doesn't have a child of the given child type,
            then it will not be in the resulting dictionary.
        """
        to_child: dict[RecordModel, WrappedType | PyRecordModel] = RecordHandler.map_to_child(models, child_type)
        by_child: dict[WrappedType | PyRecordModel, RecordModel] = {}
        for record, child in to_child.items():
            if child is None:
                continue
            if child in by_child:
                raise SapioException(f"Child {child.data_type_name} {child.record_id} encountered more than once "
                                     f"in models list.")
            by_child[child] = record
        return by_child

    @staticmethod
    def map_by_children(models: Iterable[IsRecordModel], child_type: type[WrappedType] | str) \
            -> dict[WrappedType | PyRecordModel, list[IsRecordModel]]:
        """
        Take a list of record models and map them by their children. Essentially an inversion of map_to_children. Input
        models that share a child will end up in the same list. The children must already be loaded.

        :param models: A list of record models.
        :param child_type: The record model wrapper or data type name of the children. If a data type name is
            provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ChildType, list[ModelType]]. If an input model doesn't have children of the given child type,
            then it will not be in the resulting dictionary.
        """
        to_children: dict[RecordModel, list[WrappedType] | list[PyRecordModel]] = RecordHandler\
            .map_to_children(models, child_type)
        by_children: dict[WrappedType | PyRecordModel, list[RecordModel]] = {}
        for record, children in to_children.items():
            for child in children:
                by_children.setdefault(child, []).append(record)
        return by_children

    @staticmethod
    def map_to_forward_side_link(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType] | None) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel]:
        """
        Map a list of record models to their forward side link. The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side link. If None, the side links will
            be returned as PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, SlideLink]. If an input model doesn't have a forward side link of the given type,
            then it will map to None.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[RecordModel, WrappedType | PyRecordModel] = {}
        for model in models:
            return_dict[model] = model.get(ForwardSideLink.of(field_name, side_link_type))
        return return_dict

    @staticmethod
    def map_by_forward_side_link(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType] | None) \
            -> dict[WrappedType | PyRecordModel, IsRecordModel]:
        """
        Take a list of record models and map them by their forward side link. Essentially an inversion of
        map_to_forward_side_link, but if two records share the same forward link, an exception is thrown.
        The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side links. If None, the side links will
            be returned as PyRecordModels instead of WrappedRecordModels.
        :return: A dict[SideLink, ModelType]. If an input model doesn't have a forward side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[RecordModel, WrappedType | PyRecordModel] = RecordHandler\
            .map_to_forward_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType | PyRecordModel, RecordModel] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            if side_link in by_side_link:
                raise SapioException(f"Side link {side_link.data_type_name} {side_link.record_id} encountered more "
                                     f"than once in models list.")
            by_side_link[side_link] = record
        return by_side_link

    @staticmethod
    def map_by_forward_side_links(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType] | None) \
            -> dict[WrappedType | PyRecordModel, list[IsRecordModel]]:
        """
        Take a list of record models and map them by their forward side link. Essentially an inversion of
        map_to_forward_side_link. Input models that share a forward side link will end up in the same list.
        The forward side link must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the record models where the side link is located.
        :param side_link_type: The record model wrapper of the forward side links. If None, the side links will
            be returned as PyRecordModels instead of WrappedRecordModels.
        :return: A dict[SideLink, list[ModelType]]. If an input model doesn't have a forward side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[RecordModel, WrappedType | PyRecordModel] = RecordHandler\
            .map_to_forward_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType | PyRecordModel, list[RecordModel]] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            by_side_link.setdefault(side_link, []).append(record)
        return by_side_link

    @staticmethod
    def map_to_reverse_side_link(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel]:
        """
        Map a list of record models to the reverse side link of a given type. If a given record has more than one
        reverse side link of this type, an exception is thrown. The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper or data type name of the reverse side links. If a data type
            name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, SideLink]. If an input model doesn't have reverse side links of the given type,
            then it will map to None.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[RecordModel, WrappedType | PyRecordModel] = {}
        for model in models:
            if isinstance(side_link_type, str):
                links: list[WrappedType] = model.get(ReverseSideLink.of(side_link_type, field_name))
            else:
                links: list[WrappedType] = model.get(ReverseSideLink.of_type(side_link_type, field_name))
            if len(links) > 1:
                raise SapioException(f"Model {model.data_type_name} {model.record_id} has more than one reverse link "
                                     f"of type {side_link_type.get_wrapper_data_type_name()}.")
            return_dict[model] = links[0] if links else None
        return return_dict

    @staticmethod
    def map_to_reverse_side_links(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType] | str) \
            -> dict[IsRecordModel, list[WrappedType] | list[PyRecordModel]]:
        """
        Map a list of record models to a list reverse side links of a given type. The reverse side links must already
        be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper or data type name of the reverse side links. If a data type
            name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[ModelType, list[SideLink]]. If an input model doesn't have reverse side links of the given type,
            then it will map to an empty list.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        return_dict: dict[RecordModel, list[WrappedType] | list[PyRecordModel]] = {}
        for model in models:
            if isinstance(side_link_type, str):
                return_dict[model] = model.get(ReverseSideLink.of(side_link_type, field_name))
            else:
                return_dict[model] = model.get(ReverseSideLink.of_type(side_link_type, field_name))
        return return_dict

    @staticmethod
    def map_by_reverse_side_link(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                 side_link_type: type[WrappedType] | str) \
            -> dict[WrappedType | PyRecordModel, IsRecordModel]:
        """
        Take a list of record models and map them by their reverse side link. Essentially an inversion of
        map_to_reverse_side_link. If two records share the same reverse side link, an exception is thrown.
        The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper or data type name of the reverse side links. If a data type
            name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[SideLink, ModelType]. If an input model doesn't have a reverse side link of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_link: dict[RecordModel, WrappedType | PyRecordModel] = RecordHandler\
            .map_to_reverse_side_link(models, field_name, side_link_type)
        by_side_link: dict[WrappedType | PyRecordModel, RecordModel] = {}
        for record, side_link in to_side_link.items():
            if side_link is None:
                continue
            if side_link in by_side_link:
                raise SapioException(f"Side link {side_link.data_type_name} {side_link.record_id} encountered more "
                                     f"than once in models list.")
            by_side_link[side_link] = record
        return by_side_link

    @staticmethod
    def map_by_reverse_side_links(models: Iterable[IsRecordModel], field_name: FieldIdentifier,
                                  side_link_type: type[WrappedType] | str) -> dict[WrappedType | PyRecordModel, list[IsRecordModel]]:
        """
        Take a list of record models and map them by their reverse side links. Essentially an inversion of
        map_to_reverse_side_links. Input models that share a reverse side link will end up in the same list.
        The reverse side links must already be loaded.

        :param models: A list of record models.
        :param field_name: The field name on the side linked model where the side link to the given record models is
            located.
        :param side_link_type: The record model wrapper or data type name of the reverse side links. If a data type
            name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A dict[SideLink, list[ModelType]]. If an input model doesn't have reverse side links of the given type
            pointing to it, then it will not be in the resulting dictionary.
        """
        field_name: str = AliasUtil.to_data_field_name(field_name)
        to_side_links: dict[WrappedRecordModel, list[WrappedType]] = RecordHandler\
            .map_to_reverse_side_links(models, field_name, side_link_type)
        by_side_links: dict[WrappedType, list[WrappedRecordModel]] = {}
        for record, side_links in to_side_links.items():
            for side_link in side_links:
                by_side_links.setdefault(side_link, []).append(record)
        return by_side_links

    # FR-46155: Update relationship path traversing functions to be non-static and take in a wrapper type so that the
    # output can be wrapped instead of requiring the user to wrap the output.
    def get_linear_path(self, models: Iterable[IsRecordModel], path: RelationshipPath,
                        wrapper_type: type[WrappedType] | None = None) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel | None]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy must be linear (1:1 relationship between data types at every step) and the
        relationship path must already be loaded.

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use on the record at the end of the path. If not provided,
            the record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: Each record model mapped to the record at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to None.
        """
        ret_dict: dict[RecordModel, WrappedType | PyRecordModel | None] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current: PyRecordModel | None = model if isinstance(model, PyRecordModel) else model.backing_model
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if current is None:
                    break
                if direction == RelationshipNodeType.CHILD:
                    current = current.get_child_of_type(data_type)
                elif direction == RelationshipNodeType.PARENT:
                    current = current.get_parent_of_type(data_type)
                elif direction == RelationshipNodeType.ANCESTOR:
                    ancestors: list[PyRecordModel] = list(self.an_man.get_ancestors_of_type(current, data_type))
                    if not ancestors:
                        current = None
                    elif len(ancestors) > 1:
                        raise SapioException(f"Hierarchy contains multiple ancestors of type {data_type}.")
                    else:
                        current = ancestors[0]
                elif direction == RelationshipNodeType.DESCENDANT:
                    descendants: list[PyRecordModel] = list(self.an_man.get_descendant_of_type(current, data_type))
                    if not descendants:
                        current = None
                    elif len(descendants) > 1:
                        raise SapioException(f"Hierarchy contains multiple descendants of type {data_type}.")
                    else:
                        current = descendants[0]
                elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                    current = current.get_forward_side_link(node.data_field_name)
                elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                    field_name: str = node.data_field_name
                    reverse_links: list[PyRecordModel] = current.get_reverse_side_link(data_type, field_name)
                    if not reverse_links:
                        current = None
                    elif len(reverse_links) > 1:
                        raise SapioException(f"Hierarchy contains multiple reverse links of type {data_type} on field "
                                             f"{field_name}.")
                    else:
                        current = reverse_links[0]
                else:
                    raise SapioException("Unsupported path direction.")
            ret_dict.update({model: self.wrap_model(current, wrapper_type) if current else None})
        return ret_dict

    def get_branching_path(self, models: Iterable[IsRecordModel], path: RelationshipPath,
                           wrapper_type: type[WrappedType] | None = None)\
            -> dict[IsRecordModel, list[WrappedType] | list[PyRecordModel]]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy may be non-linear (1:Many relationships between data types are allowed) and the
        relationship path must already be loaded.

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use on the records at the end of the path. If not provided,
            the records will be PyRecordModels instead of WrappedRecordModels.
        :return: Each record model mapped to the records at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to an empty list.
        """
        ret_dict: dict[RecordModel, list[WrappedType] | list[PyRecordModel]] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current_search: set[PyRecordModel] = {model if isinstance(model, PyRecordModel) else model.backing_model}
            next_search: set[PyRecordModel] = set()
            # Exhaust the records at each step in the path, then use those records for the next step.
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if len(current_search) == 0:
                    break
                for search in current_search:
                    if direction == RelationshipNodeType.CHILD:
                        next_search.update(search.get_children_of_type(data_type))
                    elif direction == RelationshipNodeType.PARENT:
                        next_search.update(search.get_parents_of_type(data_type))
                    elif direction == RelationshipNodeType.ANCESTOR:
                        next_search.update(self.an_man.get_ancestors_of_type(search, data_type))
                    elif direction == RelationshipNodeType.DESCENDANT:
                        next_search.update(self.an_man.get_descendant_of_type(search, data_type))
                    elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                        side_link: RecordModel | None = search.get_forward_side_link(node.data_field_name)
                        if side_link:
                            next_search.add(side_link)
                    elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                        next_search.update(search.get_reverse_side_link(data_type, node.data_field_name))
                    else:
                        raise SapioException("Unsupported path direction.")
                current_search = next_search
                next_search = set()
            ret_dict.update({model: self.wrap_models(current_search, wrapper_type)})
        return ret_dict

    # FR-46155: Create a relationship traversing function that returns a single function at the end of the path like
    # get_linear_path but can handle branching paths in the middle of the search like get_branching_path.
    def get_flat_path(self, models: Iterable[IsRecordModel], path: RelationshipPath,
                      wrapper_type: type[WrappedType] | None = None) \
            -> dict[IsRecordModel, WrappedType | PyRecordModel | None]:
        """
        Given a relationship path, travel the path starting from the input models. Returns the record at the end of the
        path, if any. The hierarchy may be non-linear (1:Many relationships between data types are allowed) and the
        relationship path must already be loaded.

        The path is "flattened" by only following the first record at each step. Useful for traversing 1-to-Many-to-1
        relationships (e.g. a sample which is aliquoted to a number of samples, then those aliquots are pooled back
        together into a single sample).

        :param models: A list of record models.
        :param path: The relationship path to follow.
        :param wrapper_type: The record model wrapper to use on the record at the end of the path. If not provided,
            the record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: Each record model mapped to the record at the end of the path starting from itself. If the end of the
            path couldn't be reached, the record will map to None.
        """
        ret_dict: dict[RecordModel, WrappedType | PyRecordModel | None] = {}
        # PR-46832: Update path traversal to account for changes to RelationshipPath in Sapiopylib.
        path: list[RelationshipNode] = path.path
        for model in models:
            current: list[PyRecordModel] = [model if isinstance(model, PyRecordModel) else model.backing_model]
            for node in path:
                data_type: str = node.data_type_name
                direction: RelationshipNodeType = node.direction
                if len(current) == 0:
                    break
                if direction == RelationshipNodeType.CHILD:
                    current = current[0].get_children_of_type(data_type)
                elif direction == RelationshipNodeType.PARENT:
                    current = current[0].get_parents_of_type(data_type)
                elif direction == RelationshipNodeType.ANCESTOR:
                    current = list(self.an_man.get_ancestors_of_type(current[0], data_type))
                elif direction == RelationshipNodeType.DESCENDANT:
                    current = list(self.an_man.get_descendant_of_type(current[0], data_type))
                elif direction == RelationshipNodeType.FORWARD_SIDE_LINK:
                    side_link: RecordModel | None = current[0].get_forward_side_link(node.data_field_name)
                    current = [side_link] if side_link else []
                elif direction == RelationshipNodeType.REVERSE_SIDE_LINK:
                    current = current[0].get_reverse_side_link(data_type, node.data_field_name)
                else:
                    raise SapioException("Unsupported path direction.")
            ret_dict.update({model: self.wrap_model(current[0], wrapper_type) if current else None})
        return ret_dict

    def __find_model(self, wrapper_type: type[WrappedType] | str, primary_identifier: str, id_value: FieldValue,
                     secondary_identifiers: FieldIdentifierMap | None = None) -> WrappedType | PyRecordModel | None:
        """
        Find a record from the system that matches the given field values. The primary identifier and value is used
        to query for the record, then the secondary identifiers may be optionally provided to further filter the
        returned results. If no record is found with these filters, returns None.
        """
        # Query for all records that match the primary identifier.
        results: list[WrappedType] | list[PyRecordModel] = self.query_models(wrapper_type, primary_identifier,
                                                                             [id_value])

        # Find the one record, if any, that matches the secondary identifiers.
        unique_record: WrappedType | PyRecordModel | None = None
        for result in results:
            matches_all: bool = True
            for field, value in secondary_identifiers.items():
                if result.get_field_value(field) != value:
                    matches_all = False
                    break
            if matches_all:
                # If a previous record in the results already matched all identifiers, then throw an exception.
                if unique_record is not None:
                    raise SapioException(f"More than one record of type {AliasUtil.to_data_type_name(wrapper_type)} "
                                         f"encountered in system that matches all provided identifiers.")
                unique_record = result
        return unique_record

    @staticmethod
    def __verify_data_type(record: DataRecord | PyRecordModel, wrapper_type: type[WrappedType]) -> None:
        """
        Throw an exception if the data type of the given record and wrapper don't match.
        """
        model_type: str = wrapper_type.get_wrapper_data_type_name()
        record_type: str = AliasUtil.to_data_type_name(record)
        # Account for ELN data type records.
        if ElnBaseDataType.is_eln_type(record_type):
            record_type = ElnBaseDataType.get_base_type(record_type).data_type_name
        if record_type != model_type:
            raise SapioException(f"Data record of type {record_type} cannot be wrapped by the record model wrapper "
                                 f"of type {model_type}")

    @staticmethod
    def _spoof_child_load(model: RecordModel, child: RecordModel) -> None:
        """
        Spoof the loading of a child record on a record model. This is useful for when you have records that you know
        are related but didn't use the relationship manager to load the relationship, which would make a webservice
        call.
        """
        RecordHandler._spoof_children_load(model, [child])

    @staticmethod
    def _spoof_children_load(model: RecordModel, children: list[RecordModel]) -> None:
        """
        Spoof the loading of child records on a record model. This is useful for when you have records that you know
        are related but didn't use the relationship manager to load the relationship, which would make a webservice
        """
        model: PyRecordModel = RecordModelInstanceManager.unwrap(model)
        child_dt: str = AliasUtil.to_singular_data_type_name(children)
        # noinspection PyProtectedMember
        model._mark_children_loaded(child_dt, RecordModelInstanceManager.unwrap_list(children))

    @staticmethod
    def _spoof_parent_load(model: RecordModel, parent: RecordModel) -> None:
        """
        Spoof the loading of a parent record on a record model. This is useful for when you have records that you know
        are related but didn't use the relationship manager to load the relationship, which would make a webservice
        """
        RecordHandler._spoof_parents_load(model, [parent])

    @staticmethod
    def _spoof_parents_load(model: RecordModel, parents: list[RecordModel]) -> None:
        """
        Spoof the loading of parent records on a record model. This is useful for when you have records that you know
        are related but didn't use the relationship manager to load the relationship, which would make a webservice
        """
        model: PyRecordModel = RecordModelInstanceManager.unwrap(model)
        parent_dt: str = AliasUtil.to_singular_data_type_name(parents)
        # noinspection PyProtectedMember
        model._mark_children_loaded(parent_dt, RecordModelInstanceManager.unwrap_list(parents))
