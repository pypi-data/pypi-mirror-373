import os
from pathlib import Path

import pandas as pd
import pytest
import yaml

import classifications


def test_lookup():
    result = classifications.location.datapackage.dim_level.lookup("layer")

    assert len(result.index) == 7


def test_get_children_failed():
    with pytest.raises(KeyError):
        classifications.location.datapackage.dim_level.get_children("layer")


def test_get_children():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        "01.3"
    )

    assert len(result.index) == 1


def test_get_children_multiple():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        ["01.3", "01.2"]
    )

    assert len(result.index) == 10


def test_get_children_deep():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        ["01", "03"]
    )

    assert len(result.index) == 38 + 6


def test_get_children_flat():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        ["01", "03"], deep=False
    )

    assert len(result.index) == 7 + 2


def test_get_children_with_parent():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        "01.3", return_parent=True
    )

    assert len(result.index) == 2


def test_get_children_with_parent_multiple():
    result = classifications.activitytype.datapackage.tree_nace_rev2.get_children(
        ["01.3", "01.2"], return_parent=True
    )

    assert len(result.index) == 12


def test_create_conc():
    A = pd.DataFrame(  # flowobject_from,flowobject_to,classification_from,classification_to
        {
            "activitytype_from": [
                "A_a",
                "A_b",
                "A_c",
                "A_c",
                "A_d",
                "A_d",
                "A_e",
                "A_f",
                "A_x",
            ],
            "activitytype_to": ["1", "1", "2", "3", "5", "6", "7", "7", "x"],
            "classification_from": 9 * ["XXX"],
            "classification_to": 9 * ["YYY"],
        }
    )
    B = pd.DataFrame(
        {
            "activitytype_from": [
                "111",
                "222",
                "444",
                "444",
                "555",
                "666",
                "777",
                "888",
            ],
            "activitytype_to": ["1", "1", "2", "3", "4", "5", "6", "7"],
            "classification_from": 8 * ["ZZZ"],
            "classification_to": 8 * ["YYY"],
        }
    )
    df_result = classifications.create_conc(A, B, source="XXX", target="YYY")

    df_expected = pd.DataFrame(
        {
            "activitytype_from": [
                "A_a",
                "A_a",
                "A_b",
                "A_b",
                "A_c",
                "A_d",
                "A_d",
                "A_e",
                "A_f",
            ],
            "activitytype_to": [
                "111",
                "222",
                "111",
                "222",
                "444",
                "666",
                "777",
                "888",
                "888",
            ],
            "classification_from": 9 * ["XXX"],
            "classification_to": 9 * ["YYY"],
            "comment": [
                "many-to-many correspondence",
                "many-to-many correspondence",
                "many-to-many correspondence",
                "many-to-many correspondence",
                "one-to-one correspondence",
                "one-to-many correspondence",
                "one-to-many correspondence",
                "many-to-one correspondence",
                "many-to-one correspondence",
            ],
            "skos_uri": [
                "http://www.w3.org/2004/02/skos/core#relatedMatch",
                "http://www.w3.org/2004/02/skos/core#relatedMatch",
                "http://www.w3.org/2004/02/skos/core#relatedMatch",
                "http://www.w3.org/2004/02/skos/core#relatedMatch",
                "http://www.w3.org/2004/02/skos/core#exactMatch",
                "http://www.w3.org/2004/02/skos/core#narrowMatch",
                "http://www.w3.org/2004/02/skos/core#narrowMatch",
                "http://www.w3.org/2004/02/skos/core#broadMatch",
                "http://www.w3.org/2004/02/skos/core#broadMatch",
            ],
        }
    )
    pd.testing.assert_frame_equal(df_expected, df_result)


def test_disaggregate_tree_bonsai_fails():
    with pytest.raises(ValueError):
        classifications.activitytype.datapackage.disaggregate_bonsai(
            codes_or_yaml={
                "disaggregations": [{"old_code": "ai", "new_codes": [{"code": "AI"}]}]
            }
        )


def test_disaggregate_tree_bonsai_pass():
    yaml_content = """
    disaggregations:
      - old_code: "ai"
        new_codes:
          - code: "AI"
            description: "scacaec"
            mappings: {}
          - code: "AAASSSS"
            description: ""
            mappings: {}
    """
    d = classifications.activitytype.datapackage.disaggregate_bonsai(
        codes_or_yaml=yaml.safe_load(yaml_content)
    )

    assert d["tree_bonsai"].iloc[-1]["code"] == "AAASSSS"
    assert d["tree_bonsai"].iloc[-1]["name"] == ""
    assert d["tree_bonsai"].iloc[-2]["code"] == "AI"
    assert d["tree_bonsai"].iloc[-2]["name"] == "scacaec"


