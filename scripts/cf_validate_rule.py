import requests
import json

# Cloudflare API
x_auth_email = ""
x_auth_key = ""
zone_identifier = ""

url = "https://api.cloudflare.com/client/v4/filters/validate-expr"

payload = json.dumps([{
    "expression": '(http.request.uri.path contains "/clientareafake.php?incorrect=true")',
    "description": "/clientareafake.php"
}])

headers = {
    "X-Auth-Email": x_auth_email,
    "X-Auth-Key": x_auth_key,
    "Content-Type": "application/json",
}

response = requests.request("POST", url, headers=headers, data=payload)
filter_url = f"https://api.cloudflare.com/client/v4/zones/{zone_identifier}/filters"
response_create = requests.request("POST", filter_url, headers=headers, data=payload)
print(response.text)
print(response_create.text)
