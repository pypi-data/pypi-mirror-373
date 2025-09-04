import re
import math
import json
import pandas as pd
from datetime import datetime
from typing import Optional, Any
from OTCFinUtils.data_structs import MappingFields, Condition, Operator, Category


def extract_segment_object_line(lines: list[str]) -> str:
    for line in lines:
        if "@odata.context" in line:
            return line
    raise ValueError(f"Object line not found in batch response. Lines: {lines}")


def extract_segment_response_id(lines: list[str], id_column: str) -> Optional[str]:
    """
    From a list of lines of a batch response, returns 
    the id of the entity in the response. If a null
    id column name is provided, return None.
    """
    try:
        if not id_column:
            return None

        object_line = extract_segment_object_line(lines)
        json_object = json.loads(object_line)
        object_id: str = json_object[id_column]

        return object_id
    
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON error in response id logic: {e}")
    except KeyError as e:
        raise RuntimeError(f"Key error in response id logic: {e}")
    except Exception as e:
        raise RuntimeError(f"Error in response id logic: {e}")


def extract_segment_status_code(lines: list[str]) -> int:
    """
    From a list of lines of a batch response,
    returns the HTTP status code.
    """
    status_code_line = lines[4]
    status_code_line_parts = status_code_line.split(" ")
    status_code = status_code_line_parts[1]
    status_code = int(status_code)
    
    return status_code


def extract_segment_table_name(lines: list[str]) -> str:
    """
    From a list of lines of a batch response,
    returns the table name of the entity using regex.
    """
    object_line = extract_segment_object_line(lines)
    pattern = r'metadata#([a-z0-9_]+)'
    pattern_matches = re.findall(pattern, object_line)
    
    if not pattern_matches:
        raise RuntimeError(f"Could not find table pattern in string: {object_line}")
    
    table = pattern_matches[0]
    return table


def process_data_type(data: dict) -> None:
    """
    Resolves conflicts between file data types and DV data types.
    """
    try:
        for key, value in data.items():
            if isinstance(value, pd.Timestamp):
                if pd.isna(value):
                    data[key] = None
                else:
                    data[key] = value.strftime("%Y-%m-%d")

            elif isinstance(value, datetime):
                data[key] = value.strftime("%Y-%m-%d")

            elif isinstance(value, str):
                # Try parsing string to date if the key is likely a date field
                if "date" in key.lower():
                    try:
                        parsed = pd.to_datetime(value)
                        data[key] = parsed.strftime("%Y-%m-%d")
                    except Exception:
                        data[key] = None

            elif value is None or (not isinstance(value, str) and math.isnan(value)):
                data[key] = None
    
    except Exception as e:
        raise RuntimeError(f"Error: {e}, while processing data object: {data}")
    

def extract_lookup_column(mapping: dict) -> str:
    """
    Gets the lookup column value from the 
    JSON string in the mapping.
    """
    try:
        column_string: str = mapping[MappingFields.LOOKUP_COLUMN]
        # TODO: Remove when no longer needed
        column_string = column_string.replace("'", '"')
        column = json.loads(column_string)[0]
        return column
    
    except Exception as e:
        raise RuntimeError(f"Error while extracting the lookup column: {e}")
    

def extract_file_data(row: pd.Series, mapping: dict):
    """
    Get the data from the appropriate file column, 
    depending on whether the data matches the "exclude 
    values" list from the mapping.
    """
    try:
        if data_equals_exclude_value(row, mapping):
            alternative_file_column: str = mapping[MappingFields.ALTERNATIVE_FILE_COLUMN]
            file_data = row[alternative_file_column]
        else:
            file_column: str = mapping[MappingFields.FILE_COLUMN]
            file_data = row[file_column]
        
        return trim_string_values(file_data)
    
    except Exception as e:
        raise RuntimeError(f"Could not extract file data. Error: {e}")
    

