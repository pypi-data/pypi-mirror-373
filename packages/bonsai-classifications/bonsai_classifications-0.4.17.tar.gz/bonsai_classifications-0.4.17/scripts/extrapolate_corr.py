# -*- coding: utf-8 -*-
"""
Created on Mon Dec 30 13:29:20 2024
Utility functions for creating correspondence tables in the classification package

Author: Sander van Nielen
"""
from logging import getLogger
import os
from pathlib import Path

import classifications as classif
import pandas as pd

logger = getLogger("root")

#NOTE: these variables already exist in _utils.py
ROOT_PATH = Path(os.path.dirname(__file__))
activitytype_path = "data/flow/activitytype/"
flowobject_path = "data/flow/flowobject/"

def extrapolate_corr(external_cls: str, how="up|down", save: bool=False):
    """
    Extrapolate a correspondence table to higher/lower Bonsai classification levels.

    Parameters:
        external_cls (str): External classification, for which a
            correspondence exists to Bonsai codes
        how (str): Whether to extrapolate up or down the tree
        save (bool): Whether or not to save the result (overwrites original)

    Returns:
        corr (pd.DataFrame): Table with extended correspondences 
    """
    assert how in ["up", "down"], f"Unrecognized parameter value how={how}"
    # Get correspondence table
    corr = classif.get_concordance(external_cls, "bonsai")
    if "flowobject_from" in corr.columns:
        data_path = ROOT_PATH / flowobject_path
        from_col, to_col = "flowobject_from", "flowobject_to"
    elif "activitytype_from" in corr.columns:
        data_path = ROOT_PATH / activitytype_path
        from_col, to_col = "activitytype_from", "activitytype_to"
    # Find all bonsai codes (in to_col) that have an associated external code
    corr = corr[corr[from_col].notna() & corr[to_col].notna()]
    mapped = set(corr[to_col])
    # Merge the concordance table with the bonsai tree
    tree_columns = ["code", "name", "parent_code", "level"]
    tree = pd.read_csv(data_path / "tree_bonsai.csv")[tree_columns]
    
    for bonsai_code in mapped:
        if bonsai_code not in list(tree.code):
            logger.warning(f"{bonsai_code} is missing in {data_path}/tree_bonsai.csv")
            continue
        
        # Select the correspondences of bonsai_code
        new_ext = list(corr[corr[to_col]==bonsai_code][from_col])
        new_bonsai = []
        
        # Collect all parents/children of bonsai_code that are not yet mapped
        if how == "up":
            this_code = tree[tree.code==bonsai_code].parent_code.iloc[0]
            while (tree[tree.code==this_code].level.max() > 0) & (this_code not in mapped):
                new_bonsai += len(new_ext) * [this_code]
                this_code = tree[tree.code==this_code].parent_code.iloc[0]
        else:
            this_code = bonsai_code
            children = classif._utils.get_children(tree, this_code, deep=False)
            while len(children) > 0:
                missing = set(children.code) - set(corr[from_col])
                if len(children.unique()) > len(missing):
                    logger.warning(f"Some children of {bonsai_code} are defined unexpectedly.")
                elif any(missing):
                    new_bonsai += len(new_ext) * list(missing)
                children = classif._utils.get_children(tree, missing, deep=False)
        # Apply the external codes to the collected bonsai codes
        if any(new_bonsai):
            new_corr = pd.DataFrame({from_col: int(len(new_bonsai)/len(new_ext)) * new_ext,
                                     to_col: new_bonsai})
            corr = pd.concat([corr, new_corr])
    
    # Fill the classifications columns
    for col in ["classification_from", "classification_to"]:
        corr[col] = corr[col].iloc[0]
    if save:
        file_path = data_path / f"conc_{external_cls}_bonsai.csv"
        corr.to_csv(file_path, index=False)
    return corr

