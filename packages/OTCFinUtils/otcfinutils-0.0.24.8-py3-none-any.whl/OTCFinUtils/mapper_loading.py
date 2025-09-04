from typing import Any
import json
from OTCFinUtils.dataverse_handler import DVHandler
from OTCFinUtils.data_structs import (
    IDParams,
    APIParams,
    Lookup,
    EntityLookups,
)

def _extract_key_api_params(dvh: DVHandler, id_params: IDParams) -> APIParams:
    """
    Helper function for creating appropriate DV API parameters
    from the provided id parameters.
    """
    conditions = " and ".join(id_params.conditions)
    url = dvh._create_url(
        domain=id_params.table,
        select=id_params.id_column,
        filter=conditions,
    )
    return APIParams(url=url, method="GET")


def _extract_batch_response_objects(batch_response: str) -> list:
    """
    A general helper function. Can be used for any type of batch response.
    """
    try:
        objects = []
        responses = batch_response.split("--batchresponse")
        responses = responses[1:-1]
        for response in responses:
            start_index = response.find('{')
            end_index = response.rfind('}') + 1
            json_string = response[start_index:end_index]
            parsed_json = json.loads(json_string)
            objects.append(parsed_json["value"])
        return objects
    
    except Exception as exception:
        raise Exception(
            f"Error while extracting batch response objects. "
            f"Error: {exception}. "
            f"Response: {batch_response}."
        )


def _extract_object_ids(objects: list, id_params_buffer: list[IDParams]) -> list[str]:
    """
    Returns a list of IDs from a list of json response objects.
    Uses the id-parameters-buffer to check the form of the object.
    
    If it's a lookup-key, the id will be in a different location,
    than if it were a regular key.
    
    If the entity is new, return None.
    """
    ids = []
    for object, id_params in zip(objects, id_params_buffer):
        if len(object):
            data = object[0]
        else:
            ids.append(None)
            continue
        
        # This means we have a regular key and the entity exists in the DV
        if id_params.id_column in data:
            id = data[id_params.id_column]
        # This means we have a regular key and the entity is new
        else:
            id = None
        
        ids.append(id)
    return ids


def _extract_object_lookups(objects: list, lookup_params: list[list[IDParams]]) -> list[EntityLookups]:
    """
    Helper function for getting the lookups from the batch responses.
    """
    lookups = []
    from_index = 0
    
    for entity_lookup_params in lookup_params:
        lookup_number = len(entity_lookup_params)
        to_index = from_index + lookup_number
        entity_objects = objects[from_index : to_index]
        entity_lookups = _extract_curr_object_lookups(entity_objects, entity_lookup_params)
        lookups.append(entity_lookups)
        from_index += lookup_number

    return lookups


def _extract_curr_object_lookups(entity_objects: list, entity_params: list[IDParams]) -> list[Lookup]:
    """
    Helper function. One entity can have multiple lookups. Because of this,
    it's better to group this logic into a separate function.
    """
    if len(entity_objects) != len(entity_params):
        raise RuntimeError("The lenghts of the objects and parameters do not match.")

    entity_lookups = []
    for object, params in zip(entity_objects, entity_params):
        
        if not len(object):
            lookup = Lookup(params.bind_column, params.table, id=None)
        else:
            data = object[0]
            id = data[params.id_column]
            lookup = Lookup(params.bind_column, params.table, id)
        entity_lookups.append(lookup)
    
    return entity_lookups


def get_buffer_lookups(dvh: DVHandler, lookup_params_buffer: list[list[IDParams]]) -> list[EntityLookups]:
    """
    Uses the provided buffer to get all of the ids of the lookups.
    We need the ids of the lookups in order to properly upsert the
    data to DV.
    """
    batch_params: list[APIParams] = []
    
    for entity_lookup_params in lookup_params_buffer:
        for lookup_params in entity_lookup_params:
            api_params = _extract_key_api_params(dvh, lookup_params)
            batch_params.append(api_params)
    
    batch_response = dvh._execute_batch_operation(batch_params)
    response_objects = _extract_batch_response_objects(batch_response)
    result = _extract_object_lookups(response_objects, lookup_params_buffer)
    
    return result


def get_buffer_ids(dvh: DVHandler, id_params_buffer: list[IDParams]) -> list[str]:
    """
    Uses the provided buffer to get all of the ids of the entities.
    We need the ids of the entities in order to properly upsert the
    data to DV.
    """
    batch_params: list[APIParams] = []
    
    for id_params in id_params_buffer:
        api_params = _extract_key_api_params(dvh, id_params)
        batch_params.append(api_params)
    
    batch_response = dvh._execute_batch_operation(batch_params)
    response_objects = _extract_batch_response_objects(batch_response)
    
    result = _extract_object_ids(response_objects, id_params_buffer)
    
    return result