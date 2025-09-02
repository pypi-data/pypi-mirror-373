import os
from logging import getLogger
from pathlib import Path

import pandas as pd
import yaml
from pandas._libs.parsers import STR_NA_VALUES

from ._utils import (
    CustomDataFrame,
    activitytype_path,
    dataquality_path,
    flow_path,
    flowobject_path,
    location_path,
    time_path,
    uncertainty_path,
    unit_magnitude_path,
    unit_monetary_path,
    unit_physical_path,
)

logger = getLogger("root")

ROOT_PATH = Path(os.path.dirname(__file__))

accepted_na_values = STR_NA_VALUES - {"NA"}


class DataPackage:
    def to_dict(self):
        result = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, pd.DataFrame):
                result[attr_name] = attr_value
        return result

    def disaggregate_bonsai(self, codes_or_yaml):
        """Disaggregates the code in the bonsai tables.

        Currently only for activitytype and flowobject.

        Argument
        --------
        codes_or_yaml: dict or str
            A dictionary containing the disaggregation mappings or a string path to a YAML file.
            Example::

                disaggregations:
                  - old_code: "ai"
                    new_codes:
                      - code: "ai_0"
                        description: "foo"
                        mappings: {"nace_rev1": ["0.11", "0.12"]}
                      - code: "ai_1"
                        description: ""
                        mappings: {}

        Returns
        -------
        dict
            dict with updated bonsai tables
        """

        # Determine if the input is a dictionary or a YAML file path
        if isinstance(codes_or_yaml, dict):
            disaggregations = codes_or_yaml.get("disaggregations", [])
        elif isinstance(codes_or_yaml, str):
            # Load the YAML file
            with open(codes_or_yaml, "r") as file:
                yaml_content = yaml.safe_load(file)
                disaggregations = yaml_content.get("disaggregations", [])
        else:
            raise ValueError("Input must be a dictionary or a path to a YAML file")

        # Validate the structure of the YAML content
        if not isinstance(disaggregations, list):
            raise ValueError("Disaggregations should be a list of mappings")
        if not "old_code" and "new_codes" in disaggregations[0].keys():
            raise ValueError("Make sure that you provide 'old_code' and 'new_codes'.")

        result = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, pd.DataFrame):
                result[attr_name] = attr_value

        for attr_name in result:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, pd.DataFrame) and attr_name.startswith(
                "tree_bonsai"
            ):
                # For each disaggregation in the YAML content
                for disaggregation in disaggregations:
                    old_code = disaggregation["old_code"]
                    new_codes = disaggregation["new_codes"]
                    if len(new_codes) == 1:
                        raise ValueError(
                            f"Only 1 new code provided. To disaggregate {old_code}, provide at least 2 new codes!"
                        )

                    # Replace the old code with each new code in a new row
                    new_rows = attr_value[attr_value["code"] == old_code].copy()

                    for new_code in new_codes:
                        new_rows["code"] = new_code["code"]
                        new_rows["name"] = new_code["description"]
                        new_rows["parent_code"] = old_code
                        new_rows["level"] = (
                            int(attr_value[attr_value["code"] == old_code]["level"]) + 1
                        )
                        new_rows["comment"] = ""

                        # Append the new rows to the DataFrame
                        attr_value = pd.concat(
                            [attr_value, new_rows], ignore_index=True
                        )

                    # Update the DataFrame in the instance with the modified one
                    result[attr_name] = attr_value

            if (
                isinstance(attr_value, pd.DataFrame)
                and attr_name.startswith("conc_")
                and "bonsai" in attr_name
            ):
                # For each disaggregation in the YAML content
                for disaggregation in disaggregations:
                    old_code = disaggregation["old_code"]
                    new_codes = disaggregation["new_codes"]

                    # Replace the old code with each new code in a new row
                    for new_code in new_codes:
                        other_classifications = new_code.get("mappings", {})

                        df2 = pd.DataFrame(data=None, columns=attr_value.columns)

                        if other_classifications:
                            for schema, codes_list in other_classifications.items():
                                if schema in attr_name:
                                    if "activitytype_to" in df2.columns:
                                        df2["activitytype_to"] = codes_list
                                    if "flowobject_to" in df2.columns:
                                        df2["flowobject_to"] = codes_list

                            if "activitytype_from" in df2.columns:
                                df2["activitytype_from"] = new_code["code"]
                            if "flowobject_from" in df2.columns:
                                df2["flowobject_from"] = new_code["code"]
                            df2["comment"] = ""
                            df2["skos_uri"] = ""

                            # Append the new rows to the DataFrame
                            attr_value = pd.concat([attr_value, df2], ignore_index=True)

                            # Remove old parent code from concordance DataFrame (only mapping of most detailed category required)
                            if "activitytype_from" in attr_value.columns:
                                attr_value.drop(
                                    attr_value[
                                        # attr_value["tree_bonsai"] == f"{old_code}"
                                        attr_value["activitytype_from"]
                                        == f"{old_code}"
                                    ].index,
                                    inplace=True,
                                )
                            if "flowobject_from" in attr_value.columns:
                                attr_value.drop(
                                    attr_value[
                                        # attr_value["tree_bonsai"] == f"{old_code}"
                                        attr_value["flowobject_from"]
                                        == f"{old_code}"
                                    ].index,
                                    inplace=True,
                                )
                            attr_value.reset_index(drop=True, inplace=True)

                    # Update the DataFrame in the instance with the modified one
                    result[attr_name] = attr_value

        return result


