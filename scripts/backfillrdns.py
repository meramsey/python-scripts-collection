import json
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from string import punctuation

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

link = "https://devapi.somedomain.com/api/v6.0/dns/set_reverse/"
auth_user = 'redacted'
auth_pass = 'redacted'

api_responses = {}


def set_rdns(data):
    try:
        headers = {'Content-type': 'application/json'}
        response = http.post(link, auth=HTTPBasicAuth(auth_user, auth_pass), data=json.dumps(data), headers=headers)
        print(response.text)
        api_responses[data['ip']] = response.text
        # successful range
        r = range(200, 299)
        if response.status_code in r:
            print('Success!')
        elif response.status_code == 404:
            print('Not Found.')
        else:
            print(f"Status code: {response.status_code}")

    except:
        print('The request timed out or failed to connect')
    else:
        print('The request did not time out')


ip_rdns_to_set = os.path.expanduser('~/Downloads/rdns_backfill_to_set_after-2.json')

with open(ip_rdns_to_set) as json_file:
    rdns_to_set = json.load(json_file)

# print(rdns_to_set)

for ip in rdns_to_set:
    record = rdns_to_set[ip]
    record = record.strip().replace(" ", "").strip(punctuation)
    print(f'IP: {ip} RDNs: {record}')
    dictionary = {
        "ip": ip,
        "record": record
    }
    # print(json_object)
    set_rdns(dictionary)

# print(rdns_to_set)

api_rdns_reponses = os.path.expanduser('~/Downloads/rdns_backfill_responses-4.json')

with open(api_rdns_reponses, "w") as outfile:
    json.dump(api_responses, outfile)