def test_disaggregate_conc_bonsai_cpc_2_1():
    yaml_content = """
    disaggregations:
      - old_code: "fi_01929_06"
        new_codes:
          - code: "C_Agavs_0"
            description: "scacaec"
            mappings:
              cpc_2_1:
                - "1929"
          - code: "C_Agavs_0"
            description: ""
            mappings: {}
    """
    d = classifications.flowobject.datapackage.disaggregate_bonsai(
        codes_or_yaml=yaml.safe_load(yaml_content)
    )

    assert d["conc_bonsai_cpc_2_1"].iloc[-1]["flowobject_from"] == "C_Agavs_0"
    assert d["conc_bonsai_cpc_2_1"].iloc[-1]["flowobject_to"] == "1929"

    yaml_content = """
    disaggregations:
      - old_code: "fi_01929_06"
        new_codes:
          - code: "C_Agavs_0"
            description: "scacaec"
            mappings:
              cpc_2_1:
                - "1929"
          - code: "C_Agavs_1"
            description: ""
            mappings:
              cpc_2_1:
                - "1929"
    """
    d = classifications.flowobject.datapackage.disaggregate_bonsai(
        codes_or_yaml=yaml.safe_load(yaml_content)
    )

    assert d["conc_bonsai_cpc_2_1"].iloc[-1]["flowobject_from"] == "C_Agavs_1"
    assert d["conc_bonsai_cpc_2_1"].iloc[-1]["flowobject_to"] == "1929"
    assert d["conc_bonsai_cpc_2_1"].iloc[-2]["flowobject_from"] == "C_Agavs_0"
    assert d["conc_bonsai_cpc_2_1"].iloc[-2]["flowobject_to"] == "1929"
    assert (
        "Agavs" in d["conc_bonsai_cpc_2_1"]["flowobject_from"].values
    ) == False  # check that old code is removed


def test_disaggregate_tree_bonsai_pass_yaml():
    test_path = str(
        Path(os.path.dirname(__file__)).parent / "tests/data/disaggregate.yaml"
    )

    d = classifications.activitytype.datapackage.disaggregate_bonsai(
        codes_or_yaml=test_path
    )

    assert d["tree_bonsai"].iloc[-1]["code"] == "AAASSSS"
    assert d["tree_bonsai"].iloc[-1]["name"] == ""
    assert d["tree_bonsai"].iloc[-2]["code"] == "AI"
    assert d["tree_bonsai"].iloc[-2]["name"] == "scacaec"


def test_disaggragate_multiple():
    codes = {
        "disaggregations": [
            {
                "old_code": "fi_33421",
                "new_codes": [
                    {
                        "code": "C_ETHYLENE",
                        "description": "production of ethylene",
                        "mappings": {"prodcom_total_2_0": ["20141130"]},
                    },
                    {
                        "code": "C_CHEMrest",
                        "description": "production of rest",
                        "mappings": {
                            "prodcom_total_2_0": ["20141140", "20141150", "20141160"]
                        },
                    },
                ],
            }
        ]
    }
    d = classifications.flowobject.datapackage.disaggregate_bonsai(codes_or_yaml=codes)
    assert d["tree_bonsai"].iloc[-1]["code"] == "C_CHEMrest"
    assert d["tree_bonsai"].iloc[-1]["level"] == 6
    assert d["tree_bonsai"].iloc[-2]["code"] == "C_ETHYLENE"
    assert d["tree_bonsai"].iloc[-2]["level"] == 6
    assert (
        d["conc_bonsai_prodcom_total_2_0"].iloc[-1]["flowobject_from"] == "C_CHEMrest"
    )
    assert d["conc_bonsai_prodcom_total_2_0"].iloc[-1]["flowobject_to"] == "20141160"
    assert (
        d["conc_bonsai_prodcom_total_2_0"].iloc[-2]["flowobject_from"] == "C_CHEMrest"
    )
    assert d["conc_bonsai_prodcom_total_2_0"].iloc[-2]["flowobject_to"] == "20141150"
    assert (
        d["conc_bonsai_prodcom_total_2_0"].iloc[-3]["flowobject_from"] == "C_CHEMrest"
    )
    assert d["conc_bonsai_prodcom_total_2_0"].iloc[-3]["flowobject_to"] == "20141140"
    assert (
        d["conc_bonsai_prodcom_total_2_0"].iloc[-4]["flowobject_from"] == "C_ETHYLENE"
    )
    assert d["conc_bonsai_prodcom_total_2_0"].iloc[-4]["flowobject_to"] == "20141130"


def test_convert_name():
    assert (
        classifications.location.datapackage.conc_regex_bonsai.convert_name(
            "Bosnia and Herzegovina"
        )
        == "BA"
    )
    assert (
        classifications.location.datapackage.conc_regex_bonsai.convert_name(
            "Congo (Brazzaville)"
        )
        == "CG"
    )
    assert classifications.location.datapackage.conc_regex_bonsai.convert_name(
        "Serbia and Montenegro"
    ) == ["ME", "RS"]
