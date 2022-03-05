import json
import logging
import os
import sys

import requests

mattermost_url = None
mattermost_team = None
mattermost_channel = None
mattermost_token = None
mattermost_engine = None
mattermost_company = None

# try:
#     mattermost_config_dict = {'mattermost_url': os.getenv('MATTERMOST_URL'),
#                               'mattermost_team': os.getenv('MATTERMOST_TEAM'),
#                               'mattermost_channel': os.getenv('MATTERMOST_CHANNEL'),
#                               'mattermost_token': os.getenv('MATTERMOST_TOKEN'),
#                               'mattermost_engine': os.getenv('MATTERMOST_ENGINE'),
#                               'mattermost_company': os.getenv('MATTERMOST_COMPANY')
#                               }
# except:
#     sys.exit("Missing needed MATTERMOST_ env variables")
#
# if os.getenv("MATTERMOST_TOKEN"):
#     mattermost_token = os.getenv("MATTERMOST_TOKEN")
# else:
#     sys.exit("Missing needed MATTERMOST_TOKEN env variable")

current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
logname = "mattermost_alert"
output_log_path = os.path.join(current_script_path, logname)
logging.basicConfig(
    filename=output_log_path,
    filemode="a",
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%M-%d:%H:%M:%S",
    level=logging.DEBUG,
)

logging.info("Running MatterMost Alerts!")

logger = logging.getLogger("matter_most_alerts")


# def matter_most_alert(url, team, channel, token, company, engine, mmfile):
#     logger.info("Enter Mattermost Alert")
#     try:
#         r = requests.get(
#             "https://"
#             + url
#             + "/api/v4/teams/name/"
#             + team
#             + "/channels/name/"
#             + channel,
#             data={},
#             headers={"Authorization": "Bearer " + token},
#             timeout=15,
#             verify=True,
#         )
#         obj = json.loads(r.text)
#         logger.debug(obj)
#         channelID = obj["id"]
#         logger.debug("Channel ID: " + channelID)
#     except requests.ConnectionError as e:
#         logger.error("Error making get request for channel ID")
#         logger.error(r.text)
#     try:
#         files = {"files": open(mmfile, "rb"), "channel_id": ("", channelID)}
#         r2 = requests.post(
#             "https://" + url + "/api/v4/files",
#             data={"channel_id": channelID},
#             files=files,
#             headers={"Authorization": "Bearer " + token},
#             timeout=15,
#             verify=True,
#         )
#         logger.debug(r2)
#     except requests.ConnectionError as e:
#         logger.error("Error posting the file to mattermost")
#         logger.error(r2.text)
#     # File ID of the failed jobs
#     fID = r2.json()["file_infos"][0]["id"]
#     logger.debug("File ID: " + fID)
#     try:
#         message = "@channel a release has completed for "+ company + " on engine: " + engine
#         r3 = requests.post(
#             "https://" + url + "/api/v4/posts",
#             data=json.dumps(
#                 {
#                     "channel_id": channelID,
#                     "message": message,
#                     "file_ids": [
#                         fID,
#                     ],
#                 }
#             ),
#             headers={"Authorization": "Bearer " + token},
#             timeout=15,
#             verify=True,
#         )
#         logger.info("Mattermost alert sent")
#     except requests.ConnectionError as e:
#         logger.error("Error posting to the channel in Mattermost")
#         logger.error(r3.text)
#         logger.error(e)


# try:
#     r = requests.get(
#         "https://"
#         + url
#         + "/api/v4/teams/name/"
#         + team
#         + "/channels/name/"
#         + channel,
#         data={},
#         headers={"Authorization": "Bearer " + token},
#         timeout=15,
#         verify=True,
#     )
#     obj = json.loads(r.text)
#     logger.debug(obj)
#     channelID = obj["id"]
#     logger.debug("Channel ID: " + channelID)
# except requests.ConnectionError as e:
#     print("Error making get request for channel ID")
#
#     try:
#         r3 = requests.post(
#             "https://" + url + "/api/v4/posts",
#             data=json.dumps(
#                 {
#                     "channel_id": channelID,
#                     "message": message,
#                     # "file_ids": [
#                     #     fID,
#                     # ],
#                 }
#             ),
#             headers={"Authorization": "Bearer " + token},
#             timeout=15,
#             verify=True,
#         )


def matter_most_alert(url, team, channel, token, message):
    logger.info("Enter Mattermost Alert")
    try:
        r = requests.get(
            "https://"
            + url
            + "/api/v4/teams/name/"
            + team
            + "/channels/name/"
            + channel,
            data={},
            headers={"Authorization": "Bearer " + token},
            timeout=15,
            verify=True,
        )
        obj = json.loads(r.text)
        logger.debug(obj)
        channelID = obj["id"]
        logger.debug("Channel ID: " + channelID)
    except requests.ConnectionError as e:
        print("Error making get request for channel ID")
        logger.error("Error making get request for channel ID")
        logger.error(r.text)

    try:
        r3 = requests.post(
            "https://" + url + "/api/v4/posts",
            data=json.dumps(
                {
                    "channel_id": channelID,
                    "message": message,
                    # "file_ids": [
                    #     fID,
                    # ],
                }
            ),
            headers={"Authorization": "Bearer " + token},
            timeout=15,
            verify=True,
        )
        logger.info("Mattermost alert sent")
    except requests.ConnectionError as e:
        logger.error("Error posting to the channel in Mattermost")
        logger.error(r3.text)
        logger.error(e)


message = """
@channel a release has completed
###
```
"""

# matter_most_alert(mmurl, mmteam, mmchannel, mmtoken, company, i, MMfile)
