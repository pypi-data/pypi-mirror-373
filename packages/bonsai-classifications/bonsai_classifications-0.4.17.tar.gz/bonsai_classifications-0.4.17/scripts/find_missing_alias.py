# -*- coding: utf-8 -*-
"""
Created on Fri Mar  7 08:20:13 2025

@author: nielenssvan
"""
import pandas as pd
import classifications

def find_missing_alias(tree: pd.DataFrame, code: str, check_children=False):
    """Find codes in a Bonsai classification tree with aliases.
    Print the minimal set of codes that need an alias to make
    the coverage of aliases complete.
    """
    if not check_children and tree.loc[tree.code == code, "alias_code"].notna().all():
        return True
    elif not any(tree.parent_code == code):
        return False
    children = tree.loc[tree.parent_code == code, "code"]
    found = {True: [], False: []}
    for child in children:
        answer = find_missing_alias(tree, child)
        found[answer].append(child)
    if tree.loc[tree.code == code, "alias_code"].notna().all():
        return True
    if not any(found[False]):
        return True
    elif any(found[True]):
        print(f"Add alias to: {found[False]}")
        return True
    else:
        return False
        
def find_missing_bonsut(field: str, check_children=False):
    """Combine the Bonsai tree and the Bonsut codes.
    Then check if the coverage of Bonsut codes is complete.
    """
    if field == "product":
        tree = classifications.flowobject.datapackage.tree_bonsai
        bonsut_corr = classifications.flowobject.datapackage.conc_bonsut_bonsai
        bonsut_corr = bonsut_corr[["flowobject_from", "flowobject_to"]]
        parent_codes = ["fi"]
    elif field == "activity":
        tree = classifications.activitytype.datapackage.tree_bonsai
        bonsut_corr = classifications.activitytype.datapackage.conc_bonsut_bonsai
        bonsut_corr = bonsut_corr[["activitytype_from", "activitytype_to"]]
        parent_codes = ["ai", "at"]
    else:
        print("Field not recognized. Expecting 'product' or 'activity'.")

    bonsut_corr.columns = ["alias_code", "code"]
    tree = tree[["code", "parent_code", "level"]].merge(bonsut_corr, "left")
    for code in parent_codes:
        result = find_missing_alias(tree, code, check_children)
        if result:
            print("No missing Bonsut codes identified.")
        if not check_children:
            print("Descendants only considered if parent has no Bonsut code.")
