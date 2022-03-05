import re


def find_urls_in_string(string):
    # https://www.geeksforgeeks.org/python-check-url-string/
    # findall() has been used
    # with valid conditions for urls in string
    link_regex = re.compile(r"((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", re.DOTALL)
    url = re.findall(link_regex, string)

    return [x[0] for x in url]
