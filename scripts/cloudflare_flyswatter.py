#!/usr/bin/python3
import sys
import time
import os
import platform
import re
from datetime import date, timedelta
from datetime import datetime
import collections
from collections import defaultdict
import requests as r
import json

try:
    import configparser  # py3
except ImportError:
    import ConfigParser as configparser  # py2

# Define log patterns based on host.
# /etc/nginx/nginx.conf

# 10.10.84.33 - - [17/Aug/2021:12:17:29 -0400] "GET /index.php HTTP/2.0" 200 39117 ":/https/mramsey-whmcs.dev.acmecorp.com/index.php" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
# log_format main '$http_x_forwarded_for - $remote_user [$time_local] "$host" "$request" ' '$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" $request_time';
galadriel_log_pat = (
    r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (\S+) (\S+)" (\S+) (\S+) "(\S+)" "(.*)"'
)

# 176.103.45.63 - - [05/Aug/2021:14:49:45 -0400] "POST /dologin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0" "176.103.45.63" "176.103.45.63" "clientarea.php?incorrect=true" 16.785 0.125 .
# log_format  main  '$remote_addr - $remote_user [$time_local] "$request" ' '$status $body_bytes_sent "$http_referer" ' '"$http_user_agent" "$http_x_forwarded_for" "$http_cf_connecting_ip" "$sent_http_location" ' '$request_time $upstream_response_time $pipe';
live_log_pat = r'(\S+) (\S+) (\S+) \[(.*?)\] "(\S+) (\S+) (\S+)" (\S+) (\S+) "(\S+)" "(.*)" "(\S+)" "(\S+)" "(\S+)"'

# Column name matching

galadriel_log_colnames = (
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
)

