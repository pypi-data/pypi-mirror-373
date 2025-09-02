# tests/test_cendat.py

import pytest
import re
from unittest.mock import patch, Mock

from cendat import CenDatHelper, CenDatResponse

# --- 1. Mock Data ---

SIMPLE_PRODUCTS_JSON = {
    "dataset": [
        {
            "title": "American Community Survey",
            "c_isAggregate": "true",
            "c_vintage": 2022,
            "distribution": [{"accessURL": "http://api.census.gov/data/2022/acs/acs5"}],
        },
        {
            "title": "PUMS Household Data",
            "c_isMicrodata": "true",
            "c_vintage": 2022,
            "distribution": [
                {"accessURL": "http://api.census.gov/data/2022/acs/acs5/pums"}
            ],
        },
        {
            "title": "A Timeseries Dataset",  # This product should be filtered out
            "c_isAggregate": "false",
            "c_isMicrodata": "false",
            "c_vintage": 2022,
            "distribution": [
                {"accessURL": "http://api.census.gov/data/2022/timeseries"}
            ],
        },
    ]
}

FAKE_GEOS_JSON = {
    "fips": [
        {"name": "us", "geoLevelDisplay": "010", "requires": None},
        {"name": "state", "geoLevelDisplay": "040", "requires": None},
        {
            "name": "county",
            "geoLevelDisplay": "050",
            "requires": ["state"],
            "wildcard": ["state"],
            "optionalWithWCFor": "state",
        },
        {
            "name": "tract",
            "geoLevelDisplay": "140",
            "requires": ["state", "county"],
            "wildcard": ["county"],
            "optionalWithWCFor": "county",
        },
        {
            "name": "block group",
            "geoLevelDisplay": "150",
            "referenceDate": "2020-01-01",
            "requires": ["state", "county", "tract"],
            "wildcard": ["county", "tract"],
            "optionalWithWCFor": "tract",
        },
        {
            "name": "public use microdata area",
            "geoLevelDisplay": "795",
            "requires": ["state"],
            "optionalWithWCFor": "state",
        },
    ]
}

SIMPLE_VARIABLES_JSON = {
    "variables": {
        "B01001_001E": {
            "label": "Total Population",
            "concept": "SEX BY AGE",
            "group": "B01001",
        },
        "B01001_002E": {
            "label": "Estimate!!Total:!!Male:",
            "concept": "SEX BY AGE",
            "group": "B01001",
        },
        "B19013_001E": {
            "label": "Median Household Income",
            "concept": "INCOME",
            "group": "B19013",
        },
        "PUMA": {
            "label": "Public Use Microdata Area Code",
            "concept": "GEOGRAPHY",
            "group": "GEODATA",
        },
    }
}

SIMPLE_GROUPS_JSON = {
    "groups": [
        {"name": "B01001", "description": "SEX BY AGE"},
        {
            "name": "B19013",
            "description": "MEDIAN HOUSEHOLD INCOME IN THE PAST 12 MONTHS",
        },
        {"name": "GEODATA", "description": "Geographic Identifiers"},
    ]
}

# Add this with your other mock JSON constants
VARIABLES_WITH_ATTRIBUTES_JSON = {
    "variables": {
        "B01001_001E": {
            "label": "Estimate!!Total",
            "concept": "SEX BY AGE",
            "group": "B01001",
            "attributes": "B01001_001EA,B01001_001MA",
        },
        "B01001_002E": {
            "label": "Estimate!!Total!!Male",
            "concept": "SEX BY AGE",
            "group": "B01001",
            "attributes": "N/A",
        },
        "B19013_001E": {
            "label": "Estimate!!Median household income",
            "concept": "MEDIAN HOUSEHOLD INCOME",
            "group": "B19013",
            # This variable is missing the attributes key
        },
    }
}


# --- 2. Pytest Fixtures ---
@pytest.fixture
def cdh():
    """Returns a fresh CenDatHelper instance for each test."""
    return CenDatHelper()


@pytest.fixture
def sample_response():
    """Returns a pre-populated CenDatResponse object for testing its methods."""
    data = [
        {
            "product": "Product A",
            "vintage": [2022],
            "sumlev": "040",
            "desc": "state",
            "schema": ["NAME", "POP"],
            "data": [["Alabama", "5000000"], ["Alaska", "700000"]],
        },
        {
            "product": "Product B",
            "vintage": [2022],
            "sumlev": "050",
            "desc": "county",
            "schema": ["NAME", "POP"],
            "data": [["Autauga County", "58000"]],
        },
    ]
    return CenDatResponse(data)


