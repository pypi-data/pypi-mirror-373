"""
Created on Wed Nov 13 16:32:05 2024

Author: Sander van Nielen
"""
import json

import pandas as pd
from _mapping_type import add_mapping_comment
from _unique_id import add_unique_identifiers


def read_showvoc(json_file, short_names: list, path="."):
    """Read a JSON-LD file (as downloaded from https://showvoc.op.europa.eu/)
    and save it as a table in CSV format
    """
    short_names = [name.lower() for name in short_names]
    names = ["tree_" + name for name in short_names]
    data = {name: [] for name in names}

    with open(json_file, "r") as file:
        raw_json = json.load(file)
    # Navigate through the JSON structure
    for item in raw_json:
        for key in item:
            if key != "@id":
                for match_ in item[key]:
                    # Store the code of the source classification and its matching target
                    data[names[0]].append(item["@id"].split("/")[-1])
                    data[names[1]].append(match_["@id"].split("/")[-1])

    # Create a dataframe, including some empty columns
    df = pd.DataFrame(data)
    for new_col in ["comment", "skos_uri"]:
        df[new_col] = None

    # Save as CSV, and apply filler functions to the empty columns
    csv_path = f"{path}/conc_{short_names[0]}_{short_names[1]}.csv"
    df.to_csv(csv_path, index=False)
    add_mapping_comment(csv_path)
    add_unique_identifiers(csv_path)


json_file = "C:\\Users\\nielenssvan\\OneDrive - Universiteit Leiden\\BONSAI\\correspondence_tables\\CPA_2_1_CPC_2_1.jsonld"
read_showvoc(json_file, short_names=["CPA_2_1", "CPC_2_1"])
