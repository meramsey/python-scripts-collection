#!/usr/bin/python3
import sys
import time
from datetime import date, timedelta
from datetime import datetime
import os
import platform
import re
import urllib.request
import requests
import json
import logging

try:
    import configparser  # py3
except ImportError:
    import ConfigParser as configparser  # py2

# # Get hostname so we know if were live or dev.
# machine_nicename = str(platform.node())
# print("Machine Nicename: " + machine_nicename)

####### Begin Config ########
# scripts/tailslack.py
current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Get base directory up one directory from scripts
base_directory = os.path.dirname(current_script_path)

# error_logfile = '/var/opt/rh/rh-php72/log/php-fpm/www-error.log'
# print(current_script_path)
# print(base_directory)

# if "devserver" in str(platform.node()):
#     error_logfile = os.path.join(base_directory, "logs", 'www-error.log')
# else:
#     error_logfile = '/var/opt/rh/rh-php72/log/php-fpm/www-error.log'

logname = 'TailSlackLog'
# print("Script path: ", current_script_path)
# print("Error Log: ", error_logfile)

output_log_path = os.path.join(base_directory, "logs", logname)
logging.basicConfig(filename=output_log_path,
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%M-%d:%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running TailSlackLog!")

logger = logging.getLogger('tailslack')


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

script_start_time = datetime.now()


def red(text):
    print('\033[31m', text, '\033[0m', sep='')


# Some slackbot post functions

def post_message_to_slack_channel(text, channel=None, blocks=None):
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


def post_file_to_slack_channel(text, file_name, file_bytes, channel=None, file_type=None, title=None):
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


def post_file_to_slack_webhook(text, file_name, file_bytes, webhook_url=None, file_type=None, title=None):
    if webhook_url is None:
        webhook_url = slack_webhook_url
    return requests.post(
        slack_webhook_url,
        {
            'filename': file_name,
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


def post_message_to_slack(message, endpoint=None, blocks=None):
    # Wrapper so posting to slack can be done based on populated globals whether using slack webhook or channel with token
    if slack_webhook_url is None:
        post_message_to_slack_channel(message, endpoint, blocks)

    if slack_channel is None and slack_token is None:
        post_message_to_slack_webhook(message, endpoint)


def post_file_to_slack(text, file_name, file_bytes, endpoint=None, file_type=None, title=None):
    # Wrapper so posting to slack can be done based on populated globals whether using slack webhook or channel with token
    if slack_webhook_url is None:
        post_file_to_slack_channel(text, file_name, file_bytes, endpoint, file_type, title)

    if slack_channel is None and slack_token is None:
        # (text, file_name, file_bytes, webhook_url=None, file_type=None, title=None)
        post_file_to_slack_webhook(text, file_name, file_bytes, endpoint, file_type, title)


# post_message_to_slack_webhook('Testing devalerts slack from python. Ignore me')


def get_remote_file_data(file):
    response = urllib.request.urlopen(file)
    data = response.read()
    filename = response.info().get_filename()
    data_meta = {'data': data, 'filename': filename}

    return data_meta


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


ignored_entries = [
    'InvalidArgumentException: Query string must not include a URI fragment in',
    'updateCCDetails',
    'StripeErrorCard',
    # StripeErrorCard: Your card was declined. | Your card does not support this type of purchase. |  An error occurred while processing your card
    'StripeErrorInvalidRequest',
    # You cannot cancel this PaymentIntent because it has a status of succeeded. Only a PaymentIntent with one of the following statuses may be canceled:
]

alert_words = ['fatal', 'error', 'ERROR']

big_text = """add big text here to test
"""
# post_file_to_slack('big_log_entry', 'unnamed.txt', str(big_text).encode(), None, 'text')

if __name__ == "__main__":

    if len(sys.argv) < 2:
        red('Please provide the full path to the error log to tail.')
        exit

    error_logfile = sys.argv[1]
    loglines = tail_file(error_logfile)
    # iterate over the generator
    for line in loglines:
        if any(x in line for x in alert_words):
            if not any(x in line for x in ignored_entries):
                # print ("Found a match")
                print(line)
                if len(line) >= 4000:
                    line = '```' + line + '```'
                    # We can use post file once were using tokens vs webhooks.
                    # post_file_to_slack('big_log_entry', 'unnamed.txt', str(line).encode(), None, 'text')
                post_message_to_slack(line)
