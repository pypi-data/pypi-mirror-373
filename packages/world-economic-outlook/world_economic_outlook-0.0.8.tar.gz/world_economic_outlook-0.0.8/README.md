# World Economic Outlook
[![PyPI version](https://badge.fury.io/py/world-economic-outlook.svg)](https://pypi.org/project/world-economic-outlook/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

Easily fetch IMF World Economic Outlook (**WEO**), International Financial Statistics (**IFS**), and Direction of Trade Statistics (**DOTS**) data.

**World Economic Outlook** is a Python library and CLI tool for downloading, saving, and processing major IMF datasets. It provides a convenient interface for managing data, saving it locally, and pushing it to a database.

---

## Features

- Download **WEO**, **IFS**, and **DOTS** data from the IMF.
- Save data as JSON, CSV, TXT, or original XLS (WEO only).
- Push data to a SQLite database.
- Command-line interface (CLI) for all major actions.
- Programmatic API for automation and scripting.
- Wrapper functions for flexible workflows.
- Query data conveniently using SQL.

---

## Installation

Requires **Python 3.9+**.

Install the published package:

```bash
pip install world-economic-outlook
```

---

## Quick Start

### Programmatic Usage

#### 1. Using the Wrappers

This example demonstrates how to use the wrappers to download **WEO**, **IFS**, and **DOTS** data. By default, data is returned in memory if neither `save_path` nor `database` is specified. You can also save to a file or database.

Download data and return records in-memory (no file/database):
```python
from world_economic_outlook import weo, ifs, dots

# Download WEO vintage and return records in-memory
records = weo("2025 April")

# Download IFS data and return records in-memory
records = ifs(["DE"])

# Download DOTS data and return records in-memory
records = dots(["US", "U2"])
```
> If neither `save_path` nor `database` is specified, data is always returned in-memory as a list of dicts.

Download data and save:
```python
from world_economic_outlook import weo, ifs, dots

# Download WEO vintage and save
weo("2025 April", save_path="weo.json")

# Download IFS data and save
ifs(["DE"], save_path="ifs.csv")

# Download DOTS data and save
dots(["US", "U2"], save_path="dots.txt")
```

Download data, save and return records (in-memory):
```python
from world_economic_outlook import weo, ifs, dots

# Download WEO vintage, save, and return records (in-memory)
records = weo(
    vintage="2025 April",
    database="database.db",
    table="weo",
    save_path="weo.json"
)

# Download IFS data, save, and return records (in-memory)
records = ifs(
    isos=["GB", "FR"],
    database="database.db",
    table="ifs",
    save_path="ifs.csv"
)

# Download DOTS data, save and return records (in-memory)
records = dots(
    isos=["FI", "SE", "NO", "DK"],
    database="database.db",
    table="dots",
    save_path="dots.txt",
)
```

#### 2. Fetching Specific Macroeconomic Data

This example shows how to fetch monthly exchange rate data for Mexico, Brazil, Chile, Colombia and Argentina between 2018 and 2022. Data is returned in-memory by default.

```python
from world_economic_outlook import ifs

records = ifs(
    isos=["MX", "BR", "CL", "CO", "AR"],
    indicators=["EDNA_USD_XDC_RATE"],
    start_date="2018-01-01",
    end_date="2022-01-01",
    freq="M"
)

print(records[:5])
```

#### 3. Fetching IFS Metadata

This example shows how to fetch IFS Indicator and Area Metadata as records, and optionally save them to a file and/or database. The `save_path`, `database`, and `table` arguments are optional, allowing you to persist metadata for reuse without needing to fetch it again in subsequent runs.

```python
from world_economic_outlook import ifs_indicator_metadata, ifs_area_metadata

# Download indicator metadata (optional, not required for basic data fetching)
indicator_records = ifs_indicator_metadata(
    save_path="ifs_indicator_metadata.csv",
    database="database.db",
    table="ifs_indicator_metadata"
)

# Download area metadata (optional, not required for basic data fetching)
area_records = ifs_area_metadata(
    save_path="ifs_area_metadata.csv",
    database="database.db",
    table="ifs_area_metadata"
)

print(indicator_records[:5])
print(area_records[:5])
```

---

### Command-Line Interface (CLI)

The CLI provides a convenient way to interact with all supported IMF datasets. After installation, use the `imf` command:

#### Download WEO Data and return records in-memory
```bash
imf weo "2025 April"
```
> Returns data in-memory and prints it as JSON to stdout if neither `--save` nor `--database` is specified. **Warning:** Printing large datasets may take a long time and produce a lot of output.

#### Download WEO Data and save as JSON
```bash
imf weo "2025 April" -s weodata.json
```

#### Download IFS Data and save as CSV
```bash
imf ifs JP CH GB U2 -i EDNA_USD_XDC_RATE -s exchange_rates.csv
```

#### Download IFS Data and return records in-memory
```bash
imf ifs GB FR -i EDNA_USD_XDC_RATE
```

#### Download DOTS Data and save to database
```bash
imf dots FI SE NO DK -d database.db -t trade
```

#### CLI Help
```bash
imf --help
imf weo --help
imf ifs --help
imf dots --help
```

### CLI Command Overview

| Subcommand | Flag / Argument      | Type      | Description                                         | Required | Default           |
|------------|---------------------|-----------|-----------------------------------------------------|----------|-------------------|
| weo        | `vintage`           | str       | Vintage (e.g., '2025 April')                        | Yes      | —                 |
|            | `-s`, `--save`      | str       | Path to save WEO data as .xls, .json, .csv, or .txt | No       | —                 |
|            | `-d`, `--database`  | str       | Path to SQLite database file                        | No*      | —                 |
|            | `-t`, `--table`     | str       | Table name in database                              | No*      | —                 |
| ifs        | `isos`              | str list  | List of ISO country codes (e.g., FI SE NO DK)       | Yes      | —                 |
|            | `-i`, `--indicators`| str list  | IFS indicator codes                                 | No       | —                 |
|            | `--start`           | str       | Start period (e.g., 2023-01)                        | No       | —                 |
|            | `--end`             | str       | End period (e.g., 2025-03)                          | No       | —                 |
|            | `-d`, `--database`  | str       | Path to SQLite database file                        | No*      | —                 |
|            | `-t`, `--table`     | str       | Table name in database                              | No*      | —                 |
|            | `-f`, `--frequency` | str       | Frequency: M, Q, or A                               | No       | M                 |
|            | `-s`, `--save`      | str       | Path to save IFS data as .json, .csv, or .txt       | No       | —                 |
| dots       | `isos`              | str list  | List of ISO country codes (e.g., FI SE NO DK)       | Yes      | —                 |
|            | `--start`           | str       | Start period (e.g., 2023-01)                        | No       | —                 |
|            | `--end`             | str       | End period (e.g., 2025-03)                          | No       | —                 |
|            | `-d`, `--database`  | str       | Path to SQLite database file                        | No*      | —                 |
|            | `-t`, `--table`     | str       | Table name in database                              | No*      | —                 |
|            | `-f`, `--frequency` | str       | Frequency: M, Q, or A                               | No       | M                 |
|            | `-s`, `--save`      | str       | Path to save DOTS data as .json, .csv, or .txt      | No       | —                 |

\* If either `--database` or `--table` is provided, both must be specified.

*For all commands, if neither `--save` nor `--database` is specified, data is returned in-memory. For `weo`, either `--save` or `--database` is recommended for persistence.*

---

## Exporting Data

Say we have already retrieved exchange rate data from the IMF IFS Database:

```bash
imf ifs JP CH GB U2 -i EDNA_USD_XDC_RATE -d database.db -t exchange_rates
```

Then we can easily query the database and save the output into a `json` using the CLI:

```bash
db query -d database.db -s "SELECT * FROM exchange_rates" -f exrates.json
```

Alternatively, we can export the entire table into a `csv`:

```bash
db export -d database.db -t exchange_rates -f exrates.csv
```

> **Note:** For larger database tables, bulk exporting the table may take a while.

---

## License

This project is developed by Rob Suomi and licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.