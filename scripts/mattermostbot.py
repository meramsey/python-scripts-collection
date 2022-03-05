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


mattermost_config_paths = ['.mattermost.cfg',
                           os.path.expanduser('~/.mattermost.cfg'),
                           os.path.expanduser('~/.mattermost/mattermost.cfg')]

mattermost_config_dict = {'mattermost_url': os.getenv('MATTERMOST_URL'),
                          'mattermost_team': os.getenv('MATTERMOST_TEAM'),
                          'mattermost_channel': os.getenv('MATTERMOST_CHANNEL'),
                          'mattermost_token': os.getenv('MATTERMOST_TOKEN'),
                          'mattermost_user_name': os.getenv('MATTERMOST_USERNAME'),
                          'mattermost_webhook_url': os.getenv('MATTERMOST_WEBHOOK_URL'),
                          'profile': 'MATTERMOST'}

"""
To setup config securely:
nano ~/.mattermost.cfg
"""
# Then enter the desired below with your details
"""
[MATTERMOST]
mattermost_url = 
mattermost_team =
mattermost_channel = cicd
mattermost_token = 
mattermost_user_name = 
mattermost_webhook_url = 
"""

# Read config file if it exists and override the above
mattermost_profile = read_configs(mattermost_config_paths, mattermost_config_dict)

mattermost_url = None
mattermost_team = None
mattermost_channel = None
mattermost_token = None
mattermost_user_name = None
mattermost_webhook_url = None

if 'mattermost_url' in mattermost_profile:
    mattermost_url = mattermost_profile['mattermost_url']

if 'mattermost_team' in mattermost_profile:
    mattermost_team = mattermost_profile['mattermost_team']

if 'mattermost_channel' in mattermost_profile:
    mattermost_channel = mattermost_profile['mattermost_channel']

if 'mattermost_token' in mattermost_profile:
    mattermost_token = mattermost_profile['mattermost_token']

if 'mattermost_user_name' in mattermost_profile:
    mattermost_user_name = mattermost_profile['mattermost_user_name']

if 'mattermost_webhook_url' in mattermost_profile:
    mattermost_webhook_url = mattermost_profile['mattermost_webhook_url']


# Some mattermostbot post functions

def post_message_to_mattermost_channel(url, team, text, channel=None, blocks=None):
    if channel is None:
        channel = mattermost_channel
    return requests.post(f'https:/{url}/api/v4/teams/name/{team}/channels/name/{channel}', {
        'token': mattermost_token,
        'channel': channel,
        'text': text,
        'username': mattermost_user_name,
        'blocks': json.dumps(blocks) if blocks else None
    }).json()


def post_file_to_mattermost(text, file_name, file_bytes, channel=None, file_type=None, title=None):
    if channel is None:
        channel = mattermost_channel
    return requests.post(
        'https://mattermost.com/api/files.upload',
        {
            'token': mattermost_token,
            'filename': file_name,
            'channels': channel,
            'filetype': file_type,
            'initial_comment': text,
            'title': title
        },
        files={'file': file_bytes}).json()


def post_message_to_mattermost_webhook(message, webhook_url=None):
    if webhook_url is None:
        webhook_url = mattermost_webhook_url
    mattermost_data = json.dumps({'text': message})
    response = requests.post(
        webhook_url, data=mattermost_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to mattermost returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


def post_message_to_mattermost(message, endpoint=None, blocks=None):
    # Wrapper so posting to mattermost can be done based on populated globals whether using mattermost webhook or channel
    if mattermost_webhook_url is None:
        post_message_to_mattermost_channel(message, endpoint, blocks)

    if mattermost_channel is None and mattermost_token is None:
        post_message_to_mattermost_webhook(message, endpoint)


# post_message_to_mattermost_webhook('Testing devalerts mattermost from python. Ignore me')


def get_remote_file_data(file):
    response = urllib.request.urlopen(file)
    data = response.read()
    filename = response.info().get_filename()
    data_meta = {'data': data, 'filename': filename}

    return data_meta


# https://api.mattermost.com/tools/block-kit-builder
blocks = [{
    "type": "section",
    "text": {
        "type": "mrkdwn",
        "text": ":check: The script has run successfully on the dev."
    }
}]

# print(post_message_to_mattermost("Text shown in popup.", None, blocks))

# print(post_file_to_mattermost(
#     'Check out my text file!',
#     'Hello.txt',
#     'Hello World!'))

mattermost_info = "Howdy, I'm a PythonBot"

# print(post_message_to_mattermost(mattermost_info, 'general'))
# print(post_message_to_mattermost("What is the matter with you!?", None, {}))

image = "https://images.unsplash.com/photo-1495954484750-af469f2f9be5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"
file_info = get_remote_file_data(image)

post_file_to_mattermost('Amazing day at the beach. Check out this photo.', file_info['filename'], file_info['data'])