live_log_colnames = (
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

# Get hostname so we know if were live or dev.
machine_nicename = str(platform.node())
print("Machine Nicename: " + machine_nicename)

if str(platform.node()) == "wcloud.whattheserver.com":
    access_log_name = "access_log"
    error_log_name = "error_log"
    logpats = galadriel_log_pat
    colnames = galadriel_log_colnames
    zone_identifier = ""
    default_threshold = 10
else:
    access_log_name = "access_log"
    error_log_name = "error_log"
    logpats = live_log_pat
    colnames = live_log_colnames
    zone_identifier = ""
    default_threshold = 1000

####### Begin Config ########
# scripts/access_log_attack_mitigator.py
current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Get base directory up one directory from scripts
base_directory = os.path.dirname(current_script_path)

# /home/whmcs/a2_whmcs/logs/access_log or relative path logs/access_log
access_logfile = os.path.join(base_directory, "logs", access_log_name)
error_logfile = os.path.join(base_directory, "logs", error_log_name)
# print(current_script_path)
# print(base_directory)
print("Script path: ", current_script_path)
print("Access Log: ", access_logfile)
print("Error Log: ", error_logfile)

access_logfile = '/home/whattheserver.com/logs/my.whattheserver.com.access_log'
####### End Config ########

BASE_URL = 'https://api.cloudflare.com/client/v4'


def read_cf_configs(profile=None):
    """ reading the config file for Cloudflare API"""

    # We return all these values
    config = {'email': os.getenv('CF_API_EMAIL'),
              'token': os.getenv('CF_API_KEY'),
              'certtoken': os.getenv('CF_API_CERTKEY'),
              'extras': os.getenv('CF_API_EXTRAS'),
              'base_url': os.getenv('CF_API_URL'),
              'zone_identifier': os.getenv('CF_ZONE_ID'),
              'cloudflare_auto_mitigation': os.getenv('CF_AUTO_MITIGATION'),
              'profile': None}

    # environment variables override config files - so setup first
    if profile is None:
        profile = 'CloudFlare'
    config['profile'] = profile

    # grab values from config files
    cp = configparser.ConfigParser()
    try:
        cp.read([
            '.cloudflare.cfg',
            os.path.expanduser('~/.cloudflare.cfg'),
            os.path.expanduser('~/.cloudflare/cloudflare.cfg')
        ])
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

        for option in ['email', 'token', 'certtoken', 'extras', 'base_url', 'zone_identifier',
                       'cloudflare_auto_mitigation']:
            if option not in config or config[option] is None:
                try:
                    if option == 'extras':
                        config[option] = re.sub(r"\s+", ' ', section.get(option))
                    else:
                        config[option] = re.sub(r"\s+", '', section.get(option))
                    if config[option] == '':
                        config.pop(option)
                except (configparser.NoOptionError, configparser.NoSectionError):
                    pass
                except Exception as e:
                    pass
            # do we have an override for specific calls? (i.e. token.post or email.get etc)
            for method in ['get', 'patch', 'post', 'put', 'delete']:
                option_for_method = option + '.' + method
                try:
                    config[option_for_method] = re.sub(r"\s+", '', section.get(option_for_method))
                    if config[option_for_method] == '':
                        config.pop(option_for_method)
                except (configparser.NoOptionError, configparser.NoSectionError) as e:
                    pass
                except Exception as e:
                    pass

    # do any final cleanup - only needed for extras (which are multiline)
    if 'extras' in config and config['extras'] is not None:
        config['extras'] = config['extras'].strip().split(' ')

    # remove blank entries
    for x in sorted(config.keys()):
        if config[x] is None or config[x] == '':
            try:
                config.pop(x)
            except:
                pass

    return config


"""
To setup config securely:
mkdir -p ~/.cloudflare/
nano ~/.cloudflare/cloudflare.cfg
"""
# Then enter the desired below like outlined:
# https://github.com/cloudflare/python-cloudflare#using-configuration-file-to-store-email-and-keys certtoken and
# extras can be empty as were not using them currently now. zone_identifier is per domain in CF dashboard
"""
[CloudFlare]
email = dev@acmecorp.com
token = 
certtoken = 
extras =
zone_identifier = 93a4bc273437b129212ad6938c5d17b5
cloudflare_auto_mitigation = False
"""

# Read config file if it exists and override the above
cf_profile = read_cf_configs()

if 'email' in cf_profile:
    x_auth_email = cf_profile['email']
else:
    x_auth_email = None
if 'token' in cf_profile:
    x_auth_key = cf_profile['token']
else:
    x_auth_key = None
if 'zone_identifier' in cf_profile:
    zone_identifier = cf_profile['zone_identifier']
else:
    zone_identifier = None
if 'certtoken' in cf_profile:
    certtoken = cf_profile['certtoken']
else:
    certtoken = None
if 'cloudflare_auto_mitigation' in cf_profile:
    cloudflare_auto_mitigation = cf_profile['cloudflare_auto_mitigation']
else:
    # Ensure even if config has no entry we set to False so auto mitigation is not enabled.
    cloudflare_auto_mitigation = False
if 'base_url' in cf_profile:
    base_url = cf_profile['base_url']
else:
    # We must have a base_url value
    base_url = BASE_URL

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


# examples of using colored text
# black("BLACK")
# red("RED")
# green("GREEN")
# yellow("YELLOW")
# blue("BLACK")
# magenta("MAGENTA")
# cyan("CYAN")
# gray("GRAY")


def field_map(dictseq, name, func):
    for d in dictseq:
        d[name] = func(d[name])
        yield d


def keyfunction(k):
    """Create a function which returns the value of a dictionary
    :param k: key
    :type k: (Iterable, None, bool)
    :return: dictionary key's value
    :rtype: dict[value]
    """
    return d[k]


def apache_log(lines):
    """Parse Apache Log Line

    :param lines: Apache Log Lines to parse
    :type lines: Generator[Any, Any, None]
    :return: Returns dictionary of parsed lines
    :rtype: dict
    """
    groups = (logpat.match(line) for line in lines)
    tuples = (g.groups() for g in groups if g)

    log = (dict(zip(colnames, t)) for t in tuples)
    log = field_map(log, "status", int)
    log = field_map(log, "body_bytes_sent", lambda s: int(s) if s != "-" else 0)

    return log


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


def cf_list_firewall_rules_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://api.cloudflare.com/#firewall-rules-list-of-firewall-rules
    url = f"{BASE_URL}/zones/{zone_identifier}/firewall/rules"
    response = r.get(url, headers=headers).text
    json_response_dict = json.loads(str(response))
    # print(json.dumps(filters_json_response_dict, indent=4))
    return json_response_dict


def cf_list_filters_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://developers.cloudflare.com/firewall/api/cf-filters/get/#get-all-filters
    url = f"{BASE_URL}/zones/{zone_identifier}/filters"
    response = r.get(url, headers=headers).text
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

    response = r.post(url, headers=headers, data=payload).text
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
    json_response = r.post(url, data=payload, headers=headers).text
    json_response_dict = json.loads(str(json_response))
    # print(json.dumps(json_response_dict, indent=4))
    return json_response_dict


if __name__ == "__main__":
    # loglines = tail_file(access_logfile)
    loglines = apache_log(tail_file(access_logfile))
    # Setup hit counters
    post_request_hit_count = 0
    get_request_hit_count = 0
    whmcs_cart_hit_count = 0
    whmcs_clientarea_hit_count = 0
    whmcs_dologin_hit_count = 0
    whmcs_failed_login_hit_count = 0
    # iterate over the generator
    for line in loglines:
        day_timeof = datetime.strptime(line["time_local"], "%d/%b/%Y:%H:%M:%S %z")
        day_time = day_timeof.strftime("%d/%b/%Y:%H:%M:%S")
        day_hour = day_timeof.strftime("%d/%b/%Y %H")
        day_of = day_timeof.strftime("%Y-%m-%d")
        if line["method"] == "post":
            post_request_hit_count = post_request_hit_count + 1
        if line["method"] == "get":
            get_request_hit_count = get_request_hit_count + 1
        if "cart.php" in line["request"]:
            whmcs_cart_hit_count = whmcs_cart_hit_count + 1
        if "dologin.php" in line["request"]:
            whmcs_dologin_hit_count = whmcs_dologin_hit_count + 1
        if "clientarea.php" in line["request"]:
            whmcs_clientarea_hit_count = whmcs_clientarea_hit_count + 1
        if "clientarea.php?incorrect=true" in line["request"]:
            whmcs_failed_login_hit_count = whmcs_failed_login_hit_count + 1
        # WIP: Lets add unique keys for things like requests, user_agent, IP and increment counters
        # for item in line.items():
        #     key, value = item
        #     print(key, value)
        #     if hits[day_timeof.strftime("%H")][line[key][value]]:
        #         hits[day_timeof.strftime("%H")][line[key][value]] += 1
        #     else:
        #         hits[day_timeof.strftime("%H")][line[key][value]] = 1

        if hits[day_timeof.strftime("%H")]["uri"][line["request"]]:
            hits[day_timeof.strftime("%H")]["uri"][line["request"]] += 1
        else:
            hits[day_timeof.strftime("%H")]["uri"][line["request"]] = 1

        if hits[day_timeof.strftime("%H")]["user_agent"][line["http_user_agent"]]:
            hits[day_timeof.strftime("%H")]["user_agent"][line["http_user_agent"]] += 1
        else:
            hits[day_timeof.strftime("%H")]["user_agent"][line["http_user_agent"]] = 1

        if hits[day_timeof.strftime("%H")]["remote_addr"][line["remote_addr"]]:
            hits[day_timeof.strftime("%H")]["remote_addr"][line["remote_addr"]] += 1
        else:
            hits[day_timeof.strftime("%H")]["remote_addr"][line["remote_addr"]] = 1

        print("")
        print(f'Top requested uris for {day_hour}')
        print("============================================")
        d = hits[day_timeof.strftime("%H")]["uri"]
        for key in sorted(d, key=keyfunction, reverse=True)[:10]:
            print("  %5d  %s" % (d[key], key))
        print(f"Total hits since {script_start_time}")
        print("  %5d  total hits" % sum(dict.values(d)))
        print("============================================")
        print("")
        print(f'Top user_agents for {day_hour}')
        print("============================================")
        d = hits[day_timeof.strftime("%H")]["user_agent"]
        for key in sorted(d, key=keyfunction, reverse=True)[:10]:
            print("  %5d  %s" % (d[key], key))
        print(f"Total hits since {script_start_time}")
        print("  %5d  total hits" % sum(dict.values(d)))
        print("============================================")
        print("")
        print("WHMCS Cart hitcount => " + str(whmcs_cart_hit_count))
        print("WHMCS Clientarea hitcount => " + str(whmcs_clientarea_hit_count))
        print("WHMCS Dologin hitcount => " + str(whmcs_dologin_hit_count))
        print("===============================================================")

        if hits[day_timeof.strftime("%H")]["uri"][line["request"]] >= default_threshold:
            print(f'Threshold {default_threshold} hit for {line["request"]}')
            # If key does not exist
            if not mitigated_urls[line["request"]]:
                # If not already mitigated aka set to true
                print("Creating key: ", line["request"])
                mitigated_urls[line["request"]]["Active"] = False
            # If key exists lets see if its True indicating
            if not mitigated_urls[line["request"]]["Active"]:
                print("Attack Mitigation not enabled for: ", line["request"])
                # Add url to track in mitigated_urls
                print("Attempting Mitigation for: ", line["request"])
                # Lets only explicitly enable rules if environmental variable is enabled
                if cloudflare_auto_mitigation == True and x_auth_key is not None:
                    print("As cloudflare_auto_mitigation is set to true creating and enabling rule for: ",
                          line["request"])
                    cloudflare_response = cloudflare_toggle_mitigation_for_uri(line["request"], "js_challenge",
                                                                               paused=False)
                else:
                    print("As cloudflare_auto_mitigation is set to false creating but NOT enabling rule for: ",
                          line["request"])
                    if x_auth_key is not None:
                        cloudflare_response = cloudflare_toggle_mitigation_for_uri(line["request"], "js_challenge",
                                                                                   paused=True)
                    else:
                        # Let's ensure that if no API key is set we can skip trying to hit the api which will fail.
                        cloudflare_response = {}
                        cloudflare_response["success"] = False
                # If successfully added
                if cloudflare_response["success"]:
                    # Let's set this uri as actively under mitigation
                    mitigated_urls[line["request"]]["Active"] = True
                    # Record time
                    mitigated_urls[line["request"]]["Start"] = datetime.now()
                    # Record Cloudflare rule id for later use to toggle off
                    mitigated_urls[line["request"]]["FirewallID"] = cloudflare_response["result"][0]["id"]
                    print(
                        f'Mitigation {cloudflare_response["result"][0]["id"]} enabled for attacks against {line["request"]}')
                elif not cloudflare_response["success"]:
                    print(
                        f'Mitigation failed to enable for attacks against {line["request"]} due to {cloudflare_response["errors"]}'
                    )
                else:
                    print(
                        f'Mitigation failed to enable for attacks against {line["request"]} due to Unknown Error condition'
                    )
            elif mitigated_urls[line["request"]]["Active"]:
                print(
                    f'Mitigation already enabled for attacks against {line["request"]} since: {mitigated_urls[line["request"]]["Start"]}'
                )
        # print(str(mitigated_urls[line["request"]]))

        # print("Active Mitigations status")
        # print(json.dumps(cf_list_firewall_rules_by_zone(zone_identifier), indent=4))

