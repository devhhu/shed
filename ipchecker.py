#!/usr/bin/env python3

'''
ipchecker:
Simple check of IP addresses for attribution and hits on AbuseIPDB 

  `  _ ,  '      o,*,(o o)         _|_|_     
 -  (o)o)  -    8(o o)(_)Ooo       (o o)     
-ooO'(_)--Ooo-ooO-(_)---Ooo----ooO--(_)--Ooo-

usage: checker [-h] (--ip IP | --bulk BULK)

Lookup IP Addresses against AbuseIPDB, for attribution

options:
  -h, --help   show this help message and exit
  --ip IP      Single indicator lookup (IP Address)
  --bulk BULK  Bulk search (IP Addresses) from list.csv file

'''


import requests 
import os 
from pathlib import Path
from tabulate import tabulate
import csv
from pyfiglet import Figlet
import argparse
from typing import Any


BASE_DIR = Path(__file__).parent

def indicator_list(filename: str | Path ) -> list[str]:

    path = BASE_DIR / filename if not Path(filename).is_absolute() else Path(filename)
    ips: list[str] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            ip = row[0].strip()
            if ip:
                ips.append(ip)

    return ips


def indicator_report(ipaddress: str) -> dict[dict[str, str]]:

    api_key = os.environ.get("abuseipdb_key")
    if not api_key:
        raise RuntimeError(f"ERROR: Missing environment variable: {api_key}")


    url="https://api.abuseipdb.com/api/v2/check"
    params = { "ipAddress": ipaddress, "maxAgeInDays": "365", "verbose": "true"}
    headers = {"Key": api_key, "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"AbuseIPDB request failed for {ipaddress}: {e}")

    return response.json()




def get_summaries(ipaddress: str) -> str:
    response = indicator_report(ipaddress)

    if not response or "data" not in response:
        return f"No data found for IP Address"
    
    data = response["data"]

    table = [
        ############################## ANSII Table ##############################
        ["\033[36mIP Address:\033[0m", f"\033[32m{data['ipAddress']}\033[0m"],
        ["\033[36mCN:\033[0m", f"\033[32m{data['countryCode']}\033[0m"],
        ["\033[36mLocation\033[0m", f"\033[32m{data['countryName']}\033[0m"],
        ["\033[36mUsage Type:\033[0m", f"\033[32m{data['usageType']}\033[0m"],
        ["\033[36mISP:\033[0m", f"\033[32m{data['isp']}\033[0m"],
        ["\033[36mDomain:\033[0m", f"\033[32m{data['domain']}\033[0m"],
        ["\033[36mAnonymization Service:\033[0m", f"\033[32m{str(data['isTor'])}\033[0m"],
        ["\033[36mTotal Reports:\033[0m", f"\033[31m{data['totalReports']}\033[0m"],
        ["\033[36mAbuse Confidence Score:\033[0m", f"\033[31m{data['abuseConfidenceScore']}\033[0m"]
        ############################## ANSII Table ##############################
    ]

    return tabulate(table, headers=["Field", "AbuseIPDB Results"], tablefmt="simple")



def main(argv: list[str] | None = None) -> int:

    f = Figlet(font='eftiwall')
    print(f.renderText('sdf\n'))

    # TODO: Add argparse for easier switching, to make this a CLI tool.
    # TODO: More verbose checking on CLI arguments.
    # TODO: Handling API call timeouts more better

    parser = argparse.ArgumentParser(prog="checker", description="Lookup IP Addresses against AbuseIPDB, for attribution")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ip", help="Single indicator lookup (IP Address)")
    group.add_argument("--bulk", type=Path, help="Bulk search (IP Addresses) from list.csv file")


    args = parser.parse_args(argv)
    if args.bulk and not args.bulk.exists():
        parser.error(f"File not found: {args.bulk}")


    if args.ip:
        print(get_summaries(args.ip))

    elif args.bulk:
        
        bulk_search = indicator_list(args.bulk)
        table_data = []
        
        for ip in bulk_search:
            response = indicator_report(ip)
            if response and "data" in response:
                data = response['data']
                table_data.append([
                    f"\033[32m{data['ipAddress']}\033[0m",
                    f"\033[36m{data['domain']}\033[0m",
                    f"\033[36m{data['countryCode']}\033[0m",
                    f"\033[31m{data['totalReports']}\033[0m",
                    f"\033[31m{data['abuseConfidenceScore']}\033[0m"
                ])

        if table_data:
            print(tabulate(table_data, headers=["IP Address", "Domain", "Country", "Total Reports", "Abuse Score"], tablefmt="simple"))
        else:
            print(f"\033[31mNo data to display.\033[0m")
    
    return 0

        
if __name__ == '__main__':
    raise SystemExit(main())
