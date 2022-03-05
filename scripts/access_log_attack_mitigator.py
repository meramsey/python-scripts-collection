#!/usr/bin/python3
import sys
import time
import os
import platform
import re
import urllib.request
from datetime import date, timedelta
from datetime import datetime
import collections
from collections import defaultdict
import requests
import json

try:
    import configparser  # py3
except ImportError:
    import ConfigParser as configparser  # py2

# Define log patterns based on host.
# /etc/nginx/nginx.conf

# # 10.10.84.3 - - [05/Aug/2021:14:49:45 -0400] "POST /dologin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36" "176.103.45.63" "176.103.45.63" "clientarea.php?incorrect=true" 16.785 0.125 .
# log_format  main  '$remote_addr - $remote_user [$time_local] "$request" ' '$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" "$http_x_forwarded_for" "$http_cf_connecting_ip" "$sent_http_location" ' '$request_time $upstream_response_time $pipe';
logpats = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (\S+) (\S+)" (\S+) (\S+) "(\S+)" "(.*)" "(\S+)" "(\S+)" "(\S+)"'

# Column name matching

colnames = (
    "remote_addr",
    "referrer",
    "remote_user",
    "time_local",
    "method",
    "request",
    "proto",
    "status",
    "body_bytes_sent",
    "http_referer",
    "http_user_agent",
    "http_x_forwarded_for",
    "http_cf_connecting_ip",
    "sent_http_location",
    "request_time",
    "upstream_response_time",
    "pipe",
)

access_log_name = "access_log"
error_log_name = "error_log"
zone_identifier = ""

# Get hostname so we know if were live or dev.
machine_nicename = str(platform.node())
print("Machine Nicename: " + machine_nicename)

if "devserver2" in str(platform.node()):
    default_hourly_threshold = 10
    default_minute_threshold = 1
else:
    default_hourly_threshold = 1000
    default_minute_threshold = 500

####### Begin Config ########
# scripts/access_log_attack_mitigator.py
current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Get base directory up one directory from scripts
base_directory = os.path.dirname(current_script_path)

# /home/whmcs/whmcs/logs/access_log or relative path logs/access_log
access_logfile = os.path.join(base_directory, "logs", access_log_name)
error_logfile = os.path.join(base_directory, "logs", error_log_name)
# print(current_script_path)
# print(base_directory)
print("Script path: ", current_script_path)
print("Access Log: ", access_logfile)
print("Error Log: ", error_logfile)


####### End Config ########


def read_configs(config_paths, config_dict):
    """Read a config file from filesystem

    :param config_paths: A list of config file paths.
    :type config_paths: list
    :param config_dict: A Config dictionary profile.
    :type config_dict: dict
    :return: Config profile dictionary
    :rtype: dict
    """

    # We return all these values
    config = config_dict
    profile = config['profile']

    # grab values from config files
    cp = configparser.ConfigParser()
    try:
        cp.read(config_paths)
    except Exception as e:
        raise Exception("%s: configuration file error" % profile)

    if len(cp.sections()) > 0:
        # we have a configuration file - lets use it
        try:
            # grab the section - as we will use it for all values
            section = cp[profile]
        except Exception as e:
            # however section name is missing - this is an error
            raise Exception("%s: configuration section missing" % profile)

        for option in list(config.keys()):
            if option not in config or config[option] is None:
                try:
                    config[option] = re.sub(r"\s+", '', section.get(option))
                    if config[option] == '':
                        config.pop(option)
                except (configparser.NoOptionError, configparser.NoSectionError):
                    pass
                except Exception as e:
                    pass

    # remove blank entries
    for x in sorted(config.keys()):
        if config[x] is None or config[x] == '':
            try:
                config.pop(x)
            except:
                pass

    return config


slack_config_paths = ['.slack.cfg', os.path.expanduser('~/.slack.cfg'), os.path.expanduser('~/.slack/slack.cfg')]
slack_config_dict = {'slack_token': os.getenv('SLACK_TOKEN'),
                     'slack_channel': os.getenv('SLACK_CHANNEL'),
                     'slack_icon_emoji': os.getenv('SLACK_ICON_EMOJI'),
                     'slack_user_name': os.getenv('SLACK_USER_NAME'),
                     'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
                     'profile': 'SLACK'}

