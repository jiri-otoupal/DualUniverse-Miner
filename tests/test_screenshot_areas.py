import unittest

import pygetwindow

from vision import Vision


class MyTestCase(unittest.TestCase):
    def test_areas(self):
        # TODO: pass function that will be called if is too far away and if see ore
        my = pygetwindow.getWindowsWithTitle("DualBot")[0]
        vision = Vision(my, None, None)
        vision.what_is_in_area(vision.get_left_area())


if __name__ == '__main__':
    unittest.main()
