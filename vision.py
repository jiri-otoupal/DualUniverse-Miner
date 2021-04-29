import os

import pyautogui


class Vision:
    from classifier_predict import Classifier

    def __init__(self, window, classifier: Classifier):
        self.window = window
        self.classifier = classifier

    def get_center_area(self, window_area, width=45, height=45):
        y, x = window_area.height, window_area.width
        startx = x // 2 - width // 2
        starty = y // 2 - height // 2
        return startx, starty, width, height

    def get_warning_area(self, window_area):
        y, x = window_area.height, window_area.width
        startx = x // 2 - 500 // 2
        starty = y // 1.19 - 50 // 2
        return startx, starty, 500, 55

    def what_is_ahead(self):
        """
        Returns type of ore ahead of player
        """
        image_path = "tmp.png"
        pyautogui.screenshot(image_path, region=self.get_center_area(self.window))
        a, x = self.classifier.predict(image_path)
        os.remove(image_path)
        return a, x

    def too_far_away(self):
        """
        Returns type of ore ahead of player
        """
        image_path = "tmp.png"
        pyautogui.screenshot(image_path, region=self.get_warning_area(self.window))
        a, x = self.classifier.predict(image_path)
        os.remove(image_path)
        return a == "warning" and x > 0.5
