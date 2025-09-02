import re
from importlib.resources import files

import pandas as pd
from dataio.resources import CSVResourceRepository

paths = [
    "flow/activitytype/",
    "location/",
    "dataquality/",
    "uncertainty/",
    "time/",
    "flow/flowobject/",
    "flow/",
]


source = files("classifications.data")


def test_dataio():
    for p in paths:
        path_to_resource = source.joinpath(p)
        repo = CSVResourceRepository(db_path=path_to_resource)
        resources = repo.list_available_resources()
        for r in resources:
            if r.name[0].isdigit():
                raise ValueError(
                    f"File name '{r.name}' starts with number in resource '{path_to_resource}'."
                )
            if not re.match(r"^[a-zA-Z0-9_]*$", r.name):
                raise ValueError(
                    f"File name '{r.name}' contains special character in resource '{path_to_resource}'."
                )
            df = repo.get_dataframe_for_task(r.name)
            if type(df) != pd.DataFrame:
                raise TypeError(
                    f"File '{r.name}' is not a pandas.DataFrame. Check location paths in the '{path_to_resource}/resource.csv'."
                )
