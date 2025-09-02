import importlib.resources
import os
import re
import warnings
from collections import defaultdict
from functools import lru_cache
from logging import getLogger
from pathlib import Path

import pandas
from anytree import Node, RenderTree

from ._mapping_type import get_comment, skos_uri_dict

logger = getLogger("root")

ROOT_PATH = Path(os.path.dirname(__file__))

activitytype_path = "data/flow/activitytype/"
location_path = "data/location/"
dataquality_path = "data/dataquality/"
uncertainty_path = "data/uncertainty/"
time_path = "data/time/"
flowobject_path = "data/flow/flowobject/"
flow_path = "data/flow/"
unit_monetary_path = "data/unit/monetary/"
unit_physical_path = "data/unit/physical/"
unit_magnitude_path = "data/unit/magnitude/"

# Lookup function for pandas DataFrame
def lookup(self, keyword):
    """Filter the DataFrame based on the keyword in the "name" column"""
    filtered_df = self[self["name"].str.contains(keyword, case=False)]
    return filtered_df


def get_children(
    self,
    parent_codes,
    deep=True,
    return_parent=False,
):
    """
    Get descendants (direct and indirect) for a list of parent_codes.

    Parameters
    ----------
    parent_codes: str or list
        A single parent_code or a list of parent_codes for which descendants are to be fetched.
    deep: bool, optional
        If True, fetch all descendants recursively. If False, fetch only direct children. Default is True.
    return_parent: bool, optional
        If True, include the parent codes in the returned DataFrame. Default is False.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing rows with descendants of the specified parent_codes.
    """
    if not isinstance(self, pandas.DataFrame):
        raise TypeError("The object must be a pandas DataFrame.")

    if not {"code", "parent_code"}.issubset(self.columns):
        raise KeyError("DataFrame must contain 'code' and 'parent_code' columns.")

    if isinstance(parent_codes, str):
        parent_codes = [parent_codes]
    elif not isinstance(parent_codes, (list, set, tuple)):
        raise TypeError("parent_codes must be a string or a list-like object.")

    parent_codes = set(parent_codes)

    if deep:
        to_explore = set(parent_codes)
        all_descendants = set()

        while to_explore:
            current_children = self[self["parent_code"].isin(to_explore)]
            new_descendants = set(current_children["code"]) - all_descendants

            if not new_descendants:
                break  # Exit loop if no new children found

            all_descendants.update(new_descendants)
            to_explore = new_descendants  # Continue exploring new children

        if not all_descendants:
            logger.debug(f"No children found for {parent_codes}")

        df = self[self["code"].isin(all_descendants)]
    else:
        df = self[self["parent_code"].isin(parent_codes)]
        if df.empty:
            df = self[self["code"].isin(parent_codes)]

    # Include parent codes if requested
    if return_parent:
        df = pandas.concat(
            [self[self["code"].isin(parent_codes)], df]
        ).drop_duplicates()

    return CustomDataFrame(df)


