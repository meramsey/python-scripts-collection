import os
import re
import configparser
import requests
import json
import urllib.request


# https://keestalkstech.com/2019/10/simple-python-code-to-send-message-to-slack-channel-without-packages/


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

if 'slack_token' in slack_profile:
    slack_token = slack_profile['slack_token']
else:
    slack_token = None
if 'slack_channel' in slack_profile:
    slack_channel = slack_profile['slack_channel']
else:
    slack_channel = None
if 'slack_icon_emoji' in slack_profile:
    slack_icon_emoji = slack_profile['slack_icon_emoji']
else:
    slack_icon_emoji = None
if 'slack_user_name' in slack_profile:
    slack_user_name = slack_profile['slack_user_name']
else:
    slack_user_name = None
if 'slack_webhook_url' in slack_profile:
    slack_webhook_url = slack_profile['slack_webhook_url']
else:
    slack_webhook_url = None


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


def post_message_to_slack(message, endpoint=None, blocks=None):
    # Wrapper so posting to slack can be done based on populated globals whether using slack webhook or channel
    if slack_webhook_url is None:
        post_message_to_slack_channel(message, endpoint, blocks)

    if slack_channel is None and slack_token is None:
        post_message_to_slack_webhook(message, endpoint)


# post_message_to_slack_webhook('Testing devalerts slack from python. Ignore me')


def get_remote_file_data(file):
    response = urllib.request.urlopen(file)
    data = response.read()
    filename = response.info().get_filename()
    data_meta = {'data': data, 'filename': filename}

    return data_meta


# https://api.slack.com/tools/block-kit-builder
blocks = [{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ":check: The script has run successfully on the dev."
    }
}]

# print(post_message_to_slack("Text shown in popup.", None, blocks))

# print(post_file_to_slack(
#     'Check out my text file!',
#     'Hello.txt',
#     'Hello World!'))

slack_info = "Howdy, I'm a PythonBot"

# print(post_message_to_slack(slack_info, 'general'))
# print(post_message_to_slack("What is the matter with you!?", None, {}))

image = "https://images.unsplash.com/photo-1495954484750-af469f2f9be5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"
file_info = get_remote_file_data(image)

post_file_to_slack('Amazing day at the beach. Check out this photo.', file_info['filename'], file_info['data'])