"""
To setup config securely:
nano ~/.slack.cfg
"""
# Then enter the desired below with your details
"""
[SLACK]
slack_token = 
slack_channel = alerts
slack_icon_emoji =
slack_user_name = 
slack_webhook_url = 
"""

# Read config file if it exists and override the above
slack_profile = read_configs(slack_config_paths, slack_config_dict)

slack_token = None
slack_channel = None
slack_icon_emoji = None
slack_user_name = None
slack_webhook_url = None

if 'slack_token' in slack_profile:
    slack_token = slack_profile['slack_token']
if 'slack_channel' in slack_profile:
    slack_channel = slack_profile['slack_channel']
if 'slack_icon_emoji' in slack_profile:
    slack_icon_emoji = slack_profile['slack_icon_emoji']
if 'slack_user_name' in slack_profile:
    slack_user_name = slack_profile['slack_user_name']
if 'slack_webhook_url' in slack_profile:
    slack_webhook_url = slack_profile['slack_webhook_url']

"""
To setup config securely:
mkdir -p ~/.cloudflare/
nano ~/.cloudflare/cloudflare.cfg
"""
# Then enter the desired below like outlined:
# https://github.com/cloudflare/python-cloudflare#using-configuration-file-to-store-email-and-keys
# certtoken and extras can be empty or undefined as were not using them currently now.
# zone_identifier is per domain in CF dashboard
# cloudflare_auto_mitigation defines whether you want the autocreated rule to be active after creation. It defaults even if unset to False.
"""
[CloudFlare]
email = user@somedomain.com
token = 
certtoken = 
zone_identifier = 
cloudflare_auto_mitigation = False
"""

cf_config_paths = [
    '.cloudflare.cfg',
    os.path.expanduser('~/.cloudflare.cfg'),
    os.path.expanduser('~/.cloudflare/cloudflare.cfg')
]

cf_config_dict = {'email': os.getenv('CF_API_EMAIL'),
                  'token': os.getenv('CF_API_KEY'),
                  'certtoken': os.getenv('CF_API_CERTKEY'),
                  'zone_identifier': os.getenv('CF_ZONE_ID'),
                  'cloudflare_auto_mitigation': os.getenv('CF_AUTO_MITIGATION'),
                  'profile': 'CloudFlare'}

BASE_URL = 'https://api.cloudflare.com/client/v4'

# Setup defaults
x_auth_email = None
x_auth_key = None
zone_identifier = None
certtoken = None
cloudflare_auto_mitigation = False
base_url = BASE_URL


def cf_config_read():
    global x_auth_email, x_auth_key, zone_identifier, certtoken, cloudflare_auto_mitigation, base_url
    # Read config file if it exists and override the above
    cf_profile = read_configs(cf_config_paths, cf_config_dict)

    if 'email' in cf_profile:
        x_auth_email = cf_profile['email']
    if 'token' in cf_profile:
        x_auth_key = cf_profile['token']
    if 'zone_identifier' in cf_profile:
        zone_identifier = cf_profile['zone_identifier']
    if 'certtoken' in cf_profile:
        certtoken = cf_profile['certtoken']
    if 'cloudflare_auto_mitigation' in cf_profile:
        cloudflare_auto_mitigation = cf_profile['cloudflare_auto_mitigation']
    if 'base_url' in cf_profile:
        base_url = cf_profile['base_url']


cf_config_read()

# Initialize useful globals
headers = {
    "X-Auth-Email": x_auth_email,
    "X-Auth-Key": x_auth_key,
    "Content-Type": "application/json",
}

script_start_time = datetime.now()

logpat = re.compile(logpats)

# default dictionary: https://book.pythontips.com/en/testing/collections.html#defaultdict
tree = lambda: defaultdict(tree)
hits = tree()

# Here we will be keeping a running tally of currently mitigated urls tally.
mitigated_urls = tree()


# Some functions

# Functions for printing colored text out: Source: https://stackoverflow.com/a/34443116/1621381
def black(text):
    print('\033[30m', text, '\033[0m', sep='')


def red(text):
    print('\033[31m', text, '\033[0m', sep='')


def green(text):
    print('\033[32m', text, '\033[0m', sep='')


def yellow(text):
    print('\033[33m', text, '\033[0m', sep='')


