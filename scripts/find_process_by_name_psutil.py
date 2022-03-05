import os
import signal
from subprocess import Popen

import psutil

process = 'wssh'


def find_procs_by_name(name):
    """Return a list of processes matching 'name'."""
    ls = []
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        if name == p.info['name'] or \
                p.info['exe'] and os.path.basename(p.info['exe']) == name or \
                p.info['cmdline'] and p.info['cmdline'][0] == name:
            print(p)
            psutil.Process.kill(p)
            ls.append(p)

    return ls


# pid = find_procs_by_name(process)[0].pid
# print(find_procs_by_name(process))
# print(str(pid))

# Popen.terminate(pid)
find_procs_by_name(process)
