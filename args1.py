#!/usr/bin/env python3

'''

Take a simple CSV file, parse it and create CLI filters and options, instead of using input() 

positional arguments:
  input                Path to CSV with logs

options:
  -h, --help           show this help message and exit
  --ip IP              Only include rows with this IP (exact match) (default: None)
  --only-fails         Show only rows where status == FAIL (default: False)
  --output OUTPUT      Write resutls to this file (default: None)
  --format {json,csv}  output format when --output is set (default: json)
  --verbose            Verbose logging (default: False)


'''
import argparse
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
from tabulate import tabulate
import logging



def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, keep_default_na=False)
    return df


def ensure_required_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
    cols = set(df.columns)
    missing = [c for c in required if c not in cols]
    return missing


def filter_by_ip(df: pd.DataFrame, ip: Optional[str]) -> pd.DataFrame:
    if not ip:
        return df
    return df[df["ip"].astype(str).eq(ip)]


def only_fails(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["status"].astype(str).eq("FAIL")]


def render_table(df: pd.DataFrame) -> None:
    if df.empty:
        print("(no matching rows)")
        return
    print(tabulate(df, headers="keys", tablefmt="simple", showindex=False))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="File_filterer",
        description="Take a CSV file, parse it and be able to filter it (login failures, entries etc)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Path to CSV with logs")
    parser.add_argument("--ip", help="Only include rows with this IP (exact match)")
    parser.add_argument("--only-fails", action="store_true", help="Show only rows where status == FAIL")
    parser.add_argument("--output", type=Path, help="Write resutls to this file")
    parser.add_argument("--format", choices=("json", "csv"), default="json", help="output format when --output is set")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")




    args = parser.parse_args(argv)

    if not args.input.exists():
        parser.error(f"File not found: {args.input}")


    df = load_csv(args.input)

    missing = ensure_required_columns(df, required=("ip", "status"))
    if missing:
        parser.error(f"CSV is missing required column(s): {', '.join(missing)}")


    df = filter_by_ip(df, args.ip)
    if args.only_fails:
        df = only_fails(df)


    # Still needs work, and also to print on terminal alongside an (out.[csv,json] file)
    if args.output:
        if args.format == "csv":
            df.to_csv(args.output, index=False)
        else:
            df.to_json(args.output, indent=2, index=False)
        print(f"Wrote {args.output}")

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        logging.info("Loaded %d rows (including header) from %s", len(df)+1, args.input)


    render_table(df)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
