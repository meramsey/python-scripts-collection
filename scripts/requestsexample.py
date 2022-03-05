import requests
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

link = "https://ipinfo.io/8.8.8.8"

# For requests
DEFAULT_TIMEOUT = 5  # seconds


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


def setup_timeout_http_adapter():
    http = requests.Session()
    # Mount  TimeoutHTTP adapter with retries it for both http and https usage
    adapter = TimeoutHTTPAdapter(timeout=5)
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
    http.mount("http://", TimeoutHTTPAdapter(max_retries=retries))

    return http


http = setup_timeout_http_adapter()

try:
    response = http.get(link)
    print(response.text)
except:
    print('The request timed out or failed to connect')
else:
    print('The request did not time out')

# filename = ''
# link = ''

# url = link
# r = http.get(url)
# with open(filename, 'wb') as f:
#     f.write(r.content)
