# -*- coding: utf-8 -*-
"""
Created on Wed May  7 13:37:04 2025

@author: BertramdeBoer

This script is used to obtain historic and current mapping of countries to currencies,
according to ISO4217 obtained from:
https://www.iso.org/iso-4217-currency-codes.html

ISO4217 is maintained by:
https://www.six-group.com/en/products-services/financial-information/data-standards.html

Comments:
2025-05-09 BB: The withdrawal dates for historical currencies in the original
            source file seem to be inconsistent. The wikipedia page on this standard
            seems to have more robust data:
            https://en.wikipedia.org/wiki/ISO_4217#Historical_codes
            However, the data from the wikipedia page does not refer a source,
            so it is not certain whether these data are correct.

2025-05-09 BB: CountryConverter does not seem to contain former countries.
"""

import country_converter as coco
import pandas as pd
import requests
import xml.etree.ElementTree as ET


def get_publication_date(xml):
    """
    Extracts the publication date from the XML content.

    Parameters:
    xml (str): XML content as a string.

    Returns:
    str: Publication date extracted from the XML.
    """
    # Parse the XML content with ElementTree
    root = ET.fromstring(xml)

    # Extract the Pblshd attribute
    return root.attrib["Pblshd"]


def cntr_name2iso3(row):
    """
    Converts country name to ISO3 code.

    Parameters:
    row (pd.Series): A row of the DataFrame containing country names.

    Returns:
    str: ISO3 country code.
    """

    cntr_name = row["CtryNm"]
    cntr_name = cntr_name.replace("(THE)", "")  #'CONGO (THE)' not found by coco.
    cntr_name = cntr_name.rstrip()  # remove trailing space after removing '(THE)'
    return coco.convert(cntr_name)


def currency_name_rstrip(row):
    """
    Removes trailing spaces from currency name.

    Parameters:
    row (pd.Series): A row of the DataFrame containing currency names.

    Returns:
    str: currency name without trailing space.
    """
    return row["CcyNm"].rstrip()


def split_withdrawal_date(row):
    """
    Splits the withdrawal date into year and month components.

    Parameters:
    row (pd.Series): A row of the DataFrame containing withdrawal dates.

    Returns:
    tuple: Year start, month start, year end, month end.
    """

    s_withdrawal_date = row["WthdrwlDt"]
    s_withdrawal_date_split = s_withdrawal_date.split("-")

    yr_start_default = -1
    m_start_default = -1
    m_end_default = -1
    if len(s_withdrawal_date_split) == 2:
        if len(s_withdrawal_date_split[1]) == 4:  # year-year
            yr_start, yr_end = s_withdrawal_date_split
            m_start = m_start_default
            m_end = m_end_default
        else:
            yr_end, m_end = s_withdrawal_date_split  # year-month
            yr_start = yr_start_default
            m_start = m_start_default

    else:
        s_withdrawal_date_split = s_withdrawal_date.split(" to ")
        if (
            len(s_withdrawal_date_split[0]) == 4
            and len(s_withdrawal_date_split[1]) == 4
        ):  # year to year
            yr_start, yr_end = s_withdrawal_date_split
            m_start = m_start_default
            m_end = m_end_default
        else:  # year-month to year-month
            yr_start, m_start = s_withdrawal_date_split[0].split("-")
            yr_end, m_end = s_withdrawal_date_split[1].split("-")

    return int(yr_start), int(m_start), int(yr_end), int(m_end)


def yr_m2date(row):
    """
    Converts year and month components to datetime.

    Parameters:
    row (pd.Series): A row of the DataFrame containing year and month components.

    Returns:
    tuple: Start date and end date as datetime objects.
    """

    # if no start date is given, assume Unix start time: 01-jan-1970.
    if row["yr_start"] != -1:
        yr_start = row["yr_start"]
    else:
        yr_start = 1970
    if row["m_start"] != -1:
        m_start = row["m_start"]
    else:
        m_start = 1

    yr_end = row["yr_end"]

    # if no end month is given, assume December.
    if row["m_end"] != -1:
        m_end = row["m_end"]
    else:
        m_end = 12
    return pd.to_datetime(f"{yr_start}-{m_start}", format="%Y-%m"), pd.to_datetime(
        f"{yr_end}-{m_end}", format="%Y-%m"
    )


