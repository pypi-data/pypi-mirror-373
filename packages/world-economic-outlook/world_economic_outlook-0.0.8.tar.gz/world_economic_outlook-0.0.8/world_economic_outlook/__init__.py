from .imf_weo import download as weo_download
from .imf_ifs import (
    fetch_ifs_data,
    fetch_ifs_area_metadata,
    fetch_ifs_indicator_metadata,
)
from .imf_dots import fetch_dots_data
from .utils import save_records
from simple_sqlite3 import Database
from typing import List, Optional

global DATABASE
DATABASE = "database.db"


def weo(
    vintage: str,
    save_path: Optional[str] = None,
    database: Optional[str] = None,
    table: Optional[str] = None,
):
    """
    Wrapper for downloading IMF WEO data.
    Handles saving to database, file, both, or just returning records.
    Always returns the records.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    return weo_download(
        save_path=save_path, database=database, vintage=vintage, table=table
    )


def ifs(
    isos: List[str],
    indicators: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    freq: str = "M",
    database: Optional[str] = None,
    table: Optional[str] = None,
    save_path: Optional[str] = None,
):
    """
    Wrapper for downloading IMF IFS data.
    Handles saving to database, file, both, or just returning records.
    Always returns the records.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    records = fetch_ifs_data(
        iso_codes=isos,
        indicators=indicators,
        start_date=start_date,
        end_date=end_date,
        freq=freq,
    )
    if database and table:
        with Database(database) as db:
            db.table(table).insert_fast(records)
    if save_path:
        ext = save_path.lower().rsplit(".", 1)[-1]
        if ext not in ("json", "csv", "txt"):
            raise ValueError("save_path must end with .json, .csv, or .txt")
        save_records(records, save_path, ext)
    return records


def dots(
    isos: List[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    database: Optional[str] = None,
    table: Optional[str] = None,
    freq: str = "M",
    save_path: Optional[str] = None,
):
    """
    Wrapper for downloading IMF DOTS data.
    Handles saving to database, file, both, or just returning records.
    Always returns the records.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    records = fetch_dots_data(
        isos=isos,
        start_date=start_date,
        end_date=end_date,
        freq=freq,
    )
    if database and table:
        with Database(database) as db:
            db.table(table).insert_fast(records)
    if save_path:
        ext = save_path.lower().rsplit(".", 1)[-1]
        if ext not in ("json", "csv", "txt"):
            raise ValueError("save_path must end with .json, .csv, or .txt")
        save_records(records, save_path, ext)
    return records


def ifs_area_metadata(database: Optional[str] = None, table: Optional[str] = None, save_path: Optional[str] = None):
    """
    Fetches IMF IFS area metadata and stores it in the specified database and table, saves to file, or returns records.
    Always returns the records.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    records = fetch_ifs_area_metadata()
    if database and table:
        with Database(database) as db:
            db.table(table).insert_fast(records)
    if save_path:
        ext = save_path.lower().rsplit(".", 1)[-1]
        if ext not in ("json", "csv", "txt"):
            raise ValueError("save_path must end with .json, .csv, or .txt")
        save_records(records, save_path, ext)
    return records


def ifs_indicator_metadata(database: Optional[str] = None, table: Optional[str] = None, save_path: Optional[str] = None):
    """
    Fetches IMF IFS indicator metadata and stores it in the specified database and table, saves to file, or returns records.
    Always returns the records.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    records = fetch_ifs_indicator_metadata()
    if database and table:
        with Database(database) as db:
            db.table(table).insert_fast(records)
    if save_path:
        ext = save_path.lower().rsplit(".", 1)[-1]
        if ext not in ("json", "csv", "txt"):
            raise ValueError("save_path must end with .json, .csv, or .txt")
        save_records(records, save_path, ext)
    return records
