# Changelog

## Version 0.4.17
- Add function find_missing_bonsut(), to check completeness of Bonsut codes
- add isic rev2 bulletpoints as codes for bonsai-activities
- revise bonsai-locations (tree structure with levels)
- split ebops classifications

## Version 0.4.16
- update documentation
- fix ci python version
- concordance table updates

## Version 0.4.15
- minor fix for data type

## Version 0.4.14
- Add trees for UN Extende Balance of Payments Services (EBOPS) classification and correspondence to BONSAI
- tables for BONSAI, BONSUT, hexio v.3.3.18
- Add correspondence and tree for BEA codes (used in US MSUT)
- Add correspondence and tree for FAO Crops and Livestock (FCL) codes
- Add pint unit registry

## Version 0.4.9
- fix regex

## Version 0.4.8
- split up BONSAI workflow codes and BONSAI SUT codes
- whitespaces for usgs

## Version 0.4.7
- revise get_concordance(from_classification, to_classification, category)

## Version 0.4.6
- fix for dataio
- add faostat correspondence

## Version 0.4.5
- add locations for loading to BONSAI

## Version 0.4.4
- Add correspondence and tree for codes from ADB IOTs
- raise FileNotFoundError in get_concordance()
- NEW currency classification based on iso4217
- minor fixes

## Version 0.4.3
- Add correspondence and tree for HS-1992 product codes (used in BACI)
- Adding production of mortar and concretre + water as emission flow
- add pyyaml as dependency
- add PPF steel products for bof and eaf

## Version 0.4.2
- skos fix for unfcc

## Version 0.4.0
- remove uuid (prefixed_id) column
- Add tree and correspondence for UNFCCC production activity data: `flowobject/tree_unfccc_prodvol.csv` and `flowobject/conc_bonsai_unfccc_prodvol.csv`
- Classification files for ASUT (African SUTs)
- Correspondence file for NACE Rev.2
- get_tree(): New function to easily access tree files
- add `nearest_sut_code()` to find the closest ancestor that is in the SUTs
- add a default unit to most products
- remove conc_bonsai_nace_rev2.csv, because the reverse correspondence exists

## Version 0.3.11
- Increased granularity of bonsai trees for products and activities, using the HS6 classification as a reference
- Fix various bugs in bonsai tree tables: `flowobject/tree_bonsai.csv` and `activitytype/tree_bonsai.csv`
- Revised bonsai-prodcom correspondence tables based on the latest version of the master classification
- Update the _mapping_type script to check only for links at the same level of external codes
- Update conc and tree tables for Japan
- Updated test script and test files
- New tree and correspondence for CPA 2008 (level 2 detail), CPA 2.1, and ISIC 4 to Bonsai
- New tree for NACE Rev 1.1
- Test function to check the contents of classification files
- Update to some correspondence tables for SUTs
- Extensions to include the FAOSTAT classification, ONLY for fertilisers and land use (tree_faostat.csv and conc_bonsai_faostat.csv added and tree_bonsai.csv adjusted)
- Land use will require adjustments in the future once there is a clear agreement on how to connect it with the BONSAI code or other classification.
- new `alias_code` column for `tree_bonsai`
- new `accounttype` column for `concpair_`
- allow running script `_mapping.py` on specific files using args
- revision concordances `concpair_bonsai_undata_energy_stats`, `conc_bonsai_cpc_2_1`, `conc_bonsai_isic_rev4`

## Version 0.3.10
- changed default bonsai classification from iso3 to iso2

## Version 0.3.9

- new codes added to the Bonsai tree files, to describe monetary items in SUTs
- add `print_tree()` for visualisation of the tree table
- extend `get_children()` options
- add more detailed codes to `flowobject/tree_bonsai.csv` based on HS
- revise `conc_bonsa_prodcom_total_2_0.csv`
- fix `C_CHEM` as top level for 34 and 35
- New tree and correspondence for CPA 2.1 to Bonsai
- Extended correspondence for CPC 2.1 and ISIC 4 to Bonsai
- Script to convert JSON-LD to conc_*.csv file
- Concordance tables for ANZSIC
- Tree and correspondence tables for Japanese SUT
- Concordance tables for Mexican and Canadian NAICS to ISIC Rev.4
- Concordance tables for US BEA codes to Bonsai

## Version 0.3.8

- revise structure of `conc_` table (incl. a revision of utilities)
- use `skos:broadMatch` (one-to-many) and `skos:narrowMatch` (many-to-one) instead `skos:closeMatch`
- update documentation (readme.md + sphinx)

## Version 0.3.7

- first version of tree table for USGS
- first version of concordance table between USGS and BONSAI
- Updated BONSAI tree table to add a new sub-product (code: "fi_41118", "pig iron and direct-reduced iron")
- small adjustment to `get_bonsai_classification()`
- fix mapping types in "bonsai to undata_energy_stats"
- fix of column structure  `conc_bonsai_hexio_v_3_3_18_va.csv`
- revise `get_concordance()` to return `concpair_` table type
- revise structure of `concpair_` table

## Version 0.3.6

- new structure - category `flow` includes `activitytype` and `flowobject`
- new `concpair_` table type to allow pairwise concordances
- fixes for `iea_energy_balance` tree structure in `activitytype`
- add method `classifications.<category>.get_classification_names()`
- fix `classifications.get_concordance()`

## Version 0.3.5

- bug fixes
- deploy on pypi

## Version 0.3.4

- add `disaggregate_bonsai()` method, also executable via terminal (yaml file)
- addded Hybrid-Exiobase4 codes for `units`, `emissions`, `chemical_compound`, `compartment` as Bonsai codes
- include CAS numbers for `chemical_compound`
- add concordance `conc_bonsai_ecoinvent`
- make final codes in SUT tables explicit
- minor bug fixes

## Version 0.3.3

- clarify the mapping type in the `conc_` tables (only mapping for most detailed codes allowed)
- provide classifications tables as excel sheets in the documentation website
- add method `disaggregate_bonsai` to disaggregate existing bonsai codes and revise all relevent dataframes

## Version 0.3.2

- add `tree_exio_v_3_3_18` for EXIOBASE v3
- add the `conc_bonsai_exio_v_3_3_18` concordance table between EXIOBASE v3 and BONSAI
- `resources.csv` being accordingly updated

## Version 0.3.1

- revise `tree_bonsai` for activitytype and flowobject based on `ISIC rev2` and `CPC 2.1`
- add `skos uri` in correspondence tables to specify type of mapping (e.g. "many to one")
- remove dependency to `dataio` (only for testing)
- use BONSAI colors for docs
- add `create_conc()` to generate concordance table

## Version 0.3.0

- based on new dataio version (pydantic schemes)
- bug fixes

## Version 0.2.1

- new classifications for prodcom, un data, unido
- revision, bug fixes

## Version 0.2.0

- classifications as importable python package (util)
- based on dataio.datapackage
- uuid as additional column (uuid4)
- adding sub-types for `activitytype`: such as `industry_activity`, `treatment_activity` etc
- adding sub-types for `flowobject`: such as `industry_product`, `material_for_treatment` etc
- special naming convention that is based on [Weidema et al. 2013](https://ecoinvent.org/app/uploads/2024/02/dataqualityguideline_ecoinvent_3_20130506_.pdf)
- helper functions to find keywords in and filter the tables (pd.DataFrames)