def create_conc(df_A, df_B, source="", target=""):
    """Create new concordance based on two other tables.

    Argument
    --------
    df_A : pandas.DataFrame
        concordance table A
        with mapping from "x" to "y"
    df_B : pandas.DataFrame
        concordance table B
        with mapping from "y" to "z"
    target : str
        classification name that specifies "x"
    source : str
        classification name that specifies "z"

    Returns
    -------
    pandas.DataFrame
        concordance table with mapping form "x" to "z"
    """
    if "activitytype_to" in df_B.columns and "flowobjet_to" in df_B.columns:
        raise NotImplementedError("Concpair tables not allowed")
    elif "activitytype_to" in df_A.columns and "activitytype_to" in df_B.columns:
        column_prefix = "activitytype"
    elif "flowobject_to" in df_A.columns and "flowobject_to" in df_B.columns:
        column_prefix = "flowobject"

    merged = pandas.merge(df_A, df_B, on=f"{column_prefix}_to", suffixes=("_A", "_B"))

    # Create the resulting DataFrame with required columns
    result = pandas.DataFrame(
        {
            f"{column_prefix}_from": merged[f"{column_prefix}_from_A"],
            f"{column_prefix}_to": merged[f"{column_prefix}_from_B"],
            "classification_from": source,  # Fixed value from A
            "classification_to": target,  # Fixed value for result
        }
    )

    # Drop duplicate pairs of source and target
    new_mapping = result.drop_duplicates(
        subset=[
            f"{column_prefix}_from",
            f"{column_prefix}_to",
            "classification_from",
            "classification_to",
        ]
    )

    # Calculate the counts of each source and target in the merged DataFrame
    source_counts = new_mapping[f"{column_prefix}_from"].value_counts().to_dict()
    target_counts = new_mapping[f"{column_prefix}_to"].value_counts().to_dict()
    # Apply the get_comment function to each row
    # Build relationship dictionaries first
    source_to_targets = defaultdict(set)
    target_to_sources = defaultdict(set)

    for _, row in new_mapping.iterrows():
        source = row[f"{column_prefix}_from"]
        target = row[f"{column_prefix}_to"]
        if source and target:
            source_to_targets[source].add(target)
            target_to_sources[target].add(source)

    # Apply revised comment logic using get_true_comment
    new_mapping["comment"] = new_mapping.apply(
        lambda row: get_comment(
            row[f"{column_prefix}_from"],
            row[f"{column_prefix}_to"],
            source_to_targets,
            target_to_sources,
        ),
        axis=1,
    )

    new_mapping["skos_uri"] = new_mapping["comment"].map(skos_uri_dict)

    new_mapping = new_mapping[
        [
            f"{column_prefix}_from",
            f"{column_prefix}_to",
            "classification_from",
            "classification_to",
            "comment",
            "skos_uri",
        ]
    ]
    new_mapping = new_mapping.reset_index(drop=True)
    return new_mapping


def _get_concordance_file(file_path):
    try:
        # Read the concordance CSV into a DataFrame
        return pandas.read_csv(file_path, dtype=str)
        # return multiple_dfs
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.error(f"Error reading concordance file: {e}")
        return None


def get_concordance(from_classification, to_classification, category):
    """
    Get the concordance DataFrame based on the specified classifications.
    Parameters
    ----------
    from_classification: str
        The source classification name (e.g., "bonsai").
    to_classification: str
        The target classification name (e.g., "nace_rev2").
    category: str
        category to look in (e.g. location, activitytype)
    Returns
    -------
    pd.DataFrame
        The concordance DataFrame if 1 file is found; otherwise, a dict of DataFrames.
    """
    # Construct the file name
    fitting_file_names = [
        f"conc_{from_classification}_{to_classification}.csv",
        f"concpair_{from_classification}_{to_classification}.csv",
    ]
    reversed_file_names = [
        f"conc_{to_classification}_{from_classification}.csv",
        f"concpair_{to_classification}_{from_classification}.csv",
    ]
    path_dict = {
        "activitytype": "data/flow/activitytype/",
        "location": "data/location/",
        "dataquality": "data/dataquality/",
        "uncertainty": "data/uncertainty/",
        "time": "data/time/",
        "flowobject": "data/flow/flowobject/",
        "flow": "data/flow/",
        "currency": "data/currency/",
    }

    file_path = path_dict[f"{category}"]
    file_paths = [file_path]

    multiple_dfs = {}
    for f in file_paths:
        for n in fitting_file_names:
            file_path = ROOT_PATH.joinpath(f, n)
            df = _get_concordance_file(file_path)
            if not df is None:
                multiple_dfs[f"{f}"] = df
        for n in reversed_file_names:
            file_path = ROOT_PATH.joinpath(f, n)
            df = _get_concordance_file(file_path)
            if not df is None:
                # Renaming columns
                new_columns = {}
                for col in df.columns:
                    if "_from" in col:
                        new_columns[col] = col.replace("_from", "_to")
                    elif "_to" in col:
                        new_columns[col] = col.replace("_to", "_from")
                df.rename(columns=new_columns, inplace=True)

                # Changing the comment column
                df["comment"] = df["comment"].replace(
                    {
                        "one-to-many correspondence": "many-to-one correspondence",
                        "many-to-one correspondence": "one-to-many correspondence",
                    }
                )
                df["skos_uri"] = df["skos_uri"].replace(
                    {
                        "http://www.w3.org/2004/02/skos/core#narrowMatch": "http://www.w3.org/2004/02/skos/core#broadMatch",
                        "http://www.w3.org/2004/02/skos/core#broadMatch": "http://www.w3.org/2004/02/skos/core#narrowMatch",
                    }
                )
                multiple_dfs[f"{f}"] = df

    if len(multiple_dfs) == 1:
        return multiple_dfs[next(iter(multiple_dfs))]
    elif len(multiple_dfs) > 1:
        return multiple_dfs
    else:
        raise FileNotFoundError(
            f"No concordance for '{from_classification}' and '{to_classification}' found."
        )


