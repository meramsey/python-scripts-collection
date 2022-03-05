import re
from datetime import date

from urllib.parse import urlparse
from urllib.parse import urlsplit


# url = "http://python.org"
# domain = urlsplit(url)[1].split(':')[0]
# print("The domain name of the url is: ", domain)


def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


# domain = self.domaininput.text()
# url = self.urlinput.text()
# email = self.emailinput.text()
# email2 = self.emailinput2.text()
# username = self.usernameinput.text()
# clientip = self.clientipinput.text()
# date_time_input = self.dateTimeinput.text()

# domain = 'wizardassistant.com'
url = ''  # 'https://wizardassistant.com'
email = 'admin@wizardassistant.com'
email2 = 'sales@wizardassistant.com'
username = 'cooluser666'
clientip = '192.168.10.12'
date_time_input = date.today()
domain_not_provided = 'Domain_not_provided_in_form'

try:
    x = ''  # 'wizardassistant.app'
    y = email.split("@")[1].lower() if bool(email) is not False else print('No email was provided')
    z = urlsplit(url)[1].split(':')[0] if bool(url) is not False else print('No url was provided')
except:
    NameError
pass

domain = ''

domain = x if bool(x) is not False else y if bool(y) is not False else z if bool(
    z) is not False else domain_not_provided

# print(domain)

# DomainInputField
# Email1InputField
# Email2InputField
# CPUsernameInputField
# ClientIPInputField
# DateTimeInputField

substitutions = {"DomainInputField": domain, "Email1InputField": email, "Email2InputField": email2,
                 "CPUsernameInputField": username, "ClientIPInputField": clientip,
                 "DateTimeInputField": date_time_input, }

string = """Username='CPUsernameInputField'; USER_HOME=$(eval echo ~${Username}) ; sudo grep --color -r --include=\*.php '[.*].*[.*].*eval(\|@include.*\/\\.*\/\\\|base64_decode($_POST' $USER_HOME ; echo "Checking for hidden .ico files with base64 includes"; sudo grep -Er --color --include=\*.ico 'basename|rawurldecode' $USER_HOME ;"""
# substitutions = {"foo": "FOO", "bar": "BAR"}
output = replace(string, substitutions)
print('Before')
print(string)
print('After')
print(output)
