import requests
import json
import unittest
from glob import *

api_key = ''  # Add API key. Found here: https://console.developers.google.com/apis/credentials/key/
base = 'https://example.com'
locale_code = 'en_US'


def get_insights_json(self, page_url, local, device_type, api_key, speed_or_useability, expected_score):
    url = 'https://www.googleapis.com/pagespeedonline/v2/runPagespeed?url=' + page_url + '&filter_third_party_resources=true&locale=' + local + '&screenshot=false&strategy=' + device_type + '&key=' + api_key
    # print "Getting :: " + url
    r = requests.get(url)
    return_code = r.status_code
    try:
        self.assertEqual(return_code, 200)
    except AssertionError as e:
        self.verificationErrors.append(str(page_url) + " did not return 200")
    return_text = r.text
    return_json = json.loads(return_text)
    score = return_json['ruleGroups'][speed_or_useability]['score']
    print('Getting ' + speed_or_useability + ' for ' + page_url + ' and got a score of ' + str(score))
    try:
        self.assertTrue(int(score) >= expected_score)
    except AssertionError as e:
        self.verificationErrors.append(
            str(page_url) + ' expected ' + device_type + ' speed score to be greater than ' + str(
                expected_score) + ', instead got ' + str(score))


class TestAllAPIs(unittest.TestCase):

    def setUp(self):
        self.verificationErrors = []
        self.maxDiff = None

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

    def test_desktop_speed(self):
        current_page = base + ''  # You could add to the url to test other pages, I tend to do this is a loop using a
        # list I set up by base url.
        device_type = 'desktop'
        target = 'SPEED'
        get_insights_json(self, current_page, locale_code, device_type, api_key, target, 80)

    def test_mobile_speed(self):
        current_page = base + ''
        device_type = 'mobile'
        target = 'SPEED'
        get_insights_json(self, current_page, locale_code, device_type, api_key, target, 80)

    def test_mobile_usability(self):
        current_page = base + ''
        device_type = 'mobile'
        target = 'USABILITY'
        get_insights_json(self, current_page, locale_code, device_type, api_key, target, 80)


if __name__ == "__main__":
    unittest.main()
