from sapiopycommons.general.aliases import SapioRecord
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.utils.MultiMap import SetMultimap

# FR-47421 Added module

def create_aliquot_for_samples(parent_sample_to_num_aliquots_map: dict[SapioRecord, int], user: SapioUser) -> SetMultimap[SapioRecord, int]:
    """"
    Ask server to create aliquot records for provided sample parent records.
    :param parent_sample_to_num_aliquots_map: The dictionary containing (parent sample record) -> (number of aliquots to create) mapping.
    :return: The dictionary containing (parent sample record) -> (list of new aliquot record ids) mapping.
    """
    # throw error if at least one record id is blank
    has_negative_record_ids = any([record.record_id < 0 for record in parent_sample_to_num_aliquots_map.keys()])
    if has_negative_record_ids:
        raise ValueError("At least one record requested for aliquot has a negative record ID. "
                         "You should have stored record model changes first.")
    has_blank_record_ids = any([record.record_id is None for record in parent_sample_to_num_aliquots_map.keys()])
    if has_blank_record_ids:
        raise ValueError("At least one record requested for aliquot does not currently have a record ID.")
    record_id_to_sapio_record_map = {record.record_id: record for record in parent_sample_to_num_aliquots_map.keys()}
    parent_record_id_to_num_aliquots_map = {record.record_id: num_aliquots for record, num_aliquots in parent_sample_to_num_aliquots_map.items()}
    aliquot_result: SetMultimap[int, int] = create_aliquot_for_samples_record_ids(parent_record_id_to_num_aliquots_map, user)
    ret: SetMultimap[SapioRecord, int] = SetMultimap()
    for parent_record_id in aliquot_result.keys():
        parent_record = record_id_to_sapio_record_map[parent_record_id]
        for aliquot_record_id in aliquot_result.get(parent_record_id):
            ret.put(parent_record, aliquot_record_id)
    return ret


def create_aliquot_for_samples_record_ids(parent_record_id_to_num_aliquots_map: dict[int, int], user: SapioUser) -> SetMultimap[int, int]:
    """
    Ask the server to create aliquot records for the provided sample record IDs.
    :param sample_record_id_list: The dictionary containing (parent sample record id) -> (number of aliquots to create) mapping.
    :return: The dictionary containing (parent sample record id) -> (list of new aliquot record ids) mapping.
    """
    if not parent_record_id_to_num_aliquots_map:
        return SetMultimap()
    endpoint_path = 'sample/aliquot'
    response = user.plugin_put(endpoint_path, payload=parent_record_id_to_num_aliquots_map)
    user.raise_for_status(response)
    response_map: dict[int, list[int]] = response.json()
    ret: SetMultimap[int, int] = SetMultimap()
    for parent_record_id, aliquot_record_ids in response_map.items():
        for aliquot_record_id in aliquot_record_ids:
            ret.put(int(parent_record_id), int(aliquot_record_id))
    return ret