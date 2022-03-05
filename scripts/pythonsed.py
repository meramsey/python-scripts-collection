import re
from os import path
from datetime import date

domain = 'wizardassistant.com'
url = ''  # 'https://wizardassistant.com'
email = 'admin@wizardassistant.com'
email2 = 'sales@wizardassistant.com'
username = 'cooluser666'
clientip = '192.168.10.12'
date_time_input = date.today()
domain_not_provided = 'Domain_not_provided_in_form'


def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


def replace_in_file(file_path, substitutions):
    # Check if file exists
    if not path.exists(file_path):
        print("[FILE NOT FOUND]: " + file_path)
    else:
        # Read in entire file
        with open(file_path, 'r') as content_file:
            content = content_file.read()
            new_content = replace(content, substitutions)

        # Write new content back to file.
        with open(file_path, "w") as file:
            file.write(new_content)
            file.close()

        print(f"[UPDATED]: {file_path}")


def replace_in_file_obj(file_obj, substitutions):
    content = file_obj.read()
    new_content = replace(content, substitutions)
    return new_content


substitutions = {"DomainInputField": domain, "Email1InputField": email, "Email2InputField": email2,
                 "CPUsernameInputField": username, "ClientIPInputField": clientip,
                 "DateTimeInputField": date_time_input, }

file_path = '~/some/file/path'
replace_in_file(file_path, substitutions)

example_replace = {"Pattern": 'replacementvalue', "Pattern2": 'replacementvalue2'}


def replace_line(file_path, pattern, substitute, indent=0):
    # Check if file exists
    if not path.exists(file_path):
        print("[FILE NOT FOUND]: " + file_path)
    else:
        # Read lines in nginx.conf
        with open(file_path, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if pattern in line and indent > 0:
                    lines[i] = f"{' ' * indent}{pattern}{substitute}\n"
                elif pattern in line:
                    lines[i] = f"{pattern}{substitute}\n"

        # Write lines back to file.
        with open(file_path, "w") as file:
            file.writelines(lines)

        print(f"[UPDATED]: {file_path}")
