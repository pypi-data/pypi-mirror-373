import argparse
import os

import classifications


def main():
    parser = argparse.ArgumentParser(description="Disaggregate Bonsai Codes")
    parser.add_argument(
        "category", type=str, help="Bonsai category (e.g. activitytype or flowobject)"
    )
    parser.add_argument(
        "yaml_file", type=str, help="Path to the YAML file with disaggregation data"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save the updated DataFrames",
    )

    args = parser.parse_args()

    if args.category == "activitytype":
        processor = classifications.activitytype.datapackage
    elif args.category == "flowobject":
        processor = classifications.flowobject.datapackage
    elif args.category == "location":
        processor = classifications.location.datapackage
    elif args.category == "uncertainty":
        processor = classifications.uncertainty.datapackage
    elif args.category == "dataquality":
        processor = classifications.dataquality.datapackage
    elif args.category == "time":
        processor = classifications.time.datapackage
    else:
        raise NotImplementedError(
            f"your choice '{args.category}' is not a Bonsai category"
        )

    # Call the disaggregate_bonsai method with the path to the YAML file
    result = processor.disaggregate_bonsai(args.yaml_file)

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Save each DataFrame in the result as a CSV file only if it has changed
    for attr_name in result:
        original_df = getattr(processor, attr_name)
        updated_df = result[attr_name]

        # Check if the DataFrame has changed
        if not updated_df.equals(original_df):
            output_path = os.path.join(args.output_dir, f"{attr_name}_updated.csv")
            updated_df.to_csv(output_path, index=False)
            print(f"Saved updated DataFrame '{attr_name}' to {output_path}")
        else:
            print(f"No changes detected for DataFrame '{attr_name}'. Skipping save.")


if __name__ == "__main__":
    main()
