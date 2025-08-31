import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


def save_records(records: List[Dict[str, Any]], path: str, format: str = "json"):
    """
    Save a list of records to a file in JSON, CSV, or TXT (tab-delimited) format.
    Args:
        records: List of dictionaries to save.
        path: Output file path.
        format: 'json', 'csv', or 'txt'.
    """
    if not records:
        raise ValueError("No records to save.")
    format = format.lower()
    if format == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    elif format == "csv":
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
    elif format == "txt":
        with open(path, "w", encoding="utf-8") as f:
            header = "\t".join(records[0].keys())
            f.write(header + "\n")
            for row in records:
                f.write(
                    "\t".join(str(row.get(k, "")) for k in records[0].keys()) + "\n"
                )
    else:
        raise ValueError(f"Unsupported format: {format}")


def normalise_date(time_period: str, freq: str) -> Optional[datetime]:
    """
    Converts or normalises a time period string to a Python datetime object based on freq.
    Args:
        time_period: The time period string (e.g., '2024-01', '2024-Q1', '2024').
        freq: freq ('M', 'Q', 'A').
    Returns:
        datetime object or None if parsing fails.
    """
    if freq == "M":
        try:
            return datetime.strptime(time_period, "%Y-%m")
        except Exception:
            return None
    elif freq == "Q":
        match = re.match(r"(\d{4})-Q(\d)", time_period)
        if match:
            year, quarter = int(match.group(1)), int(match.group(2))
            month = 3 * (quarter - 1) + 1
            return datetime(year, month, 1)
        else:
            return None
    elif freq == "A":
        try:
            return datetime.strptime(time_period, "%Y")
        except Exception:
            return None
    return None
