import unittest

import numpy as np
import pyautogui
import pygetwindow

from classifier_predict import Classifier
from config import ore_list
from vision import Vision


class MyTestCase(unittest.TestCase):
    def test_areas(self):
        # TODO: pass function that will be called if is too far away and if see ore
        my = pygetwindow.getWindowsWithTitle("Dual Universe")[0]
        vision = Vision(my, None, None)
        pyautogui.screenshot("ored.png", region=vision.get_ore_area())
        pyautogui.screenshot("left.png", region=vision.get_left_area(0.0))
        pyautogui.screenshot("right.png", region=vision.get_right_area(0.0))
        pyautogui.screenshot("top.png", region=vision.get_top_area(0.0))
        pyautogui.screenshot("bottom.png", region=vision.get_bottom_area(0.0))
        pyautogui.screenshot("center.png", region=vision.get_center_area())
        classifier = Classifier("../models/ores_a_v4_soft")
        print(classifier.predict("ored.png"))
        print(classifier.predict("left.png"))
        print(classifier.predict("right.png"))
        print(classifier.predict("top.png"))
        print(classifier.predict("bottom.png"))
        print(classifier.predict("center.png"))
        print("Prediction of Warnings")
        print(classifier.predict("../samples/5555.png"))
        print(classifier.predict("../samples/6666.png"))
        print(classifier.predict("../samples/7777.png"))
        print(classifier.predict("../images/warning/out_0_32-1158757324.jpg"))
        print(classifier.predict("../images/warning/out_0_256-407192141.jpg"))

    def test_signal(self):
        my = pygetwindow.getWindowsWithTitle("Dual Universe")[0]
        classifier = Classifier("../models/ores_s_v1_soft")
        vision = Vision(my, classifier, None)
        pyautogui.screenshot("signal.png", region=vision.get_signal_area())
        print(classifier.predict("signal.png"))

    def test_classify_signal_model_terrain(self):
        cs = Classifier("../models/signals_v1_soft")
        print(cs.predict("ored.png"))
        print(cs.predict("right.png"))
        print(cs.predict("tmp.png"))
        print(cs.predict("top.png"))

    def test_realtime(self):
        classifier = Classifier("../models/ores_a_v3_soft")
        my = pygetwindow.getWindowsWithTitle("Dual Universe")[0]
        vision = Vision(my, classifier, None)
        while True:
            circle_index = 0
            for i in range(0, 3):
                center = np.array(vision.what_is_in_area(vision.get_center_area()) + ("center",), dtype=object)
                left = np.array(vision.what_is_in_area(vision.get_left_area(circle_index)) + ("left",), dtype=object)
                right = np.array(vision.what_is_in_area(vision.get_right_area(circle_index)) + ("right",), dtype=object)
                top = np.array(vision.what_is_in_area(vision.get_top_area(circle_index)) + ("top",), dtype=object)
                bottom = np.array(vision.what_is_in_area(vision.get_bottom_area(circle_index)) + ("bottom",),
                                  dtype=object)
                zipped = np.vstack([center, left, right, top, bottom])
                by_confidence = np.flip(zipped[np.argsort(zipped[:, 1])])
                print("Matrix b compare ", by_confidence)
                by_confidence[:, 2] = np.isin(by_confidence[:, 2], ore_list)
                print("Matrix ", by_confidence)
                by_confidence = np.delete(by_confidence, np.where(by_confidence[:, 2] == False)[0], 0)
                print("Screen Prediction took " + classifier.time.__str__() + " s")
                if np.size(by_confidence) > 0:
                    print("Output ", by_confidence[0])
                    break
                circle_index += 0.1

    def test_matrix(self):
        left = np.array(("left", "hematite", 0.8), dtype=object)
        right = np.array(("right", "hematite", 0.8), dtype=object)
        top = np.array(("top", "hematite", 0.8), dtype=object)
        bottom = np.array(("bottom", "terrain", 0.8),
                          dtype=object)
        zipped = np.vstack([left, right, top, bottom])
        by_confidence = np.flip(zipped[np.argsort(zipped[:, 1])])
        print("Matrix b compare ", by_confidence)
        by_confidence[:, 2] = np.isin(by_confidence[:, 2], ore_list)
        print("Matrix ", by_confidence)
        by_confidence = np.delete(by_confidence, np.where(by_confidence[:, 2] == False)[0], 0)
        pass


if __name__ == '__main__':
    unittest.main()
