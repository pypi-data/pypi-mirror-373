# cendat: A Python Helper for the Census API

## Introduction

`cendat` is a Python library designed to simplify the process of exploring and retrieving data from the U.S. Census Bureau’s API. It provides a high-level, intuitive workflow for discovering available datasets, filtering geographies and variables, and fetching data concurrently.

The library handles the complexities of the Census API’s structure, such as geographic hierarchies and inconsistent product naming, allowing you to focus on getting the data you need.

You can find regular `cendat` updates and musings on the [developer blog](https://mostlyunoriginal.github.io/posts.html#category=cendat).

## Workflow

The library is designed around a simple, four-step “List -\> Set -\> Get -\> Convert/Analyze” workflow:

1.  **List**: Use the `list_*` methods (`list_products`, `list_geos`, `list_groups`, `list_variables`) with patterns to explore what’s available and filter down to what you need.
2.  **Set**: Use the `set_*` methods (`set_products`, `set_geos`, `set_groups`, `set_variables`) to lock in your selections. You can call these methods without arguments to use the results from your last “List” call. The `describe_groups` method is especially helpful for variable selection in programs with many variables, like the ACS.
3.  **Get**: Call the `get_data()` method to build and execute all the necessary API calls. This method handles complex geographic requirements automatically and utilizes thread pooling for speed.
4.  **Convert & Analyze**: Use the `to_polars()` or `to_pandas()` methods on the response object to get your data in a ready-to-use DataFrame format. The response object also includes a powerful `tabulate()` method for quick, Stata-like frequency tables.

------------------------------------------------------------------------

# Installation

You can install `cendat` using pip.

``` bash
pip install cendat
```

The library has optional dependencies for converting the response data into pandas or polars DataFrames. You can install the support you need:

### Install with pandas support

``` bash
pip install cendat[pandas]
```

### Install with polars support

``` bash
pip install cendat[polars]
```

### Install with both

``` bash
pip install cendat[all]
```

------------------------------------------------------------------------

# API Reference

## `CenDatHelper` Class

This is the main class for building and executing queries.

### `__init__(self, years=None, key=None)`

Initializes the helper object.

-   **`years`** (`int` \| `list[int]`, optional): The year or years of interest. Can be a single integer or a list of integers. Defaults to `None`.
-   **`key`** (`str`, optional): Your Census API key. Providing a key is recommended to avoid strict rate limits. Defaults to `None`.

### `set_years(self, years)`

Sets the primary year or years for data queries.

-   **`years`** (`int` \| `list[int]`): The year or years to set.

### `load_key(self, key=None)`

Loads a Census API key for authenticated requests.

-   **`key`** (`str`, optional): The API key to load.

### `list_products(self, years=None, patterns=None, to_dicts=True, logic=all, match_in='title')`

Lists available data products, filtered by year and search patterns.

-   **`years`** (`int` \| `list[int]`, optional): Filters products available for the specified year(s). Defaults to the years set on the object.
-   **`patterns`** (`str` \| `list[str]`, optional): Regex pattern(s) to search for within the product metadata.
-   **`to_dicts`** (`bool`): If `True` (default), returns a list of dictionaries with full product details. If `False`, returns a list of product titles.
-   **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.
-   **`match_in`** (`str`): The field to match patterns against. Can be `'title'` (default) or `'desc'`.

### `set_products(self, titles=None)`

Sets the active data products for the session.

-   **`titles`** (`str` \| `list[str]`, optional): The title or list of titles of the products to set. If `None`, it sets all products from the last `list_products()` call.

### `list_geos(self, to_dicts=False, patterns=None, logic=all)`

Lists available geographies for the currently set products.

-   **`to_dicts`** (`bool`): If `True`, returns a list of dictionaries with full geography details. If `False` (default), returns a list of unique summary level (`sumlev`) strings.
-   **`patterns`** (`str` \| `list[str]`, optional): Regex pattern(s) to search for within the geography description.
-   **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.

### `set_geos(self, values=None, by='sumlev')`

Sets the active geographies for the session.

-   **`values`** (`str` \| `list[str]`, optional): The geography values to set. If `None`, sets all geos from the last `list_geos()` call.
-   **`by`** (`str`): The key to use for matching `values`. Must be either `'sumlev'` (default) or `'desc'`.

### `list_groups(self, to_dicts=True, patterns=None, logic=all, match_in='description')`

Lists available variable groups for the currently set products. Not all products have groups, in which case the resulting list will be empty.

-   **`to_dicts`** (`bool`): If `True` (default), returns a list of dictionaries with full group details. If `False`, returns a list of unique group names.
-   **`patterns`** (`str` \| `list[str]`, optional): Regex pattern(s) to search for within the group metadata.
-   **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.
-   **`match_in`** (`str`): The field to match patterns against. Can be `'description'` (default) or `'name'`.

### `set_groups(self, names=None)`

Sets the active variable groups for the session. If the call to `set_groups` results in a single group for each product vintage and all group variables are wanted, `set_variables` may be skipped.

-   **`names`** (`str` \| `list[str]`, optional): The name or list of names of the groups to set. If `None`, sets all groups from the last `list_groups()` call.

### `describe_groups(self, groups=None)`

Print hierarchically-nested group descriptions to facilitate variable selection.

-   **`groups`** (`str` \| `list[str]`, optional): The name or list of names of the groups to describe. If `None`, describes all set groups or reports an error with instructions to set groups or use the `groups` parameter.

### `list_variables(self, to_dicts=True, patterns=None, logic=all, match_in='label', groups=None)`

Lists available variables for the currently set products.

-   **`to_dicts`** (`bool`): If `True` (default), returns a list of dictionaries with full variable details. If `False`, returns a list of unique variable names.
-   **`patterns`** (`str` \| `list[str]`, optional): Regex pattern(s) to search for within the variable metadata.
-   **`logic`** (`callable`): The logic to use when multiple patterns are provided. Can be `all` (default) or `any`.
-   **`match_in`** (`str`): The field to match patterns against. Can be `'label'` (default), `'name'` or `'concept'`.
-   **`groups`** (`str` \| `list[str]`, optional): Variable groups within which the listing will be limited. Groups provided here override whatever groups may be set, and set groups will be used if this is `None`.

### `set_variables(self, names=None)`

Sets the active variables for the session. If exactly one group is set for each product vintage and all group variables are wanted, `set_variables` may be skipped. Doing so allows for more than the standard API max of 50 variables.

-   **`names`** (`str` \| `list[str]`, optional): The name or list of names of the variables to set. If `None`, sets all variables from the last `list_variables()` call.

### `get_data(self, within='us', max_workers=100, timeout=30, preview_only=False, include_names=False, include_geoids=False, include_attributes=False)`

Executes the API calls based on the set parameters and retrieves the data.

-   **`within`** (`str` \| `dict` \| `list[dict]`, optional): Defines the geographic scope of the query.
    -   For **aggregate** data, this can be a dictionary filtering parent geographies (e.g., `{'state': '06'}` for California). A list of dictionaries can be provided to query multiple scopes.
    -   For **microdata**, this must be a dictionary specifying the target geography and its codes (e.g., `{'public use microdata area': ['7701', '7702']}`).
    -   Defaults to `'us'` for nationwide data where applicable.
-   **`max_workers`** (`int`, optional): The maximum number of concurrent threads to use for making API calls. For requests generating thousands of calls, it's wise to keep this value lower (e.g., `< 100`) to avoid server-side connection issues. Defaults to `100`.
-   **`timeout`** (`int`, optional): Request timeout in seconds for each API call. Defaults to `30`.
-   **`preview_only`** (`bool`, optional): If `True`, builds the list of API calls but does not execute them. Useful for debugging. Defaults to `False`.
-   **`include_names`** (`bool`, optional): If `True`, includes geography name (`NAME`) in API request--this variable is a special keyword understood by the data endpoint but is not included in `variables.json` and is therefore not discoverable through `list_variables()`. Note that NAME requests for microdata products will be ignored (with a message). Defaults to `False`.
-   **`include_geoids`** (`bool`, optional): If `True`, includes geography ID (`GEO_ID`) in API request--this variable is a special keyword understood by the data endpoint but is not included in `variables.json` and is therefore not discoverable through `list_variables()`. Note that GEO_ID requests for microdata products will be ignored (with a message). Defaults to `False`.
-   **`include_attributes`** (`bool`, optional): If `True`, includes attributes associated with set variables (e.g., margins of error) in API request if available. Defaults to `False`.

------------------------------------------------------------------------

## `CenDatResponse` Class

A container for the data returned by `CenDatHelper.get_data()`.

### `to_polars(self, schema_overrides=None, concat=False, destring=False)`

Converts the raw response data into a list of Polars DataFrames.

-   **`schema_overrides`** (`dict`, optional): A dictionary mapping column names to Polars data types to override the inferred schema. Example: `{'POP': pl.Int64}`.
-   **`concat`** (`bool`): If `True`, concatenates all resulting DataFrames into a single DataFrame. Defaults to `False`.
-   **`destring`** (`bool`): If `True`, attempts to convert string representations of numbers into native numeric types. Defaults to `False`.

### `to_pandas(self, dtypes=None, concat=False, destring=False)`

Converts the raw response data into a list of Pandas DataFrames.

-   **`dtypes`** (`dict`, optional): A dictionary mapping column names to Pandas data types, which is passed to the `.astype()` method. Example: `{'POP': 'int64'}`.
-   **`concat`** (`bool`): If `True`, concatenates all resulting DataFrames into a single DataFrame. Defaults to `False`.
-   **`destring`** (`bool`): If `True`, attempts to convert string representations of numbers into native numeric types. Defaults to `False`.

### `tabulate(self, *variables, strat_by=None, weight_var=None, weight_div=None, where=None, logic=all, digits=1)`

Generates and prints a frequency table.

-   **`*variables`** (`str`): One or more column names to include in the tabulation.
-   **`strat_by`** (`str`, optional): A column name to stratify the results by. Percentages and cumulative stats will be calculated within each stratum. Defaults to `None`.
-   **`weight_var`** (`str`, optional): The name of the column to use for weighting. If `None`, each row has a weight of 1. Defaults to `None`.
-   **`weight_div`** (`int`, optional): A positive integer to divide the weight by, useful for pooled tabulations across multiple product vintages. `weight_var` must be provided if this is used. Defaults to `None`.
-   **`where`** (`str` \| `list[str]`, optional): A string or list of strings representing conditions to filter the data before tabulation. Each condition should be in a format like `"variable operator value"` (e.g., `"AGE > 30"`) or `"variable1 / variable2 operator value"` (e.g., `"B17001_002E / B17001_001E < 0.01"`). Defaults to `None`.
-   **`logic`** (`callable`): The function to apply when multiple `where` conditions are provided. Use `all` for AND logic (default) or `any` for OR logic.
-   **`digits`** (`int`): The number of decimal places to display for floating-point numbers in the output table. Defaults to `1`.

------------------------------------------------------------------------

# Usage Examples

``` python
import os
from cendat import CenDatHelper
from dotenv import load_dotenv

load_dotenv()

# --- ACS PUMS ANALYSIS ---

# 1. Initialize and set up the query
cdh = CenDatHelper(years=[2022], key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(patterns=r"acs/acs1/pums\b")
cdh.set_products()
cdh.set_geos(values="state", by="desc")
cdh.set_variables(names=["SEX", "AGEP", "ST", "PWGTP"])

# 2. Get data for two states
response = cdh.get_data(
    within={"state": ["06", "48"]}, # California and Texas
)

# 3. Create a stratified tabulation
print("Age Distribution by Sex, Stratified by State")
response.tabulate(
    "SEX", "AGEP",
    strat_by="ST",
    weight_var="PWGTP",
    where="AGEP > 17" # Filter for adults
)

# 4. Convert to DataFrame for further analysis
df = response.to_polars(concat=True, destring=True)
print(df.head())

# --- ACS 5YR AGGREGATE ANALYSIS ---

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(years=[2023], patterns=r"acs/acs5\)")
cdh.set_products()
cdh.list_groups(patterns="sex by age")
cdh.set_groups("B17001")
cdh.describe_groups()
cdh.set_variables(["B17001_001E", "B17001_002E"])
cdh.set_geos(["160"])
response = cdh.get_data(
    include_names=True,
    include_attributes=True,
)
df = response.to_polars(concat=True, destring=True)
df.glimpse()

# --- ACS 5YR AGGREGATE ANALYSIS ---

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(years=[2023], patterns=r"/acs/acs5\)")
cdh.set_products()
cdh.set_variables("B01001_001E")  # total population
cdh.set_geos("150")
response = cdh.get_data()

# how many counties
response.tabulate("state", where="B01001_001E > 10_000")

# how many people in those counties
response.tabulate("state", weight_var="B01001_001E", where="B01001_001E > 10_000")

# --- CPS MICRODATA ANALYSIS ---

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(years=[2022, 2023], patterns="/cps/tobacco")
cdh.set_products()
cdh.list_groups()
cdh.set_variables(["PEA1", "PEA3", "PWNRWGT"])
cdh.set_geos("state", "desc")
response = cdh.get_data(within={"state": ["06", "48"]})
response.tabulate(
    "PEA1",
    "PEA3",
    strat_by="state",
    weight_var="PWNRWGT",
    weight_div=3,
)

# --- ACS ANALYSIS: see Colorado incorporated places with very low poverty across years ---

cdh = CenDatHelper(key=os.getenv("CENSUS_API_KEY"))
cdh.list_products(years=[2020, 2021, 2022, 2023], patterns=r"acs/acs5\)")
cdh.set_products()
cdh.list_groups(patterns="sex by age")
cdh.set_groups(["B17001"])
cdh.describe_groups()
cdh.set_geos(["160"])
response = cdh.get_data(
    include_names=True,
    within={"state": "08"},
)

response.tabulate(
    "NAME",
    "B17001_002E",
    "B17001_001E",
    where=[
        "B17001_001E > 1_000",
        "B17001_002E / B17001_001E < 0.01",
        "'CDP' not in NAME",
    ],
    weight_var="B17001_001E",
    strat_by="vintage",
)

```