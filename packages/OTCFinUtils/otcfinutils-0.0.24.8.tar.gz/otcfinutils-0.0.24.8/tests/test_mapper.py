import unittest
from unittest.mock import patch, Mock, call
import unittest.test
from OTCFinUtils.data_structs import MappingFields, IDParams, Lookup
from OTCFinUtils.dataverse_handler import set_up_dv_handler, DVHandler
from OTCFinUtils.mapper import DataMapper

# TODO - add more fields and mappings - choice, condition, alternative column, exclude value, data type

mock_mappings = [
    # Test Column
    {
        MappingFields.DV_COLUMN: "new_testcolumn",
        MappingFields.DV_TABLE: "new_testtable",
        MappingFields.FILE_COLUMN: "Test Column",
        MappingFields.SHEET: "sheet 1",
        MappingFields.MAP_GROUP_ORDER: 1,
        MappingFields.LOOKUP_TABLE: None,
        MappingFields.LOOKUP_RELATIONSHIP: None,
        MappingFields.LOOKUP_COLUMN: None,
        MappingFields.DEFAULT_VALUE: None,
        MappingFields.DATA_TYPE: None,
        MappingFields.IS_LOOKUP: False,
        MappingFields.IS_KEY: False,
        MappingFields.IS_CHOICE: False,
        MappingFields.CHOICE_DICTIONARY: None,
        MappingFields.CONDITION: None,
        MappingFields.ALTERNATIVE_FILE_COLUMN: None,
        MappingFields.EXCLUDE_VALUE: None,
    },
    # Test Key Column
    {
        MappingFields.DV_COLUMN: "new_testkeycolumn",
        MappingFields.DV_TABLE: "new_testtable",
        MappingFields.FILE_COLUMN: "Test Key Column",
        MappingFields.SHEET: "sheet 1",
        MappingFields.MAP_GROUP_ORDER: 1,
        MappingFields.IS_KEY: True,
        MappingFields.LOOKUP_TABLE: None,
        MappingFields.LOOKUP_RELATIONSHIP: None,
        MappingFields.LOOKUP_COLUMN: None,
        MappingFields.DEFAULT_VALUE: None,
        MappingFields.DATA_TYPE: None,
        MappingFields.IS_LOOKUP: False,
        MappingFields.IS_CHOICE: False,
        MappingFields.CHOICE_DICTIONARY: None,
        MappingFields.CONDITION: None,
        MappingFields.ALTERNATIVE_FILE_COLUMN: None,
        MappingFields.EXCLUDE_VALUE: None,
    },
    # Test Lookup Column 1
    {
        MappingFields.DV_COLUMN: "new_TestLookupColumn",
        MappingFields.DV_TABLE: "new_testtable",
        MappingFields.FILE_COLUMN: "Test Lookup Column",
        MappingFields.SHEET: "sheet 1",
        MappingFields.IS_LOOKUP: True,
        MappingFields.IS_KEY: True,
        MappingFields.MAP_GROUP_ORDER: 1,
        MappingFields.LOOKUP_TABLE: "new_testtablelookup",
        MappingFields.LOOKUP_RELATIONSHIP: "lookup 1",
        MappingFields.LOOKUP_COLUMN: "[\"new_name\"]",
        MappingFields.DEFAULT_VALUE: None,
        MappingFields.DATA_TYPE: None,
        MappingFields.IS_CHOICE: False,
        MappingFields.CHOICE_DICTIONARY: None,
        MappingFields.CONDITION: None,
        MappingFields.ALTERNATIVE_FILE_COLUMN: None,
        MappingFields.EXCLUDE_VALUE: None,
    },
    # Test Lookup Column 2
    {
        MappingFields.DV_COLUMN: "new_TestLookupColumn2",
        MappingFields.DV_TABLE: "new_testtable",
        MappingFields.FILE_COLUMN: "Test Lookup Column 2",
        MappingFields.SHEET: "sheet 1",
        MappingFields.IS_LOOKUP: True,
        MappingFields.MAP_GROUP_ORDER: 1,
        MappingFields.LOOKUP_TABLE: "new_testtablelookup2",
        MappingFields.LOOKUP_RELATIONSHIP: "lookup 2",
        MappingFields.LOOKUP_COLUMN: "[\"new_name\"]",
        MappingFields.DEFAULT_VALUE: None,
        MappingFields.DATA_TYPE: None,
        MappingFields.IS_KEY: False,
        MappingFields.IS_CHOICE: False,
        MappingFields.CHOICE_DICTIONARY: None,
        MappingFields.CONDITION: None,
        MappingFields.ALTERNATIVE_FILE_COLUMN: None,
        MappingFields.EXCLUDE_VALUE: None,
    }
]

