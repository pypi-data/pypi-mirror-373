import argparse
import csv
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from logging import getLogger
from pathlib import Path

import classifications

ROOT_PATH = Path(os.path.dirname(__file__))

logger = getLogger("root")


def build_mapping_dict(rows, source_name, target_name):
    source_to_targets = defaultdict(set)
    target_to_sources = defaultdict(set)

    for row in rows:
        source = row[source_name]
        target = row[target_name]
        source_to_targets[source].add(target)
        target_to_sources[target].add(source)

    return source_to_targets, target_to_sources


# Define a function to determine the comment based on the counts
def get_comment(source, target, source_to_targets, target_to_sources):
    targets = source_to_targets.get(source, set())
    sources = target_to_sources.get(target, set())

    if len(targets) == 1 and len(sources) == 1:
        return "one-to-one correspondence"
    elif len(targets) > 1 and len(sources) == 1:
        # Check if the *other* targets also have multiple sources
        if any(len(target_to_sources[other_target]) > 1 for other_target in targets if other_target != target):
            return "ambiguous one-to-many correspondence"
        return "one-to-many correspondence"
    elif len(targets) == 1 and len(sources) > 1:
        # Check if the *source* targets also have multiple sources
        if any(len(source_to_targets[other_source]) > 1 for other_source in sources if other_source != source):
            return "ambiguous many-to-one correspondence" 
        return "many-to-one correspondence"
    elif len(targets) > 1 and len(sources) > 1:
        return "many-to-many correspondence"
    return ""




skos_uri_dict = {
    "one-to-one correspondence": "http://www.w3.org/2004/02/skos/core#exactMatch",
    "one-to-many correspondence": "http://www.w3.org/2004/02/skos/core#narrowMatch",
    "ambiguous one-to-many correspondence": "http://www.w3.org/2004/02/skos/core#narrowMatch",
    "many-to-one correspondence": "http://www.w3.org/2004/02/skos/core#broadMatch",
    "ambiguous many-to-one correspondence": "http://www.w3.org/2004/02/skos/core#broadMatch",
    "many-to-many correspondence": "http://www.w3.org/2004/02/skos/core#relatedMatch",
    "": "",
}


def add_mapping_comment(csv_file, overwrite="True"):
    """Helper to determine the mapping type.

    Attention!
    Only use overwrite='True' if only the most detailed codes of a classification are mapped.
    If parent codes are included in the correspondence table, the automated mapping would lead to wrong results.

    Arguments
    ---------
    csv_file: string
        path to csv file
    overwrite: string
        'True' to automate the mapping
        'False' if comment the column already includes the mapping type
    """
    if not os.path.exists(csv_file):
        logger.warning(f"File {csv_file} not found. Skipping...")
        return

    with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        column_names = reader.fieldnames

    if not rows or not column_names:
        logger.warning(f"No valid data found in {csv_file}. Skipping...")
        return

    source_name, target_name = column_names[
        :2
    ]  # First two columns assumed as source & target

    # Count occurrences in advance for optimization
    source_to_targets, target_to_sources = build_mapping_dict(rows, source_name, target_name)

    if overwrite == "True":
        logger.warning(
            "Comment column, and thus the mapping type will be newly determined."
        )

        # Process rows
        for row in rows:
            source, target = row.get(source_name, ""), row.get(target_name, "")
            if source and target:
                row["comment"] = get_comment(
                    source, target, source_to_targets, target_to_sources
                )

                row["skos_uri"] = skos_uri_dict[row["comment"]]
            else:
                logger.warning(f"Skipping row with missing data: {row}")

    elif overwrite == "False":
        # Process rows
        for row in rows:
            source, target = row.get(source_name, ""), row.get(target_name, "")
            if source and target:
                row["skos_uri"] = skos_uri_dict[row["comment"]]
            else:
                logger.warning(f"Skipping row with missing data: {row}")

    # Write updated data to a temp file
    # Ensure "comment" and "skos_uri" are only added if they don't already exist
    if "comment" not in column_names:
        column_names.append("comment")
    if "skos_uri" not in column_names:
        column_names.append("skos_uri")

    fieldnames = column_names

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, newline="", encoding="utf-8"
    ) as temp_file:
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    # Replace the original file
    shutil.move(temp_file.name, csv_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process a specific CSV file to add mapping comments."
    )
    parser.add_argument("csv_file", help="Path to the CSV file you want to process.")
    parser.add_argument(
        "overwrite",
        help="Boolean, if True comment column will be overwritten, and thus the mapping type newly determined.",
    )

    args = parser.parse_args()

    if os.path.exists(args.csv_file):
        add_mapping_comment(args.csv_file, args.overwrite)
    else:
        logger.error(f"File {args.csv_file} not found.")
