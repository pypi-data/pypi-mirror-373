import importlib.resources
import re
from decimal import getcontext
from logging import getLogger

import pandas as pd
import pint
from pint.errors import DefinitionSyntaxError

logger = getLogger("root")

# Set Decimal precision
getcontext().prec = 28

start_year = 2011
end_year = 2025


def get_unit_registry():
    ureg = pint.UnitRegistry()

    ## MONETARY UNITS ##

    BASE_YEAR = 2020
    BASE_CURRENCY = f"EUR_{BASE_YEAR}"

    # --- Load exchange rates (USD base) ---
    with importlib.resources.path(
        "classifications.data.unit.monetary", "fact_currency_per_usd.csv"
    ) as exchange_rate_file:
        exchange_df = pd.read_csv(exchange_rate_file)

    # --- Load deflators for EUR ---
    with importlib.resources.path(
        "classifications.data.unit.monetary", "fact_deflator_deu.csv"
    ) as deflators_file:
        deflator_df = pd.read_csv(deflators_file)

    # --- Load dimensions for aliases ---
    with importlib.resources.path(
        "classifications.data.unit.monetary", "dim_bonsai.csv"
    ) as dim_file:
        dim_df = pd.read_csv(dim_file)

    # --- Define base EUR_<year> unit ---
    ureg.define(f"{BASE_CURRENCY} = [currency]")

    base_deflator = deflator_df.query("time == @BASE_YEAR")["value"].iloc[0]

    # 1 --- Define EUR_<year> from deflators ---
    for _, row in deflator_df.iterrows():
        year = int(row["time"])
        deflator = row["value"]
        factor = deflator / base_deflator
        unit_name = f"EUR_{year}"
        if unit_name != BASE_CURRENCY:
            definition = f"{unit_name} = {factor} * {BASE_CURRENCY}"
            ureg.define(definition)
            logger.debug(f"Defining Monetary Unit A: {definition}")

    # 2 --- Define USD_<year> in terms of EUR_<year> ---
    usd_rates = exchange_df[exchange_df["unit"] == "EUR/USD"]

    for _, row in usd_rates.iterrows():
        year = int(row["time"])
        rate_per_usd = row["value"]  # EUR per 1 USD
        eur_unit = f"EUR_{year}"
        usd_unit = f"USD_{year}"
        factor = 1.0 / rate_per_usd  # 1 USD = X EUR → 1 EUR = 1/X USD

        if eur_unit != usd_unit:  # Avoid self-reference
            definition = f"{usd_unit} = {factor} * {eur_unit}"
            ureg.define(definition)
            logger.debug(f"Defining Monetary Unit B: {definition}")

    # 3 --- Define all other currency_<year> in terms of USD_<year> ---
    other_rates = exchange_df[exchange_df["unit"] != "EUR/USD"]

    for _, row in other_rates.iterrows():
        year = int(row["time"])
        unit_str = row["unit"]
        rate_per_usd = row["value"]

        currency = unit_str.split("/")[0]  # e.g. "AFN/USD" → "AFN"
        unit_name = f"{currency}_{year}"
        usd_unit = f"USD_{year}"

        # Ensure we don’t define a unit in terms of itself
        if unit_name != usd_unit:
            factor = 1.0 / rate_per_usd
            try:
                definition = f"{unit_name} = {factor} * {usd_unit}"
                logger.debug(f"Defining Monetary Unit C: {definition}")
                ureg.define(definition)
            except Exception as e:
                logger.debug(f"Skipping {unit_name} due to error: {e}")

    # --- Define aliases ---
    alias_map = {
        str(row["code"]).strip(): str(row["alias"]).strip()
        for _, row in dim_df.iterrows()
    }

    for code, alias in alias_map.items():
        # Look for all units in registry that start with the code followed by an underscore and 4-digit year
        pattern = re.compile(rf"^{re.escape(code)}_(\d{{4}})$")

        for unit in list(ureg._units):  # Access defined unit names
            match = pattern.match(unit)
            if match:
                year = match.group(1)
                alias_unit = f"{alias}_{year}"
                try:
                    ureg.define(f"{alias_unit} = {unit}")
                    logger.debug(f"Defined alias: {alias_unit} = {unit}")
                except DefinitionSyntaxError:
                    logger.warning(
                        f"Warning: Could not define alias '{alias_unit}' = '{unit}' (syntax error)"
                    )
                except Exception as e:
                    logger.warning(
                        f"Warning: Could not define alias '{alias_unit}' = '{unit}': {e}"
                    )

    ## PHYSICAL UNITS ##
    with importlib.resources.path(
        "classifications.data.unit.physical", "dim_bonsai.csv"
    ) as pyhsical_unit_file:
        df2 = pd.read_csv(pyhsical_unit_file)

        definition = None

        for _, row in df2.iterrows():
            code = row["code"]
            name = row["name"]
            new_dim = row["new_pint_dimension"]
            scale = row["scale"]
            ref_unit = row["reference_unit"]
            alias = row["alias"]

            if pd.notna(new_dim) and new_dim.strip() != "":  # Define new base dimension
                dim_name = f"{new_dim}"
                if f"[{dim_name}]" not in ureg._dimensions:
                    logger.debug(f"Defining dimension: [{dim_name}]")
                    ureg.define(f"[{dim_name}]")
                definition = f"{code} = [{dim_name}]"
            else:  # Derived unit from reference
                ref_unit = f"{ref_unit}"
                scale_val = float(scale)
                definition = f"{code} = {scale_val} * {ref_unit}"

                # Add aliases
            if alias and not pd.isna(alias):
                definition += " = " + " = " + alias

            logger.debug(f"Defining Physical Unit: {definition}")
            ureg.define(definition)

    ## MAGNITUDES ##
    with importlib.resources.path(
        "classifications.data.unit.magnitude", "dim_bonsai.csv"
    ) as magnitude_unit_file:
        df3 = pd.read_csv(magnitude_unit_file)

        for _, row in df3.iterrows():
            code = row["code"]
            scale = row["scale"]

            ref_unit = f"{ref_unit}"
            scale_val = float(scale)
            definition = f"{code} = {scale_val}"

            logger.debug(f"Defining Magnitude: {definition}")
            ureg.define(definition)

    return ureg
