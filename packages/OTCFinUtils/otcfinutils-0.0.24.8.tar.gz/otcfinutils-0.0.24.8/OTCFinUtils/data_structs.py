from http import HTTPStatus as status
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any
from collections import namedtuple


@dataclass
class ResponseIds:
    """
    Used as a return value from the upsert operation on the DV.
    Contains the table names and ids of the entities that were 
    updated and created, stored separately.
    """
    def __init__(self) -> None:
        self.updated_entity_ids: dict[str, set[str]] = dict()
        self.created_entity_ids: dict[str, set[str]] = dict()
        self.failed_operations: list[str] = list()

    
    def append(self, status_code: int, id: str, table: str) -> None:
        """
        Depending on the status code appends the id and 
        table name to the create / update category.
        """
        if status_code == status.OK.value and table in self.updated_entity_ids:
            self.updated_entity_ids[table].add(id)
        
        elif status_code == status.OK.value and table not in self.updated_entity_ids:
            self.updated_entity_ids[table] = set()
            self.updated_entity_ids[table].add(id)
        
        elif status_code == status.CREATED.value and table in self.created_entity_ids:
            self.created_entity_ids[table].add(id)
        
        elif status_code == status.CREATED.value and table not in self.created_entity_ids:
            self.created_entity_ids[table] = set()
            self.created_entity_ids[table].add(id)
        
        return
    

    def merge(self, delta_ids: "ResponseIds") -> None:
        """
        Merges the values from the provided object onto the
        the values of the calling object.
        """
        for table, ids in delta_ids.created_entity_ids.items():
            if table not in self.created_entity_ids:
                self.created_entity_ids[table] = set()
            self.created_entity_ids[table].update(ids)

        for table, ids in delta_ids.updated_entity_ids.items():
            if table not in self.updated_entity_ids:
                self.updated_entity_ids[table] = set()
            self.updated_entity_ids[table].update(ids)

        self.failed_operations.extend(delta_ids.failed_operations)

        return
    

    def json_updated_entities(self) -> dict[str, list]:
        result = dict()
        for table, ids in self.updated_entity_ids.items():
            result[table] = list(ids)
        return result
    

    def json_created_entities(self) -> dict[str, list]:
        result = dict()
        for table, ids in self.created_entity_ids.items():
            result[table] = list(ids)
        return result
    

    def num_updated_entities(self) -> int:
        total = 0
        for ids in self.updated_entity_ids.values():
            total += len(ids)
        return total
    
    def num_created_entities(self) -> int:
        total = 0
        for ids in self.created_entity_ids.values():
            total += len(ids)
        return total
    
    def num_failed_operations(self) -> int:
        return len(self.failed_operations)
    

class FileSource(Enum):
    DV = "DV"
    SP = "SP"


@dataclass
class APIParams:
    """
    Basic helper data structure for making API calls.
    """
    url: str
    method: str
    data: dict | None = None


class QueryOperator(Enum):
    AND = "and"
    OR = "or"


@dataclass
class QueryParams:
    table: str
    columns: Optional[list[str]] = None
    conditions: Optional[list[str]] = None
    operator: QueryOperator = QueryOperator.AND
    top_num: Optional[int] = None


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class KeyLookupParams:
    lookup_id_column: str
    lookup_id: Optional[str]


EntityKeyLookupParams = dict[str, KeyLookupParams]


@dataclass
class IDParams:
    """
    A group of parameters used for querying id info of entities.
    """
    table: Optional[str] = None
    id_column: Optional[str] = None
    conditions: list[str] = field(default_factory=list)
    
    # If we have a lookup
    bind_column: Optional[str] = None
    

EntityLookupParams = list[IDParams]

"""
Used to divide and sort the file loading mappings
"""
Category = namedtuple("Category", ["group_num", "table", "sheet"])

"""
Used for storing the id info of the lookup entity
"""
Lookup = namedtuple("Lookup", ["bind_column", "table", "id"])

"""
Needed because each entity can have several lookups to other entities
"""
EntityLookups = list[Lookup]


class MappingFields:
    LOOKUP_TABLE = "new_lookuptable"
    LOOKUP_RELATIONSHIP = "new_lookuprelationship"
    LOOKUP_COLUMN = "new_lookupcolumn"
    DV_COLUMN = "new_dataversecolumnname"
    DV_TABLE = "new_dataversetablenametext"
    FILE_COLUMN = "new_filecolumnname"
    DEFAULT_VALUE = "new_defaultvalue"
    DATA_TYPE = "new_dataversedatatype"
    IS_LOOKUP = "new_islookup"
    IS_KEY = "new_iskey"
    IS_CHOICE = "new_ischoice"
    CHOICE_DICTIONARY = "new_choicedictionary"
    CONDITION = "new_condition"
    ALTERNATIVE_FILE_COLUMN = "new_alternativefilecolumnname"
    EXCLUDE_VALUE = "new_excludevalue"
    MAP_GROUP_ORDER = "new_mapgrouporder"
    SHEET = "new_sheetname"


@dataclass
class Mapping:
    dv_column: str
    dv_table: str
    file_column: str
    map_group_order: int
    sheet: str
    default_value: Optional[str] = None
    data_type: Optional[str] = None
    lookup_table: Optional[str] = None
    lookup_relationship: Optional[str] = None
    lookup_column: Optional[str] = None
    is_lookup: bool = False
    is_key: bool = False
    is_choice: bool = False
    choice_dictionary: Optional[str] = None
    condition: Optional[str] = None
    alternative_file_column: Optional[str] = None
    exclude_value: Optional[str] = None


class Operator(Enum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    IS_NULL = "IS_NULL"
    IS_NOT_NULL = "IS_NOT_NULL"
    SMALLER = "SMALLER"
    GREATER = "GREATER"
    GREATER_OR_EQUAL = "GREATER_OR_EQUAL"
    SMALLER_OR_EQUAL = "SMALLER_OR_EQUAL"


@dataclass
class Condition:
    column: str
    operator: Operator
    is_static_value: bool
    compare_value: Any
    result_value: Any

    @classmethod
    def create(cls, obj: dict) -> "Condition":
        return cls(
            column=obj["column"],
            operator=Operator(obj["operator"]),
            is_static_value=obj["is_static_value"],
            compare_value=obj["compare_value"],
            result_value=obj["result_value"],
        )
    

DEFAULT_SHEET_CHUNK_SIZE = 1000
SHEETS_RULE_TYPE_CHOICE = 12
NOT_DEFINED = "NOT DEFINED"