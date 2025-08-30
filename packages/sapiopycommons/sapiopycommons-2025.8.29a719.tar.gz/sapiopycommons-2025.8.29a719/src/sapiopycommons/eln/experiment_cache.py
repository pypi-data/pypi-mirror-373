from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.eln.ElnExperiment import ElnTemplate, TemplateExperimentQuery
from sapiopylib.rest.pojo.eln.SapioELNEnums import ElnBaseDataType
from sapiopylib.rest.pojo.eln.field_set import ElnFieldSetInfo
from sapiopylib.rest.pojo.eln.protocol_template import ProtocolTemplateInfo, ProtocolTemplateQuery

from sapiopycommons.general.aliases import UserIdentifier, AliasUtil
from sapiopycommons.general.exceptions import SapioException


# FR-47530: Created a class that caches experiment template and predefined field information.
class ExperimentCacheManager:
    """
    A class to manage the caching of experiment-related information.
    """
    user: SapioUser
    eln_man: ElnManager

    _templates: list[ElnTemplate]
    """A list of experiment templates. Only cached when first accessed."""
    _protocols: list[ProtocolTemplateInfo]
    """A list of protocol templates. Only cached when first accessed."""
    _field_sets: dict[str, ElnFieldSetInfo]
    """A dictionary of field set name to field set. Only cached when first accessed."""
    _field_set_fields: dict[int, list[AbstractVeloxFieldDefinition]]
    """A dictionary of field set ID to field definitions. Only cached when first accessed."""
    _predefined_fields: dict[str, dict[str, AbstractVeloxFieldDefinition]]
    """A dictionary of ELN data type name to predefined field definitions. Only cached when first accessed."""

    __instances: WeakValueDictionary[SapioUser, ExperimentCacheManager] = WeakValueDictionary()
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
        self.eln_man = ElnManager(self.user)

        self._field_set_fields = {}
        self._predefined_fields = {}

    def get_experiment_template(self, name: str, active: bool = True, version: int | None = None,
                                first_match: bool = False, public: bool | None = True) -> ElnTemplate:
        """
        Get the experiment template with the given information.

        :param name: The name of the template.
        :param active: Whether the template is marked as active.
        :param version: The version of the template to get. If None, the latest version will be returned.
        :param first_match: If true, returns the first match found. If false, raises an exception.
        :param public: Whether the template is public. If true, only pubic templates will be queried. If false, only
            private templates will be queried. If None, both public and private templates will be queried. Non-public
            templates do not have a version number, so this will always fail if public is false and a version number is
            provided.
        :return: The experiment template with the given information.
        """
        if not hasattr(self, "_templates"):
            query = TemplateExperimentQuery()
            query.active_templates_only = False
            query.latest_version_only = False
            self._templates = self.eln_man.get_template_experiment_list(query)
        return self._find_template(self._templates, name, active, version, first_match, public)


    def get_protocol_template(self, name: str, active: bool = True, version: int | None = None,
                              first_match: bool = False, public: bool | None = True) -> ProtocolTemplateInfo:
        """
        Get the protocol template with the given information. Will throw an exception if multiple templates match
        the given information.

        :param name: The name of the template.
        :param active: Whether the template is marked as active.
        :param version: The version of the template to get. If None, the latest version will be returned.
        :param first_match: If true, returns the first match found. If false, raises an exception.
        :param public: Whether the template is public. If true, only pubic templates will be queried. If false, only
            private templates will be queried. If None, both public and private templates will be queried. Non-public
            templates do not have a version number, so this will always fail if public is false and a version number is
            provided.
        :return: The protocol template with the given information.
        """
        if not hasattr(self, "_protocols"):
            query = ProtocolTemplateQuery()
            query.active_templates_only = False
            query.latest_version_only = False
            self._protocols = self.eln_man.get_protocol_template_info_list(query)
        return self._find_template(self._protocols, name, active, version, first_match, public)

    @staticmethod
    def _find_template(templates: list[ElnTemplate] | list[ProtocolTemplateInfo], name: str, active: bool,
                       version: int, first_match: bool, public: bool | None) -> ElnTemplate | ProtocolTemplateInfo:
        """
        Find the experiment or protocol template with the given information.
        """
        matches = []
        for template in templates:
            if template.template_name != name:
                continue
            if template.active != active:
                continue
            if version is not None and template.template_version != version:
                continue
            if public is True and template.template_version is None:
                continue
            if public is False and template.template_version is not None:
                continue
            matches.append(template)
        if not matches:
            raise SapioException(f"No template with the name \"{name}\"" +
                                 ("" if version is None else f" and the version {version}") +
                                 f" found.")
        # Only filter for the max version number if any of the matches actually have a version number.
        versioned_matches = [x for x in matches if x.template_version is not None]
        if version is None and versioned_matches:
            return max(versioned_matches, key=lambda x: x.template_version)
        if len(matches) > 1 and not first_match:
            raise SapioException(f"Multiple templates with the name \"{name}\" found. Consider setting first_match to "
                                 f"true, or restrict your search criteria further.")
        return matches[0]

    def get_predefined_field(self, field_name: str, data_type: ElnBaseDataType) -> AbstractVeloxFieldDefinition:
        """
        Get the predefined field of the given name for the given ELN data type.

        :param field_name: The name of the field.
        :param data_type: The ELN data type of the field.
        :return: The predefined field of the given name for the given ELN data type.
        """
        return self.get_predefined_fields(data_type)[field_name]

    def get_predefined_fields(self, data_type: ElnBaseDataType) -> dict[str, AbstractVeloxFieldDefinition]:
        """
        Get the predefined fields for the given ELN data type.

        :param data_type: The ELN data type to get the predefined fields for.
        :return: A dictionary of field name to field definition for the given ELN data type.
        """
        if data_type.data_type_name not in self._predefined_fields:
            fields: list[AbstractVeloxFieldDefinition] = self.eln_man.get_predefined_fields(data_type)
            self._predefined_fields[data_type.data_type_name] = {x.data_field_name: x for x in fields}
        return self._predefined_fields[data_type.data_type_name]

    def get_field_set(self, name: str) -> ElnFieldSetInfo:
        """
        Get the field set with the given name.

        :param name: The name of the field set.
        :return: The field set with the given name.
        """
        if not hasattr(self, "_field_sets"):
            self._field_sets = {x.field_set_name: x for x in self.eln_man.get_field_set_info_list()}
        return self._field_sets[name]

    def get_field_set_fields(self, field_set: ElnFieldSetInfo | int) -> list[AbstractVeloxFieldDefinition]:
        """
        Get the fields of the given field set.

        :param field_set: The field set to get the fields from. Can be either an ElnFieldSetInfo object or an integer
            for the set ID.
        :return: The fields of the given field set.
        """
        field_set: int = field_set if isinstance(field_set, int) else field_set.field_set_id
        if field_set in self._field_set_fields:
            return self._field_set_fields[field_set]
        self._field_set_fields[field_set] = self.eln_man.get_predefined_fields_from_field_set_id(field_set)
        return self._field_set_fields[field_set]