def fill_history_start_date_end_date(df_history):
    """
    Fills missing start dates with end dates from previous entries.

    Parameters:
    df_history (pd.DataFrame): DataFrame containing historical currency data.

    Returns:
    pd.DataFrame: DataFrame with filled start and end dates.
    """

    # Parse start and end dates.
    df_history[["yr_start", "m_start", "yr_end", "m_end"]] = df_history.apply(
        split_withdrawal_date, axis=1, result_type="expand"
    )
    df_history[["start_date_iso4217", "end_date_iso4217"]] = df_history.apply(
        yr_m2date, axis=1, result_type="expand"
    )

    # l_exclude = ["not found"]

    date_default = pd.to_datetime("1970-01")

    cntr_name_col = "CtryNm"
    df_history_cntr_uniq = df_history[cntr_name_col].unique()
    l_history_cntr_name_sort = []
    # For each country
    for cntr_name in df_history_cntr_uniq:
        # if cntr_name not in l_exclude:
        df_history_cntr_name = df_history[df_history[cntr_name_col] == cntr_name].copy()
        df_history_cntr_name_sort = df_history_cntr_name.sort_values("end_date_iso4217")
        # For each entry, if start date missing, fill with previous end date.
        for row_id, t_row in enumerate(df_history_cntr_name_sort.iterrows()):
            row_idx, row = t_row
            if not row_id:
                start_date = row["start_date_iso4217"]
                end_date = row["end_date_iso4217"]
            else:
                start_date = row["start_date_iso4217"]
                if start_date == date_default:
                    df_history_cntr_name_sort.loc[row_idx, "start_date_iso4217"] = (
                        end_date
                    )
                end_date = row["end_date_iso4217"]
        # Append country DataFrame
        l_history_cntr_name_sort.append(df_history_cntr_name_sort)
    df_history_cntr_name_sort_concat = pd.concat(l_history_cntr_name_sort)
    df_history_cntr_name_sort_concat = df_history_cntr_name_sort_concat.drop(
        ["yr_start", "m_start", "yr_end", "m_end"], axis=1
    )
    return df_history_cntr_name_sort_concat


def fill_current_start_date_end_date(df_current, df_history_date_fill, date_current):
    """
    Fills missing start dates in the current DataFrame using historical data.

    Parameters:
    df_current (pd.DataFrame): DataFrame containing current currency data.
    df_history_date_fill (pd.DataFrame): DataFrame with filled historical data.

    Returns:
    pd.DataFrame: DataFrame with filled start and end dates.
    """

    date_default = pd.to_datetime("1970-01")

    for row_id, row in df_current.iterrows():
        cntr_iso3 = row["cntr_iso3"]
        # if cntr in history, take end date as start date.
        if cntr_iso3 in df_history_date_fill["cntr_iso3"].values:
            df_history_date_fill_cntr_iso3 = df_history_date_fill[
                df_history_date_fill["cntr_iso3"] == cntr_iso3
            ]
            df_current.loc[row_id, "start_date_iso4217"] = max(
                df_history_date_fill_cntr_iso3["end_date_iso4217"]
            )
            df_current.loc[row_id, "start_date_iso4217"] = max(
                df_history_date_fill_cntr_iso3["end_date_iso4217"]
            )
        # else, start date is unix start date.
        else:
            df_current.loc[row_id, "start_date_iso4217"] = date_default

        df_current.loc[row_id, "end_date_iso4217"] = pd.to_datetime(date_current)

    return df_current


def fill_date(df_current, df_history, date_current):
    """
    Fills missing dates in both current and historical DataFrames and concatenates them.

    Parameters:
    df_current (pd.DataFrame): DataFrame containing current currency data.
    df_history (pd.DataFrame): DataFrame containing historical currency data.

    Returns:
    pd.DataFrame: Concatenated DataFrame with filled dates.
    """

    # Fill missing start dates with end dates from previous entry.
    df_history_date_fill = fill_history_start_date_end_date(df_history)
    df_current_date_fill = fill_current_start_date_end_date(
        df_current, df_history_date_fill, date_current
    )

    df_date_fill = pd.concat([df_current_date_fill, df_history_date_fill])

    # Sort first by country, and then by end date of currency.
    df_date_fill = df_date_fill.sort_values(["CtryNm", "end_date_iso4217"])
    df_date_fill = df_date_fill.reset_index(drop=True)

    return df_date_fill


def get_iso4217_wiki_history():
    """
    Get historical ISO 4217 currency data from Wikipedia.

    Returns:
    pd.DataFrame: The second DataFrame from the parsed HTML,
    containing historical currency data.
    """

    # Parse the ISO4271 wikipedia page.
    l_iso4217_wiki = pd.read_html("https://en.wikipedia.org/wiki/ISO_4217")

    # Historic data is the second DataFrame.
    return l_iso4217_wiki[2]


def wiki_remove_footnote(val):
    """
    Remove footnote references, e.g. [a], from values in wikipedia table.

    Parameters:
    val (str or any): The value from which to remove the footnote reference.

    Returns:
    str or any: The value without the footnote reference if it was a string,
    otherwise the original value.
    """

    if type(val) == str:
        return val.split("[")[0]
    else:
        return val


def wiki_to_datetime(row):
    """
    Convert 'From' and 'Until' columns from wikipedia table to datetime.

    Note that some cells have {{dunno}}, which are not machine-readable, but valid:
    https://en.wikipedia.org/wiki/Template:Dunno

    2025-05-09 BB: I made a minor revision to the wikipedia page, to improve the
    machine-readability by changing a hyphen from U+2013 to U+002D
    https://en.wikipedia.org/w/index.php?title=ISO_4217&oldid=1289566835

    Parameters:
    row (pd.Series): A row of the DataFrame.

    Returns:
    tuple: A tuple containing the converted 'From' and 'Until' dates as
    datetime objects.
    """

    return pd.to_datetime(row["From"], errors="coerce"), pd.to_datetime(
        row["Until"], errors="coerce"
    )


