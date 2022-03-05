import sys
import os
from glob import glob
from sys import platform

if platform == "linux" or platform == "linux2":
    for temp in glob('/sys/class/thermal/thermal_zone*/temp'):
        print(temp)
        with open(temp, encoding='utf-8') as f:
            temp_value = int(f.read()) / 1000
            print(f'{str(temp_value)}°C')
