import os
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import classifications
from classifications import _mapping_type

test_file = Path(os.path.dirname(__file__)).parent / "tests/data/conc_test.csv"
test_tree_file = (
    Path(os.path.dirname(__file__)).parent / "tests/data/tree_test_correspondence.csv"
)


def test_mapping_type():
    tree_test = pd.read_csv(test_tree_file)

    classifications.flowobject.datapackage.tree_test_correspondence = tree_test

    _mapping_type.add_mapping_comment(test_file)
    df_result = pd.read_csv(test_file)
    assert df_result["comment"].to_list() == [
        "ambiguous one-to-many correspondence",
        "many-to-many correspondence",
        "one-to-one correspondence",
        "many-to-one correspondence",
        "many-to-one correspondence",
        "ambiguous one-to-many correspondence",
        "many-to-many correspondence",
        "many-to-many correspondence",
        "many-to-many correspondence",
    ]
