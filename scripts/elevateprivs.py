import os
from elevate import elevate  # https://github.com/barneygale/elevate
from sys import platform


def is_root():
    if platform == "linux" or platform == "linux2":
        return os.getuid() == 0
    elif platform == "darwin":
        # OS X
        pass
    elif platform == "win32":
        # Windows...
        from ctypes import windll
        return windll.shell32.IsUserAnAdmin()


print("before ", is_root())
elevate()
print("after ", is_root())