@pytest.fixture
def tabulation_response():
    """Returns a more complex CenDatResponse object for testing tabulation."""
    data = [
        {
            "product": "Test Survey",
            "vintage": [2022],
            "sumlev": "040",
            "desc": "state",
            "names": ["AGE", "WEIGHT"],  # For destringing
            "schema": ["STATE", "RACE", "AGE", "WEIGHT"],
            "data": [
                ["CA", "White", "25", "100"],
                ["CA", "Black", "35", "120"],
                ["TX", "White", "25", "80"],
                ["TX", "White", "45", "90"],
                ["FL", "Asian", "50", "110"],
            ],
        }
    ]
    return CenDatResponse(data)


# --- 3. Test Functions ---


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_list_products_filters_unsupported_types(mock_get, cdh):
    mock_response = Mock()
    mock_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_get.return_value = mock_response
    products = cdh.list_products()
    assert len(products) == 2  # Should include aggregate and microdata
    assert products[0]["title"] == "American Community Survey (2022/acs/acs5)"
    assert products[1]["title"] == "PUMS Household Data (2022/acs/acs5/pums)"


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_list_variables_with_patterns_and_logic(mock_get, cdh):
    """Tests that the search and filter parameters work correctly."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_variable_response,
        mock_variable_response,
    ]  # Called twice for variables

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    variables = cdh.list_variables(
        patterns=["INCOME", "GEOGRAPHY"], logic=any, match_in="concept"
    )

    # FIX: Check for the presence of the correct names, as order is not guaranteed.
    returned_names = {v["name"] for v in variables}
    expected_names = {"B19013_001E", "PUMA"}

    assert len(variables) == 2
    assert returned_names == expected_names


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch(
    "cendat.CenDatHelper.CenDatHelper._get_json_from_url"
)  # Patch the internal helper
def test_get_data_preview_only_skips_fetching(mock_get_json, mock_get_combos, cdh):
    """Tests that preview_only=True sets n_calls but does not fetch data."""
    # This test is specifically for the preview logic, so we don't need ThreadPoolExecutor
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
    ]
    mock_get_combos.return_value = [{}]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="state", by="desc")
    cdh.set_variables(names="B01001_001E")

    # FIX: The method currently returns None in preview_only mode.
    # This test asserts the current behavior.
    response = cdh.get_data(preview_only=True)

    assert cdh.n_calls == 1
    # Check that the data-fetching part of _get_json_from_url was not called
    assert mock_get_json.call_count == 3  # Only setup calls
    assert isinstance(response, CenDatResponse)
    assert not response._data  # The response should contain no results


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_handles_microdata_correctly(mock_get_json, cdh):
    """Tests that the microdata workflow constructs the correct API call."""
    # Mock the setup calls first
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # Mock the two data calls with valid list-of-lists responses
        [["PUMA", "state"], ["01301", "08"]],
        [["PUMA", "state"], ["01302", "08"]],
    ]

    cdh.set_products(titles="PUMS Household Data (2022/acs/acs5/pums)")
    cdh.set_geos(values="public use microdata area", by="desc")
    cdh.set_variables(names="PUMA")
    response = cdh.get_data(
        within={"state": "08", "public use microdata area": ["01301", "01302"]}
    )

    assert mock_get_json.call_count == 5  # 3 setup calls + 2 data calls

    first_data_call = mock_get_json.call_args_list[-2]
    assert first_data_call.args[1]["for"] == "public use microdata area:01301"
    assert first_data_call.args[1]["in"] == "state:08"

    second_data_call = mock_get_json.call_args_list[-1]
    assert second_data_call.args[1]["for"] == "public use microdata area:01302"
    assert second_data_call.args[1]["in"] == "state:08"

    # Check that a valid response object was created
    assert isinstance(response, CenDatResponse)
    assert len(response._data[0]["data"]) == 2  # Both data rows should be aggregated


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_set_geos_requires_message(mock_get, cdh, capsys):
    mock_product_response = Mock()
    mock_product_response.json.return_value = {
        "dataset": [
            {
                "title": "American Community Survey",
                "c_isAggregate": "true",
                "c_vintage": 2022,
                "distribution": [
                    {"accessURL": "http://api.census.gov/data/2022/acs/acs5"}
                ],
            }
        ]
    }
    mock_product_response.raise_for_status.return_value = None
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_geo_response.raise_for_status.return_value = None
    mock_get.side_effect = [mock_product_response, mock_geo_response]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")

    captured = capsys.readouterr()
    expected_message = (
        "✅ Geographies set: 'tract' (requires `within` for: county, state)\n"
    )
    assert captured.out.endswith(expected_message)


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_expands_within_clauses_correctly(mock_get_json, mock_get_combos, cdh):
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # Mock data responses for the two API calls
        [["B01001_001E"], ["100"]],
        [["B01001_001E"], ["200"]],
    ]
    mock_get_combos.return_value = [{"state": "08", "county": "123"}]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")
    cdh.set_variables(names="B01001_001E")
    response = cdh.get_data(within=[{"state": "08", "county": "123"}, {"state": "56"}])

    assert mock_get_combos.call_count == 0
    assert isinstance(response, CenDatResponse)
    assert len(response._data[0]["data"]) == 2


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_handles_complex_list_expansion(mock_get_json, mock_get_combos, cdh):
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # Mock 4 data responses
        [["B01001_001E"], ["1"]],
        [["B01001_001E"], ["2"]],
        [["B01001_001E"], ["3"]],
        [["B01001_001E"], ["4"]],
    ]
    mock_get_combos.return_value = [{}]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")
    cdh.set_variables(names="B01001_001E")
    response = cdh.get_data(
        within=[{"state": "08", "county": ["069", "123"]}, {"state": ["36", "06"]}]
    )

    assert mock_get_combos.call_count == 0
    assert isinstance(response, CenDatResponse)
    assert len(response._data[0]["data"]) == 4


@pytest.mark.unit
def test_to_pandas_concatenation(sample_response):
    """Tests that concat=True returns a single pandas DataFrame."""
    import pandas as pd

    df = sample_response.to_pandas(concat=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3


@pytest.mark.unit
def test_to_polars_schema_overrides(sample_response):
    """Tests that schema_overrides correctly casts types in Polars."""
    import polars as pl

    df = sample_response.to_polars(schema_overrides={"POP": pl.Int64}, concat=True)
    assert df["POP"].dtype == pl.Int64


# --- 4. New Tests for Tabulation and Where Clauses ---


def find_row_in_output(pattern, text):
    """Helper to find a specific row in the formatted table output."""
    # Find lines that look like table rows │ ... │
    rows = re.findall(r"│(.*?)│", text)
    for row in rows:
        if re.search(pattern, row):
            return True
    return False


@pytest.mark.unit
def test_tabulate_simple_unweighted(tabulation_response, capsys):
    """Tests a simple tabulation without weights."""
    tabulation_response.tabulate("STATE", "RACE")
    captured = capsys.readouterr().out
    assert find_row_in_output(r"CA\s+┆\s+Black\s+┆\s+1", captured)
    assert find_row_in_output(r"CA\s+┆\s+White\s+┆\s+1", captured)
    assert find_row_in_output(r"TX\s+┆\s+White\s+┆\s+2", captured)
    assert find_row_in_output(r"FL\s+┆\s+Asian\s+┆\s+1", captured)


@pytest.mark.unit
def test_tabulate_weighted(tabulation_response, capsys):
    """Tests a tabulation with a weight variable."""
    tabulation_response.tabulate("STATE", weight_var="WEIGHT")
    captured = capsys.readouterr().out
    assert find_row_in_output(r"CA\s+┆\s+220", captured)
    assert find_row_in_output(r"TX\s+┆\s+170", captured)
    assert find_row_in_output(r"FL\s+┆\s+110", captured)


@pytest.mark.unit
def test_tabulate_weighted_with_divisor(tabulation_response, capsys):
    """Tests a tabulation with a weight variable and a divisor."""
    tabulation_response.tabulate("STATE", weight_var="WEIGHT", weight_div=10)
    captured = capsys.readouterr().out
    assert find_row_in_output(r"CA\s+┆\s+22.0", captured)
    assert find_row_in_output(r"TX\s+┆\s+17.0", captured)
    assert find_row_in_output(r"FL\s+┆\s+11.0", captured)


@pytest.mark.unit
def test_tabulate_with_where_clause(tabulation_response, capsys):
    """Tests that the where clause correctly filters data before tabulation."""
    tabulation_response.tabulate("STATE", where="AGE > 30")
    captured = capsys.readouterr().out
    assert find_row_in_output(r"CA\s+┆\s+1", captured)
    assert find_row_in_output(r"TX\s+┆\s+1", captured)
    assert find_row_in_output(r"FL\s+┆\s+1", captured)
    assert "White" not in captured  # The grouping variable is STATE, not RACE


@pytest.mark.unit
def test_where_clause_parser_valid(tabulation_response):
    """Tests that the _build_safe_checker method correctly parses valid conditions."""
    row1 = {"STATE": "CA", "RACE": "White", "AGE": 25, "WEIGHT": 100}
    row2 = {"STATE": "TX", "RACE": "Black", "AGE": 40, "WEIGHT": 120}

    checker_gt = tabulation_response._build_safe_checker("AGE > 30")
    assert not checker_gt(row1)
    assert checker_gt(row2)

    checker_eq = tabulation_response._build_safe_checker("RACE == 'White'")
    assert checker_eq(row1)
    assert not checker_eq(row2)

    checker_in = tabulation_response._build_safe_checker("STATE in ['CA', 'FL']")
    assert checker_in(row1)
    assert not checker_in(row2)


@pytest.mark.unit
def test_where_clause_parser_invalid(tabulation_response):
    """Tests that _build_safe_checker raises ValueError for invalid conditions."""
    # This should fail because the column doesn't exist, leading to a format error
    with pytest.raises(ValueError, match="Invalid condition format"):
        tabulation_response._build_safe_checker("INVALID_COL > 30")

    with pytest.raises(ValueError, match="Invalid condition format"):
        tabulation_response._build_safe_checker("AGE greater than 30")

    with pytest.raises(ValueError, match="Invalid value format"):
        tabulation_response._build_safe_checker("AGE > some_undefined_variable")


@pytest.mark.unit
def test_tabulate_with_multiple_where_clauses_and_any_logic(
    tabulation_response, capsys
):
    """Tests tabulation with a list of where clauses and 'any' logic."""
    tabulation_response.tabulate(
        "STATE", "RACE", where=["AGE < 30", "RACE == 'Asian'"], logic=any
    )
    captured = capsys.readouterr().out
    # Should include two people with AGE < 30 and one person who is Asian
    assert find_row_in_output(r"CA\s+┆\s+White\s+┆\s+1", captured)
    assert find_row_in_output(r"TX\s+┆\s+White\s+┆\s+1", captured)
    assert find_row_in_output(r"FL\s+┆\s+Asian\s+┆\s+1", captured)
    # The Black person in CA (age 35) should be excluded
    assert not find_row_in_output(r"CA\s+┆\s+Black", captured)


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.requests.get")
def test_get_data_with_specific_target_geos(mock_get, mock_get_combos, cdh):
    """
    Tests that get_data bypasses the parent combination search when the
    target geography is specified directly in the `within` clause.
    """
    # --- Arrange ---
    mock_product_response = Mock()
    mock_product_response.json.return_value = {
        "dataset": [
            {
                "title": "American Community Survey",
                "c_isAggregate": "true",
                "c_vintage": 2022,
                "distribution": [
                    {"accessURL": "http://api.census.gov/data/2022/acs/acs5"}
                ],
            }
        ]
    }
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON

    mock_data_response = Mock()
    mock_data_response.json.return_value = [
        ["B01001_001E", "state", "county", "tract"],
        ["1234", "08", "069", "001201"],
    ]

    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
        mock_data_response,
    ]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")
    cdh.set_variables(names="B01001_001E")
    cdh.get_data(within={"state": "08", "county": "069", "tract": "001201"})

    # --- Assert ---
    mock_get_combos.assert_not_called()

    final_call_args = mock_get.call_args
    assert final_call_args.kwargs["params"]["for"] == "tract:001201"
    assert final_call_args.kwargs["params"]["in"] == "state:08 county:069"


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_uses_wildcard_correctly(mock_get_json, mock_get_combos, cdh):
    """
    Tests that get_data correctly uses a wildcard for the most granular,
    unspecified required geography.
    """
    # --- Arrange ---
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # This is the final data call, which we will inspect
        [["B01001_001E", "state", "county", "tract"], ["1234", "08", "069", "001201"]],
    ]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")  # Requires state and county
    cdh.set_variables(names="B01001_001E")
    cdh.get_data(within={"state": "08"})  # Only state is provided

    # --- Assert ---
    # 1. Check that discovery was NOT called, since the logic can proceed directly
    # to building the wildcard query with the provided state.
    mock_get_combos.assert_not_called()

    # 2. Check that the final data-fetching call uses the wildcard for county.
    assert mock_get_json.call_count == 3 + 1  # 3 setup calls, 1 data call

    final_data_call = mock_get_json.call_args_list[-1]
    params = final_data_call.args[1]
    assert params["for"] == "tract:*"
    assert params["in"] == "state:08"


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_uses_wildcard_correctly2(mock_get_json, mock_get_combos, cdh):
    """
    Tests that get_data correctly uses a wildcard for the most granular,
    unspecified required geography.
    """
    # --- Arrange ---
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # This is the final data call, which we will inspect
        [
            ["B01001_001E", "state", "county", "tract", "block group"],
            ["1234", "08", "069", "001201", "1"],
        ],
    ]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="block group", by="desc")  # Requires state and county
    cdh.set_variables(names="B01001_001E")
    cdh.get_data(within={"state": "08"})  # Only state is provided

    # --- Assert ---
    # 1. Check that discovery was NOT called, since the logic can proceed directly
    # to building the wildcard query with the provided state.
    mock_get_combos.assert_not_called()

    # 2. Check that the final data-fetching call uses the wildcard for county.
    assert mock_get_json.call_count == 3 + 1  # 3 setup calls, 1 data call

    final_data_call = mock_get_json.call_args_list[-1]
    params = final_data_call.args[1]
    assert params["for"] == "block group:*"
    assert params["in"] == "state:08 county:*"


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_wildcard_with_us_scope(mock_get_json, mock_get_combos, cdh):
    """
    Tests the 'Everything' case: a granular geo with no 'within' clause,
    triggering state discovery followed by wildcard calls for each state.
    """
    # --- Arrange ---
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        [["B01001_001E"], ["100"]],  # Data for state 01
        [["B01001_001E"], ["200"]],  # Data for state 02
    ]
    # Mock the discovery of states
    mock_get_combos.return_value = [{"state": "01"}, {"state": "02"}]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="tract", by="desc")  # Requires state and county
    cdh.set_variables(names="B01001_001E")
    cdh.get_data()  # No parent geos provided

    # --- Assert ---
    # 1. Discovery should be called once to find all states
    mock_get_combos.assert_called_once()
    assert mock_get_combos.call_args.args[1] == ["state"]  # Should fetch states

    # 2. Two data calls should be made, one for each discovered state
    assert mock_get_json.call_count == 3 + 2

    call1_params = mock_get_json.call_args_list[-2].args[1]
    call2_params = mock_get_json.call_args_list[-1].args[1]

    assert call1_params["for"] == "tract:*"
    assert call1_params["in"] == "state:01"
    assert call2_params["for"] == "tract:*"
    assert call2_params["in"] == "state:02"


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_no_requirements_bypasses_wildcard(
    mock_get_json, mock_get_combos, cdh
):
    """
    Tests that a geography with no requirements (like 'state') bypasses
    the wildcard and discovery logic entirely.
    """
    # --- Arrange ---
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        [["B01001_001E", "state"], ["1234", "01"]],
    ]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="state", by="desc")  # No requirements
    cdh.set_variables(names="B01001_001E")
    cdh.get_data()  # Default within='us'

    # --- Assert ---
    mock_get_combos.assert_not_called()

    assert mock_get_json.call_count == 3 + 1
    final_call_params = mock_get_json.call_args.args[1]
    assert final_call_params["for"] == "state:*"
    assert "in" not in final_call_params


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_parent_geo_combinations")
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_single_requirement_uses_wildcard(mock_get_json, mock_get_combos, cdh):
    """
    Tests that a geo with a single requirement uses a wildcard for that
    requirement if it's not provided.
    """
    # --- Arrange ---
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        [["B01001_001E", "state", "county"], ["1234", "01", "001"]],
    ]

    # --- Act ---
    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="county", by="desc")  # Requires 'state'
    cdh.set_variables(names="B01001_001E")
    cdh.get_data()  # Default within='us'

    # --- Assert ---
    mock_get_combos.assert_not_called()

    assert mock_get_json.call_count == 3 + 1
    final_call_params = mock_get_json.call_args.args[1]
    assert final_call_params["for"] == "county:*"
    assert "in" not in final_call_params


@pytest.mark.unit
@patch("cendat.CenDatHelper.CenDatHelper._get_json_from_url")
def test_get_data_include_names_adds_name_to_api_call(mock_get_json, cdh):
    """
    Tests that get_data(include_names=True) correctly prepends 'NAME' to the
    'get' parameter in the final API call.
    """
    # --- Arrange ---
    # Mock the sequence of JSON metadata calls, followed by the final data call
    mock_get_json.side_effect = [
        SIMPLE_PRODUCTS_JSON,
        FAKE_GEOS_JSON,
        SIMPLE_VARIABLES_JSON,
        # Mock data response for the final API call we will inspect
        [["NAME", "B01001_001E", "state"], ["Colorado", "5877610", "08"]],
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="state", by="desc")
    cdh.set_variables(names="B01001_001E")

    # --- Act ---
    cdh.get_data(include_names=True)

    # --- Assert ---
    # The last call to the mock should be the actual data request
    final_call = mock_get_json.call_args
    # The call arguments are passed as a tuple (url, params_dict)
    api_params = final_call[0][1]

    # Check that 'NAME' was added to the 'get' string, before the data variable
    assert api_params["get"] == "NAME,B01001_001E"


# --- 5. New Tests for Group Methods ---


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_list_groups(mock_get, cdh):
    """Tests the list_groups method for correctness and filtering."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_group_response = Mock()
    mock_group_response.json.return_value = SIMPLE_GROUPS_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_group_response,
        mock_group_response,
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")

    # Test listing all groups
    groups = cdh.list_groups(to_dicts=False)
    assert "B01001" in groups
    assert "B19013" in groups
    assert len(groups) == 3

    # Test filtering with a pattern
    groups_filtered = cdh.list_groups(patterns="SEX BY AGE", to_dicts=False)
    assert "B01001" in groups_filtered
    assert len(groups_filtered) == 1


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_set_groups(mock_get, cdh):
    """Tests the set_groups method."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_group_response = Mock()
    mock_group_response.json.return_value = SIMPLE_GROUPS_JSON
    mock_get.side_effect = [
        mock_product_response,
        mock_group_response,
        mock_group_response,
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")

    # Set groups by name
    cdh.set_groups(names=["B01001", "GEODATA"])
    assert len(cdh.groups) == 2
    group_names = {g["name"] for g in cdh.groups}
    assert {"B01001", "GEODATA"} == group_names

    # Set groups from cache after listing
    cdh.list_groups(patterns="INCOME")
    cdh.set_groups()  # Should use the cached result
    assert len(cdh.groups) == 1
    assert cdh.groups[0]["name"] == "B19013"


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_list_variables_with_group_filters(mock_get, cdh):
    """Tests the group filtering logic in list_variables."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_group_response = Mock()
    mock_group_response.json.return_value = SIMPLE_GROUPS_JSON

    # Setup the sequence of mock calls
    mock_get.side_effect = [
        mock_product_response,
        mock_variable_response,  # for list_variables(groups="B01001")
        mock_group_response,  # for list_groups() inside set_groups("B19013")
        mock_variable_response,  # for list_variables() after set_groups()
        mock_variable_response,  # for the override test
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")

    # Test with 'groups' parameter
    variables = cdh.list_variables(groups="B01001", to_dicts=False)
    assert "B01001_001E" in variables
    assert "B01001_002E" in variables
    assert "B19013_001E" not in variables
    assert len(variables) == 2

    # Test with pre-set groups on the object
    cdh.set_groups(names="B19013")
    variables_from_set = cdh.list_variables(to_dicts=False)
    assert "B19013_001E" in variables_from_set
    assert len(variables_from_set) == 1

    # Test that providing 'groups' parameter overrides set_groups
    variables_overridden = cdh.list_variables(groups="GEODATA", to_dicts=False)
    assert "PUMA" in variables_overridden
    assert len(variables_overridden) == 1


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_describe_groups(mock_get, cdh, capsys):
    """Tests the describe_groups method for correct formatting and output."""
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = SIMPLE_VARIABLES_JSON
    mock_group_response = Mock()
    mock_group_response.json.return_value = SIMPLE_GROUPS_JSON

    mock_get.side_effect = [
        mock_product_response,
        mock_variable_response,  # for list_variables
        mock_group_response,  # for list_groups
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")

    cdh.describe_groups(groups="B01001")
    captured = capsys.readouterr().out

    # Check for correct headers
    assert "--- Group: B01001 (SEX BY AGE) ---" in captured
    assert "Product: American Community Survey" in captured

    # Check for correct variable formatting and indentation
    # Using regex to be flexible with whitespace
    assert re.search(r"B01001_001E:\s+Total Population", captured)
    assert re.search(r"\s{4}B01001_002E:\s+Male:", captured)


@pytest.mark.unit
@pytest.mark.parametrize(
    "include_flag, expected_vars_set",
    [
        (
            True,
            {
                "B01001_001E",
                "B01001_002E",
                "B19013_001E",
                "B01001_001EA",
                "B01001_001MA",
            },
        ),
        (
            False,
            {"B01001_001E", "B01001_002E", "B19013_001E"},
        ),
    ],
    ids=["include_attributes=True", "include_attributes=False"],
)
@patch("cendat.CenDatHelper.requests.get")
def test_get_data_handles_include_attributes(
    mock_get, cdh, include_flag, expected_vars_set
):
    """
    Tests that `get_data` correctly handles the `include_attributes` flag,
    properly requesting annotation/margin-of-error variables when True and
    correctly ignoring "N/A" or missing attribute fields.
    """
    # --- Arrange ---
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = VARIABLES_WITH_ATTRIBUTES_JSON
    mock_data_response = Mock()
    mock_data_response.json.return_value = [["header"], ["data"]]

    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
        mock_data_response,
    ]

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="state", by="desc")
    # Select one var with attributes, one with "N/A", and one with no attribute key
    cdh.set_variables(names=["B01001_001E", "B01001_002E", "B19013_001E"])

    # --- Act ---
    cdh.get_data(within="us", include_attributes=include_flag)

    # --- Assert ---
    # The final call to requests.get should be the actual data call
    final_params = mock_get.call_args.kwargs.get("params", {})
    requested_vars_str = final_params.get("get", "")
    requested_vars_set = set(requested_vars_str.split(","))

    # Check that the set of requested variables matches the expected set
    assert requested_vars_set == expected_vars_set


