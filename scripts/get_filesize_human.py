import os
import enum
from pathlib import Path


def get_file_size_in_bytes(file_path):
    """ Get size of file at given path in bytes"""
    size = os.path.getsize(file_path)
    return size


def get_file_size_in_bytes_2(file_path):
    """ Get size of file at given path in bytes"""
    # get statistics of the file
    stat_info = os.stat(file_path)
    # get size of file in bytes
    size = stat_info.st_size
    return size


def get_file_size_in_bytes_3(file_path):
    """ Get size of file at given path in bytes"""
    # get file object
    file_obj = Path(file_path)
    # Get file size from stat object of file
    size = file_obj.stat().st_size
    return size


# Enum for size units
class SIZE_UNIT(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


def convert_unit(size_in_bytes, unit):
    """ Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes / 1024
    elif unit == SIZE_UNIT.MB:
        return size_in_bytes / (1024 * 1024)
    elif unit == SIZE_UNIT.GB:
        return size_in_bytes / (1024 * 1024 * 1024)
    else:
        return size_in_bytes


def get_file_size(file_name, size_type=SIZE_UNIT.BYTES):
    """ Get file in size in given unit like KB, MB or GB"""
    size = os.path.getsize(file_name)
    return convert_unit(size, size_type)


def main():
    print('*** Get file size in bytes using os.path.getsize() ***')
    file_path = '/home/cooluser69/Downloads'
    size = get_file_size_in_bytes(file_path)
    print('File size in bytes : ', size)
    print('*** Get file size in bytes using os.stat().st_size ***')
    # file_path = '/home/cooluser69/Downloads'
    size = get_file_size_in_bytes_2(file_path)
    print('File size in bytes : ', size)
    print('*** Get file size in bytes using pathlib.Path.stat().st_size ***')
    # file_path = '/home/cooluser69/Downloads'
    size = get_file_size_in_bytes_3(file_path)
    print('File size in bytes : ', size)
    print('*** Get file size in human readable format like in KB, MB or GB ***')
    print('Get file size in Kilobyte i.e. KB')
    # file_path = '/home/cooluser69/Downloads'
    # get file size in KB
    size = get_file_size(file_path, SIZE_UNIT.KB)
    print('Size of file is : ', size, 'KB')
    print('Get file size in Megabyte  i.e. MB')
    file_path = '/home/cooluser69/Downloads'
    # get file size in MB
    size = get_file_size(file_path, SIZE_UNIT.MB)
    print('Size of file is : ', size, 'MB')
    print('Get file size in Gigabyte  i.e. GB')
    file_path = '/mnt/8TB_HDD/Catalina.iso'
    # get file size in GB
    size = get_file_size(file_path, SIZE_UNIT.GB)
    print('Size of file is : ', size, 'GB')
    print('*** Check if file exists before checking for the size of a file ***')
    file_name = '/mnt/8TB_HDD/Catalina.iso'
    if os.path.exists(file_name):
        size = get_file_size(file_name)
        print('Size of file in Bytes : ', size)
    else:
        print('File does not exist')


if __name__ == '__main__':
    main()
