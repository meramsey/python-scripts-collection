#!/usr/bin/python3
import sys
import os
from datetime import datetime
import requests
import json
import re

try:
    import configparser  # py3
except ImportError:
    import ConfigParser as configparser  # py2

####### Begin Config ########
# scripts/accesslog_attack_checker.py
current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Get base directory up one directory from scripts
base_directory = os.path.dirname(current_script_path)

# /home/whmcs/a2_whmcs/logs/access_log or relative path logs/access_log
# access_logfile = os.path.join(base_directory, "logs", access_log_name)
# error_logfile = os.path.join(base_directory, "logs", error_log_name)
# print(current_script_path)
# print(base_directory)
print("Script path: ", current_script_path)
# print("Access Log: ", access_logfile)
# print("Error Log: ", error_logfile)

default_threshold = 10

# Cloudflare API
# x_auth_email = "mike@hackerdise.me"
# x_auth_key = "37f085618e8fc67be803270cc63db8edcf211"
# zone_identifier = "87bb6415abe3df258f6cf9b1fdcf7e70"


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

        for option in ['email', 'token', 'certtoken', 'extras', 'base_url', 'zone_identifier']:
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
if 'base_url' in cf_profile:
    base_url = cf_profile['base_url']
else:
    # We must have a base_url value
    base_url = BASE_URL

# print(dir(cf_profile))

headers = {
    "X-Auth-Email": x_auth_email,
    "X-Auth-Key": x_auth_key,
    "Content-Type": "application/json",
}


def get_headers(x_auth_email, x_auth_key):
    headers = {
        "X-Auth-Email": x_auth_email,
        "X-Auth-Key": x_auth_key,
        "Content-Type": "application/json",
    }
    return headers


def cf_list_firewall_rules_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://api.cloudflare.com/#firewall-rules-list-of-firewall-rules
    filter_url = f"{BASE_URL}/zones/{zone_identifier}/firewall/rules"

    response = requests.get(
        filter_url,
        headers=headers,
    ).text
    json_response_dict = json.loads(str(response))
    # print(json.dumps(filters_json_response_dict, indent=4))
    return json_response_dict


def cf_list_filters_by_zone(zone_identifier):
    # Cloudflare list filters for zoneid
    # https://developers.cloudflare.com/firewall/api/cf-filters/get/#get-all-filters
    filter_url = f"{BASE_URL}/zones/{zone_identifier}/filters"

    response = requests.get(
        filter_url,
        headers=headers,
    ).text
    json_response_dict = json.loads(str(response))
    # print(json.dumps(filters_json_response_dict, indent=4))
    return json_response_dict


def cf_create_filter(uri, expression=None, description=None):
    # Cloudflare create filter for use in firewall rule below
    # https://developers.cloudflare.com/firewall/api/cf-filters/post
    url = f"{BASE_URL}/zones/{zone_identifier}/filters"

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
    # print(payload)
    response = requests.post(url, headers=get_headers(x_auth_email, x_auth_key), data=payload).text
    response_dict = json.loads(str(response))
    # print(json.dumps(response_dict, indent=4))
    return response_dict


def cloudflare_toggle_mitigation_for_uri(uri, action, paused=True, id=None, filter_id=None, description=None, ref=None):
    if description is None:
        description = (
            f'Rule for {uri} created {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        )

    if ref is None:
        ref = "None"

    uri = uri.split("?")[0]
    if filter_id is None:
        filters_json_response_dict = cf_create_filter(uri)
        print(filters_json_response_dict)
        # print(json.dumps(filters_json_response_dict, indent=4))
        filter_id = filters_json_response_dict["result"][0]["id"]

    # https://api.cloudflare.com/#firewall-rules-create-firewall-rules
    url = f"{BASE_URL}/zones/{zone_identifier}/firewall/rules"

    # actions allowed: valid values: block, challenge, js_challenge, allow, log, bypass

    payload = json.dumps([
        {
            "filter": {
                "id": filter_id
            },
            "action": action,
            "description": description,
        }
    ])

    json_response = requests.post(
        url,
        data=payload,
        headers=headers,
    ).text
    # print(json_response)
    json_response_dict = json.loads(str(json_response))
    # print(json_response_dict)
    print(json.dumps(json_response_dict, indent=4))
    return json_response_dict


# print(cf_list_filters())
print(cf_create_filter("/coolio2.php"))
# print(cf_list_filters_by_zone(zone_identifier))
# print(cloudflare_toggle_mitigation_for_uri("/cake8.php?incorrect=true", 'js_challenge', paused=True, id=None,
#                                            filter_id=None))
# print(json.dumps(cf_list_firewall_rules_by_zone(zone_identifier), indent=4))
