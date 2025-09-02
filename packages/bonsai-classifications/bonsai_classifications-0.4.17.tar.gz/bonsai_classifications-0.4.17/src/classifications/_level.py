import csv
import os
import tempfile
from pathlib import Path

ROOT_PATH = Path(os.path.dirname(__file__))


def update_levels(file_path):
    def read_csv(file_path):
        with open(file_path, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
        return data, reader.fieldnames

    def write_csv(file_path, fieldnames, rows):
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, newline="", dir=os.path.dirname(file_path)
        ) as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            temp_file_path = temp_file.name
        os.replace(temp_file_path, file_path)

    def compute_level(row, data):
        # Ensure that the 'code' field exists in the row
        if "code" not in row:
            raise KeyError(f"Missing 'code' field in row: {row}")
        level = 0
        parent_code = row["parent_code"]
        visited_codes = set()
        while parent_code != "":
            if parent_code in visited_codes:
                # Circular reference detected
                raise ValueError(
                    f"Circular reference detected starting at code '{row['code']}' in file '{file_path}'"
                )
            visited_codes.add(parent_code)
            level += 1
            parent_row = next(
                (item for item in data if item.get("code") == parent_code), None
            )
            if parent_row is None:
                raise ValueError(
                    f"Parent code '{parent_code}' for code '{row['code']}'."
                )

            parent_code = parent_row.get("parent_code", "")

        return level

    # Read the CSV file
    data, fieldnames = read_csv(file_path)

    # Ensure 'level' column is added to fieldnames
    if "level" not in fieldnames:
        fieldnames.append("level")

    # Compute levels for each row
    for row in data:
        try:
            row["level"] = compute_level(row, data)
        except ValueError as e:
            print(e)

    # Write the updated rows back to the same CSV file
    write_csv(file_path, fieldnames, data)


if __name__ == "__main__":
    directories = [
        ROOT_PATH.joinpath("data/flow/activitytype"),
        ROOT_PATH.joinpath("data/dataquality"),
        ROOT_PATH.joinpath("data/flow/flowobject"),
        ROOT_PATH.joinpath("data/location"),
        ROOT_PATH.joinpath("data/time"),
        ROOT_PATH.joinpath("data/uncertainty"),
    ]
    for d in directories:
        csv_files = [
            os.path.join(d, file)
            for file in os.listdir(d)
            if file.endswith(".csv") and not file.startswith("bonsai")
        ]
        for file in csv_files:
            print(f"{file}")
            if "tree_" in str(file):
                update_levels(file_path=file)
