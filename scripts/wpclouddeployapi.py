import json
import requests
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import base64

DEFAULT_TIMEOUT = 5  # seconds

domain = 'example.com'

# Was a test script probably nonfunctional currently
# https://wpclouddeploy.com/documentation/rest-api/rest-api-introduction/
# https://smiinc.stoplight.io/docs/wpclouddeploy/YXBpOjI1MDMwOTYz-wp-cloud-deploy-core-rest-api


# https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
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

link = f'https://{domain}/sites'

# try:
#     response = http.get(link)
#     print(response.text)
#     print('=============================')
#     json_response_dict = response.json()
#     print(response.text)
# except Exception as e:
#     print(f'The request timed out or failed to connect due to: {e}')
# else:
#     print('The request did not time out')

url = f"https://{domain}/?rest_route=/sites"
user = ''
passw = ''

# headers = {'Content-Type': 'application/json',
#            "Authorization": 'Basic %s' % base64.b64encode(bytes(f"{user}:{passw}", "utf-8")).decode("ascii")}
#
# response = http.post(link, headers=headers)
#
# print(response.text)

headers = {'Content-Type': 'application/json'}

response = requests.request("GET", url, headers=headers)

print(response.text)
