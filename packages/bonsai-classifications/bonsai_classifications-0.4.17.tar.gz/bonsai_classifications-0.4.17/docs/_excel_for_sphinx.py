# generate_excel.py
import os

import pandas as pd

# def generate_excel_files():
#    # Get the directory where the script is located
#    script_dir = os.path.dirname(os.path.abspath(__file__))
#
#    directories = [
#        "flow/activitytype",
#        # "dataquality",
#        "flow/flowobject",
#        # "location",
#        # "time",
#        # "uncertainty",
#    ]
#
#    # Define the output directory for Excel files within the Sphinx _static directory
#    excel_dir = os.path.join(script_dir, "_static", "excel_files")
#
#    # Create the output directory if it doesn't exist
#    os.makedirs(excel_dir, exist_ok=True)
#
#    # Convert all CSV files to Excel
#    for d in directories:
#        csv_dir = os.path.normpath(
#            os.path.join(script_dir, "..", "src", "classifications", "data", d)
#        )
#
#        dict_with_dfs = {}
#
#        for csv_file in os.listdir(csv_dir):
#            if csv_file.endswith(".csv") and "conc_bonsai" in csv_file and "bonsai.csv" in csv_file:
#                # Read the CSV file
#                csv_path = os.path.join(csv_dir, csv_file)
#                df = pd.read_csv(csv_path, encoding="utf-8", sep=",", dtype="str")
#                dict_with_dfs[f"{csv_file}"] = df
#            if csv_file.endswith(".csv") and "tree_bonsai" in csv_file:
#                # Read the CSV file
#                csv_path = os.path.join(csv_dir, csv_file)
#                df_merged = pd.read_csv(
#                    csv_path, encoding="utf-8", sep=",", dtype="str"
#                )
#
#        matching_keys = [key for key in dict_with_dfs if "tree_bonsai" in key]
#        if len(matching_keys) > 1:
#            raise ValueError(
#                f"Too many files with 'tree_bonsai' in filename inside {d}"
#            )
#        try:
#            for k, df in dict_with_dfs.items():
#                if k != "tree_bonsai":
#                    if "activitytype_from" in df.columns:
#                        if df["classification_from"][0].lower() == "bonsai":
#                             column_to_merge = "activitytype_from"
#                             class_name = df["classification_to"][0]
#                             df = df.drop(columns=["comment", "skos_uri", "alias_code"])
#                             class_name = df["classification_to"][0]
#                             df = df.rename(columns={"activitytype_to": class_name})
#                             df = (
#                                 df.groupby("activitytype_from")[df.columns[1]]
#                                 .apply(list)
#                                 .reset_index()
#                             )
#
#                             df_merged = pd.merge(
#                                 df_merged,
#                                 df,
#                                 left_on="code",
#                                 right_on=str(column_to_merge),
#                                 how="left",
#                             )
#                        elif df["classification_to"][0].lower() == "bonsai":
#                            column_to_merge = "activitytype_to"
#                            class_name = df["classification_from"][0]
#                            df = df.drop(columns=["comment", "skos_uri", "alias_code"], errors="ignore")
#                            df = df.rename(columns={"activitytype_from": class_name})
#                            df = (
#                                df.groupby(column_to_merge)[df.columns[1]]
#                                .apply(list)
#                                .reset_index()
#                            )
#                            df_merged = pd.merge(
#                                df_merged,
#                                df,
#                                left_on="code",
#                                right_on=column_to_merge,
#                                how="left",
#                            )
#                    if "flowobject_from" in df.columns:
#                        if df["classification_from"][0].lower() == "bonsai":
#                             column_to_merge = "flowobject_from"
#                             class_name = df["classification_to"][0]
#                             df = df.drop(columns=["comment", "skos_uri", "alias_code"])
#                             class_name = df["classification_to"][0]
#                             df = df.rename(columns={"flowobject_to": class_name})
#                             df = (
#                                 df.groupby("flowobject_from")[df.columns[1]]
#                                 .apply(list)
#                                 .reset_index()
#                             )
#
#                             df_merged = pd.merge(
#                                 df_merged,
#                                 df,
#                                 left_on="code",
#                                 right_on=str(column_to_merge),
#                                 how="left",
#                             )
#                        elif df["classification_to"][0].lower() == "bonsai":
#                            column_to_merge = "flowobject_to"
#                            class_name = df["classification_from"][0]
#                            df = df.drop(columns=["comment", "skos_uri", "alias_code"], errors="ignore")
#                            df = df.rename(columns={"flowobject_from": class_name})
#                            df = (
#                                df.groupby(column_to_merge)[df.columns[1]]
#                                .apply(list)
#                                .reset_index()
#                            )
#                            df_merged = pd.merge(
#                                df_merged,
#                                df,
#                                left_on="code",
#                                right_on=column_to_merge,
#                                how="left",
#                            )
#            df_merged = df_merged.loc[
#                :, ~df_merged.columns.str.startswith("flowobject_from")
#            ]
#            df_merged = df_merged.loc[
#                :, ~df_merged.columns.str.startswith("activitytype_from")
#            ]
#
#        except (KeyError, IndexError):
#            pass
#
#        # Define the Excel file name and path
#        if d.startswith("flow/"):
#            d = d[len("flow/") :]
#        else:
#            pass
#        excel_file = f"{d}_tree_bonsai.xlsx"
#        excel_path = os.path.join(excel_dir, excel_file)
#        # Save the data as an Excel file
#        df_merged.to_excel(excel_path, index=False)
#
#
# if __name__ == "__main__":
#    generate_excel_files()


