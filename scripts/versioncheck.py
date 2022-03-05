import requests

current_version = '1.0.18'
# current release version url
current_release_url = 'https://wizardassistant.com/current_release.txt'
try:
    # Parse current release version from url
    response = requests.get(current_release_url)
    current_release = response.text

    print('Current Version: ' + current_version)
    print('Current Release: ' + current_release)

    def versiontuple(v):
        return tuple(map(int, (v.split("."))))

    # Compare versions
    if versiontuple(current_release) > versiontuple(current_version):
        print('New Update Available: ' + current_release)
        update_available = True
    else:
        update_available = False

    print(update_available)
except:
    pass