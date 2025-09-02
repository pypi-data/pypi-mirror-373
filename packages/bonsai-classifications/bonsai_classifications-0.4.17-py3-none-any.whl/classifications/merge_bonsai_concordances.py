import argparse
import os

import pandas as pd

import classifications


def restructure_dataframe(original_df, folder_name, suffix):
    columns = original_df.columns[:2]
    final_df = pd.DataFrame()

    # Rename columns based on folder_name
    final_df["tree_bonsai_activitytype"] = (
        original_df["tree_bonsai"] if folder_name == "activitytype" else None
    )
    final_df["tree_bonsai_flowobject"] = (
        original_df["tree_bonsai"] if folder_name == "flowobject" else None
    )

    for col in columns:
        if folder_name == "activitytype":
            final_df["tree_other_activitytype"] = original_df[col]
            final_df["tree_other_flowobject"] = None  # Ensure flowobject column is None
        elif folder_name == "flowobject":
            final_df[
                "tree_other_activitytype"
            ] = None  # Ensure activitytype column is None
            final_df["tree_other_flowobject"] = original_df[col]

    final_df["comment"] = original_df["comment"]
    final_df["skos_uri"] = original_df["skos_uri"]

    final_df["other_classification"] = suffix.replace("tree_", "")

    # Replace NaN with None for clarity
    final_df = final_df.where(pd.notnull(final_df), None)

    return final_df


def main():
    parser = argparse.ArgumentParser(
        description="Merge all Bonsai concordance tables into one"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save the updated DataFrames",
    )

    args = parser.parse_args()

    # (table, other_classification_name)
    attributes = dir(classifications.activitytype.datapackage)
    # value = getattr(getattr(classifications, 'activitytype.datapackage'), attr_string)
    conc_activitytype = [
        (
            getattr(
                getattr(classifications, "activitytype"), "datapackage"
            ).__getattribute__(attr),
            attr[len("conc_bonsai_") :],
        )
        for attr in attributes
        if attr.startswith("conc_bonsai_")
    ]

    attributes = dir(classifications.flowobject.datapackage)
    conc_flowobject = [
        (
            getattr(
                getattr(classifications, "flowobject"), "datapackage"
            ).__getattribute__(attr),
            attr[len("conc_bonsai_") :],
        )
        for attr in attributes
        if attr.startswith("conc_bonsai_")
    ]

    attributes = dir(classifications.flow.datapackage)
    conc_flow = [
        (
            getattr(getattr(classifications, "flow"), "datapackage").__getattribute__(
                attr
            ),
            attr[len("concpair_bonsai_") :],
        )
        for attr in attributes
        if attr.startswith("concpair_bonsai_")
    ]

    # Desired column order
    new_order = [
        "activitytype_from",
        "flowobject_from",
        "activitytype_to",
        "flowobject_to",
        "classification_from",
        "classification_to",
        "comment",
        "skos_uri",
    ]

    conc_merged = conc_flow[0][0]
    for c in conc_flow[1:]:
        conc_merged = pd.concat([conc_merged, c[0]], ignore_index=True)

    for c in conc_activitytype:
        conc_merged = pd.concat([conc_merged, c[0]], ignore_index=True)

    for c in conc_flowobject:
        conc_merged = pd.concat([conc_merged, c[0]], ignore_index=True)

    conc_merged = conc_merged[new_order]

    print(conc_merged)
    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    output_path = f"{args.output_dir}/merged_concordance.csv"
    # Save each DataFrame in the result as a CSV file only if it has changed
    conc_merged.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