def blue(text):
    print('\033[34m', text, '\033[0m', sep='')


def magenta(text):
    print('\033[35m', text, '\033[0m', sep='')


def cyan(text):
    print('\033[36m', text, '\033[0m', sep='')


def gray(text):
    print('\033[90m', text, '\033[0m', sep='')


# Some slackbot post functions

def post_message_to_slack(text, channel=None, blocks=None):
    if channel is None:
        channel = slack_channel
    return requests.post('https://slack.com/api/chat.postMessage', {
        'token': slack_token,
        'channel': channel,
        'text': text,
        'icon_emoji': slack_icon_emoji,
        'username': slack_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


def post_file_to_slack(text, file_name, file_bytes, channel=None, file_type=None, title=None):
    if channel is None:
        channel = slack_channel
    return requests.post(
        'https://slack.com/api/files.upload',
        {
            'token': slack_token,
            'filename': file_name,
            'channels': channel,
            'filetype': file_type,
            'initial_comment': text,
            'title': title
        },
        files={'file': file_bytes}).json()


def post_message_to_slack_webhook(message, webhook_url=None):
    if webhook_url is None:
        webhook_url = slack_webhook_url
    slack_data = json.dumps({'text': message})
    response = requests.post(
        webhook_url, data=slack_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


# post_message_to_slack_webhook('Testing devalerts slack from python. Ignore me')


def get_remote_file_data(file):
    response = urllib.request.urlopen(file)
    data = response.read()
    filename = response.info().get_filename()
    data_meta = {'data': data, 'filename': filename}

    return data_meta


def field_map(dictseq, name, func):
    for d in dictseq:
        d[name] = func(d[name])
        yield d


def get_datetime_object_from_string(str):
    return datetime.strptime(str, "%d/%b/%Y:%H:%M:%S %z")


def keyfunction(k):
    """Create a function which returns the value of a dictionary
    :param k: key
    :type k: (Iterable, None, bool)
    :return: dictionary key's value
    :rtype: dict[value]
    """
    return d[k]


def access_log(lines):
    """Parse Access Log Line

    :param lines: Access Log Lines to parse
    :type lines: Generator[Any, Any, None]
    :return: Returns dictionary of parsed lines
    :rtype: dict
    """
    groups = (logpat.match(line) for line in lines)
    tuples = (g.groups() for g in groups if g)

    log = (dict(zip(colnames, t)) for t in tuples)
    # Change Access log items into Python types
    log = field_map(log, 'status', int)
    # Convert the timestamp into a datetime object
    log = field_map(log, 'time_local', get_datetime_object_from_string)
    # Some dashes become None
    log = field_map(log, 'remote_user', lambda s: s if s != "-" else None)
    log = field_map(log, 'http_referer', lambda s: s if s != "-" else None)
    log = field_map(log, 'referrer', lambda s: s if s != "-" else None)
    log = field_map(log, 'http_user_agent', lambda s: s if s != "-" else None)
    # The size/body_bytes_sent dash becomes 0
    log = field_map(log, 'body_bytes_sent', lambda s: int(s) if s != "-" else 0)

    return log


def print_sorted_dict_top(d, top):
    print("============================================")
    for key in sorted(d, key=keyfunction, reverse=True)[:top]:
        print("  %5d  %s" % (d[key], key))
    print("  %5d  total hits" % sum(dict.values(d)))
    print("============================================")


def tail_file(file):
    """generator function that yields new lines in a file

    :param file:File Path as a string
    :type file: str
    :rtype: object
    """
    seek_end = True
    while True:  # handle moved/truncated files by allowing to reopen
        with open(file) as f:
            if seek_end:  # reopened files must not seek end
                f.seek(0, 2)
            while True:  # line reading loop
                line = f.readline()
                if not line:
                    try:
                        if f.tell() > os.path.getsize(file):
                            # rotation occurred (copytruncate/create)
                            f.close()
                            seek_end = False
                            break
                    except FileNotFoundError:
                        # rotation occurred but new file still not created
                        pass  # wait 1 second and retry
                    time.sleep(1)
                yield line


def purge_old_stats():
    """
    This function will compare the current time and day and then delete the nested keys in the global hits dictionary.
    This ensures the hits kept in memory is low and self prunes.
    """
    current_time = datetime.now()
    current_day_hour = current_time.strftime("%d/%b/%Y %H")
    current_day_of = current_time.strftime("%Y-%m-%d")

    for day in list(hits.keys()):
        # print(f'Printing day keys before {list(hits.keys())}')
        # Let's prune old days keys from dictionary to prevent excessive usage
        if day != current_day_of:
            del hits[day]
            # print(f'Printing keys after {list(hits.keys())}')

        # print(f'Printing day_hour keys before {list(hits[day].keys())}')
        # Let's prune old hours keys from dictionary to prevent excessive usage
        for hour in list(hits[day].keys()):
            if hour != current_day_hour:
                del hits[day][hour]
            # print(f'Printing day_hour keys before {list(hits[day].keys())}')


def check_date_past_interval(check_date, interval=None):
    """Return True if given check_date is past the interval from current time.

    :param check_date: Datetime string like '2021-08-23 18:14:05'
    :type check_date: str
    :param interval: Hours amount to check in past.
    :type interval: int
    :return: Returns True if date exceeds interval.
    :rtype: bool
    """
    from datetime import datetime, time, timedelta
    if interval is None:
        interval = 1
    date = datetime.strptime(str(check_date), '%Y-%m-%d %H:%M:%S')
    # date = check_date
    past = datetime.now() - timedelta(hours=interval)
    # Change period to period timedelta range provided as needed.
    period = 'hours'
    if past > date:
        print(f"This is older than {interval} {period}")
        return True
    elif past > date:
        return False
    else:
        return False


def cf_list_firewall_rules_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://api.cloudflare.com/#firewall-rules-list-of-firewall-rules
    url = f"{BASE_URL}/zones/{zone_identifier}/firewall/rules"
    response = requests.get(url, headers=headers).text
    json_response_dict = json.loads(str(response))
    # print(json.dumps(filters_json_response_dict, indent=4))
    return json_response_dict


def cf_list_filters_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://developers.cloudflare.com/firewall/api/cf-filters/get/#get-all-filters
    url = f"{BASE_URL}/zones/{zone_identifier}/filters"
    response = requests.get(url, headers=headers).text
    json_response_dict = json.loads(str(response))
    # print(json.dumps(filters_json_response_dict, indent=4))
    return json_response_dict


def cf_create_filter(uri, expression=None, description=None):
    # Cloudflare create filter for use in firewall rule below
    # https://developers.cloudflare.com/firewall/api/cf-filters/post
    url = f"{BASE_URL}/zones/{zone_identifier}/filters"

    # Lets strip query parameters for base uri path
    uri = uri.split("?")[0]

    if expression is None:
        expression = '(http.request.uri contains \"' + uri + '\")'

    if description is None:
        description = f'Rule for {uri} created {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    # Here we serialize and wrap the dictionary with brackets cause CF API is lame. :
    # https://community.cloudflare.com/t/whats-the-problem-with-firewallrules-api-malformed-request-body/109433/2
    payload = json.dumps([{
        "expression": expression,
        "description": description
    }])

    response = requests.post(url, headers=headers, data=payload).text
    response_dict = json.loads(str(response))
    # print(json.dumps(response_dict, indent=4))
    # print(response_dict)
    return response_dict


def cloudflare_toggle_mitigation_for_uri(uri, action, paused=True, id=None, filter_id=None, description=None, ref=None):
    """Toggle Cloudflare mitigation for an uri.
    # https://api.cloudflare.com/#firewall-rules-create-firewall-rules

    :param uri: Uri path
    :type uri: str
    :param action: The action to apply to a matched request. Actions allowed: block, challenge, js_challenge, allow, log, bypass
    :type action: str
    :param paused: Whether this filter is currently paused
    :type paused: bool
    :param id:  for Rule
    :type id: str Firewall Rule identifier
    :param filter_id: Filter identifier
    :type filter_id:  str
    :param description: A note that you can use to describe the purpose of the filter
    :type description: str
    :param ref: Short reference tag to quickly select related rules.
    :type ref: str
    :return: Returns dict of the cloudflare API response for the rule
    :rtype: dict
    """

    if description is None:
        description = (
            f'Rule for {uri} created {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )

    if ref is None:
        ref = "None"

    if filter_id is None:
        filters_json_response_dict = cf_create_filter(uri)
        if not filters_json_response_dict["success"]:
            filter_id = filters_json_response_dict['errors'][0]["meta"]["id"]
        elif filters_json_response_dict["result"][0]["id"]:
            filter_id = filters_json_response_dict["result"][0]["id"]
        else:
            return filters_json_response_dict

    payload = json.dumps([
        {
            "filter": {
                "id": filter_id
            },
            "action": action,
            "paused": paused,
            "description": description,
        }
    ])
    url = f"{BASE_URL}/zones/{zone_identifier}/firewall/rules"
    json_response = requests.post(url, data=payload, headers=headers).text
    json_response_dict = json.loads(str(json_response))
    # print(json.dumps(json_response_dict, indent=4))
    return json_response_dict


def apply_mitigation(url, threshold, period):
    # Put this here so we can toggle stuff in configs and its read again before taking actions.
    # This prevents us from needing to stop and restart the script to make changes such as auto_mitigation_enabled.
    cf_config_read()
    message = f'Accesslog threshold {threshold} hit for {url} in {period}'
    red(message)
    # If key does not exist
    print(mitigated_urls[url])
    if not mitigated_urls[url]:
        # If not already mitigated aka set to true
        print("Creating key: ", url)
        mitigated_urls[url]["Active"] = False
    # If key exists lets see if its True indicating mitigation already is enabled
    if mitigated_urls[url]["Active"] is False:
        message = f'Accesslog threshold {threshold} hit for {url} in {period}. ' \
                  f'Attack Mitigation not enabled for: {url}. Attempting Mitigation now for: {url} '
        post_message_to_slack_webhook(message)
        print("Attack Mitigation not enabled for: ", url)
        # Add url to track in mitigated_urls
        print("Attempting Mitigation for: ", url)
        # Lets only explicitly enable rules if environmental variable is enabled
        if cloudflare_auto_mitigation is True and x_auth_key is not None:
            message = f'As cloudflare_auto_mitigation is set to true creating and enabling rule for: {url}'
            green(message)
            post_message_to_slack_webhook(message)
            cloudflare_response = cloudflare_toggle_mitigation_for_uri(url, "js_challenge", paused=False)
        else:
            if x_auth_key is not None:
                message = f'As cloudflare_auto_mitigation is false creating but NOT enabling rule for: {url}. ' \
                          f'Please Login to Cloudflare Dashboard and enable rule manually if desired.'
                yellow(message)
                post_message_to_slack_webhook(message)
                cloudflare_response = cloudflare_toggle_mitigation_for_uri(url, "js_challenge", paused=True)
            else:
                # Let's ensure that if no API key is set we can skip trying to hit the api which will fail.
                cloudflare_response = {"success": False}
        # If successfully added
        if cloudflare_response["success"]:
            # Let's set this uri as actively under mitigation
            mitigated_urls[url]["Active"] = True
            # Record time
            mitigated_urls[url]["Start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Record Cloudflare rule id for later use to toggle off
            mitigated_urls[url]["FirewallID"] = cloudflare_response["result"][0]["id"]
            message = f'Mitigation {cloudflare_response["result"][0]["id"]} enabled for attacks against {url}'
            green(message)
            post_message_to_slack_webhook(message)
        elif not cloudflare_response["success"]:
            message = f'Mitigation failed to enable for attacks against {url} due to {cloudflare_response["errors"]}'
            red(message)
            post_message_to_slack_webhook(message)
        else:
            message = f'Mitigation failed to enable for attacks against {url} due to Unknown Error condition'
            red(message)
            post_message_to_slack_webhook(message)
    elif mitigated_urls[url]["Active"] == True:
        green(
            f'Mitigation already enabled for attacks against {url} since: {mitigated_urls[url]["Start"]}'
        )
    # Let's set mitigation as active so we don't get followup messages for each hit after threshold till hour resets
    mitigated_urls[url]["Active"] = True
    mitigated_urls[url]["Start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mitigated_urls[url]["Stop"] = None


# Let's only worry about setting up rules for known rules which match these common ones
urls_of_interest = ['/cart.php', '/dologin.php', '/clientarea.php', '/clientarea.php?incorrect=true']
thresholds = {'/cart.php': 5,
              '/dologin.php': 10,
              '/clientarea.php': 10,
              '/clientarea.php?incorrect=true': 10}

if __name__ == "__main__":
    # loglines = tail_file(access_logfile)
    loglines = access_log(tail_file(access_logfile))
    # iterate over the generator
    for line in loglines:
        # print(line)
        # Lines are an associated array dictionary like below.
        # {'remote_addr': '10.10.84.3', 'referrer': None, 'remote_user': None, 'time_local': datetime.datetime(2021, 8, 25, 8, 37, 10, tzinfo=datetime.timezone(datetime.timedelta(-1, 72000))), 'method': 'GET', 'request': '/dologin.php', 'proto': 'HTTP/2.0', 'status': 302, 'body_bytes_sent': 5, 'http_referer': '-', 'http_user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36', 'http_x_forwarded_for': '176.103.45.63', 'http_cf_connecting_ip': '176.103.45.63', 'sent_http_location': 'clientarea.php?incorrect=true'}
        day_time = line["time_local"].strftime("%Y-%m-%d:%H:%M:%S")
        day_minute = line["time_local"].strftime("%Y-%m-%d:%H:%M")
        day_hour = line["time_local"].strftime("%Y-%m-%d:%H")
        day_of = line["time_local"].strftime("%Y-%m-%d")

        # Loops through all logline keys and initializes hit counters for all keys and unique values
        for item in line.items():
            key, value = item
            # print(key, value)
            if value is not None and value != '-':
                # the hour
                if hits[day_of][day_hour][key][value]:
                    hits[day_of][day_hour][key][value] += 1
                else:
                    hits[day_of][day_hour][key][value] = 1

                # the minute
                if hits[day_of][day_minute][key][value]:
                    hits[day_of][day_minute][key][value] += 1
                else:
                    hits[day_of][day_minute][key][value] = 1

        # Lets now loop through hour stats for each logline key and see top hits
        for item in hits[day_of][day_hour].items():
            key, value = item
            # Filter the console output to the more useful fields for live viewing pleasure.
            if key in ['request', 'remote_addr', 'http_user_agent', 'http_referer']:
                print("")
                print(f'Top hits for {key} for {day_hour}')
                d = hits[day_of][day_hour][key]
                print_sorted_dict_top(d, 5)

        url = line["request"]

        if hits[day_of][day_hour]["request"][url] >= default_hourly_threshold and url in urls_of_interest:
            message = f'Accesslog threshold {default_hourly_threshold} hit for {url} in last hour'
            red(message)
            apply_mitigation(url, thresholds[url], 'hour')

        if hits[day_of][day_minute]["request"][url] >= default_minute_threshold and url in urls_of_interest:
            message = f'Accesslog threshold {default_minute_threshold} hit for {url} in minute'
            red(message)
            apply_mitigation(url, thresholds[url], 'minute')

        if hits[day_of][day_minute]["request"][url] >= default_minute_threshold and url not in urls_of_interest:
            message = f'Accesslog threshold {default_minute_threshold} hit for {url} in minute.' \
                      f'Url is not in whitelist to mitigate. ' \
                      f'Please add to urls of interest if this is not a false positive'
            red(message)
            post_message_to_slack_webhook(message)
            # Need to add some logic so this alerts only once per period.
            # This is so were notified of unknown urls being targeted and can know to enable a rule.

            # # If key does not exist
            # print(mitigated_urls[line["request"]])
            # if not mitigated_urls[line["request"]]:
            #     # If not already mitigated aka set to true
            #     print("Creating key: ", line["request"])
            #     mitigated_urls[line["request"]]["Active"] = False
            # # If key exists lets see if its True indicating mitigation already is enabled
            # if mitigated_urls[line["request"]]["Active"] == False:
            #     message = f'Accesslog threshold {default_threshold} hit for {line["request"]} in last hour. Attack Mitigation not enabled for: {line["request"]}. Attempting Mitigation now for: {line["request"]}'
            #     post_message_to_slack_webhook(message)
            #     print("Attack Mitigation not enabled for: ", line["request"])
            #     # Add url to track in mitigated_urls
            #     print("Attempting Mitigation for: ", line["request"])
            #     # Lets only explicitly enable rules if environmental variable is enabled
            #     if cloudflare_auto_mitigation == True and x_auth_key is not None:
            #         message = f'As cloudflare_auto_mitigation is set to true creating and enabling rule for: {line["request"]}'
            #         green(message)
            #         post_message_to_slack_webhook(message)
            #         cloudflare_response = cloudflare_toggle_mitigation_for_uri(line["request"], "js_challenge",
            #                                                                    paused=False)
            #     else:
            #         if x_auth_key is not None:
            #             message = f'As cloudflare_auto_mitigation is false creating but NOT enabling rule for: {line["request"]}. Please Login to Cloudflare Dashboard and enable rule manually if desired.'
            #             yellow(message)
            #             post_message_to_slack_webhook(message)
            #             cloudflare_response = cloudflare_toggle_mitigation_for_uri(line["request"], "js_challenge",
            #                                                                        paused=True)
            #         else:
            #             # Let's ensure that if no API key is set we can skip trying to hit the api which will fail.
            #             cloudflare_response = {"success": False}
            #     # If successfully added
            #     if cloudflare_response["success"]:
            #         # Let's set this uri as actively under mitigation
            #         mitigated_urls[line["request"]]["Active"] = True
            #         # Record time
            #         mitigated_urls[line["request"]]["Start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #         # Record Cloudflare rule id for later use to toggle off
            #         mitigated_urls[line["request"]]["FirewallID"] = cloudflare_response["result"][0]["id"]
            #         message = f'Mitigation {cloudflare_response["result"][0]["id"]} enabled for attacks against {line["request"]}'
            #         green(message)
            #         post_message_to_slack_webhook(message)
            #     elif not cloudflare_response["success"]:
            #         message = f'Mitigation failed to enable for attacks against {line["request"]} due to {cloudflare_response["errors"]}'
            #         red(message)
            #         post_message_to_slack_webhook(message)
            #     else:
            #         message = f'Mitigation failed to enable for attacks against {line["request"]} due to Unknown Error condition'
            #         red(message)
            #         post_message_to_slack_webhook(message)
            # elif mitigated_urls[line["request"]]["Active"] == True:
            #     green(
            #         f'Mitigation already enabled for attacks against {line["request"]} since: {mitigated_urls[line["request"]]["Start"]}'
            #     )
            # # Let's set mitigation as active so we don't get followup messages for each hit after threshold till hour resets
            # mitigated_urls[line["request"]]["Active"] = True
            # mitigated_urls[line["request"]]["Start"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # mitigated_urls[line["request"]]["Stop"] = None
        # This will check and prune old hours or days stats when day roll's over and next line iteration hits this.
        purge_old_stats()

        active_mitigations = [x for x in mitigated_urls.keys() if mitigated_urls[x]["Active"]]
        inactive_mitigations = [x for x in mitigated_urls.keys() if not mitigated_urls[x]["Active"]]
        print()
        print('Active Mitigations:')
        for url in active_mitigations:
            green(f'Url: {url} active since: {mitigated_urls[url]["Start"]}')
        print('============================================================')
        print('Previously active Mitigations:')
        for url in inactive_mitigations:
            yellow(f'Url: {url} last active : {mitigated_urls[url]["Stop"]}')
        print('============================================================')
        print()
        print('Checking if active mitigations should be disabled')
        for url in active_mitigations:
            green(f'Url: {url} active since: {mitigated_urls[url]["Start"]}')
            # Lets disable previously active mitigations after .5 hrs aka 30 mins if not already set with a Stop time
            if check_date_past_interval(mitigated_urls[url]["Start"], .5) and mitigated_urls[url]["Stop"] is None:
                message = f'Disabling mitigation for: {url} due to expiration.'
                yellow(message)
                if cloudflare_auto_mitigation is True and x_auth_key is not None:
                    # Let's only try to disable something we have a rule for.
                    if mitigated_urls[url]["FirewallID"]:
                        cf_response = cloudflare_toggle_mitigation_for_uri(url, 'log', paused=True,
                                                                           id=mitigated_urls[url]["FirewallID"])
                        message = message + str(cf_response)
                mitigated_urls[line["request"]]["Active"] = False
                mitigated_urls[url]["Stop"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print()
                post_message_to_slack_webhook(message)
                print('============================================================')
