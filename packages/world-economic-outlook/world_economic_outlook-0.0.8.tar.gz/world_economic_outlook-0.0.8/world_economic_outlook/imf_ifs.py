"""
imf_ifs.py
------------
IMF International Financial Statistics (IFS) data retrieval module.
Provides functions to fetch macroeconomic time series and metadata from the IMF SDMX JSON API.
All functions return records as lists of dictionaries.
"""

import requests
from typing import List, Optional
from .utils import normalise_date


def fetch_ifs_data(
    iso_codes: List[str],
    indicators: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    freq: str = "M",
) -> list:
    """
    Fetch macroeconomic time series from the IMF International Financial Statistics (IFS) database.

    Args:
        iso_codes: List of ISO country codes (e.g., ["US", "CN"]).

        indicators: Optional list of IFS indicator codes (e.g., ["EDNA_USD_XDC_RATE"]).

        start_date: Optional start period (e.g., "2020-01").

        end_date: Optional end period (e.g., "2023-12").

        freq: Frequency of data: "M" (monthly), "Q" (quarterly), or "A" (annual). Default is "M".

    Returns:
        List of records, each as a dict with keys:
            iso, indicator, date, freq, value
    """
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
    iso_str = "+".join(iso_codes)
    indicator_str = "+".join(indicators) if indicators else "?"
    freq = freq.upper() if freq.upper() in ["M", "Q", "A"] else "M"
    key = f"CompactData/IFS/{freq}.{iso_str}.{indicator_str}"
    params = {}
    if start_date:
        params["startPeriod"] = start_date
    if end_date:
        params["endPeriod"] = end_date

    records = []
    response = requests.get(f"{url}{key}", params=params)
    data = response.json()
    try:
        series_list = data["CompactData"]["DataSet"]["Series"]
    except (KeyError, TypeError):
        series_list = []
    if isinstance(series_list, dict):
        series_list = [series_list]
    elif not isinstance(series_list, list):
        series_list = []
    for series in series_list:
        iso = series.get("@REF_AREA", "UNKNOWN")
        indicator = series.get("@INDICATOR", "UNKNOWN")
        obs_list = series.get("Obs", [])
        if isinstance(obs_list, dict):
            obs_list = [obs_list]
        elif not isinstance(obs_list, list):
            obs_list = []
        for obs in obs_list:
            if not isinstance(obs, dict):
                continue
            time_period = obs.get("@TIME_PERIOD")
            obs_value = obs.get("@OBS_VALUE")
            try:
                obs_value = float(obs_value) if obs_value is not None else None
            except (ValueError, TypeError):
                obs_value = None
            date_dt = normalise_date(time_period, freq)
            records.append(
                {
                    "iso": iso,
                    "indicator": indicator,
                    "date": date_dt,
                    "freq": freq,
                    "value": obs_value,
                }
            )
    return records


def fetch_ifs_indicator_metadata() -> list:
    """
    Fetch the full list of IFS indicator codes and descriptions from the IMF SDMX JSON API.

    Returns:
        List of dicts, each with keys:
            code, description
    """
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/CL_INDICATOR_IFS"
    response = requests.get(url)
    data = response.json()
    try:
        codes = data["Structure"]["CodeLists"]["CodeList"]["Code"]
        records = [
            {
                "code": code["@value"],
                "description": code.get("Description", {}).get("#text", ""),
            }
            for code in codes
        ]
        return records
    except (KeyError, TypeError):
        return []


def fetch_ifs_area_metadata() -> list:
    """
    Fetch the full list of IFS ISO area codes and descriptions from the IMF SDMX JSON API.

    Returns:
        List of dicts, each with keys:
            iso, description
    """
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/CL_AREA_IFS"
    response = requests.get(url)
    data = response.json()
    try:
        codes = data["Structure"]["CodeLists"]["CodeList"]["Code"]
        records = [
            {
                "iso": code["@value"],
                "description": code.get("Description", {}).get("#text", ""),
            }
            for code in codes
        ]
        return records
    except (KeyError, TypeError):
        return []
