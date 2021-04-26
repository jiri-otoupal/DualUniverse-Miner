import struct
import unittest
import numpy as np
from PIL import Image
from pyocr import pyocr
from pytesseract import pytesseract

from main import image_to_matrix, image_weight_by_color, image_recognize_by_color, intersect_colors, image_recognize, \
    image_weight, compare_to_all_samples, apply_filter, img_frombytes, apply_filter_dilation


class MyTestCase(unittest.TestCase):

    def test_something(self):
        imgs = image_to_matrix("../images/samples/fullhdlacobus.png")
        #tools = pyocr.get_available_tools()
        #langs = tools[0].get_available_languages()
        #digits = tools[0].image_to_string(
        #    Image.open("../images/samples/fullhdlacobus.png"),
        #    lang=langs[0],
        #    builder=pyocr.tesseract.DigitBuilder()
        #)
        #print(digits)

        rec = compare_to_all_samples(imgs)
        mat = apply_filter(rec, 25)
        x = apply_filter_dilation(mat,1)
        img_frombytes(mat).show()
        pass


if __name__ == '__main__':
    unittest.main()
