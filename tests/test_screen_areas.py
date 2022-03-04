import unittest

import pyautogui


class ScreenTests(unittest.TestCase):
    def test_signal_area(self):
        pyautogui.screenshot("signal.png", region=vision.get_signal_area())


if __name__ == '__main__':
    unittest.main()
