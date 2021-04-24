import unittest
import numpy as np

from main import image_to_matrix, image_weight


class MyTestCase(unittest.TestCase):
    def test_something(self):
        img = image_to_matrix("../images/bauxite/d.jpg")
        weight = image_weight(img,img,0)
        pass




if __name__ == '__main__':
    unittest.main()