mock_data = [
    {
        "Test Column": "TEST VALUE",
        "Test Key Column": "TEST VALUE",
        "Test Lookup Column": "TEST VALUE",
        "Test Lookup Column 2": "TEST VALUE",
    }
]

upsert_data_params = [
    {
        'new_testcolumn': 'TEST VALUE', 
        'new_testkeycolumn': 'TEST VALUE', 
        'table_name': 'new_testtables', 
        'id_column': 'new_testtableid', 
        'new_TestLookupColumn@odata.bind': 
        'new_testtablelookups(6a709716-2687-ef11-ac20-7c1e52194aa8)', 
        'new_TestLookupColumn2@odata.bind': 
        'new_testtablelookup2s(ab755a1d-2687-ef11-ac20-7c1e52194aa8)', 
        'entity_id': None, 
        'ownerid@odata.bind': 
        'teams(6746bba8-de61-ee11-8def-000d3a17af6f)'
    }
]

get_buffer_ids_params = [
    IDParams(
        table='new_testtables', 
        id_column='new_testtableid', 
        conditions=[
            "new_testkeycolumn eq 'TEST VALUE'", 
            "new_TestLookupColumn/new_testtablelookupid eq '6a709716-2687-ef11-ac20-7c1e52194aa8'"
        ], 
        bind_column=None,
    ),
]

get_buffer_ids_return_value = [None]

get_buffer_lookups_params = [[
    IDParams(
        table='new_testtablelookups', 
        id_column='new_testtablelookupid', 
        conditions=["new_name eq 'TEST VALUE'"], 
        bind_column='new_TestLookupColumn',
    ), 
    IDParams(
        table='new_testtablelookup2s', 
        id_column='new_testtablelookup2id', 
        conditions=["new_name eq 'TEST VALUE'"], 
        bind_column='new_TestLookupColumn2',
    ),
]]

get_buffer_lookups_return_value = [[
    Lookup(
        bind_column='new_TestLookupColumn', 
        table='new_testtablelookups', 
        id='6a709716-2687-ef11-ac20-7c1e52194aa8',
    ), 
    Lookup(
        bind_column='new_TestLookupColumn2', 
        table='new_testtablelookup2s', 
        id='ab755a1d-2687-ef11-ac20-7c1e52194aa8',
    ),
]]

table_definition_calls = [
    call("new_testtablelookup", "PrimaryIdAttribute,EntitySetName"),
    call("new_testtablelookup2", "PrimaryIdAttribute,EntitySetName"),
    call("new_testtable", "PrimaryIdAttribute,EntitySetName"),
]

table_definition_outputs = [
    {'PrimaryIdAttribute': 'new_testtablelookupid', 'EntitySetName': 'new_testtablelookups',},
    {'PrimaryIdAttribute': 'new_testtablelookup2id', 'EntitySetName': 'new_testtablelookup2s',},
    {'PrimaryIdAttribute': 'new_testtableid', 'EntitySetName': 'new_testtables',},
]

OTC_TEAM_ID = "6746bba8-de61-ee11-8def-000d3a17af6f"
DEV_DATAVERSE_URL = "https://org873d3f04.crm.dynamics.com/"

class TestMyClass(unittest.TestCase):
    def setUp(self):
        dataverse_url = DEV_DATAVERSE_URL
        owner_id = OTC_TEAM_ID
        user_id = "nonexistent-user-id"
        self.dvh = set_up_dv_handler(dataverse_url)
        self.mapper = DataMapper(self.dvh, owner_id, user_id)

    
    @patch("OTCFinUtils.mapper.get_buffer_lookups")
    @patch("OTCFinUtils.mapper.get_buffer_ids")
    @patch.object(DVHandler, "upsert_bulk")
    @patch.object(DVHandler, "get_table_definition")
    def test_run_logic_calls_upsert_bulk(
        self, 
        mock_get_table_definition: Mock,
        mock_upsert_bulk: Mock, 
        mock_get_buffer_ids: Mock, 
        mock_get_buffer_lookups: Mock
    ):
        # Configure the mock return values
        mock_get_table_definition.side_effect = table_definition_outputs
        mock_get_buffer_ids.return_value = get_buffer_ids_return_value
        mock_get_buffer_lookups.return_value = get_buffer_lookups_return_value

        # Call the tested function 
        self.mapper.map_data(mock_data, mock_mappings)

        # Assert that mocked functions were called with the correct data
        self.assertEqual(mock_get_table_definition.mock_calls, table_definition_calls)
        mock_get_buffer_lookups.assert_called_once_with(self.dvh, get_buffer_lookups_params)
        mock_get_buffer_ids.assert_called_once_with(self.dvh, get_buffer_ids_params)
        mock_upsert_bulk.assert_called_once_with(upsert_data_params)


if __name__ == '__main__':
    unittest.main()