class BonsaiTreeMaster:
    def __init__(self, code, parent_code, name, level, alias_code):
        self.code = code
        self.parent_code = parent_code
        self.name = name
        self.level = level
        self.alias_code = alias_code


class TreeMasterFlowobject(BonsaiTreeMaster):
    def __init__(
        self,
        code,
        parent_code,
        name,
        level,
        compartment,
        chemical_compound,
        default_unit,
        alias_code,
    ):
        super().__init__(code, parent_code, name, level, alias_code)
        self.compartment = compartment
        self.chemical_compound = chemical_compound
        self.default_unit = default_unit


class BonsaiDimMaster:
    def __init__(self, code, name, description, comment):
        self.code = code
        self.name = name
        self.description = description
        self.comment = comment


def list_csv_files_excluding(directory_path, exclude_file):
    # List all CSV files in the directory, excluding the specified file
    csv_files = [
        file for file in directory_path.glob("*.csv") if file.name != exclude_file
    ]
    return csv_files


def read_csv_files_as_dataframes(directory_path, exclude_file, prefix_dtype_mapping):
    csv_files = list_csv_files_excluding(directory_path, exclude_file)
    dataframes = {}
    for csv_file in csv_files:
        try:
            # Get the dtype dictionary based on the column name prefixes
            dtype_dict = get_dtype_dict_by_prefixes(csv_file, prefix_dtype_mapping)
            # Read each CSV file into a DataFrame with the specified dtypes
            file_stem = csv_file.stem  # Get the filename without the extension
            dataframes[file_stem] = pd.read_csv(
                csv_file, dtype=dtype_dict, na_values=[], keep_default_na=False
            )
        except Exception as e:
            logger.info(f"Error reading {csv_file.name}: {e}")
    return dataframes


def get_dtype_dict_by_prefixes(file_path, prefix_dtype_mapping):
    # Read the first row to get column names
    temp_df = pd.read_csv(file_path, nrows=0)
    column_names = temp_df.columns.tolist()

    # Create a dictionary mapping column names to dtypes based on prefix_dtype_mapping
    dtype_dict = {}
    for prefix, dtype in prefix_dtype_mapping.items():
        dtype_dict.update(
            {col: dtype for col in column_names if col.startswith(prefix)}
        )
    return dtype_dict


dtype_dict = {
    "code": "str",
    "parent_code": "str",
    "tree_": "str",
    "dim_": "str",
    "flowobject_from": "str",
    "flowobject_to": "str",
    "activitytype_from": "str",
    "activitytype_to": "str",
}


class ObjectNames:
    def __init__(self, code):
        self.code = code


class EmptyClass:
    def __init__(self) -> None:
        pass


