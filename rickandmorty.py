import requests
from urllib.parse import urljoin
from time import sleep
import argparse
import json

# api testing, fetching, pagination etc

'''
usage: Add (fetch) as a command line argument

API Endpoints:

{
  "characters":"https://rickandmortyapi.com/api/character",
  "locations":"https://rickandmortyapi.com/api/location",
  "episodes":"https://rickandmortyapi.com/api/episode"
}

options:
  -h, --help           show this help message and exit
  --base-url BASE_URL  This is the (base url) for the HTTP handler
  --path PATH          This is to specify the (endpoint)
  --timeout TIMEOUT    Threshold for HTTP conn (timeout) 
  --tries TRIES        This is to indicate the number of (retries)
  --token TOKEN        If available an (access token) can be entered here
  --verbose            Verbose logging
  --page PAGE          The page you are interested in navigating to
  --all ALL            Fetch all pages
  --max-pages MAX_PAGES
                        cap for (--all) parameter
  
Example Usage:

python3 <script_name.py fetch \
  --base-url https://rickandmortyapi.com \
  --path /api/location \
  --page 1


python3 <script_name>.py fetch \
  --base-url https://rickandmortyapi.com \
  --path /api/location \
  --all

  python3 <script_name>.py fetch \
  --base-url https://rickandmortyapi.com \
  --path /api/location \
  --all \
  --max-pages 2

python3 <script_name>.py fetch \
  --base-url https://rickandmortyapi.com \
  --path /api/location \
  --all \
  --page 3 \
  --max-pages 3

'''

RETRY_CODES = {429, 504, 503, 502, 501}

def build_session(token: str | None = None) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent":"layer-cli"})
    if token:
        session.headers['Authorization'] = f"Bearer {token}"

    return session 


def fetcher(
        session: requests.Session,
        url: str,
        params: dict | None = None,
        timeout: tuple[float,float] = (3.05, 10.0),
        tries: int = 3,
        initial_backoff: float = 0.5,
            ):
    backoff = initial_backoff
    last_exc: Exception | None = None


    for attempt in range(1,tries +1):
        try:
            response = session.get(url, params=params, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout, requests.ReadTimeout) as e:
            last_exc = e
            print(f"Something happened here {last_exc}")
            if attempt == tries:
                raise
            sleep(backoff)
            backoff *= 2

            if response.status_code in RETRY_CODES:
                if attempt == tries:
                    raise
                sleep(backoff)
                backoff *= 2
                continue
        
            response.raise_for_status()

    #TODO: Add something here to gracefully handle non JSON returns 
            
    
    return response.json()


def fetch_page(
        session: requests.Session,
        base_url: str,
        path: str,
        page_number: int,
        base_params=None,
):
    url = urljoin(base_url.rstrip("/") + '/', path.lstrip("/"))
    
    params = dict(base_params or {})
    params['page'] = page_number


    data = fetcher(session, url, params)

    if 'info' not in data or 'results' not in data:
        raise "Missing expected keys in response"
    
    items = data['results']
    next_url = data['info']['next']


    return items, next_url


def iter_pages(
        session: requests.Session,
        base_url: str,
        path: str,
        base_params: dict | None = None,
        start_page: int = 1,
        max_pages: int | None = None
):
    items, next_url = fetch_page(session, base_url, path, start_page, base_params)

    pages_fetched = 0 

    while True:
        if not items:
            break 

        yield items
        pages_fetched += 1

        if max_pages is not None and pages_fetched >= max_pages:
            break 

        if next_url is None:
            break

        data = fetcher(session, next_url)

        if 'info' not in data or 'results' not in data:
            raise "Missing expected keys in response"
        
        items = data['results']
        next_url = data['info']['next']


def parse_cli(argv):

    parser = argparse.ArgumentParser(
        prog="API_TEST",
        description="API-TEST",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch",usage="Add (fetch) as a command line argument")

    fetch.add_argument("--base-url", required=True, help="This is the (base url) for the HTTP handler")
    fetch.add_argument("--path", required=True, help="This is to specify the (endpoint)")
    fetch.add_argument("--timeout", type=float, default=10.5, help="Threshold for (timeout) before retrying")
    fetch.add_argument("--tries", type=int, default=3, help="This is to indicate the number of (retries)")
    fetch.add_argument("--token", help="If available an (access token) can be entered here")
    fetch.add_argument("--verbose", action="store_true", help="Verbose logging") 
    fetch.add_argument('--page', type=int, default=1, help="The page you are interested in navigating to" )
    fetch.add_argument('--all', action="store_true", help="Fetch all pages")
    fetch.add_argument('--max-pages', type=int,default=10, help="Safety cap for (--all) parameter")

    args = parser.parse_args(argv)

    return args

def main(argv: None = None):


    args = parse_cli(argv)

    if args.command != 'fetch':
        raise SystemExit("Only fetch command is supported")

    session = build_session()
    
    if args.all:
    
        start_page = args.page
        max_pages = args.max_pages
        base_params = None 



        total_items = 0
        pages = 0 


        for page_items in iter_pages(
            session,
            args.base_url,
            args.path, 
            base_params,
            start_page, 
            max_pages
        ):

            pages += 1
            total_items = total_items + len(page_items)


            print(f"pages_fetched: {pages}")
            print(f"total_items: {total_items}")


    else:
        page_items, next_link = fetch_page(session,args.base_url, args.path, args.page)
        print(f"Length of items: {len(page_items)}")            
        print(f"Sample Item from page: {page_items[0]['name']}")      
        print(f"Pointer to the next page: {next_link}")  
    

if __name__ == '__main__':
    raise SystemExit(main())
