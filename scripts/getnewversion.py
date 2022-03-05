import re


def get_new_version(version):
    """
    Get new version by bumping only the last digit group in the string.
    Args:
        version (): Version: like 2.7.epic14859_9

    Returns: New version: like 2.7.epic14859_10
    Original credit: https://stackoverflow.com/questions/23820883/incrementing-the-last-digit-in-a-python-string
    """
    new_version = re.sub(r"(\d+)(?!.*\d)", lambda x: str(int(x.group(0)) + 1), version)
    return new_version