def get_tree(for_classification, ctype):
    """
    Get the tree table as DataFrame for a classification
    Parameters
    ----------
    for_classification: str
        Name of the requested classification (e.g., "nace_rev2").
    Returns
    -------
    pd.DataFrame
        The tree as DataFrame
    """
    # Search all file_paths
    if ctype in ["activitytype", "flowobject"]:
        ctype = f"flow/{ctype}"
    file_path = ROOT_PATH.joinpath("data", ctype, f"tree_{for_classification}.csv")
    return _get_concordance_file(file_path)


def print_tree(self, toplevelcode):
    """Print the tree structure for a given code.

    Bold text represent sub-categories which are included when applying it in the Bonsai SUT.
    Italic text represent sub-categories which are not included, since these are separate codes in the Bonsai SUT.

    """
    all_codes = self.get_children(
        toplevelcode,
        deep=True,
        return_parent=True,
    )
    sut_codes = self.get_children(
        toplevelcode,
        deep=True,
        return_parent=True,
    )
    # Create nodes from the data
    nodes = {}
    for _, row in all_codes.iterrows():
        nodes[row["code"]] = Node(
            row["code"], parent=nodes.get(row["parent_code"]), descript=row["name"]
        )

    italic_codes = set(sut_codes["code"])  # Set of codes to make italic
    for pre, fill, node in RenderTree(nodes[toplevelcode]):
        if node.name in italic_codes:
            print(f"{pre}\033[1m{node.name} - {node.descript}\033[0m")  # Italicize text
        else:
            print(f"{pre}\033[3m{node.name} - {node.descript}\033[0m")


def convert_name(self, name):
    """
    Convert a name or list of names based on regex matching rules defined in the DataFrame.

    This method searches for matches using the 'location_from' regex patterns
    and returns the corresponding 'location_to' values for each match.

    Parameters:
    ----------
    name : str or list of str
        A single name (string) or a list of names to convert.

    Returns:
    -------
    list or list of lists or None
        - If a single name is provided, returns a list of matched 'location_to' values,
          or None if no matches are found.
        - If a list of names is provided, returns a list where each element is either:
            * a list of matched 'location_to' values for the corresponding input name, or
            * None if no matches are found for that name.

    Raises:
    ------
    NotImplementedError
        If the 'classification_from' column does not contain the value 'regex'.

    Example:
    -------
    >>> conc_bonsai_regex.convert_name("USA")
    'US'

    >>> conc_bonsai_regex.convert_name(["Great Britain", "China"])
    ['GB', 'CN']
    """
    if "regex" not in self["classification_from"].values:
        raise NotImplementedError("Method not applicable, since no 'regex' column.")

    def get_matches(single_name):
        matches = []
        for _, row in self.iterrows():
            if re.search(row["location_from"], single_name):
                matches.append(row["location_to"])
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        return matches

    if isinstance(name, list):
        return [get_matches(n) for n in name]
    else:
        return get_matches(name)


