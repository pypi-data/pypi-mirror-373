import re
import operator
import ast
from typing import List, Union, Dict, Optional, Callable


class CenDatResponse:
    """
    A container for data returned by CenDatHelper.get_data().

    This class holds the raw JSON response from the Census API and provides
    methods to easily filter, tabulate, and convert the data into Polars or
    Pandas DataFrames for analysis.

    Attributes:
        _data (List[Dict]): The raw data structure from the API calls.
        all_columns (set): A set of all unique column names found in the data.
    """

    def __init__(self, data: List[Dict]):
        """
        Initializes the CenDatResponse object.

        Args:
            data (List[Dict]): The list of dictionaries representing the
                                 API response data, typically from CenDatHelper.
        """
        self._data = data
        self.OPERATOR_MAP = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
            "in": lambda a, b: a in b,
            "not in": lambda a, b: a not in b,
        }
        self.ALLOWED_OPERATORS = set(self.OPERATOR_MAP.keys())
        self.all_columns = set(
            col for item in self._data for col in item.get("schema", [])
        )

    def _build_safe_checker(self, condition_string: str) -> Callable:
        """
        Parses a condition string and returns a function to check it.

        This internal method uses regex to safely parse a condition like
        "AGE > 50" or "10 in MY_VAR", validates the column name and operator,
        and returns a callable function that can be applied to a data row (dict).

        Args:
            condition_string (str): The condition to parse (e.g., "POP >= 1000").

        Returns:
            Callable: A function that takes a dictionary row and returns True or False.

        Raises:
            ValueError: If the condition string format, column name, or value
                        is invalid.
        """

        if not self.all_columns:
            # Fallback or handle case with no data/names
            all_columns_pattern = ""
        else:
            # FIX: Add re.escape() to handle column names with special regex characters.
            all_columns_pattern = "|".join(re.escape(col) for col in self.all_columns)

        sorted_operators = sorted(self.ALLOWED_OPERATORS, key=len, reverse=True)
        operators_pattern = "|".join(re.escape(op) for op in sorted_operators)

        patternL = re.compile(
            r"^\s*("
            + all_columns_pattern
            + r")\s*("
            + operators_pattern
            + r")\s*(.+?)\s*$"
        )
        patternR = re.compile(
            r"^\s*(.+?)\s*("
            + operators_pattern
            + r")\s*("
            + all_columns_pattern
            + r")\s*$"
        )
        patternFrac = re.compile(
            r"^\s*(("
            + all_columns_pattern
            + r")\s*/\s*("
            + all_columns_pattern
            + r"))\s*("
            + operators_pattern
            + r")\s*(.+?)\s*$"
        )
        matchL = patternL.match(condition_string)
        matchR = patternR.match(condition_string)
        matchFrac = patternFrac.match(condition_string)

        if not (matchL or matchR or matchFrac):
            raise ValueError(f"Invalid condition format: '{condition_string}'")

        if matchL:
            variable, op_string, value_string = matchL.groups()
        elif matchR:
            value_string, op_string, variable = matchR.groups()
        else:
            discard, numerator, denominator, op_string, value_string = (
                matchFrac.groups()
            )

        if (matchL or matchR) and variable not in self.all_columns:
            raise ValueError(f"Invalid column name: '{variable}'")
        elif matchFrac and numerator not in self.all_columns:
            raise ValueError(f"Invalid column name: '{numerator}'")
        elif matchFrac and denominator not in self.all_columns:
            raise ValueError(f"Invalid column name: '{denominator}'")

        op_func = self.OPERATOR_MAP[op_string]

        try:
            value = ast.literal_eval(value_string)
        except (ValueError, SyntaxError):
            raise ValueError(f"Invalid value format: '{value_string}'")

        if matchL:
            return lambda row: (op_func(row[variable], value))
        elif matchR:
            return lambda row: (op_func(value, row[variable]))
        else:
            # Safely handle division by zero. If the denominator is 0, the condition is False.
            return lambda row: (
                op_func(row[numerator] / row[denominator], value)
                if row[denominator] != 0
                else False
            )

    def _prepare_dataframe_data(self, destring: bool, _data: Optional[List[Dict]]):
        """
        Prepares and yields data for DataFrame conversion.

        This internal generator iterates through the data source, handles the
        'destringing' of values (converting string numbers to numeric types),
        and yields the processed data in a format suitable for DataFrame
        constructors.

        Args:
            destring (bool): If True, attempts to convert string representations
                             of numbers into native numeric types.
            _data (Optional[List[Dict]]): An optional alternative data source to
                                           process, used internally by `tabulate`.

        Yields:
            tuple: A tuple containing the source item (dict), the processed data
                   (list of lists or list of dicts), and the orientation
                   ("row" or "dicts").
        """
        data_source = _data if _data is not None else self._data

        for item in data_source:
            if not item.get("data"):
                continue  # Skip if no data was returned for this parameter set

            if not destring:
                yield item, item["data"], "row"
            else:
                # Create a list of dictionaries and evaluate string values to native types
                processed_data = []
                for row in item["data"]:
                    row_dict = {}
                    # Use schema to ensure all columns are included in the dict
                    for k, v in zip(item.get("schema", []), row):
                        # Check if the column is a variable that should be destringed
                        if isinstance(v, str) and (
                            k in item.get("names", [])
                            or k
                            in [
                                var
                                for sub in item.get("attributes", [])
                                for var in sub.split(",")
                            ]
                            or item.get("group_name", "N/A") in k
                        ):
                            try:
                                row_dict[k] = ast.literal_eval(v)
                            except (ValueError, SyntaxError):
                                row_dict[k] = v  # Keep as string if eval fails

                        else:
                            row_dict[k] = v
                    processed_data.append(row_dict)
                yield item, processed_data, "dicts"

    def to_polars(
        self,
        schema_overrides: Optional[Dict] = None,
        concat: bool = False,
        destring: bool = False,
        *,
        _data=None,
    ) -> Union[List["pl.DataFrame"], "pl.DataFrame"]:
        """
        Converts the response data into Polars DataFrames.

        Each distinct API call result is converted into its own DataFrame.
        Contextual columns (product, vintage, etc.) are added automatically.

        Args:
            schema_overrides (dict, optional): A dictionary to override inferred
                Polars schema types. Passed directly to pl.DataFrame().
                Example: {'POP': pl.Int64, 'GEO_ID': pl.Utf8}.
            concat (bool): If True, concatenates all resulting DataFrames into a
                single DataFrame. Defaults to False.
            destring (bool): If True, attempts to convert string representations
                of numbers into native numeric types. Defaults to False.
            _data: For internal use by other methods. Do not set manually.

        Returns:
            Union[List[pl.DataFrame], pl.DataFrame]: A list of Polars DataFrames,
            or a single concatenated DataFrame if `concat=True`. Returns an empty
            list if Polars is not installed or no data is available.
        """
        try:
            import polars as pl
        except ImportError:
            print(
                "❌ Polars is not installed. Please install it with 'pip install polars'"
            )
            return []

        dataframes = []
        for item, processed_data, orient in self._prepare_dataframe_data(
            destring, _data
        ):
            df = pl.DataFrame(
                processed_data,
                schema=item["schema"],
                orient=orient,
                schema_overrides=schema_overrides,
            )

            # Add context columns
            df = df.with_columns(
                [
                    pl.lit(item["product"]).alias("product"),
                    pl.lit(item["vintage"][0]).cast(str).alias("vintage"),
                    pl.lit(item["sumlev"]).alias("sumlev"),
                    pl.lit(item["desc"]).alias("desc"),
                ]
            )
            dataframes.append(df)

        if not dataframes:
            return []

        return pl.concat(dataframes, how="diagonal") if concat else dataframes

    def to_pandas(
        self,
        dtypes: Optional[Dict] = None,
        concat: bool = False,
        destring: bool = False,
        *,
        _data=None,
    ) -> Union[List["pd.DataFrame"], "pd.DataFrame"]:
        """
        Converts the response data into Pandas DataFrames.

        Each distinct API call result is converted into its own DataFrame.
        Contextual columns (product, vintage, etc.) are added automatically.

        Args:
            dtypes (dict, optional): A dictionary of column names to data types,
                passed to the pandas.DataFrame.astype() method.
                Example: {'POP': 'int64', 'GEO_ID': 'str'}.
            concat (bool): If True, concatenates all resulting DataFrames into a
                single DataFrame. Defaults to False.
            destring (bool): If True, attempts to convert string representations
                of numbers into native numeric types. Defaults to False.
            _data: For internal use by other methods. Do not set manually.

        Returns:
            Union[List[pd.DataFrame], pd.DataFrame]: A list of Pandas DataFrames,
            or a single concatenated DataFrame if `concat=True`. Returns an empty
            list if Pandas is not installed or no data is available.
        """
        try:
            import pandas as pd
        except ImportError:
            print(
                "❌ Pandas is not installed. Please install it with 'pip install pandas'"
            )
            return []

        dataframes = []
        for item, processed_data, orient in self._prepare_dataframe_data(
            destring, _data
        ):
            # Pandas DataFrame constructor can handle both orientations
            df = pd.DataFrame(
                processed_data, columns=item["schema"] if orient == "row" else None
            )

            if dtypes:
                df = df.astype(dtypes, errors="ignore")

            # Add context columns
            df["product"] = item["product"]
            df["vintage"] = item["vintage"][0]
            df["vintage"] = df["vintage"].astype("string")
            df["sumlev"] = item["sumlev"]
            df["desc"] = item["desc"]
            dataframes.append(df)

        if not dataframes:
            return []

        return pd.concat(dataframes, ignore_index=True) if concat else dataframes

    def tabulate(
        self,
        *variables: str,
        strat_by: Optional[str] = None,
        weight_var: Optional[str] = None,
        weight_div: Optional[int] = None,
        where: Optional[Union[str, List[str]]] = None,
        logic: Callable = all,
        digits: int = 1,
    ):
        """
        Generates and prints a frequency table for specified variables.

        This method creates a crosstabulation, similar to Stata's `tab` command,
        calculating counts, percentages, and cumulative distributions. It can
        dynamically use either the Polars or Pandas library for data manipulation,
        whichever is available.

        Args:
            *variables (str): One or more column names to include in the tabulation.
            strat_by (Optional[str]): A column name to stratify the results by.
                Percentages and cumulative stats will be calculated within each
                stratum. Defaults to None.
            weight_var (Optional[str]): The name of the column to use for weighting.
                If None, each row has a weight of 1. Defaults to None.
            weight_div (Optional[int]): A positive integer to divide the weight by,
                useful for pooled tabulations across multiple product vintages.
                `weight_var` must be provided if this is used. Defaults to None.
            where (Optional[Union[str, List[str]]]): A string or list of strings
                representing conditions to filter the data before tabulation.
                Each condition should be in a format like "variable operator value"
                (e.g., "age > 30"). Defaults to None.
            logic (Callable): The function to apply when multiple `where` conditions
                are provided. Use `all` for AND logic (default) or `any` for OR logic.
            digits (int): The number of decimal places to display for floating-point
                numbers in the output table. Defaults to 1.
        """
        try:
            import polars as pl

            df_lib = "pl"
        except ImportError:
            try:
                import pandas as pd

                df_lib = "pd"
            except ImportError:
                print(
                    "❌ Neither Polars nor Pandas are installed. Please install "
                    "whichever you prefer to proceed with tabulations"
                )
                return

        bad_vars = [
            variable
            for variable in variables
            if variable
            not in self.all_columns.union({"product", "vintage", "sumlev", "desc"})
        ]
        if bad_vars:
            print(
                f"❌ Cross-tabulation variables {bad_vars} not found in available variables."
            )
            return

        if strat_by and strat_by not in self.all_columns.union(
            {"product", "vintage", "sumlev", "desc"}
        ):
            print(
                f"❌ Stratification variable '{strat_by}' not found in available variables."
            )
            return

        if weight_var and weight_var not in self.all_columns.union(
            {"product", "vintage", "sumlev", "desc"}
        ):
            print(f"❌ Weight variable '{weight_var}' not found in set variables.")
            return

        if weight_div is not None:
            if not isinstance(weight_div, int) or weight_div <= 0:
                print("❌ Error: `weight_div` must be a positive integer.")
                return
            if not weight_var:
                print("ℹ️ `weight_div` is only valid if `weight_var` is provided.")

        if where:
            where_list = [where] if isinstance(where, str) else where
            try:
                checker_functions = [self._build_safe_checker(w) for w in where_list]

                dat_filtered = []
                for item in self._data:
                    if not item.get("data"):
                        continue

                    # Convert rows to dicts for filtering
                    dict_rows = [
                        dict(zip(item["schema"], row)) for row in item.get("data", [])
                    ]

                    # Destring values before checking
                    group_vars = set(
                        [
                            var
                            for var in item["schema"]
                            if item.get("group_name", "N/A") in var
                        ]
                    )
                    attribute_vars = set(
                        [
                            var
                            for sub in item.get("attributes", [])
                            for var in sub.split(",")
                        ]
                    )
                    all_variable_names = set(item.get("names", [])).union(
                        group_vars, attribute_vars
                    )
                    for row in dict_rows:
                        for key, val in row.items():
                            if key in all_variable_names and isinstance(val, str):
                                try:
                                    row[key] = ast.literal_eval(val)
                                except (ValueError, SyntaxError):
                                    pass  # Keep as string if it fails

                    filtered_rows = [
                        row
                        for row in dict_rows
                        if logic(checker(row) for checker in checker_functions)
                    ]

                    if filtered_rows:
                        # Reconstruct item with filtered data (as dicts)
                        new_item = item.copy()
                        new_item["data"] = filtered_rows
                        dat_filtered.append(new_item)

            except ValueError as e:
                print(f"Error processing conditions: {e}")
                return
        else:
            dat_filtered = self._data

        if not dat_filtered:
            print("ℹ️ No data to tabulate after filtering.")
            return

        table = None
        if df_lib == "pl":
            try:
                if weight_var and weight_div:
                    wgt_agg = (pl.col(weight_var) / weight_div).sum()
                elif weight_var:
                    wgt_agg = pl.col(weight_var).sum()
                else:
                    wgt_agg = pl.len()

                df = self.to_polars(
                    concat=True,
                    destring=True if not where else False,
                    _data=dat_filtered,
                )

                if df.height == 0:
                    print("ℹ️ DataFrame is empty, cannot tabulate.")
                    return

                table = (
                    (
                        df.with_columns(wgt_agg.over(strat_by).alias("N"))
                        .group_by(strat_by, *variables)
                        .agg(
                            wgt_agg.alias("n"),
                            ((wgt_agg * 100) / pl.col("N").first()).alias("pct"),
                        )
                        .sort(strat_by, *variables)
                        .with_columns(
                            pl.col("n").cum_sum().over(strat_by).alias("cumn"),
                            pl.col("pct").cum_sum().over(strat_by).alias("cumpct"),
                        )
                    )
                    if strat_by
                    else (
                        df.with_columns(wgt_agg.alias("N"))
                        .group_by(*variables)
                        .agg(
                            wgt_agg.alias("n"),
                            ((wgt_agg * 100) / pl.col("N").first()).alias("pct"),
                        )
                        .sort(*variables)
                        .with_columns(
                            pl.col("n").cum_sum().alias("cumn"),
                            pl.col("pct").cum_sum().alias("cumpct"),
                        )
                    )
                )

            except pl.exceptions.ColumnNotFoundError:
                print(
                    f"❌ Error: The weight column '{weight_var}' was not found in the DataFrame."
                )
                return
            except TypeError:
                print(
                    f"❌ Error: The weight column '{weight_var}' contains non-numeric values."
                )
                return
            except Exception as e:
                print(f"❌ Polars tabulation failed: {e}")
                return

        else:  # df_lib == "pd"
            try:
                df = self.to_pandas(
                    concat=True,
                    destring=True if not where else False,
                    _data=dat_filtered,
                )
                if df.empty:
                    print("ℹ️ DataFrame is empty, cannot tabulate.")
                    return

                group_cols = list(variables)
                if strat_by:
                    group_cols.insert(0, strat_by)

                # Determine the weight column and calculate n
                if weight_var:
                    wgt_col = weight_var
                    if weight_div:
                        wgt_col = "_temp_wgt"
                        df[wgt_col] = df[weight_var] / weight_div
                    table = (
                        df.groupby(group_cols, observed=True)[wgt_col]
                        .sum()
                        .reset_index(name="n")
                    )
                else:
                    table = (
                        df.groupby(group_cols, observed=True)
                        .size()
                        .reset_index(name="n")
                    )

                # Calculate N (total per stratum or overall) and percentages
                if strat_by:
                    if weight_var:
                        wgt_col_for_n = wgt_col  # Use temp col if it exists
                        stratum_totals = (
                            df.groupby(strat_by, observed=True)[wgt_col_for_n]
                            .sum()
                            .reset_index(name="N")
                        )
                    else:
                        stratum_totals = (
                            df.groupby(strat_by, observed=True)
                            .size()
                            .reset_index(name="N")
                        )
                    table = pd.merge(table, stratum_totals, on=strat_by)
                else:
                    if weight_var:
                        wgt_col_for_n = wgt_col  # Use temp col if it exists
                        table["N"] = df[wgt_col_for_n].sum()
                    else:
                        table["N"] = len(df)

                table["pct"] = (table["n"] * 100) / table["N"]
                table = table.sort_values(by=group_cols)

                # Calculate cumulative sums (within strata or overall)
                if strat_by:
                    table["cumn"] = table.groupby(strat_by, observed=True)["n"].cumsum()
                    table["cumpct"] = table.groupby(strat_by, observed=True)[
                        "pct"
                    ].cumsum()
                else:
                    table["cumn"] = table["n"].cumsum()
                    table["cumpct"] = table["pct"].cumsum()

                # Cleanup
                table.drop(columns=["N"], inplace=True)
                if weight_var and weight_div:
                    df.drop(columns=["_temp_wgt"], inplace=True)

            except KeyError:
                print(
                    f"❌ Error: A specified column (e.g., '{weight_var}' or '{strat_by}') was not found."
                )
                return
            except TypeError:
                print(
                    f"❌ Error: The weight column '{weight_var}' contains non-numeric values."
                )
                return
            except Exception as e:
                print(f"❌ Pandas tabulation failed: {e}")
                return

        if table is None:
            return

        with (
            pl.Config(
                float_precision=digits,
                set_tbl_rows=-1,
                set_tbl_cols=-1,
                set_tbl_width_chars=-1,
                set_thousands_separator=",",
                set_tbl_hide_column_data_types=True,
                set_tbl_cell_alignment="RIGHT",
            )
            if df_lib == "pl"
            else pd.option_context(
                "display.float_format",
                lambda x: f"{x:,.{digits}f}",
                "display.max_rows",
                None,
                "display.max_columns",
                None,
                "display.max_colwidth",
                None,
                "styler.format.thousands",
                ",",
            )
        ):
            print(table)

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the object."""
        return f"<CenDatResponse with {len(self._data)} result(s)>"

    def __getitem__(self, index: int) -> Dict:
        """Allows accessing individual raw result dictionaries by index."""
        return self._data[index]
