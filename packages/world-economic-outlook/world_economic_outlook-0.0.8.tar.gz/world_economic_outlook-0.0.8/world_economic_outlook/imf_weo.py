import requests
import re
import io
import csv
from simple_sqlite3 import Database
from typing import Optional, List, Dict
from .iso_mappings import iso_alpha3_to_alpha2
from .utils import save_records


def download_weo_data(year: int, month: str) -> bytes:
    """
    Downloads the IMF WEO data file for a given year and month.
    Args:
        year (int): The year of the WEO vintage.
        month (str): The month of the WEO vintage (e.g., 'April', 'October').
    Returns:
        bytes: The downloaded WEO data file as bytes.
    Raises:
        ValueError: If the WEO data link is not found on the IMF page.
        Exception: For network or download errors.
    """
    url = f"https://www.imf.org/en/Publications/WEO/weo-database/{year}/{month}/download-entire-database"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        raise Exception(f"Failed to fetch WEO page: {e}")
    match = re.search(
        r'href="(/-/media/Files/Publications/WEO/WEO-Database[^"]+)"', html
    )
    if not match:
        raise ValueError("WEO data link not found on the IMF page.")
    file_url = "https://www.imf.org" + match.group(1)
    try:
        file_response = requests.get(file_url, timeout=60)
        file_response.raise_for_status()
        data = file_response.content
    except Exception as e:
        raise Exception(f"Failed to download WEO data file: {e}")
    return data


def push_weo_data(
    data: bytes,
    database: str,
    vintage: str,
    table: str = "weo",
) -> None:
    """
    Parses and pushes WEO data into a SQLite database table.
    Args:
        data (bytes): The WEO data file as bytes.
        database (str): Path to the SQLite database file.
        table (str): Name of the table to insert data into.
        vintage (str): The vintage string (e.g., '2025 April').
    Raises:
        RuntimeError: If the data cannot be read with any of the tried encodings.
    """
    encodings_to_try = ["utf-16-le", "utf-8", "windows-1250", "latin-1"]
    last_exception = None
    for encoding in encodings_to_try:
        try:
            file = io.TextIOWrapper(
                io.BytesIO(data), encoding=encoding, errors="replace"
            )
            reader = csv.reader(file, delimiter="\t")
            headers = next(reader)
            # Remove null bytes and strip whitespace from all headers
            headers = [
                h.replace("\x00", "")
                .replace("\u0000", "")
                .replace("\0", "")
                .replace(chr(0), "")
                .strip()
                for h in headers
            ]
            break
        except Exception as e:
            last_exception = e
            continue
    else:
        raise RuntimeError(
            f"Failed to read WEO data with tried encodings {encodings_to_try}: {last_exception}"
        )
    try:
        estimates_start_after_idx = headers.index("Estimates Start After")
    except ValueError:
        raise RuntimeError(
            "'Estimates Start After' column not found in WEO data headers. Headers found: "
            + str(headers)
        )
    rows = []
    for row in reader:
        try:
            iso = iso_alpha3_to_alpha2.get(row[1], row[1])
            iso_alpha3 = row[1]
            weo_subject_code = row[2]
            country = row[3]
            subject_descriptor = row[4]
            units = row[6]
            scale = row[7] if len(row) > 7 else None
            estimates_start_after = (
                int(row[estimates_start_after_idx])
                if row[estimates_start_after_idx].isdigit()
                else None
            )
            for col_idx in range(9, estimates_start_after_idx):
                year_col = "".join(filter(str.isdigit, headers[col_idx]))
                try:
                    value = float(row[col_idx])
                except (ValueError, TypeError):
                    value = None
                if year_col:
                    rows.append(
                        (
                            iso,
                            iso_alpha3,
                            weo_subject_code,
                            country,
                            subject_descriptor,
                            units,
                            scale,
                            int(year_col),
                            value,
                            estimates_start_after,
                            int(
                                estimates_start_after is not None
                                and int(year_col) > estimates_start_after
                            ),
                            vintage,
                        )
                    )
        except IndexError:
            continue
    schema = """
        iso TEXT,
        iso_alpha3 TEXT,
        weo_subject_code TEXT,
        country TEXT,
        subject_descriptor TEXT,
        units TEXT,
        scale TEXT,
        year INTEGER,
        value REAL,
        estimates_start_after INTEGER,
        estimate INTEGER,
        vintage TEXT
    """
    columns = tuple(col.strip().split()[0] for col in schema.strip().split(",\n"))
    try:
        db = Database(database)
        table = db.table(table)
        table.insert_many(rows=rows, columns=columns, schema=schema)
    except Exception as e:
        raise Exception(f"Database error: {e}")


def save_weo_data(
    year: int, month: str, data: bytes, path: Optional[str] = None
) -> None:
    """
    Saves the WEO data as an .xls file to the specified path.
    Args:
        year (int): The year of the WEO data.
        month (str): The month of the WEO data.
        data (bytes): The WEO data to save.
        path (str, optional): The file path to save the data. Defaults to '{year}_{month}.xls'.
    Raises:
        ValueError: If no data is provided.
        Exception: If file writing fails.
    """
    if not data:
        raise ValueError("No data to save. Please download the data first.")
    if path is None:
        path = f"{year}_{month}.xls"
    try:
        with open(path, "wb") as file:
            file.write(data)
        print(f"WEO data saved to '{path}' successfully.")
    except Exception as e:
        print(f"Failed to save WEO data: {e}")
        raise


