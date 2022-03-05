import io
import sys
import os.path

path = '~/.ssh/id_rsa'

# Expand an initial ~ component
# in the given path
# using os.path.expanduser() method
full_path = os.path.expanduser(path)

# print the path after
# expanding the initial ~ component
# in the given path
print(full_path)

# Open a file: file
file = open(full_path, mode='rb')

# read all lines at once
all_of_it = file.read()

# close the file
file.close()

type(all_of_it)

print(all_of_it)
