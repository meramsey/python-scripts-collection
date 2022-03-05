# Python program to find SHA256 hash string of a file
import hashlib

import requests

filename = input("Enter the input file name: ")
sha256_hash = hashlib.sha256()
with open(filename, "rb") as f:
    # Read and update hash string value in blocks of 4K
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
    print(sha256_hash.hexdigest())


def md5_checksum(filepath, url):
    m = hashlib.md5()
    if url is None:
        with open(filepath, 'rb') as fh:
            m = hashlib.md5()
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
