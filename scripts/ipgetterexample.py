# -*- coding: utf-8 -*-
from ipgetter2 import IPGetter


# https://pypi.org/project/ipgetter2/

def my_ip():
    """Get your external IP.

    Returns:
        str: Return your external IP.

    """
    getter = IPGetter()
    return getter.get()


print('Your Current Ipv4: ' + str(my_ip().v4))
print('Your Current Ipv6: ' + str(my_ip().v6))
