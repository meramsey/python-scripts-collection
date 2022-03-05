#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# import os
# import sys
# import select
# import termios
# import tty
# import pty
# from subprocess import Popen
#
# command = 'bash'
# # command = 'docker run -it --rm centos /bin/bash'.split()
#
# # save original tty setting then set it to raw mode
# old_tty = termios.tcgetattr(sys.stdin)
# tty.setraw(sys.stdin.fileno())
#
# # open pseudo-terminal to interact with subprocess
# master_fd, slave_fd = pty.openpty()
#
# # use os.setsid() make it run in a new process group, or bash job control will not be enabled
# p = Popen(command,
#           preexec_fn=os.setsid,
#           stdin=slave_fd,
#           stdout=slave_fd,
#           stderr=slave_fd,
#           universal_newlines=True)
#
# while p.poll() is None:
#     r, w, e = select.select([sys.stdin, master_fd], [], [])
#     if sys.stdin in r:
#         d = os.read(sys.stdin.fileno(), 10240)
#         os.write(master_fd, d)
#     elif master_fd in r:
#         o = os.read(master_fd, 10240)
#         if o:
#             os.write(sys.stdout.fileno(), o)
#
# # restore tty settings back
# termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
import ctypes
import os
import pty
import subprocess

my_env = os.environ.copy()
my_env["TERM"] = 'xterm'
libc = ctypes.CDLL('libc.so.6')

master, slave = pty.openpty()
p = subprocess.Popen('top', preexec_fn=libc.setsid, stdin=slave, stdout=slave, stderr=slave,
                     encoding='utf8', env=my_env)
os.close(slave)

# ... do stuff here ...

x = os.read(master, 1026)
print(x)
