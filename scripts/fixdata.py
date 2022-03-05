import json
import os
import requests
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5  # seconds


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


http = requests.Session()

# Mount  TimeoutHTTP adapter with retries it for both http and https usage
adapter = TimeoutHTTPAdapter(timeout=2.5)
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
http.mount("http://", TimeoutHTTPAdapter(max_retries=retries))

link = "https://api.somedomain.com/api/v6.0/dns/set_reverse/"


def set_rdns(data):
    try:
        response = http.post(link)
        print(response.text)
    except:
        print('The request timed out or failed to connect')
    else:
        print('The request did not time out')


ip_rdns_to_set = os.path.expanduser('~/Downloads/rdns_backfill_to_set.json')

with open(ip_rdns_to_set) as json_file:
    rdns_to_set = json.load(json_file)

print(rdns_to_set)

for ip in rdns_to_set:
    print(ip)
    domain = rdns_to_set[ip]['domain']
    print(domain)

# print(rdns_to_set)
