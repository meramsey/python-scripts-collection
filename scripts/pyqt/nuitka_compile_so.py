import os
import shutil

os.system("pip install nuitka")
path = "./"
for root, dirs, files in os.walk(path):
    for file in files:
        if ((file.endswith(".py") and (not ('__init__.py' in file))) and (not 'compile.py' in file)) and (
                not 'main.py' in file):
            os.system("python3 -m nuitka --module " + os.path.join(root, file))
            os.remove(os.path.join(root, file))
            os.rename(file.replace(".py", ".cpython-386_64-linux-gnu.so"),
                      os.path.join(root, file).replace(".py", ".so"))
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".pyi"):
            os.remove(os.path.join(root, file))
for root, dirs, files in os.walk(path):
    for dir in dirs:
        if ('__pycache__' in dir) or ('.build' in dir):
            shutil.rmtree(os.path.join(root, dir))

os.system("pip uninstall nuitka")
