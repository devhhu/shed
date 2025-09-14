
import requests 
from time import sleep 

# Okay lets contact an API client which doesn't exist and dable a little bit in retries and backoff:

RETRY_CODES = (429, 501, 502, 503, 504) --> useful to have transient error codes to retry on, mainly reference for now.


session = requests.Session() # connection pool reuse, stateful 

timeout: tuple[float, float] = (3.05, 10.05) #connect timeout thresholds
params: dict | None = None 
backoff: float = 0.5

tries: int = 6

for attempt in range(1, tries+1):
    try: 
        response = session.get("https://nonexistingerrorcodegeneratortest.com", params=params, timeout=timeout)

    except Exception as e:
        
        sleep(backoff)
        backoff *= 2
        print(f"Current Attempt to connect to URL: {attempt}")
        print(f"Exponential Backoff Increased: {backoff}")
        print(f"\n{e}\n")
    


'''
Error Code:
HTTPSConnectionPool(host='nonexistingerrorcodegeneratortest.com', port=443): Max retries exceeded with url: 
/ (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x104720590>, 
'Connection to nonexistingerrorcodegeneratortest.com timed out. (connect timeout=3.05)'))


Flow:

Current Attempt to connect to URL: 1
Exponential Backoff Increased: 1.0
               |
               |
              \ /

Current Attempt to connect to URL: 2
Exponential Backoff Increased: 2.0
               |
               |
              \ /

Current Attempt to connect to URL: 3
Exponential Backoff Increased: 4.0
               |
               |
              \ /

Current Attempt to connect to URL: 4
Exponential Backoff Increased: 8.0
               |
               |
              \ /


Current Attempt to connect to URL: 5
Exponential Backoff Increased: 16.0
               |
               |
              \ /

Current Attempt to connect to URL: 6
Exponential Backoff Increased: 32.0



'''


