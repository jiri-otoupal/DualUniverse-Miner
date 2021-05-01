import unittest
from time import sleep

import pyautogui
import pygetwindow

from vision import Vision


class MyTestCase(unittest.TestCase):
    def test_areas(self):
        # TODO: pass function that will be called if is too far away and if see ore
        sleep(3)
        my = pygetwindow.getWindowsWithTitle("DualBot")[0]
        vision = Vision(my, None, None)
        pyautogui.screenshot("left.png", region=vision.get_left_area())
        pyautogui.screenshot("right.png", region=vision.get_right_area())
        pyautogui.screenshot("top.png", region=vision.get_top_area())
        pyautogui.screenshot("bottom.png", region=vision.get_bottom_area())


if __name__ == '__main__':
    unittest.main()
