from sapiopylib.rest.utils.Protocols import ElnEntryStep
from sapiopylib.rest.utils.plates.PlatingUtils import PlateLocation
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.datatype.data_fields import PlateDesignerWellElementFields
from sapiopycommons.eln.experiment_handler import ExperimentHandler
from sapiopycommons.eln.experiment_tags import PLATE_IDS_TAG
from sapiopycommons.general.aliases import RecordIdentifier, AliasUtil, RecordModel, FieldValue
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler

# Shorthands for longer type names.
WellElement = PlateDesignerWellElementFields


# FR-47486: Change the PlateDesignerEntry class to extend ElnEntryStep instead of containing one.
class PlateDesignerEntry(ElnEntryStep):
    """
    A wrapper for 3D plate designer entries in experiments, providing functions for common actions when dealing with
    such entries.
    """
    _exp_handler: ExperimentHandler
    _rec_handler: RecordHandler
    _plates: list[RecordModel] | None
    _aliquots: list[RecordModel] | None
    _sources: list[RecordModel] | None
    _designer_elements: list[RecordModel] | None
    _designer_elements_by_plate: dict[int, list[RecordModel]] | None
    _plate_ids: list[int] | None

    def __init__(self, step: ElnEntryStep, exp_handler: ExperimentHandler):
        """
        :param step: The ElnEntryStep that is the 3D plate designer entry.
        :param exp_handler: An ExperimentHandler for the experiment that this entry comes from.
        """
        super().__init__(exp_handler.protocol, step.eln_entry)
        self._exp_handler = exp_handler
        self._rec_handler = RecordHandler(exp_handler.user)
        self._plates = None
        self._aliquots = None
        self._sources = None
        self._designer_elements = None
        self._designer_elements_by_plate = None
        self._plate_ids = None

    @property
    def step(self) -> ElnEntryStep:
        return self

    def clear_cache(self) -> None:
        """
        Clear the caches for the plates and plate designer well elements in this plate designer entry. This will require
        a new webservice call to get the plates and designer elements the next time they are requested.
        """
        self._plates = None
        self._designer_elements = None
        self._designer_elements_by_plate = None

    # CR-47491: Support not providing a wrapper type to receive PyRecordModels instead of WrappedRecordModels.
    def get_plates(self, wrapper_type: type[WrappedType] | None = None) -> list[WrappedType] | list[PyRecordModel]:
        """
        Get the plates that are in the designer entry.

        Makes a webservice query to get the plates from the entry and caches the result for future calls. This cache
        will be invalidated if a set_plates or add_plates call is made, requiring a new webservice call the next time
        this function is called.

        :param wrapper_type: The record model wrapper to use on the plates. If not provided, the returned records will
            be PyRecordModels instead of WrappedRecordModels.
        :return: A list of the plates in the designer entry.
        """
        if self._plates is not None:
            return self._plates
        if wrapper_type is None:
            wrapper_type = "Plate"
        self._plates = self._rec_handler.query_models_by_id(wrapper_type, self.__get_plate_ids())
        return self._plates

    def set_plates(self, plates: list[RecordIdentifier]) -> None:
        """
        Set the plates that are in the plate designer entry. This removes any existing plates that are in the entry
        but not in the given list.

        Makes a webservice call to update the plate designer entry's entry options.

        :param plates: The plates to set the plate designer entry with.
        """
        record_ids: list[int] = AliasUtil.to_record_ids(plates)
        self.__set_plate_ids(record_ids)

    def add_plates(self, plates: list[RecordIdentifier]) -> None:
        """
        Add the given plates to the plate designer entry. This preserves any existing plates that are in the entry.

        Makes a webservice call to update the plate designer entry's entry options.

        :param plates: The plates to add to the plate designer entry.
        """
        record_ids: list[int] = AliasUtil.to_record_ids(plates)
        self.__set_plate_ids(self.__get_plate_ids() + record_ids)

    def get_sources(self, wrapper_type: type[WrappedType] | str) -> list[WrappedType] | list[PyRecordModel]:
        """
        Get the source records that were used to populate the plate designer entry's sample table. This looks for the
        entries that the plate designer entry is implicitly dependent upon and gets their records if they match the
        data type name of the given wrapper.

        Makes a webservice call to retrieve the dependent entries if the experiment handler had not already cached it.
        Makes another webservice call to get the records from the dependent entry and caches them for future calls.

        :param wrapper_type: The record model wrapper or data type name of the records to retrieve. If a data type name
            is provided, then the returned records will be PyRecordModels instead of WrappedRecordModels.
        :return: A list of the source records that populate the plate designer entry's sample table.
        """
        if self._sources is not None:
            return self._sources

        records: list[WrappedType] = []
        dependent_ids: list[int] = self.step.eln_entry.related_entry_id_set
        for step in self._exp_handler.get_all_steps(wrapper_type):
            if step.get_id() in dependent_ids:
                records.extend(self._exp_handler.get_step_models(step, wrapper_type))

        self._sources = records
        return self._sources

    def get_aliquots(self, wrapper_type: type[WrappedType] | None = None) -> list[WrappedType] | list[PyRecordModel]:
        """
        Get the aliquots that were created from this plate designer entry upon its submission.

        Makes a webservice call to retrieve the aliquots from the plate designer entry and caches them for future calls.

        :param wrapper_type: The record model wrapper to use. If not provided, the returned records will be
            PyRecordModels instead of WrappedRecordModels.
        :return: A list of the aliquots created by the plate designer entry.
        """
        if not self._exp_handler.step_is_submitted(self.step):
            raise SapioException("The plate designer entry must be submitted before its aliquots can be retrieved.")
        if self._aliquots is not None:
            return self._aliquots
        self._aliquots = self._exp_handler.get_step_models(self.step, wrapper_type)
        return self._aliquots

    def get_plate_designer_well_elements(self, wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Get the plate designer well elements for the plates in the plate designer entry. These are the records in the
        system that determine how wells are displayed on each plate in the entry.

        Makes a webservice call to get the plate designer well elements of the entry and caches them for future calls.
        This cache will be invalidated if a set_plates or add_plates call is made, requiring a new webservice call the
        next time this function is called.

        :param wrapper_type: The record model wrapper to use. If not provided, the returned records will be
            PyRecordModels instead of WrappedRecordModels.
        :return: A list of the plate designer well elements in the designer entry.
        """
        if self._designer_elements is not None:
            return self._designer_elements
        if wrapper_type is None:
            wrapper_type: str = WellElement.DATA_TYPE_NAME
        self._designer_elements = self._rec_handler.query_models(wrapper_type,
                                                                 WellElement.PLATE_RECORD_ID__FIELD,
                                                                 self.__get_plate_ids())
        if self._designer_elements_by_plate is None:
            self._designer_elements_by_plate = {}
        self._designer_elements_by_plate.clear()
        for element in self._designer_elements:
            plate_id: int = element.get_field_value(WellElement.PLATE_RECORD_ID__FIELD.field_name)
            self._designer_elements_by_plate.setdefault(plate_id, []).append(element)
        return self._designer_elements

    def get_well_elements_by_plate(self, plate: RecordIdentifier, wrapper_type: type[WrappedType] | None = None) \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Get the plate designer well elements for the given plate in the plate designer entry. These are the records in
        the system that determine how wells are displayed on the plate in the entry.

        Makes a webservice call to get the plate designer well elements of the entry and caches them for future calls.
        This cache will be invalidated if a set_plates or add_plates call is made, requiring a new webservice call the
        next time this function is called.

        :param plate: The plate to get the well elements for.
        :param wrapper_type: The record model wrapper to use. If not provided, the returned records will be
            PyRecordModels instead of WrappedRecordModels.
        :return: A list of the plate designer well elements in the designer entry.
        """
        plate: int = AliasUtil.to_record_id(plate)
        if plate not in self.__get_plate_ids():
            raise SapioException(f"Plate record ID {plate} is not in this plate designer entry.")
        if self._designer_elements_by_plate is None:
            self.get_plate_designer_well_elements(wrapper_type)
        return self._designer_elements_by_plate[plate]

    def create_well_element(self, sample: RecordModel, plate: RecordModel, location: PlateLocation | None = None,
                            layer: int = 1, wrapper_type: type[WrappedType] | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Create a new plate designer well element for the input sample and plate. A record model manager store and commit
        must be called to save this new well element to the server.

        :param sample: The sample that the element is for. Must exist in the system (i.e. have a >0 record ID).
        :param plate: The plate that the element is for. Must exist in the system (i.e. have a >0 record ID).
        :param location: The location of the well element. If not provided, the row and column position fields of the
            sample will be used.
        :param layer: The layer that the well element is on.
        :param wrapper_type: The record model wrapper to use for the plate designer well element. If not provided, the
            returned record will be a PyRecordModel instead of a WrappedRecordModel.
        :return: The newly created PlateDesignerWellElementModel.
        """
        # Confirm that we can actually make a designer element for the input records.
        if AliasUtil.to_record_id(sample) <= 0:
            raise SapioException("Cannot create plate designer well element for sample without a record ID.")
        if AliasUtil.to_record_id(plate) <= 0:
            raise SapioException("Cannot create plate designer well element for plate without a record ID.")
        if AliasUtil.to_data_type_name(sample) != "Sample":
            raise SapioException("Sample record must be of type Sample.")
        if AliasUtil.to_data_type_name(plate) != "Plate":
            raise SapioException("Plate record must be of type Plate.")
        if layer < 1:
            raise SapioException("Layer must be greater than 0.")

        dt: type[WrappedType] | str = wrapper_type if wrapper_type else WellElement.DATA_TYPE_NAME
        plate_id: int = AliasUtil.to_record_id(plate)
        fields: dict[str, FieldValue] = {
            WellElement.SOURCE_RECORD_ID__FIELD: AliasUtil.to_record_id(sample),
            WellElement.PLATE_RECORD_ID__FIELD: plate_id,
            WellElement.ROW_POSITION__FIELD: location.row_pos if location else sample.get_field_value("RowPosition"),
            WellElement.COL_POSITION__FIELD: str(location.col_pos) if location else sample.get_field_value("ColPosition"),
            WellElement.SOURCE_DATA_TYPE_NAME__FIELD: "Sample",
            WellElement.LAYER__FIELD: layer,
        }
        element = self._rec_handler.add_models_with_data(dt, [fields])[0]

        # Add the new element to the cache.
        if self._designer_elements is not None:
            self._designer_elements.append(element)
        if self._designer_elements_by_plate is not None and plate_id in self._designer_elements_by_plate:
            self._designer_elements_by_plate.setdefault(plate_id, []).append(element)
        return element

    def __get_plate_ids(self) -> list[int]:
        if self._plate_ids is not None:
            return self._plate_ids
        id_tag: str = self._exp_handler.get_step_option(self.step, PLATE_IDS_TAG)
        if not id_tag:
            raise SapioException("No plates in the plate designer entry")
        self._plate_ids = [int(x) for x in id_tag.split(",")]
        return self._plate_ids

    def __set_plate_ids(self, record_ids: list[int]) -> None:
        record_ids.sort()
        self._exp_handler.add_step_options(self.step, {PLATE_IDS_TAG: ",".join([str(x) for x in record_ids])})
        self._plate_ids = record_ids
        # The plates and designer elements caches have been invalidated.
        self.clear_cache()
