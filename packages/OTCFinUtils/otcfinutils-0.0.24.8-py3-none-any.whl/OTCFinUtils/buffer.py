from OTCFinUtils.data_structs import (
    EntityKeyLookupParams, 
    EntityLookupParams, 
    IDParams,
)


class Buffer:
    def __init__(self) -> None:
        """
        Buffers for temporarily storing entity information.
        Need to use them for the batch reading / writing operations.
        """
        self.entity_data:                dict = dict()
        self.entity_id_params:           IDParams = IDParams()
        self.entity_lookup_params:       dict[str, IDParams] = dict()
        self.entity_key_lookup_params:   EntityKeyLookupParams = dict()

        """
        Buffers for temporarily storing information for all entities in a category.
        Need to use them for the batch reading / writing operations.
        """
        self.category_data:              list[dict] = []
        self.category_id_params:         list[IDParams] = []
        self.category_lookup_params:     list[EntityLookupParams] = []
        self.category_key_lookup_params: list[EntityKeyLookupParams] = []


    def _load_id_params_buffer(self) -> None:
        """
        Loads the buffer for the entity to the buffer for the category.
        This buffer is used for a batch query for the ids of the entities.
        Resets the entity buffer.
        """
        self.category_id_params.append(self.entity_id_params)
        self.entity_id_params = IDParams()


    def _load_data_buffer(self) -> None:
        """
        Loads the buffer for the entity to the buffer for the category.
        This is the buffer that will be bulk-upserted in the end.
        Resets the entity buffer.
        """
        self.category_data.append(self.entity_data)
        self.entity_data = dict()


    def _load_lookup_params_buffer(self) -> None:
        """
        Loads the lookup buffer for the entity, which is a dictionary,
        into the lookup buffer for the category. Transforms the dictionary 
        to a list, because that's how the the DV Handler requires it.
        Resets the entity buffer.
        """
        entity_lookup_params_list = list(self.entity_lookup_params.values())
        self.category_lookup_params.append(entity_lookup_params_list)
        self.entity_lookup_params = dict()


    def _load_key_lookup_params_buffer(self) -> None:
        """
        Loads the key-lookup params for the entity into
        the key-lookup buffer for the category of data.
        """
        self.category_key_lookup_params.append(self.entity_key_lookup_params)
        self.entity_key_lookup_params = dict()


    def reset_entity_buffers(self) -> None:
        """
        Resets all buffers for the current entity.
        Used in the entity cycle.
        """
        self.entity_data = dict()
        self.entity_id_params = IDParams()
        self.entity_lookup_params = dict()
        self.entity_key_lookup_params = dict()


    def reset_category_buffers(self):
        """
        Reset all category-level buffers.
        """
        self.category_id_params = []
        self.category_lookup_params = []
        self.category_key_lookup_params = []
        self.category_data = []


    def load_buffers(self) -> None:
        """
        Because we will query and upsert the data in batches,
        we need to store everything in our buffers.
        """
        try:
            self._load_lookup_params_buffer()
            self._load_id_params_buffer()
            self._load_data_buffer()
            self._load_key_lookup_params_buffer()
        
        except Exception as e:
            raise RuntimeError(f"Error while loading buffers: {e}")