def parse_weo_data(data: bytes, vintage: str) -> List[Dict]:
    """
    Parses the WEO data bytes into a list of records (dicts).
    Args:
        data (bytes): The WEO data file as bytes.
        vintage (str): The vintage string (e.g., '2025 April').
    Returns:
        List[Dict]: List of parsed records.
    """
    encodings_to_try = ["utf-16-le", "utf-8", "windows-1250", "latin-1"]
    last_exception = None
    for encoding in encodings_to_try:
        try:
            file = io.TextIOWrapper(
                io.BytesIO(data), encoding=encoding, errors="replace"
            )
            reader = csv.reader(file, delimiter="\t")
            headers = next(reader)
            headers = [
                h.replace("\x00", "")
                .replace("\u0000", "")
                .replace("\0", "")
                .replace(chr(0), "")
                .strip()
                for h in headers
            ]
            break
        except Exception as e:
            last_exception = e
            continue
    else:
        raise RuntimeError(
            f"Failed to read WEO data with tried encodings {encodings_to_try}: {last_exception}"
        )
    try:
        estimates_start_after_idx = headers.index("Estimates Start After")
    except ValueError:
        raise RuntimeError(
            "'Estimates Start After' column not found in WEO data headers. Headers found: "
            + str(headers)
        )
    records = []
    for row in reader:
        try:
            iso = iso_alpha3_to_alpha2.get(row[1], row[1])
            iso_alpha3 = row[1]
            weo_subject_code = row[2]
            country = row[3]
            subject_descriptor = row[4]
            units = row[6]
            scale = row[7] if len(row) > 7 else None
            estimates_start_after = (
                int(row[estimates_start_after_idx])
                if row[estimates_start_after_idx].isdigit()
                else None
            )
            for col_idx in range(9, estimates_start_after_idx):
                year_col = "".join(filter(str.isdigit, headers[col_idx]))
                try:
                    value = float(row[col_idx])
                except (ValueError, TypeError):
                    value = None
                if year_col:
                    records.append({
                        "iso": iso,
                        "iso_alpha3": iso_alpha3,
                        "weo_subject_code": weo_subject_code,
                        "country": country,
                        "subject_descriptor": subject_descriptor,
                        "units": units,
                        "scale": scale,
                        "year": int(year_col),
                        "value": value,
                        "estimates_start_after": estimates_start_after,
                        "estimate": int(estimates_start_after is not None and int(year_col) > estimates_start_after),
                        "vintage": vintage,
                    })
        except IndexError:
            continue
    return records


def save_weo_records(records: List[Dict], save_path: str):
    """
    Save WEO records as JSON, CSV, or TXT using save_records utility.
    Args:
        records (List[Dict]): The WEO records.
        save_path (str): The file path (extension determines format).
    Raises:
        ValueError: If extension is not supported.
    """
    ext = save_path.lower().rsplit(".", 1)[-1]
    if ext not in ("json", "csv", "txt"):
        raise ValueError("save_path must end with .json, .csv, or .txt")
    save_records(records, save_path, ext)


def download(
    vintage: str,
    save_path: Optional[str] = None,
    database: Optional[str] = None,
    table: Optional[str] = None,
):
    """
    Downloads IMF WEO data for a given vintage and optionally saves to file or database.
    Args:
        vintage (str): The vintage string (e.g., '2025 April').
        save_path (str, optional): Path to save the WEO data as a file (by extension).
        database (str, optional): Path to the SQLite database file.
        table (str, optional): Name of the table to insert data into.
    Returns:
        List[Dict]: The WEO records (always returned).
    Raises:
        Exception: If download or save/push fails.
    """
    if (database and not table) or (table and not database):
        raise ValueError("Both 'database' and 'table' must be provided together.")
    year, month = vintage.split()
    year = int(year)
    data = download_weo_data(year, month)
    records = parse_weo_data(data, vintage)
    if database and table:
        db = Database(database)
        db.table(table).insert_many(rows=[tuple(r.values()) for r in records], columns=tuple(records[0].keys()), schema=None)
    if save_path:
        save_weo_records(records, save_path)
    return records


class WEO:
    """
    Wrapper object for downloading, saving, and pushing IMF WEO data.
    """

    def __init__(self) -> None:
        """
        Initializes a WEO object. Vintage is now provided in download().
        """
        self.year: Optional[int] = None
        self.month: Optional[str] = None
        self.vintage: Optional[str] = None
        self.data: Optional[bytes] = None

    def download(self, vintage: str) -> bytes:
        """
        Downloads the WEO data for the specified vintage and stores it in the instance.
        Args:
            vintage (str): The vintage string (e.g., '2025 April').
        Returns:
            bytes: The downloaded WEO data.
        Raises:
            Exception: If download fails.
        """
        self.year, self.month = vintage.split()
        self.year = int(self.year)
        self.vintage = vintage
        self.data = download_weo_data(self.year, self.month)
        return self.data

    def save(self, path: Optional[str] = None) -> None:
        """
        Saves the downloaded data as an .xls file.
        Args:
            path (str, optional): The file path to save the data. Defaults to '{year}_{month}.xls'.
        Raises:
            ValueError: If no data has been downloaded yet.
            Exception: If file writing fails.
        """
        if self.data is None:
            raise ValueError("No data downloaded. Call download() first.")
        save_weo_data(self.year, self.month, self.data, path)

    def push(self, database: str, table: str) -> None:
        """
        Pushes the downloaded data to a database as clean data.
        Args:
            database (str): Path to the SQLite database file.
            table (str): Name of the table to insert data into.
        Raises:
            ValueError: If no data has been downloaded yet.
            Exception: If database operation fails.
        """
        if self.data is None:
            raise ValueError("No data downloaded. Call download() first.")
        push_weo_data(self.data, database, table, self.vintage)
