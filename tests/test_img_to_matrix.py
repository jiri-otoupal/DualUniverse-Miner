from threading import Thread

import cv2
import unittest

import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from numpy.lib.stride_tricks import as_strided

from main import image_to_matrix, image_weight_by_color, image_recognize_by_color, intersect_colors, image_recognize, \
    image_weight, compare_to_all_samples, apply_filter, img_frombytes, apply_filter_dilation


class MyTestCase(unittest.TestCase):

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
        mat = apply_filter(rec, 25)
        c = apply_filter_dilation(mat, 1)
        img_frombytes(c).show()


if __name__ == 'main':
    unittest.main()
