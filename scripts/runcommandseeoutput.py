import ctypes
import os
import pty
import shlex
import subprocess

libc = ctypes.CDLL('libc.so.6')
master, slave = pty.openpty()


def run_command(command):
    my_env = os.environ.copy()
    my_env["TERM"] = 'xterm'
    process = subprocess.Popen(shlex.split(command), preexec_fn=libc.setsid, stdin=slave,
                               stdout=subprocess.PIPE, env=my_env, encoding='utf8')
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    rc = process.poll()
    return rc


# run_command('df -h')
# run_command('tail -5000 /var/log/syslog')
run_command('top')
