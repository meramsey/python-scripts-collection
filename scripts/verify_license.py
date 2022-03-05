import json
import platform
import requests
from PyQt5 import QtCore
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

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


http = requests.Session()

# Mount  TimeoutHTTP adapter with retries it for both http and https usage
adapter = TimeoutHTTPAdapter(timeout=2.5)
retries = Retry(total=1, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
http.mount("https://", TimeoutHTTPAdapter(max_retries=retries))
http.mount("http://", TimeoutHTTPAdapter(max_retries=retries))

# Testing new Licensing
# https://www.storeapps.org/product/woocommerce-serial-key/
host = "https://example.com"
skus = ['Wizard-Premium-Monthly', 'Wizard-Premium-Yearly', 'Wizard-Premium-Trial', 'Wizard-Premium-Monthly-Renewal',
        'Wizard-Premium-Yearly-Renewal']
sku = ''
uuid = ''
trial_license = False

license_string = 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX'


def verify_account_key(account_key_to_check, uuid):
    global license_key_is_valid, lite_license, license_string, premium_license, license_type, license_expiration, trial_license
    machine_nicename = str(platform.node())
    # print('Machine Nicename: ' + machine_nicename)
    license_key_is_valid = False
    for sku in skus:
        if license_key_is_valid is False:
            try:
                url = host + "/?wc-api=validate_serial_key&serial=" + account_key_to_check + '&sku=' + sku + '&uuid=' + str(
                    uuid)
                json_response = http.get(url).text
                # print(json_response)
                json_response_dict = json.loads(str(json_response))
                # print(json_response_dict)
                print(json.dumps(json_response_dict, indent=4))
                if json_response_dict['success'] == 'true':
                    verify_response = 'License verification Success: ' + sku + ' ' + account_key_to_check
                    print(verify_response + ' ' + str(uuid))
                    license_key_is_valid = True
                    if 'Wizard-Premium-Trial' in json_response_dict['product_sku']:
                        trial_license = True
                    elif 'Monthly' or 'Yearly' in json_response_dict['product_sku']:
                        premium_license = True
                    license_string = account_key_to_check
                    license_expiration = json_response_dict['access_expires']
                    settings = QtCore.QSettings('WizardAssistant', 'WizardAssistantDesktop')
                    settings.setValue('license', license_string)
            except:
                print('Unable to contact License server')

    if license_key_is_valid:
        return True
    else:
        verify_response = 'License verification failed!: ' + sku + ' ' + account_key_to_check
        print(verify_response + ' ' + str(uuid))
        license_key_is_valid = False
        lite_license = True
        return False


verify_account_key(license_string, str(platform.node()))
print(f"Trial license: {trial_license}")
print(f"Premium license: {premium_license}")
