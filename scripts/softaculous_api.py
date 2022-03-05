import json
import requests

url = 'https://api.softaculous.com/scripts.php?in=json'

json_response = requests.get(url).text
# print(json_response)
json_response_dict = json.loads(str(json_response))
# print(json_response_dict)
# print(json.dumps(json_response_dict, indent=4))

softaculous_scripts = {}

# print(str(json_response_dict.values()))

for scriptid in json_response_dict.values():
    sid = scriptid
    name = scriptid['name']
    softname = scriptid['softname']
    fullname = scriptid['fullname']

    softname_dict = {softname: name}
    if 'conc' in softname:
        softaculous_scripts.update(softname_dict)

print(softaculous_scripts)
print('=============================')

print('=============================')
print(json.dumps(softaculous_scripts, indent=4))

# Write dictionary to json file locally
with open("softaculous.json", "w") as outfile:
    json.dump(softaculous_scripts, outfile)