def data_equals_exclude_value(row: pd.Series, mapping: dict) -> bool:
    """
    Checks if the file data matches one of the 
    "exclude values" from the mapping.
    """
    try:
        file_column: str = mapping[MappingFields.FILE_COLUMN]
        exclude_values_list: str = mapping[MappingFields.EXCLUDE_VALUE]
        
        if not exclude_values_list:
            return False
        
        exclude_values: list = json.loads(exclude_values_list)
        
        if row[file_column] in exclude_values:
            return True
        
        return False
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not decode JSON string: {exclude_values_list}. Error: {e}") # type: ignore
    
    except KeyError as e:
        raise KeyError(f"Key error for 'exclude value' logic: {e}")

    except Exception as e:
        raise RuntimeError(f"Error for 'exclude value' logic: {e}")
    

def trim_string_values(value: Any) -> Any:
    """
    If the value is a string trims and returns it.
    Returns all other types of values.
    """
    if isinstance(value, str):
        return value.strip()
    return value


def is_date(value: Any) -> bool:
    """
    Helper function.
    """
    if isinstance(value, pd.Timestamp):
        return True 
    
    elif isinstance(value, str) and re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", value):
        return True
    
    return False


def extract_date_string(value: pd.Timestamp | str) -> str:
    """
    Helper function.
    """
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    elif isinstance(value, str):
        return value
    else:
        raise RuntimeError(f"The provided value is not a Timestamp or string: {value}")


def choice_value(file_data: str, mapping: dict) -> int | bool:
    """
    Should return the DV value (number) of the choice we need,
    based on the file data value. 
    """
    choice_string: str = mapping[MappingFields.CHOICE_DICTIONARY]
    
    try:
        choice_mappings: list[dict] = json.loads(choice_string)
    except json.JSONDecodeError:
        raise RuntimeError(f"The choice dictionary: {choice_string} is not a valid JSON object.")
    
    choice_mapping: dict = normalize_choice_map(choice_mappings)
    
    # To normalize the choice strings
    file_data = str(file_data).upper()
    
    return choice_mapping[file_data]


def normalize_choice_map(choice_mappings: list[dict]) -> dict:
    """
    Should return a normalized dictionary of the mappings,
    from the un-normalized list of mappings.
    """
    try:
        choice_mapping = dict()
        
        for item in choice_mappings:
            dv_value: int | bool = item["Value"]
            excel_value: str = item["Excel_Value"]
            
            # To normalize the choice strings
            excel_value = excel_value.upper()
            
            choice_mapping[excel_value] = dv_value
        
        return choice_mapping
    
    except KeyError as e:
        raise KeyError(f"Key Error for choice map normalization: {e}")
    
    except Exception as e:
        raise RuntimeError(f"Error while normalizing choice map: {e}")
    

def default_value(default_value_string: str):
    """
    Extract the default value from a JSON string, 
    based on hardcoded rules.
    """
    try:
        default_value_info = json.loads(default_value_string)
        
        if default_value_info["type"] == "current_date":
            date_format = default_value_info["format"]
            current_time = datetime.now()
            date_string = current_time.strftime(date_format)
            return pd.to_datetime(date_string)
        else:
            return default_value_info["value"]
    
    except json.JSONDecodeError:
        raise ValueError(f"Could not decode the string: {default_value_string}")
    
    except KeyError as e:
        raise KeyError(f"Could not read key for default value logic: {e}")
    

def cast_data(value: Any, data_type: str) -> Any:
    """
    Casts the provided value to the given data type.
    Return the value if the data type is unknown.
    """
    try:
        if pd.isna(value):
            return value
        elif data_type == "string":
            return str(value)
        elif data_type == "integer":
            return int(value)
        elif data_type == "decimal":
            return float(value)
        elif data_type == "boolean":
            return bool(value)
        else:
            return value
    
    except Exception as e:
        raise RuntimeError(f"Error while type-casting data: {e}")
    

def get_skip_flag(row: pd.Series, mapping: dict) -> bool:
    """
    Return a flag for whether to skip the current entity or not,
    depending on whether the file data matches one of the "exclude 
    values" in the mapping or if the file data is an empty value.
    """
    is_key: bool = mapping[MappingFields.IS_KEY]

    return (
        (is_key and data_is_empty(row, mapping)) or 
        data_equals_exclude_value(row, mapping)
    )


def data_is_empty(row: pd.Series, mapping: dict) -> bool:
    """
    Checks if the file data is an empty cell. Returns True 
    if empty. Returns False otherwise. Does not take into 
    consideration the alternative file column.
    """
    file_column: str = mapping[MappingFields.FILE_COLUMN]
    file_data = row[file_column]
    
    if pd.isna(file_data) or not file_data:
        return True
    
    return False


