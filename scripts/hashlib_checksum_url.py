import hashlib
import os
import pathlib
import sys

import requests

# current release version url
current_release_url = 'https://somedomain.here/current_release.txt'
current_release_notes_url = 'https://somedomain.here/current_release_notes.txt'

# current database release  version url
current_db_release_url = 'https://somedomain.here/current_db_release.txt'
current_db_release_notes_url = 'https://somedomain.here/current_db_release_notes.txt'
current_db_release_notes_hash_url = 'https://somedomain.here/current_db_release_hash.txt'
current_db_release = ''
wizard_db_version = ''

# Default commands DB url
wizard_cmd_db_url = 'https://somedomain.here/sqlite.db'

wizard_cmd_db = 'some/path'

checksum_local = ''
checksum_remote = ''
checksum_remote_hash = ''
checksum_status = ''


def download_cmd_db():
    try:
        print('Downloading database update version: ' + str(current_db_release))
        url = wizard_cmd_db_url
        r = requests.get(url)
        with open(wizard_cmd_db, 'wb') as f:
            f.write(r.content)

        # Retrieve HTTP meta-data
        print(r.status_code)
        # print(r.headers['content-type'])
        # print(r.encoding)
        # settings.setValue('wizard_db_version', current_db_release)
        print('Database downloaded to:' + str(wizard_cmd_db))
    except:
        print('Commands Database download failed.... ;( ')


def sha256_checksum(filepath, url):
    m = hashlib.sha256()
    if url is None:
        with open(filepath, 'rb') as fh:
            m = hashlib.sha256()
            while True:
                data = fh.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()
    else:
        r = requests.get(url)
        for data in r.iter_content(8192):
            m.update(data)
        return m.hexdigest()


def wizard_db_hash_check():
    global checksum_local, checksum_remote, checksum_status
    try:
        checksum_local = sha256_checksum(wizard_cmd_db, None)
        checksum_remote = sha256_checksum(None, wizard_cmd_db_url)
        print("checksum_local : " + checksum_local)
        print("checksum_remote: " + checksum_remote)
        print("checksum_remote_hash: " + checksum_remote_hash)

        if checksum_local == checksum_remote_hash:
            print('Hash Check passed')
            checksum_status = True
        else:
            print('Hash Check Failed')
            checksum_status = False
    except:
        print('Could not perform wizard_db_hash_check')


# Sanity check for missing database file
file = pathlib.Path(wizard_cmd_db)
if file.exists():
    print("DB File exists: " + wizard_cmd_db)
    wizard_db_hash_check()
else:
    print("DB File does NOT exist: " + wizard_cmd_db)
    download_cmd_db()
    wizard_db_hash_check()

# Check hash

# # Logic to decide when to download DB here
try:
    if int(current_db_release) > int(wizard_db_version):
        print('Database update available: ' + str(current_db_release))
        download_cmd_db()
        wizard_db_hash_check()
except:
    print('Unable to check wizard_db_release')

if checksum_local != checksum_remote:
    download_cmd_db()
    wizard_db_hash_check()

# Logic to fallback to default packaged DB if no internet to download and compare hash
if checksum_status is True:
    target_db = str(wizard_cmd_db)
else:
    print('All hash checks and attempts to update commands DB have failed. Switching to bundled DB')
    target_db = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "sqlite.db")

print('Sanity Checks completed')
