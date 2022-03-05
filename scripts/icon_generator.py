import os
import sys
from PIL import Image

# https://pillow.readthedocs.io/en/stable/installation.html#basic-installation

base_icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
linux_icon_sizes = [(128, 128), (256, 256), (512, 512), (1024, 1024)]
mac_icon_sizes = [(128, 128), (256, 256), (512, 512), (1024, 1024)]
image = Image.open('chevron_logo.png')

# Create base icon sizes in src/main/icons/base
for size in base_icon_sizes:
    # print(size[0])
    fileoutname = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "base", str(size[0]) + ".png")
    new_image = image.resize(size)
    new_image.save(fileoutname)
    print('Icon created: ' + fileoutname)

# Create linux icon sizes in src/main/icons/linux
for size in linux_icon_sizes:
    # print(size[0])
    fileoutname = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "linux", str(size[0]) + ".png")
    new_image = image.resize(size)
    new_image.save(fileoutname)
    print('Icon created: ' + fileoutname)

# Create mac icon sizes in src/main/icons/mac
for size in mac_icon_sizes:
    # print(size[0])
    fileoutname = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "mac", str(size[0]) + ".png")
    new_image = image.resize(size)
    new_image.save(fileoutname)
    print('Icon created: ' + fileoutname)

# Create Icon.ico in src/main/icons/Icon.ico
new_logo_ico_filename = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "Icon.ico")
new_logo_ico = image.resize((128, 128))
new_logo_ico.save(new_logo_ico_filename, format="ICO", quality=90)
print('Icon created: ' + new_logo_ico_filename)

