# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 14:42:24 2021

@author: liu
"""
from blind_pen_proto import main
from PIL import Image
from pathlib import Path
import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key)] 
    return sorted(l, key = alphanum_key)

for f in Path().resolve().parent.glob('*.png'):
    f.unlink()

main(200)

pngs = []
png_files = []
for f in Path(__file__).resolve().parent.glob('*.png'):
    png_files.append(str(f))
png_files = natural_sort(png_files)

images = []
for f in png_files:
    images.append(Image.open(f))
    Path(f).unlink()
images[0].save('animation.gif', save_all=True, duration=100,
               append_images=images[1:], loop=0)