def extrapolate_down(external_cls: str, save: bool=False):
    """
    Extrapolate a correspondence table to higher Bonsai classification levels.

    Parameters:
        external_cls (str): External classification, for which a
            correspondence exists to Bonsai codes
        save (bool): Whether or not to save the result (overwrites original)

    Returns:
        corr (pd.DataFrame): Table with extended correspondences 
    """
    # Get correspondence table
    corr = classif.get_concordance(external_cls, "bonsai")
    if "flowobject_from" in corr.columns:
        data_path = ROOT_PATH / flowobject_path
        from_col, to_col = "flowobject_from", "flowobject_to"
    elif "activitytype_from" in corr.columns:
        data_path = ROOT_PATH / activitytype_path
        from_col, to_col = "activitytype_from", "activitytype_to"
    # Find all bonsai codes (in to_col) that have an associated external code
    corr = corr[corr[from_col].notna() & corr[to_col].notna()]
    mapped = corr[to_col].unique()
    # Merge the concordance table with the bonsai tree
    tree_columns = ["code", "name", "parent_code", "level"]
    tree = pd.read_csv(data_path / "tree_bonsai.csv")[tree_columns]
    
    for bonsai_code in mapped:
        # Select the correspondences of bonsai_code
        new_ext = list(corr[corr[to_col]==bonsai_code][from_col])
        new_bonsai = []
        if len(new_ext) == 0:
            logger.warning(f"{bonsai_code} is missing in {data_path}/tree_bonsai.csv")
            continue
        # Collect all children of bonsai_code that are not yet mapped
        this_code = bonsai_code
        children = classif._utils.get_children(tree, this_code, deep=False)
        while len(children) > 0:
            missing = set(children.code) - set(corr[from_col])
            if len(children.unique()) > len(missing):
                logger.warning(f"Some children of {bonsai_code} are defined unexpectedly.")
            elif any(missing):
                new_bonsai += len(new_ext) * list(missing)
            children = classif._utils.get_children(tree, missing, deep=False)
        # Apply the codes of the child to 
        if any(new_bonsai):
            new_corr = pd.DataFrame({from_col: int(len(new_bonsai)/len(new_ext)) * new_ext,
                                     to_col: new_bonsai})
            corr = pd.concat([corr, new_corr])
    
    # Fill the classifications columns
    for col in ["classification_from", "classification_to"]:
        corr[col] = corr.loc[0, col]
    if save:
        file_path = data_path / f"conc_{external_cls}_bonsai.csv"
        corr.to_csv(file_path, index=False)
    return corr

def extrapolate_bea():
    # Products
    corr = classif.flowobject.datapackage.conc_bea_prod_bonsai
    tree = classif.flowobject.datapackage.tree_bea_prod
    tree = tree[["code", "name", "parent_code", "level"]]
    # combi = tree.rename(columns={"code": "flowobject_from"}).merge(corr, "outer")
    # missing = set(tree.code) - set(corr.flowobject_from)
    
    # Find all bea codes (in from_col) that have an associated bonsai code
    from_col, to_col = "flowobject_from", "flowobject_to"
    corr = corr[corr[from_col].notna() & corr[to_col].notna()]
    mapped = set(corr[from_col])
    
    for bea_code in mapped:
        if bea_code not in list(tree.code):
            logger.warning(f"{bea_code} is missing in tree_bea_prod.csv")
            continue
        
        # Select the correspondences of bea_code
        new_bonsai = list(corr[corr[from_col]==bea_code][to_col])
        new_bea = []
        
        # Collect all parents/children of bea_code that are not yet mapped
        this_code = tree[tree.code==bea_code].parent_code.iloc[0]
        while (tree[tree.code==this_code].level.max() > 0) & (this_code not in mapped):
            new_bea += len(new_bonsai) * [this_code]
            this_code = tree[tree.code==this_code].parent_code.iloc[0]
        # Apply the bonsai codes to the collected bea codes
        if any(new_bea):
            new_corr = pd.DataFrame({to_col: int(len(new_bea)/len(new_bonsai)) * new_bonsai,
                                     from_col: new_bea})
            corr = pd.concat([corr, new_corr])
    
    # Fill the classifications columns
    for col in ["classification_from", "classification_to"]:
        corr[col] = corr[col].iloc[0]
    
    # Activities
    corr = classif.activitytype.datapackage.conc_bea_activ_bonsai
    tree = classif.activitytype.datapackage.tree_bea_activ
    combi = tree.rename(columns={"code": "activitytype_from"}).merge(corr, "outer")
    print(len(combi[combi.activitytype_to.isna()]))
    for code in combi[combi.activitytype_to.isna()].activitytype_from:
        child_rows = combi[combi.parent_code == code]
        if len(child_rows)==1 and child_rows.activitytype_to.any():
            combi.loc[combi.activitytype_from==code, "activitytype_to"] = child_rows.activitytype_to.values[0]
    print(len(combi[combi.activitytype_to.isna()]))
    for code in combi[combi.activitytype_to.isna()].activitytype_from:
        child_rows = combi[combi.parent_code == code]
        if len(child_rows)==1 and child_rows.activitytype_to.any():
            combi.loc[combi.activitytype_from==code, "activitytype_to"] = child_rows.activitytype_to.values[0]
        elif len(child_rows)>1 and child_rows.activitytype_to.any():
            match = list(child_rows.activitytype_to.dropna().unique())
            match.sort()
            match = ", ".join(match)
            combi.loc[combi.activitytype_from==code, "activitytype_to"] = match
    print(len(combi[combi.activitytype_to.isna()]))
