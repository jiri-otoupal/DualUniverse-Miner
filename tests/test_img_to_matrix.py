import struct
import unittest
import numpy as np

from main import image_to_matrix, image_weight_by_color, image_recognize_by_color, intersect_colors, image_recognize, \
    image_weight, compare_to_all_samples, apply_filter, img_frombytes, apply_filter_dilation


class MyTestCase(unittest.TestCase):

    def test_something(self):
        imgs = image_to_matrix("../images/samples/fullhdlacobus.png")
        rec = compare_to_all_samples(imgs)
        mat = apply_filter(rec, 11)
        x = apply_filter_dilation(mat,1)
        img_frombytes(x).show()
        pass


if __name__ == '__main__':
    unittest.main()