def evaluate_condition(row: pd.Series, mappping: dict) -> bool:
    """
    Checks if the mapping has a condition and 
    if the row satisfies the condtition. If true,
    returns the resulting value, otherwise "None".
    """
    try:
        condition_string = mappping[MappingFields.CONDITION]

        if not condition_string:
            return False
        
        condition_dict = json.loads(condition_string)
        condition = Condition.create(condition_dict)
        
        return is_valid(condition, row)
    
    except Exception as e:
        raise RuntimeError(f"Could not evaluate condition. Mapping: {mappping}. Error: {e}")
    

def is_valid(condition: Condition, row: pd.Series) -> bool:
    """
    Evaluates if the row satisfies the given condition.
    """
    if (
        condition.operator == Operator.EQUALS and 
        condition.is_static_value and 
        row[condition.column] == condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.EQUALS and 
        not condition.is_static_value and 
        row[condition.column] == row[condition.compare_value]
    ):
        return True
    
    # ----------------------------------------------------
    
    elif (
        condition.operator == Operator.NOT_EQUALS and
        condition.is_static_value and
        row[condition.column] != condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.NOT_EQUALS and
        not condition.is_static_value and
        row[condition.column] != row[condition.compare_value]
    ):
        return True
    
    # ----------------------------------------------------
    
    elif (
        condition.operator == Operator.IS_NULL and
        row[condition.column] == None
    ):
        return True
    
    elif (
        condition.operator == Operator.IS_NOT_NULL and
        row[condition.column] != None
    ):
        return True
    
    # ----------------------------------------------------
    
    elif (
        condition.operator == Operator.SMALLER and
        condition.is_static_value and
        row[condition.column] < condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.SMALLER and
        not condition.is_static_value and
        row[condition.column] < row[condition.compare_value]
    ):
        return True
    
    # ----------------------------------------------------
    
    elif (
        condition.operator == Operator.GREATER and
        condition.is_static_value and
        row[condition.column] > condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.GREATER and
        not condition.is_static_value and
        row[condition.column] > row[condition.compare_value]
    ):
        return True
    
    # ----------------------------------------------------

    elif (
        condition.operator == Operator.SMALLER_OR_EQUAL and
        condition.is_static_value and
        row[condition.column] <= condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.SMALLER_OR_EQUAL and
        not condition.is_static_value and
        row[condition.column] <= row[condition.compare_value]
    ):
        return True
    
    # ----------------------------------------------------
    
    elif (
        condition.operator == Operator.GREATER_OR_EQUAL and
        condition.is_static_value and
        row[condition.column] >= condition.compare_value
    ):
        return True
    
    elif (
        condition.operator == Operator.GREATER_OR_EQUAL and
        not condition.is_static_value and
        row[condition.column] >= row[condition.compare_value]
    ):
        return True
    
    return False


def group_mappings(mappings: list[dict]) -> dict[Category, list[dict]]:
    """
    From all the mapping, return a dictionary of grouped mapping lists,
    based on their categories (sheet name + order number + DV table).
    """
    grouped_mappings: dict[Category, list[dict]] = dict()

    for mapping in mappings:
        group: int = mapping[MappingFields.MAP_GROUP_ORDER]
        table: str = mapping[MappingFields.DV_TABLE]
        sheet: str = mapping[MappingFields.SHEET]

        file_mapping_category = Category(group, table, sheet)

        if file_mapping_category not in grouped_mappings:
            grouped_mappings[file_mapping_category] = list()

        grouped_mappings[file_mapping_category].append(mapping)

    return grouped_mappings


def extract_sorted_categories(grouped_mappings: dict[Category, list]) -> list[Category]:
    categories: list[Category] = list(grouped_mappings.keys())
    return sorted(categories, key=lambda category: category.group_num)


def extract_sheets(ordered_categories: list[Category]) -> list[str]:
    """
    From the provided categories, returns an ordered list of the sheet names,
    based on the map group ordering of the categories.
    """
    sheets: list[str] = []
    for category in ordered_categories:
        if category.sheet not in sheets:
            sheets.append(category.sheet)
    return sheets


def trim_string_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def test_func():
    return "..."