def merge_concordance(df_merged, df, entity_type):
    # Detect if bonsai is from or to
    classification_from = df["classification_from"].iloc[0].lower()
    classification_to = df["classification_to"].iloc[0].lower()

    if classification_from == "bonsai":
        from_col = f"{entity_type}_from"
        to_col = f"{entity_type}_to"
        class_name = df["classification_to"].iloc[0]
    elif classification_to == "bonsai":
        from_col = f"{entity_type}_to"
        to_col = f"{entity_type}_from"
        class_name = df["classification_from"].iloc[0]
    else:
        return df_merged  # Not a bonsai mapping

    # Clean and group
    df = df.drop(columns=["comment", "skos_uri", "alias_code"], errors="ignore")
    df = df.rename(columns={to_col: class_name})

    df_grouped = df.groupby(from_col)[class_name].apply(list).reset_index()

    df_merged = pd.merge(
        df_merged, df_grouped, left_on="code", right_on=from_col, how="left"
    )

    df_merged = df_merged.drop(columns=[from_col], errors="ignore")
    return df_merged


def generate_excel_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    directories = [
        "flow/activitytype",
        "flow/flowobject",
    ]

    excel_dir = os.path.join(script_dir, "_static", "excel_files")
    os.makedirs(excel_dir, exist_ok=True)

    for d in directories:
        csv_dir = os.path.normpath(
            os.path.join(script_dir, "..", "src", "classifications", "data", d)
        )

        dict_with_dfs = {}
        df_merged = None

        for csv_file in os.listdir(csv_dir):
            csv_path = os.path.join(csv_dir, csv_file)

            # Load tree bonsai file
            if "tree_bonsai" in csv_file and csv_file.endswith(".csv"):
                df_merged = pd.read_csv(
                    csv_path, encoding="utf-8", sep=",", dtype="str"
                )

            # Load all conc_*.csv concordance files
            elif csv_file.startswith("conc_") and csv_file.endswith(".csv"):
                df = pd.read_csv(csv_path, encoding="utf-8", sep=",", dtype="str")

                # Check if bonsai is involved
                if (
                    df["classification_from"].iloc[0].lower() == "bonsai"
                    or df["classification_to"].iloc[0].lower() == "bonsai"
                ):
                    dict_with_dfs[csv_file] = df

        if df_merged is None:
            print(f"Warning: No tree_bonsai file found in {d}")
            continue

        for k, df in dict_with_dfs.items():
            if "activitytype_from" in df.columns or "activitytype_to" in df.columns:
                df_merged = merge_concordance(df_merged, df, "activitytype")
            elif "flowobject_from" in df.columns or "flowobject_to" in df.columns:
                df_merged = merge_concordance(df_merged, df, "flowobject")

        # Remove any leftover source columns
        df_merged = df_merged.loc[:, ~df_merged.columns.str.startswith("activitytype_")]
        df_merged = df_merged.loc[:, ~df_merged.columns.str.startswith("flowobject_")]

        # Save Excel
        d_clean = d.split("/")[-1]
        excel_file = f"{d_clean}_tree_bonsai.xlsx"
        excel_path = os.path.join(excel_dir, excel_file)
        df_merged.to_excel(excel_path, index=False)
        print(f"Saved: {excel_file}")


if __name__ == "__main__":
    generate_excel_files()
