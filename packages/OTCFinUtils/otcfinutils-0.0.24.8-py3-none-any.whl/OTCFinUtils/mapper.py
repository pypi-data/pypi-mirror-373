from io import BytesIO
from OTCFinUtils.utils import (
    cast_data,
    choice_value,
    default_value,
    evaluate_condition,
    extract_sheets,
    extract_sorted_categories,
    get_skip_flag,
    group_mappings,
    process_data_type, 
    extract_lookup_column, 
    extract_file_data, 
    is_date, 
    extract_date_string,
    trim_string_fields
)
from OTCFinUtils.data_structs import (
    DEFAULT_SHEET_CHUNK_SIZE,
    NOT_DEFINED,
    Condition,
    Category,
    ResponseIds, 
    EntityLookups, 
    MappingFields, 
    IDParams,
    Lookup,
    KeyLookupParams,
    EntityKeyLookupParams,
)
from OTCFinUtils.mapper_loading import (
    get_buffer_ids,
    get_buffer_lookups,
)
from OTCFinUtils.dataverse_handler import DVHandler
from OTCFinUtils.buffer import Buffer
from typing import Any, Optional
import pandas as pd
import json


class DataMapper:
    """
    Used for loading data into the Dataverse with the help of mappings from the File Mappings table.

    **IMPORTANT TO UNDERSTAND:**

    The code follows a somewhat specific logic to implement this.
    Without understanding the logic, it will be difficult to follow the code.

    On a high level, the code does the following steps:

    - Reads the provided file / data (input data)
    - Reads the provided mappings
    - Applies the mappings to the input data
    - Extracts query params for getting the entity ids (for checking if the data has already been loaded)
    - Extracts query params for getting the lookup ids for the input data
    - Queries the Dataverse for the entity ids (so we can know whether to perform a POST or PATCH request)
    - Queries the Dataverse for the lookup ids (so we can link the input data to the lookups)
    - Assigns the entity ids to the input data
    - Assigns the lookup ids to the input data
    - Performs a bulk upsert operation to the Dataverse
    - Returns the ids of the created and updated entities
    """
    
    def __init__(self, dvh: DVHandler, owner_id: str, user_id: str) -> None:
        """
        Because we constantly interact with the DV API.
        Need to keep track of the connection information.
        """
        self.dvh: DVHandler = dvh
        self.owner_id: str = owner_id
        self.user_id: str = user_id
        self.SHEET_CHUNK_SIZE: int = DEFAULT_SHEET_CHUNK_SIZE
        self.current_row: int = 0
        self.current_column: str = NOT_DEFINED
        self.current_sheet: str = NOT_DEFINED
        
        """
        Stored in order to query the table definitions only once,
        and not for every entity.
        """
        self.table_definitions:     dict[str, dict] = dict()

        """
        For storing buffered data that will be upserted in bulk.
        """
        self.buffer = Buffer()


    def _resolve_type_conflicts(self) -> None:
        """
        Necessary in the case the file types don't match the DV types.
        """
        for entity_data in self.buffer.category_data:
            entity_data = process_data_type(entity_data)
        return

    
    def _table_definition(self, table: str, fields: list[str]) -> dict:
        """
        Uses a caching approach to minimize number of queries to DV.
        """
        select_param = ",".join(fields)
        if table not in self.table_definitions:
            self.table_definitions[table] = self.dvh.get_table_definition(table, select_param)
        return self.table_definitions[table]


    def _resolve_empty_id_conditions(self) -> None:
        """
        In the case the ID parameter buffer has items with
        an empty list of conditions to filter by, add an 
        "impossible" condition.

        In such cases the not DV should return any entity ID.
        """
        for entity_id_params in self.buffer.category_id_params:
            if not entity_id_params.conditions:
                # An impossible condition, so the DV returns empty data
                entity_id_params.conditions = ["statecode eq 10"]
        return


    def _link_ids_with_data(self, ids: list[str]) -> None:
        """
        For adding the ids to the data buffer.
        Necessary for the bulk upsert operation.
        """
        for entity, id in zip(self.buffer.category_data, ids):
            entity["entity_id"] = id


    def _link_lookups(self, lookups: list[EntityLookups]) -> None:
        """
        For adding the lookups to the data buffer.
        Necessary for the bulk upsert operation.
        """
        if len(self.buffer.category_data) != len(lookups):
            raise RuntimeError(f"Category data buffers size ({len(self.buffer.category_data)}) and lookup list size ({len(lookups)}) do not match.")

        for entity, entity_lookups in zip(self.buffer.category_data, lookups):
            for lookup in entity_lookups:
                column = f"{lookup.bind_column}@odata.bind"
                if not lookup.id:
                    entity[column] = None
                else:
                    entity[column] = f"{lookup.table}({lookup.id})"

    
    def _upsert_data_buffer(self) -> ResponseIds:
        """
        This operation is the ultimate goal of the whole code.
        """
        try:
            response = self.dvh.upsert_bulk(self.buffer.category_data)
            return response
        
        except Exception as e:
            raise RuntimeError(f"Error while upserting the data: {e}")


    def _extract_lookup_vars(self, mapping: dict) -> tuple:
        """
        For increased readability, this logic is 
        grouped into one function.
        """
        try:
            table: str = mapping[MappingFields.LOOKUP_TABLE]
            relationship: str = mapping[MappingFields.LOOKUP_RELATIONSHIP]
            column = extract_lookup_column(mapping)
            
            table_definition_fields = ["PrimaryIdAttribute", "EntitySetName"]
            table_definition: dict = self._table_definition(table, table_definition_fields)
            
            id_column: str = table_definition.get("PrimaryIdAttribute", "")
            table_plural: str = table_definition.get("EntitySetName", "")

            return column, id_column, table_plural, relationship
        
        except KeyError as e:
            raise KeyError(f"Key error while extracting lookup variables: {e}")
    

    def _skip_entity_logic(self) -> None:
        """
        In the case we need to skip this entity (there is no entity in the file).
        """
        self.buffer.entity_data["skip"] = True

    
    def _lookup_logic(self, row: pd.Series, mapping: dict) -> None:
        """
        Extracts and appends the appropriate lookup parameters to the
        entity lookup buffer. 
        
        This buffer will later be loaded to the category buffer.
        
        The category buffer will be used for a bulk-reading of the 
        necessary lookup ids.

        If no lookup value is found in the file, 
        run the skip-entity logic.
        """
        column, id_column, table, relationship = self._extract_lookup_vars(mapping)        
        dv_column: str = mapping[MappingFields.DV_COLUMN]
        file_data = extract_file_data(row, mapping)

        if not file_data:
            self._skip_entity_logic()
            return

        if isinstance(file_data, pd.Timestamp):
            file_data = file_data.strftime("%Y-%m-%d")
            condition = f"{column} eq {file_data}"
        else:
            condition = f"{column} eq '{file_data}'"
        
        if not relationship in self.buffer.entity_lookup_params:
            self.buffer.entity_lookup_params[relationship] = IDParams(
                table=table,
                id_column=id_column,
                bind_column=dv_column
            )
        
        self.buffer.entity_lookup_params[relationship].conditions.append(condition)


    def _setup_key_parameters(self, loading_data: Any, dv_column: str) -> None:
        """
        Loads the parameters for getting the id of the entity based on its key.
        """
        try:
            if is_date(loading_data):
                date = extract_date_string(loading_data)
                condition = f"{dv_column} eq {date}"
            else:
                condition = f"{dv_column} eq '{loading_data}'"

            self.buffer.entity_id_params.conditions.append(condition)
        
        except Exception as e:
            raise RuntimeError(f"Error while running 'key parameter logic': {e}")


    def _key_logic(self, row: pd.Series, mapping: dict) -> None:
        """
        Has two main steps:
        
        - Extracts and loads the appropriate id parameters in the
          entity id params buffer. This buffer will later be used
          to get the actual DV id of the entity, and not just the
          logical key of the entity.

        - Loads the logical key data to the entity data buffer.
          The entity data buffer will later be loaded to the
          category data buffer, which will be bulk-upserted to
          the DV.
        """
        try:
            file_column: str = mapping[MappingFields.FILE_COLUMN]
            file_data = row[file_column]
            dv_column: str = mapping[MappingFields.DV_COLUMN]
            self._setup_key_parameters(file_data, dv_column)
            self.buffer.entity_data[dv_column] = file_data
        
        except Exception as e:
            raise RuntimeError(f"Error while running 'key logic': {e}")
        

    def _save_key_lookup_column(self, mapping: dict) -> None:
        """
        For getting the ids later, if some lookups are part of the key.
        """
        dv_column = mapping[MappingFields.DV_COLUMN]
        table = mapping[MappingFields.LOOKUP_TABLE]
        lookup_id_column = f"{table}id"
        lookup_id = None
        params = KeyLookupParams(lookup_id_column, lookup_id)
        self.buffer.entity_key_lookup_params[dv_column] = params

    
    def _key_lookup_logic(self, row: pd.Series, mapping: dict) -> None:
        """
        In the case the mapping is for a lookup and for a key of the entity.
        This is one of the most complicated cases. Later we get the id of the
        key using the 'expand' option in the DV API.

        We don't need to add the file data to the data buffer.
        This step is already done in the link-lookups step.
        """
        try:
            self._lookup_logic(row, mapping)
            self._save_key_lookup_column(mapping)
            
        except Exception as e:
            raise RuntimeError(f"Error while runnung 'key lookup' logic: {e}")


    def _choice_logic(self, row: pd.Series, mapping: dict) -> None:
        """
        In the case the mapping is for a choice. Assigns 
        the DV choice value in the entity buffer. If the
        file field is empty, does not add anything to the
        data buffer.
        """
        try:
            file_column: str = mapping[MappingFields.FILE_COLUMN]
            dv_column: str = mapping[MappingFields.DV_COLUMN]
            file_data = row[file_column]
            
            if not file_data or pd.isna(file_data):
                return
            
            if not isinstance(file_data, str):
                raise RuntimeError(f"File value must be a string: {file_data}")
            
            dv_choice_value = choice_value(file_data, mapping)
            self.buffer.entity_data[dv_column] = dv_choice_value

        except Exception as e:
            raise RuntimeError(f"Error in choice logic [{e}], for mapping: [{mapping}]")

    
    def _default_value_logic(self, mapping: dict) -> Any:
        """
        In the case the mapping is for a default value.
        """
        try:
            dv_column = mapping[MappingFields.DV_COLUMN]
            default_value_string = mapping[MappingFields.DEFAULT_VALUE]
            result = default_value(default_value_string)
            self.buffer.entity_data[dv_column] = result
            return result
        except Exception as e:
            raise RuntimeError(f"Error in default-value logic: [{e}] for mapping: [{mapping}]")
        

    def _default_value_key_logic(self, mapping: dict) -> None:
        """
        If the mapping defines a default value and if this field is part of the entity key.
        """
        default_value = self._default_value_logic(mapping)
        dv_column: str = mapping[MappingFields.DV_COLUMN]
        self._setup_key_parameters(default_value, dv_column)


    def _normal_data_logic(self, row: pd.Series, mapping: dict) -> None:
        """
        The simplest case - just map the file data to the data buffer.
        No modifications to the data are necessary.
        """
        try:
            dv_column = mapping[MappingFields.DV_COLUMN]
            file_column = mapping[MappingFields.FILE_COLUMN]
            self.buffer.entity_data[dv_column] = row[file_column]
        except Exception as e:
            raise RuntimeError(f"Error in noraml-data-field logic: [{e}] for mapping [{mapping}]")
        

    def _condition_logic(self, row: pd.Series, mapping: dict) -> None:
        condition_string = mapping[MappingFields.CONDITION]
        condition_dict = json.loads(condition_string)
        condition = Condition.create(condition_dict)
        dv_column = mapping[MappingFields.DV_COLUMN]
        self.buffer.entity_data[dv_column] = condition.result_value


    def _preprocess_row(self, row: pd.Series, mapping: dict) -> pd.Series:
        if mapping[MappingFields.DATA_TYPE] is None:
            return row
        
        data_type: str = mapping[MappingFields.DATA_TYPE].lower()
        file_column: str = mapping[MappingFields.FILE_COLUMN]
        file_value = row[file_column]
        
        if pd.notna(file_value) and isinstance(file_value, str):
            file_value = file_value.replace("'", "''")
        
        if data_type is not None and pd.notna(file_value):
            row[file_column] = cast_data(file_value, data_type)
        
        return row
    
    
    def _run_mapping_cycle(self, row: pd.Series, mapping: dict) -> None:
        """
        Checks the current type of mapping and calls the corresponding 
        function for each type of mapping.
        """
        self.current_column = mapping[MappingFields.FILE_COLUMN]

        try:
            is_lookup: bool = mapping[MappingFields.IS_LOOKUP]
            is_key: bool = mapping[MappingFields.IS_KEY]
            choice_dictionary: str = mapping[MappingFields.CHOICE_DICTIONARY]
            default_value_string: str = mapping[MappingFields.DEFAULT_VALUE]
            skip_entity: bool = get_skip_flag(row, mapping)
            
            row = self._preprocess_row(row, mapping)

            if evaluate_condition(row, mapping):
                self._condition_logic(row, mapping)

            elif choice_dictionary:
                self._choice_logic(row, mapping)

            elif default_value_string and is_key:
                self._default_value_key_logic(mapping)
            
            elif default_value_string:
                self._default_value_logic(mapping)
            
            elif is_lookup and not is_key:
                self._lookup_logic(row, mapping)

            elif skip_entity:
                self._skip_entity_logic()
            
            elif is_key and not is_lookup:
                self._key_logic(row, mapping)

            elif is_key and is_lookup:
                self._key_lookup_logic(row, mapping)
            
            else:
                self._normal_data_logic(row, mapping)

        except Exception as e:
            raise e


    def _link_table_metadata(self, table: str) -> None:
        """
        Because we need the metadata (the table name and id column)
        for correctly upserting the data.
        """
        try:
            table_definition_fields = ["PrimaryIdAttribute", "EntitySetName"]
            table_definition: dict = self._table_definition(table, table_definition_fields)
            
            id_column: str = table_definition.get("PrimaryIdAttribute", "")
            table_plural: str = table_definition.get("EntitySetName", "")

            self.buffer.entity_data["table_name"] = table_plural
            self.buffer.entity_data["id_column"] = id_column

            self.buffer.entity_id_params.table = table_plural
            self.buffer.entity_id_params.id_column = id_column

        except Exception as e:
            raise RuntimeError(f"Error while linking table metadata: {e}")


    def _run_entity_cycle(self, row: pd.Series, category: Category) -> None:
        """
        Resets all required buffers before everything else.
        
        For the entity of the specified category, in the given row, implements 
        all associated mappings. 
        
        Loads all associated entity buffer data into the category buffers. 
        
        Skips the loading steps if the mapping code has marked the entity as 
        a skip-entity.
        """
        self.current_row += 1

        try:
            self.buffer.reset_entity_buffers()
            category_mappings = self.grouped_mappings[category]

            for mapping in category_mappings:
                self._run_mapping_cycle(row, mapping)

            if "skip" in self.buffer.entity_data:
                return
            
            self._link_table_metadata(category.table)
            self.buffer.load_buffers()
        
        except Exception as e:
            raise e
        

    @staticmethod
    def _create_key_lookup_condition(entity_key_lookup_params: EntityKeyLookupParams, lookup: Lookup) -> str:
        """
        Helper function, for creating the DV API query filter parameter.
        """
        params = entity_key_lookup_params[lookup.bind_column]
        return f"{lookup.bind_column}/{params.lookup_id_column} eq '{lookup.id}'"
    
    
    def _attach_entity_lookups_to_buffer(self, entity_index: int, entity_lookups: EntityLookups) -> None:
        """
        So we can get the id of the entity, based on all its key-fields.
        """
        for lookup in entity_lookups:
            entity_params = self.buffer.category_key_lookup_params[entity_index]
            if lookup.bind_column not in entity_params:
                continue
            elif not lookup.id:
                raise RuntimeError(
                    f"Id of lookup '{lookup.bind_column}' cannot be null if part of key. "
                    f"Query conditions: {self.buffer.category_lookup_params[entity_index]}"
                )

            condition = DataMapper._create_key_lookup_condition(entity_params, lookup)
            self.buffer.category_id_params[entity_index].conditions.append(condition)
        

    def _attach_lookups_to_buffer(self, lookups: list[EntityLookups]) -> None:
        """
        Adds the filtering conditions for the key-
        lookup fields, so we can get the entity id.
        """
        for entity_index, entity_lookups in enumerate(lookups):
            self._attach_entity_lookups_to_buffer(entity_index, entity_lookups)


    def _process_lookups(self) -> None:
        """
        Because we need the lookup-fields to be 
        upserted as well.
        """
        lookups = get_buffer_lookups(self.dvh, self.buffer.category_lookup_params)
        self._link_lookups(lookups)
        self._attach_lookups_to_buffer(lookups)


    def _process_ids(self) -> None:
        """
        Because we need the ids to upserted as 
        well - for the entities that exist.
        """
        self._resolve_empty_id_conditions()
        entity_ids = get_buffer_ids(self.dvh, self.buffer.category_id_params)
        self._link_ids_with_data(entity_ids)


    def _process_buffered_data(self) -> None:
        """
        Because we need the lookups and ids to 
        be added to the loading data.
        """
        self._process_lookups()
        self._process_ids()


    def _link_data_owner(self) -> None:
        """
        Add the "global" account id as the owner 
        for all buffered entity data.
        """
        for entity in self.buffer.category_data:
            entity["ownerid@odata.bind"] = f"teams({self.owner_id})"

    
    def _postprocess_data(self) -> None:
        """
        Because we need to add missing data and 
        execute clean ups before upserting.
        """
        self._resolve_type_conflicts()
        self._process_buffered_data()
        self._link_data_owner()


    def _run_category_cycle(self, chunk, category):
        try:
            for _, row in chunk.iterrows():
                self._run_entity_cycle(row, category)
        except Exception as e:
            raise Exception(
                f"Error: {e} | "
                f"Sheet: {self.current_sheet} | "
                f"Column: {self.current_column} | "
                f"Row: {self.current_row}"
            )

        self._postprocess_data()
        category_response_ids = self._upsert_data_buffer()
        self.buffer.reset_category_buffers()
        return category_response_ids
    

    def extract_category_key_columns(self, category: Category) -> list[str]:
        category_mappings = self.grouped_mappings[category]
        key_mappings = [mapping for mapping in category_mappings if mapping[MappingFields.IS_KEY] == True]
        key_file_columns = []
        for mapping in key_mappings:
            key_file_column = mapping[MappingFields.FILE_COLUMN]
            key_file_columns.append(key_file_column)
        return key_file_columns
    

    def extract_data_chunk(self, category_distinct_data: pd.DataFrame, index: int) -> pd.DataFrame:
        start_index = index * self.SHEET_CHUNK_SIZE
        end_index = start_index + self.SHEET_CHUNK_SIZE
        data_chunk = category_distinct_data.iloc[start_index:end_index]
        return data_chunk
    

    def load_category_data(self, category_distinct_data: pd.DataFrame, category: Category) -> ResponseIds:
        category_response_ids = ResponseIds()
        num_chunks = len(category_distinct_data) // self.SHEET_CHUNK_SIZE + 1
        
        for index in range(num_chunks):
            data_chunk = self.extract_data_chunk(category_distinct_data, index)
            chunk_response_ids = self._run_category_cycle(data_chunk, category)
            category_response_ids.merge(chunk_response_ids)
        
        return category_response_ids
    

    @staticmethod
    def extract_sheet_column_converters(column_converters: Optional[dict], sheet: str) -> Optional[dict]:
        if column_converters is None:
            return None
        
        return column_converters[sheet]
    
    
    def _load_sheet(
        self, 
        input_data: BytesIO | list[dict], 
        categories: list[Category], 
        sheet: str,
        header_row_number: int,
        column_type_converters: Optional[dict],
    ) -> ResponseIds:
        """
        Gets the sheet metadata and runs the loading 
        process for the given sheet. Returns the ids 
        of the updated and created entities.
        """
        # Reset the file row number for each sheet
        self.current_sheet = sheet
        self.current_column = NOT_DEFINED
        self.current_row = 0
        
        sheet_response_ids = ResponseIds()

        if isinstance(input_data, BytesIO):
            sheet_column_converters = DataMapper.extract_sheet_column_converters(column_type_converters, sheet)
            sheet_data = pd.read_excel(
                io=input_data, 
                sheet_name=sheet, 
                header=header_row_number, 
                keep_default_na=False, 
                na_values=[""],
                converters=sheet_column_converters,
            )
        elif isinstance(input_data, list):
            sheet_data = pd.DataFrame(input_data)

        sheet_data = trim_string_fields(sheet_data)
        
        for category in categories:
            category_key_columns = self.extract_category_key_columns(category)
            
            if len(category_key_columns) == 0:
                raise Exception(f"Entity key columns are not provided in mappings for: {category}")
            
            category_distinct_data = sheet_data.drop_duplicates(subset=category_key_columns)
            category_response_ids = self.load_category_data(category_distinct_data, category)
            sheet_response_ids.merge(category_response_ids)
        
        return sheet_response_ids


    # TODO - Add sheet name to parameter list - not needed anymore?
    # TODO - Remove table name and sheet name from categories - not needed anymore?

    def map_data(
        self, 
        input_data: BytesIO | list[dict], 
        mappings: list[dict], 
        sheet_chunk_size: Optional[int] = None,
        header_row_number: int = 0,
        column_converters: Optional[dict] = None,
    ) -> ResponseIds:
        """
        Prepare mappings, categories, and sheet names. Run the 
        mappings for each sheet. Return the ids of the updated 
        and created entities, grouped by table names.
        """
        # Override loading configuration parameter
        if sheet_chunk_size is not None:
            self.SHEET_CHUNK_SIZE = sheet_chunk_size

        self.grouped_mappings = group_mappings(mappings)
        categories = extract_sorted_categories(self.grouped_mappings)
        
        sheets: list[str] = extract_sheets(categories)
        final_response_ids = ResponseIds()

        for sheet in sheets:
            sheet_categories = list(filter(lambda x: x.sheet == sheet, categories))
            sheet_response_ids = self._load_sheet(input_data, sheet_categories, sheet, header_row_number, column_converters)
            final_response_ids.merge(sheet_response_ids)

        return final_response_ids
