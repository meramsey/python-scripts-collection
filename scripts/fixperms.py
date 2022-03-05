import os
import shutil

my_path = os.path.expanduser('~/test_chmod_folder')


# https://docs.python.org/3/library/shutil.html
def recursive_chown(path, owner):
    for dirpath, dirnames, filenames in os.walk(path):
        try:
            shutil.chown(dirpath, owner)
        except PermissionError:
            print('Could not change permissions for: ' + dirpath + ' to: ' + owner)
            pass
        for filename in filenames:
            try:
                shutil.chown(os.path.join(dirpath, filename), owner)
            except PermissionError:
                print('Could not change permissions for: ' + os.path.join(dirpath, filename) + ' to: ' + owner)
                pass


# https://docs.python.org/3.6/library/os.html#os.walk
# Defaults to chmod top level directory but can be optionaly toggled off when you want to chmod only contents of like a user's homedir vs homedir itself
def recursive_permissions(path, dir_mode=0o755, file_mode=0o644, topdir=True):
    if topdir:
        # Set chmod on top level path
        try:
            os.chmod(path, dir_mode)
        except:
            print('Could not chmod :' + path + ' to ' + str(dir_mode))
    for root, dirs, files in os.walk(path):
        for d in dirs:
            try:
                os.chmod(os.path.join(root, d), dir_mode)
            except:
                print('Could not chmod :' + os.path.join(root, d) + ' to ' + str(dir_mode))
                pass
        for f in files:
            try:
                os.chmod(os.path.join(root, f), file_mode)
            except:
                print('Could not chmod :' + path + ' to ' + str(file_mode))
                pass


recursive_chown(my_path, 'root')

# explicitly set permissions for directories/folders to 0755 and files to 0644
# recursive_permissions(my_path, 0o755, 0o644)

# Fix permissions and use default values
recursive_permissions(my_path)