@pytest.mark.unit
@patch("cendat.CenDatHelper.requests.get")
def test_get_data_handles_names_and_attributes_together(mock_get, cdh):
    """
    Tests that `get_data` correctly includes both NAME and attribute
    variables when both flags are True.
    """
    # --- Arrange ---
    mock_product_response = Mock()
    mock_product_response.json.return_value = SIMPLE_PRODUCTS_JSON
    mock_geo_response = Mock()
    mock_geo_response.json.return_value = FAKE_GEOS_JSON
    mock_variable_response = Mock()
    mock_variable_response.json.return_value = VARIABLES_WITH_ATTRIBUTES_JSON
    mock_data_response = Mock()
    mock_data_response.json.return_value = [["header"], ["data"]]

    mock_get.side_effect = [
        mock_product_response,
        mock_geo_response,
        mock_variable_response,
        mock_data_response,
    ]

    expected_vars_set = {"NAME", "B01001_001E", "B01001_001EA", "B01001_001MA"}

    cdh.set_products(titles="American Community Survey (2022/acs/acs5)")
    cdh.set_geos(values="state", by="desc")
    cdh.set_variables(names=["B01001_001E"])  # Just one variable with attributes

    # --- Act ---
    cdh.get_data(within="us", include_attributes=True, include_names=True)

    # --- Assert ---
    final_params = mock_get.call_args.kwargs.get("params", {})
    requested_vars_str = final_params.get("get", "")
    requested_vars_set = set(requested_vars_str.split(","))

    assert requested_vars_set == expected_vars_set
