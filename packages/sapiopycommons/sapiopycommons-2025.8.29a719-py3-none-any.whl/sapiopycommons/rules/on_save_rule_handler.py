from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.aliases import FieldMap, DataTypeIdentifier, AliasUtil
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class OnSaveRuleHandler:
    """
    A class which helps with the parsing and navigation of the on save rule result map of a webhook context.
    """
    _context: SapioWebhookContext
    """The context that this handler is working from."""

    _rec_handler: RecordHandler
    """The record handler, used for wrapping the data records as record models."""

    # Reformatted and cached version of the Velox on save rule result map for easier handling.
    _records: dict[str, set[DataRecord]]
    """A mapping of data type to the set of data records from the context that match that data type."""
    _base_id_to_records: dict[int, dict[str, set[DataRecord]]]
    """A mapping of record IDs of records in the context.data_record_list to the sets of data records related to that
    record, each set of records being mapped by its data type."""
    _field_maps: dict[str, dict[int, FieldMap]]
    """A mapping of data type to the field maps from the context that match that data type. In order to prevent
    duplicate field maps, each field map is in a dict keyed by the RecordId field in the field map, since field maps
    are just dictionaries and dictionaries aren't hashable and therefore can't go in a set."""
    _base_id_to_field_maps: dict[int, dict[str, dict[int, FieldMap]]]
    """A mapping of record IDs of records in the context.data_record_list to the field maps related to that
    record, each grouping of field maps being mapped by its data type."""

    __instances: WeakValueDictionary[SapioUser, OnSaveRuleHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: SapioWebhookContext):
        if context.velox_on_save_result_map is None:
            raise SapioException("No Velox on save rule result map in context for OnSaveRuleHandler to parse.")
        user = context if isinstance(context, SapioUser) else context.user
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, context: SapioWebhookContext):
        if self.__initialized:
            return
        self.__initialized = True

        if context.velox_on_save_result_map is None:
            raise SapioException("No Velox on save rule result map in context for OnSaveRuleHandler to parse.")
        self._context = context
        self._rec_handler = RecordHandler(context)
        self.__cache_records()

    def __cache_records(self) -> None:
        """
        Cache the records from the context into dictionaries. Two caches are created. One cache maps the data type of
        each record to a set of all records of that data type. The other cache maps the record ID that the records relate
        to with another dict that maps the data types to the records of that type. Doesn't cache any relationship info.
        """
        self._records = {}
        self._base_id_to_records = {}
        # Each record ID in the context has a list of results for that record.
        for record_id, rule_results in self._context.velox_on_save_result_map.items():
            # Keep track of the records for this specific record ID.
            id_dict: dict[str, set[DataRecord]] = {}
            # The list of results for a record consist of a list of data records and a VeloxType that specifies
            # how the records in the list relate to the main record.
            for record_result in rule_results:
                # For the purposes of caching, we don't care about the VeloxType.
                for record in record_result.data_records:
                    # Get the data type of this record. If this is an ELN type, ignore the digits.
                    data_type: str = record.data_type_name
                    # PR-46331: Ensure that all ELN types are converted to their base data type name.
                    if ElnBaseDataType.is_eln_type(data_type):
                        data_type = ElnBaseDataType.get_base_type(data_type).data_type_name
                    # Update the list of records of this type that exist so far globally.
                    self._records.setdefault(data_type, set()).add(record)
                    # Do the same for the list of records of this type that relate to this record ID.
                    id_dict.setdefault(data_type, set()).add(record)
            # Update the related records for this record ID.
            self._base_id_to_records.update({record_id: id_dict})

        self._field_maps = {}
        self._base_id_to_field_maps = {}
        # Repeat the same thing for the field map results.
        for record_id, rule_results in self._context.velox_on_save_field_map_result_map.items():
            id_dict: dict[str, dict[int, FieldMap]] = {}
            for record_result in rule_results:
                data_type: str = record_result.velox_type_pojo.data_type_name
                if ElnBaseDataType.is_eln_type(data_type):
                    data_type = ElnBaseDataType.get_base_type(data_type).data_type_name
                for field_map in record_result.field_map_list:
                    rec_id: int = field_map.get("RecordId")
                    self._field_maps.setdefault(data_type, {}).update({rec_id: field_map})
                    id_dict.setdefault(data_type, {}).update({rec_id: field_map})
            self._base_id_to_field_maps.update({record_id: id_dict})

    def get_base_record_ids(self) -> list[int]:
        """
        :return: A list of the record IDs that may be used with the get_records and get_models functions. These are the
            record IDs to the records that caused the rule to trigger.
        """
        return list(self._base_id_to_records.keys())

    def get_field_maps_base_record_ids(self) -> list[int]:
        """
        :return: A list of the record IDs that may be used with the get_field_maps function. These are the
            record IDs to the records that caused the rule to trigger.
        """
        return list(self._base_id_to_field_maps.keys())

    # CR-47529: Add info about HVDT behavior to the docstring of these functions.
    def get_records(self, data_type: DataTypeIdentifier, record_id: int | None = None) -> list[DataRecord]:
        """
        Get records from the cached context with the given data type. Capable of being filtered to searching within
        the context of a record ID. If the given data type or record ID does not exist in the context,
        returns an empty list.

        Note that if you are attempting to retrieve record that are high volume data types and are receiving nothing,
        the HVDTs may have been sent as field maps. Consider using the get_field_maps function if this occurs.

        :param data_type: The data type of the records to return.
        :param record_id: The record ID of the base record to search from. If None, returns the records that match the
            data type from every ID. If an ID is provided, but it does not exist in the context, returns an empty list.
        :return: The records from the context that match the input parameters.
        """
        data_type: str = AliasUtil.to_data_type_name(data_type)
        records: dict[str, set[DataRecord]] = self._base_id_to_records.get(record_id, {}) if record_id else self._records
        return list(records.get(data_type, []))

    # FR-46701: Add functions to the rule handlers for accessing the field maps of inaccessible records in the context.
    def get_field_maps(self, data_type: DataTypeIdentifier, record_id: int | None = None) -> list[FieldMap]:
        """
        Get field maps from the cached context with the given data type. Capable of being filtered to searching within
        the context of a record ID. If the given data type or record ID does not exist in the context,
        returns an empty list.

        Field maps will only exist in the context if the data record that the fields are from is no longer accessible
        to the user. This can occur because the data record was deleted, or because the user does not have access to the
        record due to ACL. This can also occur under certain circumstances if the records are HVDTs.

        :param data_type: The data type of the field maps to return.
        :param record_id: The record ID of the base record to search from. If None, returns the field maps that match
            the data type from every ID. If an ID is provided, but it does not exist in the context, returns an empty
            list.
        :return: The field maps from the context that match the input parameters.
        """
        data_type: str = AliasUtil.to_data_type_name(data_type)
        field_maps: dict[str, dict[int, FieldMap]] = self._base_id_to_field_maps.get(record_id, {}) if record_id else self._field_maps
        return list(field_maps.get(data_type, {}).values())

    # CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
    def get_models(self, wrapper_type: type[WrappedType] | str, record_id: int | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Get records from the cached context with the given data type. Capable of being filtered to searching within
        the context of a record ID. If the given data type or record ID does not exist in the context,
        returns an empty list.

        Note that if you are attempting to retrieve record that are high volume data types and are receiving nothing,
        the HVDTs may have been sent as field maps. Consider using the get_field_maps function if this occurs.

        :param wrapper_type: The record model wrapper or data type name of the record to get from the context.
        :param record_id: The record ID of the base record to search from. If None, returns the records that match the
            data type from ID. If an ID is provided, but it does not exist in the context, returns an empty list.
        :return: The record models from the context that match the input parameters. If a data type name was used
            instead of a model wrapper, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        """
        dt: str = AliasUtil.to_data_type_name(wrapper_type)
        return self._rec_handler.wrap_models(self.get_records(dt, record_id), wrapper_type)
