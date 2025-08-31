"""
CLI for the World Economic Outlook (WEO, IFS, DOTS) Data Module.
Provides commands to download, save, and push IMF datasets.
"""

import argparse
import sys
import json
import datetime
from . import (
    weo,
    ifs,
    dots,
)


def validate_db_table(user_set_database, user_set_table):
    # Only error if exactly one of --database or --table was provided by the user
    if user_set_database != user_set_table:
        print("Error: Both --database and --table must be provided together.")
        sys.exit(1)


def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def main():
    parser = argparse.ArgumentParser(
        prog="imf",
        description="IMF Data CLI: Download and store WEO, IFS, or DOTS datasets.",
    )
    subparsers = parser.add_subparsers(dest="dataset", required=True)

    # WEO subcommand
    weo_parser = subparsers.add_parser("weo", help="Download WEO data")
    weo_parser.add_argument("vintage", type=str, help="Vintage (e.g., '2025 April')")
    weo_parser.add_argument(
        "-s",
        "--save",
        type=str,
        help="Path to save WEO data as .xls file or as JSON/CSV/TXT",
    )
    weo_parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="Path to SQLite database file",
    )
    weo_parser.add_argument(
        "-t",
        "--table",
        type=str,
        help="Table name in database",
    )

    # IFS subcommand
    ifs_parser = subparsers.add_parser("ifs", help="Download IFS data")
    ifs_parser.add_argument(
        "isos", nargs="+", help="List of ISO country codes (e.g., FI SE NO DK)"
    )
    ifs_parser.add_argument(
        "-i",
        "--indicators",
        nargs="+",
        help="IFS indicator codes (e.g., EDNA_USD_XDC_RATE)",
    )
    ifs_parser.add_argument("--start", type=str, help="Start period (e.g., 2023-01)")
    ifs_parser.add_argument("--end", type=str, help="End period (e.g., 2025-03)")
    ifs_parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="Path to SQLite database file",
    )
    ifs_parser.add_argument(
        "-t",
        "--table",
        type=str,
        help="Table name in database",
    )
    ifs_parser.add_argument(
        "-f",
        "--freq",
        type=str,
        choices=["M", "Q", "A"],
        default="M",
        help="Frequency: M, Q, or A (default: M)",
    )
    ifs_parser.add_argument(
        "-s",
        "--save",
        type=str,
        help="Path to save IFS data as JSON, CSV, or TXT",
    )

    # DOTS subcommand
    dots_parser = subparsers.add_parser("dots", help="Download DOTS data")
    dots_parser.add_argument(
        "isos", nargs="+", help="List of ISO country codes (e.g., FI SE NO DK)"
    )
    dots_parser.add_argument("--start", type=str, help="Start period (e.g., 2023-01)")
    dots_parser.add_argument("--end", type=str, help="End period (e.g., 2025-03)")
    dots_parser.add_argument(
        "-d",
        "--database",
        type=str,
        help="Path to SQLite database file",
    )
    dots_parser.add_argument(
        "-t",
        "--table",
        type=str,
        help="Table name in database",
    )
    dots_parser.add_argument(
        "-f",
        "--freq",
        type=str,
        choices=["M", "Q", "A"],
        default="M",
        help="Frequency: M, Q, or A (default: M)",
    )
    dots_parser.add_argument(
        "-s",
        "--save",
        type=str,
        help="Path to save DOTS data as JSON, CSV, or TXT",
    )

    args = parser.parse_args()

    # Only validate db/table if user explicitly set --database/-d or --table/-t in the command line
    user_set_database = any(arg in sys.argv for arg in ["--database", "-d"])
    user_set_table = any(arg in sys.argv for arg in ["--table", "-t"])
    if user_set_database or user_set_table:
        validate_db_table(user_set_database, user_set_table)

    if args.dataset == "weo":
        if not (args.save or args.database):
            print("Note: No output specified. Data will only be returned in-memory.")
        try:
            records = weo(
                vintage=args.vintage,
                save_path=args.save,
                database=args.database,
                table=args.table,
            )
            if not (args.save or args.database):
                print(json.dumps(records, indent=2, ensure_ascii=False, default=json_serial))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.dataset == "ifs":
        if not (args.save or args.database):
            print("Note: No output specified. Data will only be returned in-memory.")
        try:
            records = ifs(
                isos=args.isos,
                indicators=args.indicators,
                start_date=args.start,
                end_date=args.end,
                database=args.database,
                table=args.table,
                save_path=args.save,
                freq=args.freq,
            )
            if not (args.save or args.database):
                print(json.dumps(records, indent=2, ensure_ascii=False, default=json_serial))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif args.dataset == "dots":
        if not (args.save or args.database):
            print("Note: No output specified. Data will only be returned in-memory.")
        try:
            records = dots(
                isos=args.isos,
                start_date=args.start,
                end_date=args.end,
                database=args.database,
                table=args.table,
                save_path=args.save,
                freq=args.freq,
            )
            if not (args.save or args.database):
                print(json.dumps(records, indent=2, ensure_ascii=False, default=json_serial))
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
