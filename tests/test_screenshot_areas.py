import unittest
from time import sleep

import pyautogui
import pygetwindow

from classifier_predict import Classifier
from vision import Vision


class MyTestCase(unittest.TestCase):
    def test_areas(self):
        # TODO: pass function that will be called if is too far away and if see ore
        sleep(3)
        my = pygetwindow.getWindowsWithTitle("Dual Universe")[0]
        vision = Vision(my, None, None)
        pyautogui.screenshot("left.png", region=vision.get_left_area())
        pyautogui.screenshot("right.png", region=vision.get_right_area())
        pyautogui.screenshot("top.png", region=vision.get_top_area())
        pyautogui.screenshot("bottom.png", region=vision.get_bottom_area())
        pyautogui.screenshot("center.png", region=vision.get_center_area())
        classifier = Classifier("../models/ores_pk_v3_aug")
        print(classifier.predict("left.png"))
        print(classifier.predict("right.png"))
        print(classifier.predict("top.png"))
        print(classifier.predict("bottom.png"))
        print(classifier.predict("center.png"))


if __name__ == '__main__':
    unittest.main()
