import os
from os.path import exists


def ensure_permissions(mode_flags=os.stat.S_IWUSR):
    """decorator to ensure a filename has given permissions.

    If changed, original permissions are restored after the decorated
    modification.
    """

    def decorator(f):
        def modify(filename, *args, **kwargs):
            m = chmod_perms(filename) if exists(filename) else mode_flags
            if not m & mode_flags:
                os.chmod(filename, m | mode_flags)
            try:
                return f(filename, *args, **kwargs)
            finally:
                # restore original permissions
                if not m & mode_flags:
                    os.chmod(filename, m)

        return modify

    return decorator


def chmod_plus_x(file):
    import os
    import stat
    umask = os.umask(0)
    os.umask(umask)
    st = os.stat(file)
    os.chmod(file, st.st_mode | ((stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) & ~umask))


def globs(pathnames, dirpath='.'):
    import glob
    files = []
    for pathname in pathnames:
        files.extend(glob.glob(os.path.join(dirpath, pathname)))
    return files


def touch(filepath: str):
    import pathlib
    pathlib.Path(filepath).touch()


# Creates the directory if no other file or directory with the same path exists
def mkdir_p(path):
    if not os.path.exists(path):
        print('creating directory: ' + path)
        os.makedirs(path)
