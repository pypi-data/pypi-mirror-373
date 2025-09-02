import re
import requests
import itertools
import builtins
from collections import defaultdict
from typing import List, Union, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from .CenDatResponse import CenDatResponse


class CenDatHelper:
    """
    A helper for exploring and retrieving data from the US Census Bureau API.

    This class provides a chainable, stateful interface to list, select, and
    combine datasets, geographies, and variables to build and execute API calls.

    Attributes:
        years (List[int]): The primary year or years of interest for data queries.
        products (List[Dict]): The currently selected data product details.
        geos (List[Dict]): The currently selected geographies.
        groups (List[Dict]): The currently selected variable groups.
        variables (List[Dict]): The currently selected variables.
        params (List[Dict]): The combined geo/variable parameters for API calls.
        n_calls (int): The number of API calls that will be made by get_data().
    """

    def __init__(
        self, years: Optional[Union[int, List[int]]] = None, key: Optional[str] = None
    ):
        """
        Initializes the CenDatHelper object.

        Args:
            years (Union[int, List[int]], optional): The year or years of
                interest. If provided, they are set upon initialization.
                Defaults to None.
            key (str, optional): A Census Bureau API key to load upon
                initialization. Defaults to None.
        """
        self.years: Optional[List[int]] = None
        self.products: List[Dict] = []
        self.geos: List[Dict] = []
        self.groups: List[Dict] = []
        self.variables: List[Dict] = []
        self.params: List[Dict] = []
        self.__key: Optional[str] = None
        self._products_cache: Optional[List[Dict[str, str]]] = None
        self._filtered_products_cache: Optional[List[Dict]] = None
        self._filtered_geos_cache: Optional[List[Dict]] = None
        self._filtered_groups_cache: Optional[List[Dict]] = None
        self._filtered_variables_cache: Optional[List[Dict]] = None
        self.n_calls: Optional[int] = None

        if years is not None:
            self.set_years(years)
        if key is not None:
            self.load_key(key)

    def __getitem__(self, key: str) -> Union[List[Dict], Optional[int]]:
        """
        Allows dictionary-style access to key attributes.

        Args:
            key (str): The attribute to access. One of 'products', 'geos',
                       'groups', 'variables', 'params', or 'n_calls'.

        Returns:
            The value of the requested attribute.

        Raises:
            KeyError: If the key is not a valid attribute name.
        """
        if key == "products":
            return self.products
        elif key == "geos":
            return self.geos
        elif key == "groups":
            return self.groups
        elif key == "variables":
            return self.variables
        elif key == "params":
            return self.params
        elif key == "n_calls":
            return self.n_calls
        else:
            raise KeyError(
                f"'{key}' is not a valid key. Available keys are: 'products', 'geos', 'groups', 'variables', 'params', 'n_calls'"
            )

    def set_years(self, years: Union[int, List[int]]):
        """
        Sets the object's active years for filtering API metadata.

        Args:
            years (Union[int, List[int]]): The year or list of years to set.

        Raises:
            TypeError: If `years` is not an integer or a list of integers.
        """
        if isinstance(years, int):
            self.years = [years]
        elif isinstance(years, list) and all(isinstance(y, int) for y in years):
            self.years = sorted(list(set(years)))
        else:
            raise TypeError("'years' must be an integer or a list of integers.")
        print(f"✅ Years set to: {self.years}")

    def load_key(self, key: Optional[str] = None):
        """
        Loads a Census API key for authenticated requests.

        Using a key is recommended to avoid stricter rate limits on anonymous
        requests.

        Args:
            key (str, optional): The API key string. Defaults to None.
        """
        if key:
            self.__key = key
            print("✅ API key loaded successfully.")
        else:
            print("⚠️ No API key provided. API requests may have stricter rate limits.")

    def _get_json_from_url(
        self, url: str, params: Optional[Dict] = None, timeout: int = 30
    ) -> Optional[List[List[str]]]:
        """
        Internal helper to fetch and parse JSON from a URL with error handling.

        Args:
            url (str): The URL to fetch.
            params (Dict, optional): Dictionary of query parameters.
            timeout (int): Request timeout in seconds.

        Returns:
            Optional[List[List[str]]]: The parsed JSON data (typically a list
            of lists), or None if an error occurs.
        """
        if not params:
            params = {}
        if self.__key:
            params["key"] = self.__key

        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"❌ Failed to decode JSON from {url}. Server response: {e}")
            params_minus = {key: value for key, value in params.items() if key != "key"}
            print(f"Query parameters: {params_minus}")
            print(
                "Note: this may be the result of the 'in' geography being a special case "
                "in which the 'for' summary level does not exist. All valid parent geographies "
                "are queried without regard for whether or not the requested summary level exists "
                "within them. If this is the case, your results will still be valid (barring other "
                "errors)."
            )
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if e.response is not None:
                api_error = e.response.text.strip()
                if api_error:
                    error_message += f" - API Message: {api_error}"
            print(
                f"❌ Error fetching data from {url} with params {params}: {error_message}"
            )
        return None

    def _parse_vintage(self, vintage_input: Union[str, int]) -> List[int]:
        """
        Robustly parses a vintage value which can be a single year or a range.

        Args:
            vintage_input (Union[str, int]): The vintage string or integer
                                             (e.g., 2020, "2010-2014").

        Returns:
            List[int]: A list of integer years.
        """
        if not vintage_input:
            return []
        vintage_str = str(vintage_input)
        try:
            if "-" in vintage_str:
                start, end = map(int, vintage_str.split("-"))
                return list(range(start, end + 1))
            return [int(vintage_str)]
        except (ValueError, TypeError):
            return []

    def list_products(
        self,
        years: Optional[Union[int, List[int]]] = None,
        patterns: Optional[Union[str, List[str]]] = None,
        to_dicts: bool = True,
        logic: Callable[[iter], bool] = all,
        match_in: str = "title",
    ) -> Union[List[str], List[Dict[str, str]]]:
        """
        Lists available data products, with options for filtering.

        Fetches all available datasets from the main Census API endpoint and
        filters them based on year and string patterns. Results are cached
        for subsequent calls.

        Args:
            years (Union[int, List[int]], optional): Filter products available
                for this year or list of years. Defaults to years set on the object.
            patterns (Union[str, List[str]], optional): A regex pattern or list
                of patterns to search for in the product metadata.
            to_dicts (bool): If True (default), returns a list of dictionaries
                with full product details. If False, returns a list of titles.
            logic (Callable): The function to apply when multiple `patterns` are
                provided. Use `all` (default) for AND logic or `any` for OR logic.
            match_in (str): The metadata field to search within. Must be 'title'
                (default) or 'desc'.

        Returns:
            A list of product dictionaries or a list of product titles.
        """
        if not self._products_cache:
            data = self._get_json_from_url("https://api.census.gov/data.json")
            if not data or "dataset" not in data:
                return []
            products = []
            for d in data["dataset"]:
                is_micro = str(d.get("c_isMicrodata", "false")).lower() == "true"
                is_agg = str(d.get("c_isAggregate", "false")).lower() == "true"
                if not is_micro and not is_agg:
                    continue

                access_url = next(
                    (
                        dist.get("accessURL")
                        for dist in d.get("distribution", [])
                        if "api.census.gov/data" in dist.get("accessURL", "")
                    ),
                    None,
                )
                if not access_url:
                    continue
                c_dataset_val = d.get("c_dataset")
                dataset_type = "N/A"
                if isinstance(c_dataset_val, list) and len(c_dataset_val) > 1:
                    dataset_type = "/".join(c_dataset_val)
                elif isinstance(c_dataset_val, str):
                    dataset_type = c_dataset_val

                title = d.get("title")
                title = (
                    f"{title} ({re.sub(r'http://api.census.gov/data/','', access_url)})"
                )

                products.append(
                    {
                        "title": title,
                        "desc": d.get("description"),
                        "vintage": self._parse_vintage(d.get("c_vintage")),
                        "type": dataset_type,
                        "url": access_url,
                        "is_microdata": is_micro,
                        "is_aggregate": is_agg,
                    }
                )
            self._products_cache = products

        target_years = self.years
        if years is not None:
            target_years = [years] if isinstance(years, int) else list(years)

        filtered = self._products_cache
        if target_years:
            target_set = set(target_years)
            filtered = [
                p
                for p in filtered
                if p.get("vintage") and target_set.intersection(p["vintage"])
            ]

        if patterns:
            if match_in not in ["title", "desc"]:
                print("❌ Error: `match_in` must be either 'title' or 'desc'.")
                return []
            pattern_list = [patterns] if isinstance(patterns, str) else patterns
            try:
                regexes = [re.compile(p, re.IGNORECASE) for p in pattern_list]
                filtered = [
                    p
                    for p in filtered
                    if p.get(match_in)
                    and logic(regex.search(p[match_in]) for regex in regexes)
                ]
            except re.error as e:
                print(f"❌ Invalid regex pattern: {e}")
                return []

        self._filtered_products_cache = filtered
        return filtered if to_dicts else [p["title"] for p in filtered]

    def set_products(self, titles: Optional[Union[str, List[str]]] = None):
        """
        Sets the active data products for subsequent method calls.

        Args:
            titles (Union[str, List[str]], optional): The title or list of
                titles of the products to set. If None, sets all products from
                the last `list_products` call.
        """
        prods_to_set = []
        if titles is None:
            if not self._filtered_products_cache:
                print("❌ Error: No products to set. Run `list_products` first.")
                return
            prods_to_set = self._filtered_products_cache
        else:
            title_list = [titles] if isinstance(titles, str) else titles
            all_prods = self.list_products(to_dicts=True, years=self.years or [])
            for title in title_list:
                matching_products = [p for p in all_prods if p.get("title") == title]
                if not matching_products:
                    print(
                        f"⚠️ Warning: No product with the title '{title}' found. Skipping."
                    )
                    continue
                prods_to_set.extend(matching_products)
        self.products = []
        if not prods_to_set:
            print("❌ Error: No valid products were found to set.")
            return
        for product in prods_to_set:
            product["base_url"] = product.get("url", "")
            self.products.append(product)
            print(
                f"✅ Product set: '{product['title']}' (Vintage: {product.get('vintage')})"
            )

    def list_geos(
        self,
        to_dicts: bool = False,
        patterns: Optional[Union[str, List[str]]] = None,
        logic: Callable[[iter], bool] = all,
    ) -> Union[List[str], List[Dict[str, str]]]:
        """
        Lists available geographies for the currently set products.

        Args:
            to_dicts (bool): If True, returns a list of dictionaries with full
                geography details. If False (default), returns a sorted list of
                unique summary level names ('sumlev').
            patterns (Union[str, List[str]], optional): A regex pattern or list
                of patterns to search for in the geography description.
            logic (Callable): The function to apply when multiple `patterns` are
                provided. Use `all` (default) for AND logic or `any` for OR logic.

        Returns:
            A list of geography dictionaries or a list of summary level strings.
        """
        if not self.products:
            print("❌ Error: Products must be set first via `set_products()`.")
            return []
        flat_geo_list = []
        for product in self.products:
            url = f"{product['base_url']}/geography.json"
            data = self._get_json_from_url(url)
            if not data or "fips" not in data:
                continue
            for geo_info in data["fips"]:
                sumlev = geo_info.get("geoLevelDisplay")
                if not sumlev:
                    continue
                # NUANCED WILDCARD LOGIC: Capture wildcard metadata
                flat_geo_list.append(
                    {
                        "sumlev": sumlev,
                        "desc": geo_info.get("name"),
                        "product": product["title"],
                        "vintage": product["vintage"],
                        "requires": geo_info.get("requires"),
                        "wildcard": geo_info.get("wildcard"),
                        "optionalWithWCFor": geo_info.get("optionalWithWCFor"),
                        "url": product["url"],
                    }
                )
        result_list = flat_geo_list
        if patterns:
            pattern_list = [patterns] if isinstance(patterns, str) else patterns
            try:
                regexes = [re.compile(p, re.IGNORECASE) for p in pattern_list]
                result_list = [
                    g
                    for g in result_list
                    if g.get("desc")
                    and logic(regex.search(g["desc"]) for regex in regexes)
                ]
            except re.error as e:
                print(f"❌ Invalid regex pattern: {e}")
                return []
        self._filtered_geos_cache = result_list
        return (
            result_list
            if to_dicts
            else sorted(list(set([g["sumlev"] for g in result_list])))
        )

    def set_geos(
        self,
        values: Optional[Union[str, List[str]]] = None,
        by: str = "sumlev",
    ):
        """
        Sets the active geographies for data retrieval.

        Args:
            values (Union[str, List[str]], optional): The geography values to set.
                If None, sets all geos from the last `list_geos` call.
            by (str): The key to use for matching `values`. Must be either
                'sumlev' (default) or 'desc'.
        """
        if by not in ["sumlev", "desc"]:
            print("❌ Error: `by` must be either 'sumlev' or 'desc'.")
            return

        geos_to_set = []
        if values is None:
            if not self._filtered_geos_cache:
                print("❌ Error: No geos to set. Run `list_geos` first.")
                return
            geos_to_set = self._filtered_geos_cache
        else:
            value_list = [values] if isinstance(values, str) else values
            all_geos = self.list_geos(to_dicts=True)
            geos_to_set = [g for g in all_geos if g.get(by) in value_list]

        if not geos_to_set:
            print("❌ Error: No valid geographies were found to set.")
            return

        is_microdata_present = any(
            p.get("is_microdata")
            for p in self.products
            if p["title"] in [g["product"] for g in geos_to_set]
        )

        unique_geos = set(g["desc"] for g in geos_to_set)
        if is_microdata_present and len(unique_geos) > 1:
            print(
                "❌ Error: Only a single geography type (e.g., 'public use microdata area') can be set when working with microdata products."
            )
            return

        self.geos = geos_to_set
        messages = {}
        for geo in self.geos:
            desc = geo["desc"]
            reqs = geo.get("requires") or []
            if desc not in messages:
                messages[desc] = set(reqs)
            else:
                messages[desc].update(reqs)
        message_parts = []
        for desc, reqs in messages.items():
            if reqs:
                message_parts.append(
                    f"'{desc}' (requires `within` for: {', '.join(sorted(list(reqs)))})"
                )
            else:
                message_parts.append(f"'{desc}'")
        print(f"✅ Geographies set: {', '.join(message_parts)}")

    def list_groups(
        self,
        to_dicts: bool = True,
        patterns: Optional[Union[str, List[str]]] = None,
        logic: Callable[[iter], bool] = all,
        match_in: str = "description",
    ) -> Union[List[str], List[Dict[str, str]]]:
        """
        Lists available variable groups for the currently set products.

        Args:
            to_dicts (bool): If True (default), returns a list of dictionaries
                with full group details. If False, returns a sorted list of
                unique group names.
            patterns (Union[str, List[str]], optional): A regex pattern or list
                of patterns to search for in the group metadata.
            logic (Callable): The function to apply when multiple `patterns` are
                provided. Use `all` (default) for AND logic or `any` for OR logic.
            match_in (str): The metadata field to search within. Must be
                'description' (default) or 'name'.

        Returns:
            A list of group dictionaries or a list of group name strings.
        """
        if not self.products:
            print("❌ Error: Products must be set first via `set_products()`.")
            return []

        flat_group_list = []
        for product in self.products:
            url = f"{product['base_url']}/groups.json"
            data = self._get_json_from_url(url)
            if not data or "groups" not in data:
                continue
            for group_details in data["groups"]:
                flat_group_list.append(
                    {
                        "name": group_details.get("name", "N/A"),
                        "description": group_details.get("description", "N/A"),
                        "product": product["title"],
                        "vintage": product["vintage"],
                        "url": product["url"],
                    }
                )
        result_list = flat_group_list

        if match_in not in ["description", "name"]:
            print("❌ Error: `match_in` must be either 'description' or 'name'.")
            return []

        if patterns:
            pattern_list = [patterns] if isinstance(patterns, str) else patterns
            try:
                regexes = [re.compile(p, re.IGNORECASE) for p in pattern_list]
                result_list = [
                    g
                    for g in result_list
                    if g.get(match_in)
                    and logic(regex.search(g[match_in]) for regex in regexes)
                ]
            except re.error as e:
                print(f"❌ Invalid regex pattern: {e}")
                return []

        self._filtered_groups_cache = result_list
        return (
            result_list
            if to_dicts
            else sorted(list(set([g["name"] for g in result_list])))
        )

    def set_groups(self, names: Optional[Union[str, List[str]]] = None):
        """
        Sets the active variable groups for subsequent method calls.

        Args:
            names (Union[str, List[str]], optional): The name or list of names
                of the groups to set. If None, sets all groups from the
                last `list_groups` call.
        """
        groups_to_set = []
        if names is None:
            if not self._filtered_groups_cache:
                print("❌ Error: No groups to set. Run `list_groups` first.")
                return
            groups_to_set = self._filtered_groups_cache
        else:
            name_list = [names] if isinstance(names, str) else names
            all_groups = self.list_groups(to_dicts=True)
            groups_to_set = [g for g in all_groups if g.get("name") in name_list]

        if not groups_to_set:
            print("❌ Error: No valid groups were found to set.")
            return

        self.groups = groups_to_set
        self.variables = []
        unique_names = sorted(list(set(g["name"] for g in self.groups)))
        print(f"✅ Groups set: {', '.join(unique_names)}")

    def describe_groups(self, groups: Optional[Union[str, List[str]]] = None):
        """
        Displays the variables within specified groups in a formatted, indented list.

        This method fetches all variables for the currently set products and
        filters them to show only those belonging to the specified groups. The
        output is formatted to reflect the hierarchical structure of the variables
        as indicated by their labels.

        Args:
            groups (Union[str, List[str]], optional): A group name or list of
                names to describe. If None, it will use the groups previously
                set on the helper object via `set_groups()`.
        """
        if not self.products:
            print("❌ Error: Products must be set first via `set_products()`.")
            return

        # Determine which groups to filter by
        groups_to_filter = None
        if groups is not None:
            groups_to_filter = groups
        elif self.groups:
            groups_to_filter = [g["name"] for g in self.groups]

        if not groups_to_filter:
            print(
                "❌ Error: No groups specified or set. Use `set_groups()` or the 'groups' parameter."
            )
            return

        if isinstance(groups_to_filter, str):
            groups_to_filter = [groups_to_filter]

        group_set = set(groups_to_filter)

        # Fetch all variables and group descriptions
        all_vars = self.list_variables(to_dicts=True)
        all_groups_details = self.list_groups(to_dicts=True)

        # Create a lookup for group descriptions
        group_descriptions = {g["name"]: g["description"] for g in all_groups_details}

        # Filter variables that belong to the selected groups
        group_vars = [v for v in all_vars if v.get("group") in group_set]

        if not group_vars:
            print(
                f"ℹ️ No variables found for the specified group(s): {', '.join(group_set)}"
            )
            return

        # Organize variables by group and product/vintage for structured printing
        vars_by_group_product = {}
        for var in group_vars:
            key = (var["group"], var["product"], var["vintage"][0])
            if key not in vars_by_group_product:
                vars_by_group_product[key] = []
            vars_by_group_product[key].append(var)

        # Print the formatted output
        last_group_printed = None
        for key in sorted(vars_by_group_product.keys()):
            group_name, product_title, vintage = key

            if group_name != last_group_printed:
                group_desc = group_descriptions.get(
                    group_name, "No description available."
                )
                print(f"\n--- Group: {group_name} ({group_desc}) ---")
                last_group_printed = group_name

            print(f"\n  Product: {product_title} (Vintage: {vintage})")

            sorted_vars = sorted(vars_by_group_product[key], key=lambda x: x["name"])

            for var in sorted_vars:
                label = var.get("label", "")

                # Use the count of '!!' as a reliable depth indicator
                depth = label.count("!!")
                indent = "  " * depth

                # Get the last part of the label after splitting by '!!'
                final_label_part = label.split("!!")[-1]

                print(f"    {indent}{var['name']}: {final_label_part.strip()}")

    def list_variables(
        self,
        to_dicts: bool = True,
        patterns: Optional[Union[str, List[str]]] = None,
        logic: Callable[[iter], bool] = all,
        match_in: str = "label",
        groups: Optional[Union[str, List[str]]] = None,
    ) -> Union[List[str], List[Dict[str, str]]]:
        """
        Lists available variables for the currently set products.

        Args:
            to_dicts (bool): If True (default), returns a list of dictionaries
                with full variable details. If False, returns a sorted list of
                unique variable names.
            patterns (Union[str, List[str]], optional): A regex pattern or list
                of patterns to search for in the variable metadata.
            logic (Callable): The function to apply when multiple `patterns` are
                provided. Use `all` (default) for AND logic or `any` for OR logic.
            match_in (str): The metadata field to search within. Must be 'label'
                (default), 'name', or 'concept'.
            groups (Union[str, List[str]], optional): A group name or list of
                names to filter variables by. If provided, only variables
                belonging to these groups will be returned.

        Returns:
            A list of variable dictionaries or a list of variable name strings.
        """
        if not self.products:
            print("❌ Error: Products must be set first via `set_products()`.")
            return []
        flat_variable_list = []
        for product in self.products:
            url = f"{product['base_url']}/variables.json"
            data = self._get_json_from_url(url)
            if not data or "variables" not in data:
                continue
            for name, details in data["variables"].items():
                if name in ["GEO_ID", "for", "in", "ucgid"]:
                    continue
                flat_variable_list.append(
                    {
                        "name": name,
                        "label": details.get("label", "N/A"),
                        "concept": details.get("concept", "N/A"),
                        "group": details.get("group", "N/A"),
                        "values": details.get("values", "N/A"),
                        "type": details.get("predicateType", "N/A"),
                        "attributes": details.get("attributes", "N/A"),
                        "sugg_wgt": details.get("suggested-weight", "N/A"),
                        "product": product["title"],
                        "vintage": product["vintage"],
                        "url": product["url"],
                    }
                )
        result_list = flat_variable_list

        # Determine which groups to filter by: use the 'groups' parameter if
        # provided, otherwise fall back to the groups set on the object.
        groups_to_filter = None
        if groups is not None:
            groups_to_filter = groups
        elif self.groups:
            # Extract group names from the list of group dictionaries
            groups_to_filter = [g["name"] for g in self.groups]

        # Apply the group filter if there are any groups to filter by
        if groups_to_filter:
            # Ensure groups_to_filter is a list for set creation
            if isinstance(groups_to_filter, str):
                groups_to_filter = [groups_to_filter]
            group_set = set(groups_to_filter)
            result_list = [v for v in result_list if v.get("group") in group_set]

        if match_in not in ["label", "name", "concept"]:
            print("❌ Error: `match_in` must be either 'label', 'name', or 'concept'.")
            return []

        if patterns:
            pattern_list = [patterns] if isinstance(patterns, str) else patterns
            try:
                regexes = [re.compile(p, re.IGNORECASE) for p in pattern_list]
                result_list = [
                    v
                    for v in result_list
                    if v.get(match_in)
                    and logic(regex.search(v[match_in]) for regex in regexes)
                ]
            except re.error as e:
                print(f"❌ Invalid regex pattern: {e}")
                return []

        self._filtered_variables_cache = result_list
        return (
            result_list
            if to_dicts
            else sorted(list(set([v["name"] for v in result_list])))
        )

    def set_variables(
        self,
        names: Optional[Union[str, List[str]]] = None,
    ):
        """
        Sets the active variables for data retrieval.

        Args:
            names (Union[str, List[str]], optional): The name or list of names
                of the variables to set. If None, sets all variables from the
                last `list_variables` call.
        """
        vars_to_set = []
        if names is None:
            if not self._filtered_variables_cache:
                print("❌ Error: No variables to set. Run `list_variables` first.")
                return
            vars_to_set = self._filtered_variables_cache
        else:
            name_list = [names] if isinstance(names, str) else names
            all_vars = self.list_variables(to_dicts=True, patterns=None)
            vars_to_set = [v for v in all_vars if v.get("name") in name_list]
        if not vars_to_set:
            print("❌ Error: No valid variables were found to set.")
            return
        collapsed_vars = {}
        for var_info in vars_to_set:
            key = (var_info["product"], tuple(var_info["vintage"]), var_info["url"])
            if key not in collapsed_vars:
                collapsed_vars[key] = {
                    "product": var_info["product"],
                    "vintage": var_info["vintage"],
                    "url": var_info["url"],
                    "names": [],
                    "labels": [],
                    "values": [],
                    "types": [],
                    "attributes": [],
                    "sugg_wgts": [],
                }
            for collapsed, granular in zip(
                ["names", "labels", "values", "types", "attributes", "sugg_wgts"],
                ["name", "label", "values", "type", "attributes", "sugg_wgt"],
            ):
                collapsed_vars[key][collapsed].append(var_info[granular])
        self.variables = list(collapsed_vars.values())
        print("✅ Variables set:")
        for var_group in self.variables:
            print(
                f"  - Product: {var_group['product']} (Vintage: {var_group['vintage']})"
            )
            print(f"    Variables: {', '.join(var_group['names'])}")

    def _create_params(self):
        """
        Internal method to combine set geos, variables, and/or groups into API parameters.

        This method joins the user-selected geographies with either selected
        variables or a single selected group, based on matching product and vintage.
        This creates the final parameter sets for `get_data`.
        """
        if not self.geos:
            print("❌ Error: Geographies must be set before creating parameters.")
            return

        self.params = []  # Reset params

        micro_indicators = {
            p["url"]: p.get("is_microdata", False) for p in self.products
        }

        # Case 1: Variables are set (standard behavior)
        if self.variables:
            for geo in self.geos:
                for var_group in self.variables:
                    if (
                        geo["product"] == var_group["product"]
                        and geo["vintage"] == var_group["vintage"]
                        and geo["url"] == var_group["url"]
                    ):
                        # NUANCED WILDCARD LOGIC: Pass wildcard metadata into params
                        self.params.append(
                            {
                                "product": geo["product"],
                                "vintage": geo["vintage"],
                                "sumlev": geo["sumlev"],
                                "desc": geo["desc"],
                                "requires": geo.get("requires"),
                                "wildcard": geo.get("wildcard"),
                                "optionalWithWCFor": geo.get("optionalWithWCFor"),
                                "names": var_group["names"],
                                "labels": var_group["labels"],
                                "values": var_group["values"],
                                "types": var_group["types"],
                                "attributes": var_group["attributes"],
                                "url": geo["url"],
                                "is_microdata": micro_indicators[geo["url"]],
                            }
                        )

        # Case 2: No variables, but exactly one group is set per vintage * geo
        elif self.groups:
            mult_check = defaultdict(set)
            for group in self.groups:
                mult_check[group["url"]].update({group["name"]})
            if [k for k, v in mult_check.items() if len(v) > 1]:
                print(
                    "❌ Error: You must set variables if any set product has more than 1 set group."
                )
                return
            for geo in self.geos:
                for group in self.groups:
                    if (
                        geo["product"] == group["product"]
                        and geo["vintage"] == group["vintage"]
                        and geo["url"] == group["url"]
                    ):
                        self.params.append(
                            {
                                "product": geo["product"],
                                "vintage": geo["vintage"],
                                "sumlev": geo["sumlev"],
                                "desc": geo["desc"],
                                "requires": geo.get("requires"),
                                "wildcard": geo.get("wildcard"),
                                "optionalWithWCFor": geo.get("optionalWithWCFor"),
                                "group_name": group[
                                    "name"
                                ],  # Key to identify group call
                                "url": geo["url"],
                                "is_microdata": micro_indicators[geo["url"]],
                            }
                        )

        # Case 3: Invalid state
        else:
            print(
                "❌ Error: You must set variables (using `set_variables`) OR set exactly one group (using `set_groups`) before getting data."
            )
            return  # self.params is already empty

        if not self.params:
            print(
                "⚠️ Warning: No matching product-vintage combinations found between set geos and variables/groups."
            )
        else:
            print(
                f"✅ Parameters created for {len(self.params)} geo-variable/group combinations."
            )

    def _get_parent_geo_combinations(
        self,
        base_url: str,
        required_geos: List[str],
        current_in_clause: Dict = {},
        timeout: int = 30,
        max_workers: Optional[int] = None,
    ) -> List[Dict]:
        """
        Recursively fetches all valid combinations of parent geographies.

        For aggregate data, if a geography requires parent geos (e.g., a county
        requires a state), this method fetches all possible parent FIPS codes
        to build the necessary `in` clauses for the final data query.

        Args:
            base_url (str): The base API URL for the product.
            required_geos (List[str]): A list of parent geo levels to fetch.
            current_in_clause (Dict): The `in` clause built so far in the recursion.
            timeout (int): Request timeout in seconds.
            max_workers (int, optional): Max concurrent threads for fetching.

        Returns:
            List[Dict]: A list of dictionaries, where each dict is a valid
                        `in` clause for a data request.
        """
        if not required_geos:
            return [current_in_clause]
        level_to_fetch = required_geos[0]
        remaining_levels = required_geos[1:]
        params = {"get": "NAME", "for": f"{level_to_fetch}:*"}
        if current_in_clause:
            in_parts = []
            for k, v in current_in_clause.items():
                if isinstance(v, list):
                    in_parts.append(f"{k}:{','.join(v)}")
                else:
                    in_parts.append(f"{k}:{v}")
            params["in"] = " ".join(in_parts)
        data = self._get_json_from_url(base_url, params, timeout=timeout)
        if not data or len(data) < 2:
            return []
        try:
            fips_index = data[0].index(level_to_fetch)
        except ValueError:
            print(
                f"❌ Could not find FIPS column for '{level_to_fetch}' in API response."
            )
            return []
        all_combinations = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_fips = {
                executor.submit(
                    self._get_parent_geo_combinations,
                    base_url,
                    remaining_levels,
                    {**current_in_clause, level_to_fetch: row[fips_index]},
                    timeout=timeout,
                    max_workers=max_workers,
                ): row[fips_index]
                for row in data[1:]
            }
            for future in as_completed(future_to_fips):
                all_combinations.extend(future.result())
        return all_combinations

    def get_data(
        self,
        within: Union[str, Dict, List[Dict]] = "us",
        max_workers: Optional[int] = 100,
        timeout: int = 30,
        preview_only: bool = False,
        include_names: bool = False,
        include_geoids: bool = False,
        include_attributes: bool = False,
    ) -> "CenDatResponse":
        """
        Retrieves data from the Census API based on the set parameters.

        This is the final method in the chain. It constructs and executes all
        necessary API calls in parallel, aggregates the results, and returns
        a CenDatResponse object for further processing.

        Args:
            within (Union[str, Dict, List[Dict]]): Specifies the geographic
                scope. Can be "us" (default), or a dictionary defining parent
                geographies (e.g., `{'state': '06'}` for California), or a list
                of such dictionaries for multiple scopes.
            max_workers (int, optional): The maximum number of concurrent
                threads to use for API calls. Defaults to 100.
            timeout (int): Request timeout in seconds for each API call.
                Defaults to 30.
            preview_only (bool): If True, builds the list of API calls but does
                not execute them. Useful for debugging. Defaults to False.

        Returns:
            CenDatResponse: An object containing the aggregated data from all
                            successful API calls.
        """
        self._create_params()

        if not self.params:
            print(
                "❌ Error: Could not create parameters. Please set geos and variables."
            )
            return CenDatResponse([])

        results_aggregator = {
            i: {"schema": None, "data": []} for i in range(len(self.params))
        }
        all_tasks = []

        raw_within_clauses = within if isinstance(within, list) else [within]

        expanded_within_clauses = []
        for clause in raw_within_clauses:
            # NUANCED WILDCARD LOGIC: Use builtins.dict to prevent shadowing errors
            if not isinstance(clause, builtins.dict):
                expanded_within_clauses.append(clause)
                continue

            # Separate keys with list values from those with single values
            list_items = {k: v for k, v in clause.items() if isinstance(v, list)}
            single_items = {k: v for k, v in clause.items() if not isinstance(v, list)}

            if not list_items:
                expanded_within_clauses.append(clause)
                continue

            # Create all combinations of the list values
            keys, values = zip(*list_items.items())
            for v_combination in itertools.product(*values):
                new_clause = single_items.copy()
                new_clause.update(builtins.dict(zip(keys, v_combination)))
                expanded_within_clauses.append(new_clause)

        for i, param in enumerate(self.params):
            product_info = next(
                (p for p in self.products if p["title"] == param["product"]), None
            )
            if not product_info:
                continue

            # Conditionally build the 'get' parameter string based on call type
            if "group_name" in param:  # This is a group-based call
                vars_to_get = [f"group({param['group_name']})"]
                if include_geoids and param["is_microdata"]:
                    print("ℹ️ GEO_ID not valid for microdata - request ignored.")
                elif include_geoids:
                    vars_to_get.insert(0, "GEO_ID")
                if include_names and param["is_microdata"]:
                    print("ℹ️ NAME not valid for microdata - request ignored.")
                elif include_names:
                    vars_to_get.insert(0, "NAME")
                # `include_attributes` is ignored for group calls.
            else:
                vars_to_get = param["names"].copy()
                if include_geoids and param["is_microdata"]:
                    print("ℹ️ GEO_ID not valid for microdata - request ignored.")
                elif include_geoids:
                    vars_to_get.insert(0, "GEO_ID")
                if include_names and param["is_microdata"]:
                    print("ℹ️ NAME not valid for microdata - request ignored.")
                elif include_names:
                    vars_to_get.insert(0, "NAME")
                if include_attributes:
                    all_attributes = set()
                    # Iterate through the list of attribute strings for the selected variables
                    for attr_string in param.get("attributes", []):
                        # Check if the string is valid and not the "N/A" placeholder
                        if attr_string and attr_string != "N/A":
                            # The 'attributes' key contains a comma-separated string of variable names.
                            # We split this string and add the names to our set.
                            all_attributes.update(attr_string.split(","))

                    # Add the unique, valid attributes to the list of variables to request.
                    if all_attributes:
                        vars_to_get.extend(list(all_attributes))

            variable_names = ",".join(vars_to_get)
            target_geo = param["desc"]
            vintage_url = param["url"]
            context = {"param_index": i}

            for within_clause in expanded_within_clauses:
                if product_info.get("is_microdata"):
                    if not isinstance(within_clause, builtins.dict):
                        print(
                            "❌ Error: A `within` dictionary or list of dictionaries is required for microdata requests."
                        )
                        continue

                    within_copy = within_clause.copy()
                    target_geo_codes = within_copy.pop(target_geo, None)

                    if target_geo_codes is None:
                        print(
                            f"❌ Error: `within` dictionary must contain the target geography: '{target_geo}'"
                        )
                        continue

                    codes_str = (
                        target_geo_codes
                        if isinstance(target_geo_codes, str)
                        else ",".join(target_geo_codes)
                    )

                    api_params = {
                        "get": variable_names,
                        "for": f"{target_geo}:{codes_str}",
                    }
                    if within_copy:
                        api_params["in"] = " ".join(
                            [f"{k}:{v}" for k, v in within_copy.items()]
                        )
                    all_tasks.append((vintage_url, api_params, context))

                elif product_info.get("is_aggregate"):
                    required_geos = param.get("requires") or []
                    provided_parent_geos = {}
                    target_geo_codes = None

                    if isinstance(within_clause, builtins.dict):
                        within_copy = within_clause.copy()
                        target_geo_codes = within_copy.pop(target_geo, None)
                        provided_parent_geos = {
                            k: v for k, v in within_copy.items() if k in required_geos
                        }

                    if target_geo_codes:
                        codes_str = (
                            target_geo_codes
                            if isinstance(target_geo_codes, str)
                            else ",".join(map(str, target_geo_codes))
                        )
                        api_params = {
                            "get": variable_names,
                            "for": f"{target_geo}:{codes_str}",
                        }
                        if provided_parent_geos:
                            api_params["in"] = " ".join(
                                [f"{k}:{v}" for k, v in provided_parent_geos.items()]
                            )
                        all_tasks.append((vintage_url, api_params, context))
                        continue

                    final_in_clause = {}
                    if required_geos:
                        for geo in required_geos:
                            if geo in provided_parent_geos:
                                final_in_clause[geo] = provided_parent_geos[geo]
                            elif param.get("wildcard") and geo in param["wildcard"]:
                                final_in_clause[geo] = "*"
                            else:
                                final_in_clause[geo] = None  # Needs discovery

                    optional_level = param.get("optionalWithWCFor")
                    if optional_level and optional_level not in provided_parent_geos:
                        final_in_clause.pop(optional_level, None)

                    geos_to_fetch = [
                        geo for geo, code in final_in_clause.items() if code is None
                    ]

                    combinations = []
                    if geos_to_fetch:
                        print(f"ℹ️ Discovering parent geographies for: {geos_to_fetch}")
                        resolved_parents = {
                            k: v
                            for k, v in final_in_clause.items()
                            if v is not None and v != "*"
                        }
                        combinations = self._get_parent_geo_combinations(
                            vintage_url,
                            geos_to_fetch,
                            resolved_parents,
                            timeout=timeout,
                            max_workers=max_workers,
                        )
                    else:
                        combinations = [final_in_clause]

                    if combinations:
                        print(
                            f"✅ Found {len(combinations)} combinations. Building API queries..."
                        )

                    for combo in combinations:
                        call_in_clause = final_in_clause.copy()
                        call_in_clause.update(combo)
                        call_in_clause = {
                            k: v for k, v in call_in_clause.items() if v is not None
                        }

                        api_params = {"get": variable_names, "for": f"{target_geo}:*"}
                        if call_in_clause:
                            api_params["in"] = " ".join(
                                [f"{k}:{v}" for k, v in call_in_clause.items()]
                            )
                        all_tasks.append((vintage_url, api_params, context))

        if not all_tasks:
            print("❌ Error: Could not determine any API calls to make.")
            return CenDatResponse([])

        self.n_calls = len(all_tasks)

        if preview_only:
            print(f"ℹ️ Preview: this will yield {self.n_calls} API call(s).")
            for i, (url, params, _) in enumerate(all_tasks[:5]):
                print(
                    f"  - Call {i+1}: {url}?get={params.get('get')}&for={params.get('for')}&in={params.get('in','')}"
                )
            if len(all_tasks) > 5:
                print(f"  ... and {len(all_tasks) - 5} more.")
            return CenDatResponse([])

        else:
            print(f"ℹ️ Making {self.n_calls} API call(s)...")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_context = {
                    executor.submit(
                        self._get_json_from_url, url, params, timeout
                    ): context
                    for url, params, context in all_tasks
                }
                for future in as_completed(future_to_context):
                    context = future_to_context[future]
                    param_index = context["param_index"]
                    try:
                        data = future.result()
                        if data and len(data) > 1:
                            if results_aggregator[param_index]["schema"] is None:
                                results_aggregator[param_index]["schema"] = data[0]
                            results_aggregator[param_index]["data"].extend(data[1:])
                    except Exception as exc:
                        print(f"❌ Task for {context} generated an exception: {exc}")

            for i, param in enumerate(self.params):
                aggregated_result = results_aggregator[i]
                param["schema"] = aggregated_result["schema"]
                param["data"] = aggregated_result["data"]

            return CenDatResponse(self.params)
