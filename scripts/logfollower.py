#!/usr/bin/python3
import sys
import time
import os
import platform
import re

# Get hostname so we know if were live or dev.
machine_nicename = str(platform.node())
print('Machine Nicename: ' + machine_nicename)

if str(platform.node()) == 'cooler.servers.com':
    access_log_name = 'access_log'
    error_log_name = 'error_log'
else:
    access_log_name = 'access.log'
    error_log_name = 'error.log'

####### Begin Config ########
# scripts/logfollower.py
current_script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# Get base directory up one directory from scripts
base_directory = os.path.dirname(current_script_path)

# /home/whmcs/whmcs/logs/access_log or relative path logs/access_log
access_logfile = os.path.join(base_directory, 'logs', access_log_name)
error_logfile = os.path.join(base_directory, 'logs', error_log_name)
# print(current_script_path)
# print(base_directory)
print('Script path: ', current_script_path)
print('Access Log: ', access_logfile)
print('Error Log: ', error_logfile)
####### End Config ########


# Examples:
# 10.10.84.15 - - [17/Aug/2021:10:47:39 -0400] "GET /dl.php?type=i&id=2463613 HTTP/2.0" 200 102031 "https://my.acmecorp.com/viewinvoice.php?id=2463613&view_as_client=1" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36" "-" "-" "-" 0.243 0.243 .

# 176.103.45.63 - - [05/Aug/2021:14:49:45 -0400] "POST /dologin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0" "176.103.45.63" "176.103.45.63" "clientarea.php?incorrect=true" 16.785 0.125 .

# Log format main: 14 groups
"""log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for" "$http_cf_connecting_ip" "$sent_http_location" '
   		      '$request_time $upstream_response_time $pipe';
"""


def field_map(dictseq, name, func):
    for d in dictseq:
        d[name] = func(d[name])
        yield d


# 14 groups
logpats = r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'\[(.*?)\] ' \
          r'"(\S+) ' \
          r'(\S+) ' \
          r'(\S+)" ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+) ' \
          r'(\S+)'

logpat = re.compile(logpats)


def apache_log(lines):
    groups = (logpat.match(line) for line in lines)
    tuples = (g.groups() for g in groups if g)

    # 140.180.132.213 - - [24/Feb/2008:00:08:59 -0600] "GET /ply/ply.html HTTP/1.1" 200 97238
    # colnames = ('host', 'referrer', 'user', 'datetime',
    #             'method', 'request', 'proto', 'status', 'bytes')

    # 176.103.45.63 - - [05/Aug/2021:14:49:45 -0400] "POST /dologin.php HTTP/1.1" 302 5 "-" "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0" "176.103.45.63" "176.103.45.63" "clientarea.php?incorrect=true" 16.785 0.125 .
    colnames = ('remote_addr', 'remote_user', 'time_local', 'method', 'request', 'proto',
                'status', 'body_bytes_sent', 'http_referer', 'http_user_agent', 'http_x_forwarded_for',
                'http_cf_connecting_ip', 'sent_http_location', 'request_time', 'upstream_response_time', 'pipe')

    log = (dict(zip(colnames, t)) for t in tuples)
    log = field_map(log, "status", int)
    log = field_map(log, "body_bytes_sent",
                    lambda s: int(s) if s != '-' else 0)

    return log


def follow(file):
    """generator function that yields new lines in a file
    """
    # seek the end of the file
    file.seek(0, os.SEEK_END)

    # start infinite loop
    while True:
        # read last line of file
        line = file.readline()
        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            continue

        yield line


def tail_file(file):
    """generator function that yields new lines in a file

    :param file:File Path as a string
    :type file: str
    :rtype: collections.Iterable
    """
    seek_end = True
    while True:  # handle moved/truncated files by allowing to reopen
        with open(file) as f:
            if seek_end:  # reopened files must not seek end
                f.seek(0, 2)
            while True:  # line reading loop
                line = f.readline()
                if not line:
                    try:
                        if f.tell() > os.path.getsize(file):
                            # rotation occurred (copytruncate/create)
                            f.close()
                            seek_end = False
                            break
                    except FileNotFoundError:
                        # rotation occurred but new file still not created
                        pass  # wait 1 second and retry
                    time.sleep(1)
                yield line


access_logfile = '/var/log/syslog'

if __name__ == '__main__':
    # logfile = open(access_logfile, "r")
    # logfile = open('/var/log/syslog', "r")
    # loglines = apache_log(follow(logfile))
    # iterate over the generator
    loglines = tail_file(access_logfile)
    for line in loglines:
        print(line)
