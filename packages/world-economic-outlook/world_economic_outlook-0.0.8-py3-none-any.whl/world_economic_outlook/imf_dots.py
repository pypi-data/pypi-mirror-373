"""
imf_dots.py
------------
IMF Direction of Trade Statistics (DOTS) data retrieval module.
Provides functions to fetch bilateral trade data from the IMF SDMX JSON API.
All functions return records as lists of dictionaries.
"""

import requests
from typing import List, Optional, Dict, Any
from .utils import normalise_date


def fetch_dots_data(
    isos: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    freq: str = "M",
) -> list:
    """
    Fetch bilateral trade data from the IMF Direction of Trade Statistics (DOTS) database.

    Args:
        isos: List of ISO country codes to fetch data for (e.g., ["US", "CN"]).
        start_date: Optional start period (e.g., "2020").
        end_date: Optional end period (e.g., "2023").
        freq: Frequency of data: "M" (monthly), "Q" (quarterly), or "A" (annual). Default is "M".

    Returns:
        List of records, each as a dict with keys:
            iso, iso_star, date, freq, imports, exports, trade_balance, twoway_trade

    """
    url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
    freq = freq.upper() if freq.upper() in ["M", "Q", "A"] else "M"
    params: Dict[str, Any] = {}
    if start_date:
        params["startPeriod"] = start_date
    if end_date:
        params["endPeriod"] = end_date

    records: List[Dict[str, Any]] = []
    record_map: Dict[tuple, Dict[str, Any]] = {}
    for iso in isos:
        counterparts = [c for c in isos if c != iso]
        if not counterparts:
            continue
        cp_str = "+".join(counterparts)
        for indicator, flow in [("TXG_FOB_USD", "exports"), ("TMG_CIF_USD", "imports")]:
            key = f"CompactData/DOT/{freq}.{iso}.{indicator}.{cp_str}"
            try:
                response = requests.get(f"{url}{key}", params=params, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"Request failed for {key}: {e}")
                continue
            try:
                data = response.json()
            except Exception as e:
                print(
                    f"Non-JSON response for {key}: {e}\nContent: {response.content[:200]}"
                )
                continue
            try:
                series_list = data["CompactData"]["DataSet"]["Series"]
            except (KeyError, TypeError):
                continue
            if isinstance(series_list, dict):
                series_list = [series_list]
            for s in series_list:
                counterpart = s.get("@COUNTERPART_AREA")
                obs_list = s.get("Obs", [])
                if isinstance(obs_list, dict):
                    obs_list = [obs_list]
                elif not isinstance(obs_list, list):
                    obs_list = []
                for obs in obs_list:
                    if not isinstance(obs, dict):
                        continue  # For unexpected formats...
                    time_period = obs.get("@TIME_PERIOD")
                    value = obs.get("@OBS_VALUE")
                    try:
                        value = float(value) if value is not None else None
                    except (ValueError, TypeError):
                        value = None
                    date_dt = normalise_date(time_period, freq)
                    key_tuple = (iso, counterpart, date_dt)
                    if key_tuple not in record_map:
                        rec = {
                            "iso": iso,
                            "iso_star": counterpart,
                            "date": date_dt,
                            "freq": freq,
                            "imports": None,
                            "exports": None,
                        }
                        records.append(rec)
                        record_map[key_tuple] = rec
                    else:
                        rec = record_map[key_tuple]
                    rec[flow] = value
    # Calculate trade_balance and twoway_trade
    for rec in records:
        imports = rec["imports"] if rec["imports"] is not None else 0
        exports = rec["exports"] if rec["exports"] is not None else 0
        rec["trade_balance"] = exports - imports
        rec["twoway_trade"] = exports + imports
    return records