if __name__ == "__main__":

    save_raw = True
    save_proc = True
    save_bonsai_tree = True
    save_bonsai_conc = True

    # URLs for current and history ISO 4217 country-currency mapping
    url_current = (
        "https://www.six-group.com/dam/download/financial-information/"
        "data-center/iso-currrency/lists/list-one.xml"
    )
    url_history = (
        "https://www.six-group.com/dam/download/financial-information/"
        "data-center/iso-currrency/lists/list-three.xml"
    )

    # Get XMLs for country-currency mappings
    xml_current = requests.get(url_current).content
    xml_history = requests.get(url_history).content

    # Cast XMLs to pandas DataFrames.
    df_current = pd.read_xml(xml_current, xpath=".//CcyNtry")
    df_history = pd.read_xml(xml_history, xpath=".//HstrcCcyNtry")

    df_current_raw = df_current.copy()
    df_history_raw = df_history.copy()

    # Get XML publication dates.
    date_current = get_publication_date(xml_current)
    date_history = get_publication_date(xml_history)

    # Save raw ISO4217 to csv.
    if save_raw:
        df_current.to_csv(f"iso4217_current_raw_{date_current}.csv", index=False)
        df_history.to_csv(f"iso4217_history_raw_{date_history}.csv", index=False)

    # Remove trailing spaces in currency names.
    df_current["CcyNm"] = df_current.apply(currency_name_rstrip, axis=1)
    df_history["CcyNm"] = df_history.apply(currency_name_rstrip, axis=1)

    # Add ISO3 country codes.
    df_current["cntr_iso3"] = df_current.apply(cntr_name2iso3, axis=1)
    df_history["cntr_iso3"] = df_history.apply(cntr_name2iso3, axis=1)

    # Fill start and end dates, and concatenate history and current ISO4217.
    df_iso4217_date = fill_date(df_current, df_history, date_current)

    # Get historical ISO 4217 currency data from Wikipedia.
    df_iso4217_wiki_history = get_iso4217_wiki_history()

    # Remove footnotes, e.g. [a], from values.
    pd_major, pd_minor, pd_patch = pd.__version__.split(".")
    if int(pd_major) >= 2 and int(pd_minor) >= 1:
        df_iso4217_wiki_history = df_iso4217_wiki_history.map(wiki_remove_footnote)
    else:
        df_iso4217_wiki_history = df_iso4217_wiki_history.applymap(wiki_remove_footnote)

    # Cast from and until dates to datetime.
    df_iso4217_wiki_history[["From", "Until"]] = df_iso4217_wiki_history.apply(
        wiki_to_datetime, axis=1, result_type="expand"
    )

    # Merge from and until dates with iso4217 DataFrame.
    df_iso4217_date_wiki = pd.merge(
        df_iso4217_date,
        df_iso4217_wiki_history[["Code", "From", "Until"]],
        left_on="Ccy",
        right_on="Code",
        how="left",
    )
    df_iso4217_date_wiki = df_iso4217_date_wiki.drop(columns=["Code"])
    df_iso4217_date_wiki = df_iso4217_date_wiki.rename(
        {"From": "start_date_wiki", "Until": "end_date_wiki"}, axis=1
    )

    # Drop US Dollar Same Day and Next Day, change USD start date to Unix start.
    df_iso4217_date_wiki = df_iso4217_date_wiki[df_iso4217_date_wiki["Ccy"] != "USS"]
    df_iso4217_date_wiki = df_iso4217_date_wiki[df_iso4217_date_wiki["Ccy"] != "USN"]
    df_iso4217_date_wiki.loc[
        df_iso4217_date_wiki["Ccy"] == "USD", "start_date_iso4217"
    ] = "1970-01-01"

    if save_proc:
        df_iso4217_date_wiki.to_csv(f"iso4217_current_history_wiki_{date_current}.csv")

    if save_bonsai_tree:
        df_tree = df_iso4217_date_wiki[["Ccy", "CcyNm", "CcyNbr"]]
        df_tree = df_tree.drop_duplicates("Ccy")
        df_tree = df_tree.sort_values("CcyNbr")
        df_tree = df_tree.reset_index(drop=True)
        df_tree = df_tree.rename(
            {"Ccy": "code", "CcyNm": "name", "CcyNbr": "alias_code"}, axis=1
        )
        df_tree["description"] = ""
        df_tree["comment"] = ""
        df_tree.to_csv("dim_bonsai.csv", float_format="%.0f", index=False)

    if save_bonsai_conc:
        df_conc = df_iso4217_date_wiki[
            [
                "Ccy",
                "cntr_iso3",
                "start_date_iso4217",
                "end_date_iso4217",
                "start_date_wiki",
                "end_date_wiki",
            ]
        ]
        df_conc = df_conc.rename({"Ccy": "currency_code_alpha"}, axis=1)
        df_conc.to_csv("bonsai_currency_to_country.csv", index=False)
