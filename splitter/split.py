import os
from itertools import product
from random import randint

import cv2
from PIL import Image


def tile(filename, dir_in, dir_out, d):
    name, ext = os.path.splitext(filename)
    img = Image.open(os.path.join(dir_in, filename))
    img = img.convert("RGB")
    w, h = img.size
    ran = randint(0, 999999999)

    grid = list(product(range(0, h - h % d, d), range(0, w - w % d, d)))
    for i, j in grid:
        box = (j, i, j + d, i + d)
        out = os.path.join(dir_out, f'{name}_{i}_{j}{ran}.jpg')
        img.crop(box).save(out)


tile("terrain.png", "", "", 32)
os.remove("terrain.png")

for imgy in os.listdir("."):
    img = cv2.imread(imgy, cv2.IMREAD_GRAYSCALE)
    if img is None:
        continue
    h, w = img.shape
    if (not (h == 32 and w == 32)):
        os.remove(imgy)