class Resources:
    def __init__(self, path_to_resource):
        self.datapackage = DataPackage()
        self.bonsai = DataPackage()
        self.classification_name = EmptyClass()

        dfs = read_csv_files_as_dataframes(
            directory_path=path_to_resource,
            exclude_file=None,  # ,"resource.csv",
            prefix_dtype_mapping=dtype_dict,
        )

        def _remove_keywords(text, keywords):
            for keyword in keywords:
                text = text.replace(keyword, "")
            return text

        for file_name, df in dfs.items():

            if isinstance(df, pd.DataFrame):  # and "resources.csv" not in file_name:
                setattr(self.datapackage, file_name, df)

        self._create_attributes()
        self._create_attributes_names()

        # Inject the CustomDataFrame class into the DataFrame objects in datapackage
        # Iterate over DataFrame attributes in datapackage
        for attr_name in dir(self.datapackage):
            attr = getattr(self.datapackage, attr_name)
            if isinstance(attr, pd.DataFrame):
                # Replace the DataFrame with an instance of CustomDataFrame
                setattr(self.datapackage, attr_name, CustomDataFrame(attr))

    def _create_attributes(self):
        def _remove_keywords(text, keywords):
            for keyword in keywords:
                text = text.replace(keyword, "")
            return text

        if hasattr(self.datapackage, "tree_bonsai"):
            for index, row in self.datapackage.tree_bonsai.iterrows():
                if "compartment" in self.datapackage.tree_bonsai.columns:
                    obj = TreeMasterFlowobject(
                        code=row["code"],
                        parent_code=row["parent_code"],
                        name=row["name"],
                        level=row["level"],
                        default_unit=row["default_unit"],
                        compartment=row["compartment"],
                        chemical_compound=row["chemical_compound"],
                        alias_code=row["alias_code"],
                    )
                else:
                    obj = BonsaiTreeMaster(
                        code=row["code"],
                        parent_code=row["parent_code"],
                        name=row["name"],
                        level=row["level"],
                        alias_code=row["alias_code"],
                    )
                setattr(self.bonsai, row["code"], obj)
        elif hasattr(self.datapackage, "dim_bonsai"):
            for index, row in self.datapackage.dim_bonsai.iterrows():
                obj = BonsaiDimMaster(
                    code=row["code"],
                    name=row["name"],
                    description=row["description"],
                    comment=row["comment"],
                )
                setattr(self.bonsai, row["code"], obj)

    def _create_attributes_names(self):
        def _remove_keywords(text, keywords):
            for keyword in keywords:
                text = text.replace(keyword, "")
            return text

        if hasattr(self.datapackage, "resources"):
            exclude_strings = [
                "level",
                "compartment",
                "chemical_compound",
                "lcia",
                "urban_rural",
                "distribution",
                "calendar",
                "year",
                "unit",
                "unit_conversion",
            ]
            for index, row in self.datapackage.resources.iterrows():
                _name = row["name"]
                if ("tree_" in _name or "dim_" in _name) and not any(
                    excl in _name for excl in exclude_strings
                ):
                    class_name = _remove_keywords(_name, ["tree_", "dim_"])
                    obj = ObjectNames(code=class_name)
                    # setattr(
                    #    self.classification_name,
                    #    class_name,
                    #    class_name,
                    # )
                    setattr(self.classification_name, class_name, obj)

    def get_classification_names(self):
        """
        Return considerred classification names.

        Returns
        -------
        list of strings
        """
        attribute_list = [
            attr for attr in dir(self.classification_name) if not attr.startswith("__")
        ]
        return attribute_list


def get_bonsai_classification():
    """
    Returns a dictionary of all the default bonsai classification names
    """
    bonsai_classifications = {
        "location": "bonsai",
        "activitytype": "bonsai",
        "flowobject": "bonsai",
        "flow": "bonsai",
    }
    return bonsai_classifications


def get_bonsai_schemas_mapping():
    """
    Returns dictionary that mapps bonsai schemas to bonsai codes.
    """
    mapping = {
        "ProductionVolumes": {"activitytype": ["ai"], "flowobject": ["fi"]},
        "Trade": {"activitytype": ["oa_imp", "oa_exp"], "flowobject": ["fi"]},
        "ConsumptionVolumes": {"activitytype": ["ai"], "flowobject": ["fi"]},
        "Use": {"activitytype": ["ai", "am", "aa_comp"], "flowobject": ["fi", "fm"]},
        "WasteSupply": {"activitytype": ["at"], "flowobject": ["ft"]},
        "Supply": {"activitytype": ["ai", "am", "aa_comp"], "flowobject": ["fi", "fm"]},
        "Imports": {"activitytype": ["oa_imp"], "flowobject": ["fi"]},
        "FinalUses": {"activitytype": ["oa_FU"], "flowobject": ["fi"]},
        "ValueAdded": {"activitytype": ["ai"], "flowobject": ["fec_VA"]},
        "SocialSatellite": {"activitytype": ["ai"], "flowobject": ["fs"]},
        "Valuation": {"activitytype": ["oa_VALU"], "flowobject": ["fi"]},
    }
    return mapping


activitytype = Resources(ROOT_PATH.joinpath(activitytype_path))
location = Resources(ROOT_PATH.joinpath(location_path))
dataquality = Resources(ROOT_PATH.joinpath(dataquality_path))
uncertainty = Resources(ROOT_PATH.joinpath(uncertainty_path))
time = Resources(ROOT_PATH.joinpath(time_path))
flowobject = Resources(ROOT_PATH.joinpath(flowobject_path))
flow = Resources(ROOT_PATH.joinpath(flow_path))
unit_monetary = Resources(ROOT_PATH.joinpath(unit_monetary_path))
unit_physical = Resources(ROOT_PATH.joinpath(unit_physical_path))
unit_magnitude = Resources(ROOT_PATH.joinpath(unit_magnitude_path))