def nearest_other_code(self, code, correspondence_to_other):
    """
    Return the nearest OTHER code that corresponds to the given code of a classification tree.

    Searches for any descendant (child, grandchild, etc.) with the same name
    and in_final_sut == True. If not found, moves up to ancestors.

    :param self: Pandas DataFrame containing the hierarchical tree (with 'code', 'parent_code', 'name', 'in_final_sut')
    :param code: The code to check
    :param correspondence_to_other: Pandas DataFrame with corresponding mapping to another classification
    :return tuple: (original_code, corresponding_sut_code) or None if no match is found
    """
    visited_codes = set()

    correspondence_to_other

    def get_sut_mapping(original_code):
        code_str = str(original_code)

        df = correspondence_to_other.copy()

        # List of possible from/to column pairs
        column_pairs = [
            ("flowobject_from", "flowobject_to"),
            ("activitytype_from", "activitytype_to"),
            ("location_from", "location_to"),
        ]

        for col_from, col_to in column_pairs:
            # Normalize columns
            if col_from in df.columns and col_to in df.columns:
                df[col_from] = df[col_from].astype(str)
                df[col_to] = df[col_to].astype(str)

                # Forward match: code == to → return from
                forward = df[df[col_to] == code_str]
                if not forward.empty:
                    return forward[col_from].values[0]

                # Reverse match: code == from → return to
                reverse = df[df[col_from] == code_str]
                if not reverse.empty:
                    return reverse[col_to].values[0]

        return None

    def find_valid_descendant(current_code, name):
        descendants = self[self["parent_code"] == current_code]
        matches = []
        for _, descendant in descendants.iterrows():
            sut_code = get_sut_mapping(descendant["code"])
            if sut_code:
                matches.append((descendant["code"], sut_code))
            child_matches = find_valid_descendant(descendant["code"], name)
            matches.extend(child_matches)
        return matches

    while True:
        if code in visited_codes:
            return None  # Avoid cycles
        visited_codes.add(code)

        row = self[self["code"] == code]
        if row.empty:
            return None

        name = row["name"].values[0]

        # Check descendants
        descendant_result = find_valid_descendant(code, name)
        if descendant_result:
            return descendant_result

        # Check current code
        if row["code"].values[0] == code:
            sut_code = get_sut_mapping(code)
        if sut_code:
            return code, sut_code

        # Move to parent
        parent_code = row["parent_code"].values[0]
        if pandas.isna(parent_code) or parent_code == "":
            return None

        code = parent_code


# Subclass pandas DataFrame
class CustomDataFrame(pandas.DataFrame):
    lookup = lookup
    get_children = get_children
    print_tree = print_tree
    convert_name = convert_name
    nearest_other_code = nearest_other_code


@lru_cache(maxsize=1)
def get_currency_rate_df():
    with importlib.resources.files("classifications.data.unit.monetary").joinpath(
        "fact_currency_per_usd.csv"
    ).open("r") as file:
        return pandas.read_csv(file)


@lru_cache(maxsize=1)
def get_deflator_df():
    with importlib.resources.files("classifications.data.unit.monetary").joinpath(
        "fact_deflator_deu.csv"
    ).open("r") as file:
        return pandas.read_csv(file)


def convert_currency(value_from, from_currency, to_currency, ureg):
    df_curr_rate = get_currency_rate_df()
    df_defl_factor = get_deflator_df()

    # split up the currency
    from_currency, from_year = from_currency.split("_", 1)
    to_currency, to_year = to_currency.split("_", 1)
    from_year = int(from_year)
    to_year = int(to_year)

    row_from = df_curr_rate[
        (df_curr_rate["unit"] == f"{from_currency}/USD")
        & (df_curr_rate["time"] == from_year)
    ]
    if row_from.empty:
        raise ValueError(f"No rate for {from_currency}/USD in from_year {from_year}")
    rate_from_per_usd = row_from["value"].iloc[0]

    # Get rate of to_currency per USD
    row_to = df_curr_rate[
        (df_curr_rate["unit"] == f"{to_currency}/USD")
        & (df_curr_rate["time"] == from_year)
    ]
    if row_to.empty:
        raise ValueError(f"No rate for {to_currency}/USD in to_year {to_year}")
    rate_to_per_usd = row_to["value"].iloc[0]

    # Convert: from/USD divided by to/USD
    rate_from_per_to = rate_from_per_usd / rate_to_per_usd

    # Adjust with the deflator
    deflator_to = df_defl_factor[df_defl_factor["time"] == to_year]["value"].iloc[0]
    deflator_from = df_defl_factor[df_defl_factor["time"] == from_year]["value"].iloc[0]

    new_currency = rate_from_per_to * deflator_to / deflator_from

    return value_from / new_currency * (getattr(ureg, f"{to_currency}_{to_year}"))
