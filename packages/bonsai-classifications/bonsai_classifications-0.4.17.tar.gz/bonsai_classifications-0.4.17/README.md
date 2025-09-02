# BONSAI classifications

The BONSAI classifications Python package is a part of the [Getting The Data Right](https://bonsamurais.gitlab.io/bonsai/documentation) project.

**If you want to contribute, please check the [guidelines](https://bonsamurais.gitlab.io/bonsai/util/classifications/contributing.html).**

Here, all the classifications, which are used in the Bonsai database, are created and stored as csv files. The structure of organising these files follows the [Bonsai ontology](https://github.com/BONSAMURAIS/ontology) and thus has the following folders:
- flow (includes: pairwise corrrespondence tables and mappings between `activities` and `products`)
  - activitytype (includes: `industry_activity`, `government_activity`, `treatment_activity`, `non_profit_institution_serving_household`, `household_production`, `household_consumption`, `market_activity`, `natural_activity`, `auxiliary_production_activity`, `change_in_stock_activity`, `other_activity`)
  - flowobject (includes `industry_product`, `material_for_treatment`, `market_product`, `government_product`, `household_product`, `needs_satisfaction`, `direct_physical_change`, `environmental_flow`, `economic_flow`, `social_flow`)
- location
- time

Since the Bonsai ontology does not cover all required topics, additional folders are added:
- dataquality
- uncertainty

**A comprehensive documentation of the classification package is availbale [here](https://bonsamurais.gitlab.io/bonsai/util/classifications/index.html)**

## Format
The csv files (tables) of each folder (datapackage) are organised in tabular format. Each of the mentioned folders represents a valid `dataio.datapackage` created with the Python package [dataio](https://bonsamurais.gitlab.io/bonsai/util/dataio/index.html). The following types of tables with its prefixes are used:
- tree table `tree_`
- concordance table `conc_`
- dimension table `dim_`
- pairwise cocncordance table `concpair_`

:::{note} We use UTF-8 encoding and comma (,) as the separator for all CSV files. On Windows, the default system encoding is not UTF-8, so when editing these files (for example, in Excel or Notepad), always ensure that you save them using UTF-8 encoding and preserve the comma separator to meet these requirements.
:::

### Tree table
Tree tables are used for classifications which have a tree structure, meaning that the classification is structured hierarchically with multiple levels. The classification starts with broad categories at the top level and then branches out into more specific subcategories as you move down the hierarchy.

The following column names are used:
- `code`: code of the item
- `parent_code`: code of the items parent
- `name`: name of the item
- `level`: the items level in the tree structure (from 0 to n)

:::{note} There are two classifications used in the BONSAI project, `tree_bonsai` and `tree_bonsut`.`tree_bonsai` includes the codes used in the workflow (after loading the data into the database). `tree_bonsut` includes the codes used in the final Supply, Use and Emission tables.
:::

### Concordance table (correspondence)
A concordance table is used to establish equivalences or relationships between different classification systems. It provides mappings between codes of a classification system and codes from another classification system. A relationship between codes can have four different types:

- **one-to-one (1:1) correspondence**: In a one-to-one correspondence, each category or code in one classification system is mapped to exactly one category or code in another classification system, and vice versa. This type of mapping implies a direct and unambiguous correspondence between the two systems. The skos uri is http://www.w3.org/2004/02/skos/core#exactMatch

- **one-to-many (1:M) correspondence**: In a one-to-many correspondence, each category or code in one classification system is mapped to multiple categories or codes in another classification system. However, each category or code in the second system is only mapped to one category or code in the first system. This type of mapping implies that one category or code in the first system may encompass multiple categories or codes in the second system. The skos uri is http://www.w3.org/2004/02/skos/core#narrowMatch . Indicating `<A> skos:narrowMatch <B>` means "B is narrower than A"

- **many-to-one (M:1) correspondence**: In a many-to-one correspondence, multiple categories or codes in one classification system are mapped to a single category or code in another classification system. However, each category or code in the second system is only mapped to one category or code in the first system. This type of mapping implies that multiple categories or codes in the first system are aggregated or collapsed into a single category or code in the second system. The skos uri is http://www.w3.org/2004/02/skos/core#broadMatch . Indicating `<A> skos:broadwMatch <B>` means "B is broader than A"

- **many-to-many (M:M) correspondence**: In a many-to-many correspondence, multiple categories or codes in one classification system are mapped to multiple categories or codes in another classification system. This type of mapping indicates complex relationships where neither a straightforward one-to-one correspondence exists, nor a parent-child relationship. The skos uri is http://www.w3.org/2004/02/skos/core#relatedMatch

- **Ambiguity**: In certain cases of `many-to-one` or `one-to-many` correspondences, the relation can be still ambiguos. An example is the mapping for `A_IRON` to `ai_0710`. It is a "one-to-manny", since `A_IRON` is also mapped to `ai_0990`. However, it is some kind of "ambiguous" mapping, since we cannot just add the codes to which `A_IRON` is mapped to and add all values together. This is because `ai_0990` is also related to other things, which needs to be considered.

|activiytype_from|activitytype_to|classification_from|classification_to|comment|
|----------------|---------------|-------------------|-----------------|--------|
|A_IRON|ai_0710|bonsut|bonsai|ambiguous one-to-many correspondence|
|A_IRON|ai_0990|bonsut|bonsai|many-to-many correspondence|
|A_ORAN|ai_0990|bonsut|bonsai|many-to-many correspondence|


The following column names are used:
- `<category>_from`: code of classification A
- `<category>_to`: code of classification B which is mapped to the code of classification A
- `classification_from`: name of classification A
- `classification_to`: name of classification B which is mapped to the code of classification A
- `comment`: comment on the type of concordance
- `skos_uri`: skos uri

The requirements for these table types are specified [here](https://dataio-bonsamurais-bonsai-util-a55d63cbbbcf635b952059f8b8a12a71.gitlab.io/syntax.html#field).

### Dimension table
A dimension table is used for classifications which do not have a tree structure.

The following column names are used:
- `code`: code of the item
- `name`: name of the item
- `description`: description of the item


### Pairwise concordance table (for Bonsai)
This type of concordance table is used to map pairwise codes. For instance, some data providers such as `UNdata` and `IEA` are using combined codes for an activity (e.g. for "production of", "electricity production by") and `flowobject` (e.g. "coal") to express a `bonsai_activitytype` ("A_COAL", "A_PowC"). In some cases, when the `conc_` tables for  `activitytype` and `flowobject`, which map single relations, are not sufficient to create these pairwise concordances, it is reasonable to make it explicit. The mapping relationships between the pairwise codes can be the same as in the `conc_` tables.


The following column names are used:
activitytype_from,flowobject_from,activitytype_to,flowobject_to,classification_from,classification_to

- `activitytype_from`: code for activitytype of `<from>` classification
- `flowobject_from`: code for flowobject of `<from>` classification
- `activitytype_to`: code for the activitytype of `<other>` classification
- `flowobject_to`: code for the flowobject of `<other>` classification
- `classification_from`: name of the `<from>` classification schema
- `classification_to`: name of the `<other>` classification schema
- `skos_uri`: skos uri
- `comment`: comment on the type of concordance

## Usage
To use the classification, you can install the package via pip. Replace `<version>` by a specific tag or branch name.

```
pip install git+ssh://git@gitlab.com/bonsamurais/bonsai/util/classifications@<version>
```

From pypi, do:
```
pip install bonsai_classifications
```


All classifications are provided as `dataio.datapackage` which include the tables as `pandas.DataFrame`. Therefore, you can do the following get the classification `tree` for e.g. industry activities of Bonsai:
```python
import classifications

bonsai_tree = classifications.activitytype.datapackage.tree_bonsai
```
:::{note} The datapackage object includes also the tables of other classifications.
:::

You can also get the concordance tables and external classifications in the similar way, using the `datapackage` object.

To access trees without hard-coding their name and path, you can use `get_tree()`, e.g. for the "bonsai" classification:
```python
bonsai_tree = classifications._utils.get_tree("bonsai", "flowobject")
```
This method is preferred for classifications that appears both as an activity and as a product classification.

The activities and flowobjects of Bonsai can be also used directly as objects. By doing the following, you would get the `name` of the `A_Chick` activity.
```python
classifications.activitytype.bonsai.A_Chick.name
```

### Special methods

There are the following methods attached to the dataframes for tree tables:
- `lookup()` for searching strings in code names
- `get_children()` to get all codes that have the same parent code
- `print_tree()` prints the tree structure of a given code
- `nearest_other_code()` returns the closest code af another classification
- `convert_name()` converts a location's name into a code (only for locations with regex)

To search for certain key words in a table, you can use the line of code below. This returns a pandas DataFrame with rows that have "coal" in the `name` column. Note that this lookup is case sensitive.
```python
bonsai_tree.lookup("coal")
```

To get all children of a certain code (here for treatment activities in Bonsai), you can do use the following method. By setting the option `deep=True`, you get all descandents. With `deep=False` you get only the direct children. The option `return_parent=True` will include the selected parent code. The option `exclude_sut_children=True` will return only the children that are included by another code in the SUT.
```python
classifications.activitytype.datapackage.tree_bonsai.get_children(parent_codes="at", deep=True, return_parent=False, exclude_sut_children=False)
```

To get the closest match of another classification, you can do the following. For a code `fi_5` that used in the BONSAI workflow, you need provide the correspondence table to another classification (here BONSUT) as argument in the `nearest_other_code()` for the bonsai tree for flowobjects.
```
classifications.flowobject.datapackage.tree_bonsai.nearest_other_code("fi_5",classifications.flowobject.datapackage.conc_bonsut_bonsai)
```
,which returns:
```
[('fi_53', 'C_CONS'), ('fi_54', 'C_METC')]
```

The `print_tree(toplevelcode)` method helps to inspect the tree structure for a given code.

```python
classifications.flowobject.datapackage.tree_bonsai.print_tree("C_Wine")
```

The differentiation between bold and italic text is only relevant for the Bonsai-SUT. Italic written codes are "not part" of the inspected `toplevelcode`, since these are explicitly in the SUTs. Since these codes are seperatly in the SUT, the definition of the `toplevelcode` is thus "code, excluding the the italic children".

```
𝐂_𝐖𝐢𝐧𝐞
├── 𝐟𝐢_𝟐𝟒𝟐𝟏𝟏
├── 𝘊_𝘎𝘳𝘢𝘱𝘵

```


To find the corresponding code for a region used in a certain classification (currently only for BONSAI workflow codes), you can provide the names:

```
import classifications

classification.location.datapackage.conc_regex_bonsai.convert_name(["USA", "China"])

```
returns:
```
["US", "CN"]
```

#### Units

The `classifications` package provides a `pint` unit regisitry that includes costumized monetary and physical unit definitions as well as magnitudes used in the BONSAI project. To use the registry for unit conversion, you can do the following:
```
from classifications import get_unit_registry
ureg = get_unit_registry()

q = 1000000 * ureg.DKK_2017
q.to("Meuro_2016")
```

