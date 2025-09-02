# Contributing

This Python package is developed in the context of the `Getting The Data Right` project.

The package is the central place to store and maintain the classification files that are used in the Bonsai database.
These classification files change during the development of the database and the main development will be under the directory `src/classifications/data` (e.g., by adding/revising csv files and revising the metadata.yaml).
To keep track of this development, we use a version number `v.<major>.<minor>.<patch>`, which also correponds with the `tag` of the repository.
Thus, each new release of the `classification` has a `tag`.

To update the classification, two general cases may occur:
1. Adding new codes to an existing `tree_bonsai` csv table (disaggregation). In this case, add a new row to the corresponding `tree_bonsai` table with for the new code and point to the `parent_code` that you want to disaggregate. Please follow the naming convention. There should be at least two new codes added, if the aim is disaggregating an existing code. The new codes added to a `tree_bonsai` should be also added to the existing concordance tables!
2. Adding a new table (e.g. a tree table that represents an external classification schema; or a concordance table that maps the Bonsai classification schema to an external schema)

## Workflow
1. Clone the package `git clone git@gitlab.com:bonsamurais/bonsai/util/classifications.git`.
2. You should install the package in editable mode in a separate Python environment: `pip install -e .`
3. Make changes. When working on the csv files make sure the [format requirements](https://bonsamurais.gitlab.io/bonsai/util/classifications/index.html) are fulfilled.
4. Furthermore, please use `tox` and `pre-commit` already locally to check if things work properly.
5. If ready, create a merge request.
6. (Optional) Create a `tag` to publish a new version of the package on PyPi.

:::{note} If you do not want to install, but still to want to have changes implemented, please reach out. You can also create an [issue](https://gitlab.com/bonsamurais/bonsai/clean/classifications/-/issues) and describe your ideas (or contribute to an existing discussion).
:::


## Testing

To make sure that the datapackages are valid, run `pytest` or `tox` (there are tests implemented to check for missing codes etc.).
Please create no merge-request in case the tests are failing.

Make sure that added files are also mentioned in the existing `resources.csv` of the corresponding folder (this allows for automated tests).

## Required table headers

The `tree_` , `conc_` and `dim_` csv files (currently) require the following headers.

`conc_<classification_A classification_B>`:
| tree_<classification_A> | tree_<classification_B> | comment | skos_uri |
| ----------------------- | ----------------------- | ------- | -------- |
| ... | ... | ... | ... |

:::{note} Only map codes that belong to the most detailed levels of each category. In principle it would be possible to map codes for all levels. However, this complicates things unnecessarily, since we are only interested in the most detailed representation.
:::

`tree_<classification_A>`:
| code | parent_code | name | level  | comment |
| ---- | ----------- | ---- | -----  | ------- |
| ... | ... | ... | ... | ...  |


`dim_<something>`:
| code | name | description |
| ---- | ---- | ----------- |
| ... | ... | ... |

### Automated generation

The package includes srcipts to add/fill columns of existing csv files.

1. run `python src/classifications/_level.py` to add the corresponding `level` of codes in `tree_`files (the fields for `code` and `parent_code` must already exist)
2. run `python src/classifications/_mapping_type.py <path/to/conc_file.csv> True` to add the corresponding `comment` and `skos_uri` of codes in `conc_` files (the fileds `tree_<classification_A>` and `tree_<classification_B>` must already exist)


## Naming convention (only for BONSAI project)
### Names

For the names of the objects in the `name` column, we follow a specific convention, which is based on [Weidema et al. 2013](https://ecoinvent.org/app/uploads/2024/02/dataqualityguideline_ecoinvent_3_20130506_.pdf).
- lower case
- singular (e.g. `barley grain`, not "barley grains")
- the simplest form of an activity isa production; which is added after the product (e.g. `lime producion`)
- the term construction is used for activities that have buildings, transport infrastructure, factories and facilities as their product outputs (e.g. `bridge construction`)
- if the activity has multiple products, the activity can instead be named after the nature of the process, e.g. `air separation, cryogenic` with the products `oxygen`, `nitrogen` and `argon`
- when an activity is described in terms of the process of converting a raw material to a product, the order `process`, `raw material`, `detail of process` is preferred, e.g. `leaching of spodumene with sulphuric acid`
- the ending "-ing" is preserved for services
- for infrastructure, the name `factory` or `facility` is preferred to "plant", except in traditional combinations such as `power plant`
- treatment activities are named `treatment of <material>, <nature or output of the treatment>`
- market activities start with `market for`
- market activities, production mixes, supply mixes, export and re-export activities have the same products as inputs and outputs, e.g. `market for barley grain` has `barley grain` as input and `barley grain` as output
- activity datasets with the term `operation` as part of their name signifies activities that use specific infrastructures, e.g. `mine operation` as opposed to `mine construction`
- product names begin with the most generic form of the product that is generally recognized as a product, e.g. `cement, blast furnace slag` rather than "blast furnace slag cement", but avoiding artificial names, e.g. not "fertiliser, nitrogen" but `nitrogen fertiliser`.
- indication of the production route or specific product characteristics are only included if this is part of the marketable product properties, i.e. if there is a market or market niche where the production route or property is a part of the obligatory product properties. For example, the product `straw` is named as such, not with separate names for "barley straw" and "wheat straw", since the market for straw does not distinguish between these two products
- for dissolved chemicals, the traditional nomenclature of the chemical industry is to indicate the active substance and then add the water separately, so that e.g. 1 kg of `sodium hydroxide, in 50% solution state, measured as 100% NaOH`, refers to the production of 2 kg NaOH solution with a water content of 50%, i.e., 1 kg pure NaOH plus 1 kg pure H2O
- treatment activities provide services to other activities to treat their material outputs, in particular wastes. Since the service and the input are intimately linked, the service output is named by the treated material. Thus, the activity `treatment of blast furnace gas` has as its determining (reference) product `treating blast furnace gas`
- the name for a chemical element or a compound is the same for all environmental compartments, the list of compartments is the same as in ecoinvent Table 9.1


### Codes

The codes shall use prefixes followed by numbers: `<prefix>_<number>`.

| flowobject | prefix |
| ---------- | ------ |
| industry_product | fi |
| material_for_treatment | ft |
| market_product | fm |
| government_product | fg |
| household_product | fhp |
| needs_satisfaction | fhc |
| emission | fe |
| direct_physical_change | fp |
| natural_resource | fn |
| economic_flow | fe |
| social_flow | fs |

| activitytype | prefix |
| ---------- | ------ |
| industry_activity | ai |
| government_activity | ag |
| treatment_activity | at |
| non_profit_institution_serving_household | anp |
| household_production | ahp |
| household_consumption | ahc |
| market_activity | am |
| natural_activity | ana |
| auxiliary_production_activity | aa |
| schange_in_stock_activity | ast |

:::{note}
Currently, we use Exiobase code convention (`A_`, `C_`, `M_`). This needs to be revised later.
:::