from threading import Thread
from time import sleep

import cv2
import unittest

import numpy as np
import pyautogui
import pydirectinput as pydirectinput
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import as_strided
from scipy.ndimage import gaussian_filter

from main import image_to_matrix, image_weight_by_color, image_recognize_by_color, intersect_colors, image_recognize, \
    image_weight, compare_to_all_samples, apply_filter, img_frombytes, apply_filter_dilation, unsharp_mask, blur


class MyTestCase(unittest.TestCase):

    def unsharp_mask(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        # For details on unsharp masking, see:
        # https://en.wikipedia.org/wiki/Unsharp_masking
        # https://homepages.inf.ed.ac.uk/rbf/HIPR2/unsharp.htm
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    def test_something(self):
        imgs = image_to_matrix("../images/samples/lacobus2.png")
        # tools = pyocr.get_available_tools()
        # langs = tools[0].get_available_languages()
        # digits = tools[0].image_to_string(
        #    Image.open("../images/samples/fullhdlacobus.png"),
        #    lang=langs[0],
        #    builder=pyocr.tesseract.DigitBuilder()
        # )
        # print(digits)

        rec = compare_to_all_samples(imgs, False)
        mat = apply_filter(rec, 100)
        mat = blur(mat, 1)
        c = unsharp_mask(mat, 5, 5, 1)
        # c = apply_filter_dilation(mat, 2)
        img_frombytes(c).show()

    def test_auto(self):
        sleep(5)
        pydirectinput.click(100, 100, duration=2)
        # color = (0, 188, 252)


#
# s = pyautogui.screenshot()
# for x in range(s.width):
#    for y in range(s.height):
#        if s.getpixel((x, y)) == color:
#            pyautogui.click(x, y)  # do something here


if __name__ == 'main':
    unittest.main()
