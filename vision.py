import logging
import os
from threading import Thread

import numpy as np
import pyautogui

import controller
from config import ore_list, rotation_angle, forward_time


class Vision:
    from classifier_predict import Classifier

    from ControlDispatcher import ControlDispatcher

    def __init__(self, window, classifier: Classifier, dispatcher: ControlDispatcher):
        self.window = window
        self.classifier = classifier
        self.dispatcher = dispatcher
        self.too_f_away_counter = 0
        self.angle_sum = 0
        self.angle_down = 0

    def start(self):
        Thread(target=self._recognize_in_loop_center, daemon=True).start()

    def _rotate_camera_left(self):
        self.dispatcher.request_rotate(lambda: controller.LookLeft(rotation_angle))
        self.angle_sum -= rotation_angle

    def _rotate_camera_right(self):
        self.dispatcher.request_rotate(lambda: controller.LookRight(rotation_angle))
        self.angle_sum += rotation_angle

    def _recognize_in_loop_center(self):
        while not self.dispatcher.stopped:
            warning_tfa = self.too_far_away()
            ore_type, confidence = self.what_is_in_area()
            logging.info("Ahead of me is " + ore_type)
            is_ore = ore_type in ore_list
            if is_ore and not warning_tfa:
                logging.info("Requesting Mine of " + ore_type)
                self.dispatcher.request_tool_event(controller.Mine)
                logging.debug("Clearing Movement and Rotation")
                self.dispatcher.clear_movement_rotation()
            elif warning_tfa and self.too_f_away_counter > 3:
                self.too_f_away_counter = 0
                if not self.rotate_to_closest_ore():
                    self.dispatcher.request_rotate(lambda: controller.LookRight(90))
                    logging.debug("Requesting Rotation Right Because none ore was found")
            elif warning_tfa:
                logging.info("Too Far Away ! => Requesting Jump and Movement")
                self.dispatcher.request_jump(controller.Jump)
                self.dispatcher.request_movement(lambda: controller.Forward(forward_time))
            else:
                logging.info("Rotating to closest ore")
                self.too_f_away_counter = 0
                self.rotate_to_closest_ore()

    def rotate_to_closest_ore(self):
        left = np.array(self.what_is_in_area(self.get_left_area()) + ("left",), dtype=object)
        right = np.array(self.what_is_in_area(self.get_right_area()) + ("right",), dtype=object)
        top = np.array(self.what_is_in_area(self.get_top_area()) + ("top",), dtype=object)
        bottom = np.array(self.what_is_in_area(self.get_bottom_area()) + ("bottom",), dtype=object)
        zipped = np.vstack([left, right, top, bottom])
        by_confidence = np.flip(zipped[np.argsort(zipped[:, 1])])
        by_confidence[:, 2] = by_confidence[:, 2] == ore_list
        by_confidence = np.delete(by_confidence, np.where(by_confidence[:, 2] == False)[0], 0)
        if np.size(by_confidence) > 0:
            highest = by_confidence[0]

            logging.info("Highest now: " + highest[0] + " Ore: " + str(highest[2]))

            if highest[0] == "left" and highest[2]:
                logging.info("Requesting Rotation Left")
                self.dispatcher.request_rotate(lambda: controller.LookLeft(rotation_angle))
                self.angle_sum -= 1
                return 2
            elif highest[0] == "right" and highest[2]:
                logging.info("Requesting Rotation Right")
                self.dispatcher.request_rotate(lambda: controller.LookRight(rotation_angle))
                self.angle_sum += 1
                return -2
            elif highest[0] == "top" and highest[2]:
                logging.info("Requesting Rotation Up")
                self.dispatcher.request_rotate(lambda: controller.LookUp(rotation_angle))
                self.angle_sum = 0
                self.angle_down -= 1
                return 1
            elif highest[0] == "bottom" and highest[2]:
                logging.info("Requesting Rotation Down")
                self.dispatcher.request_rotate(lambda: controller.LookDown(rotation_angle))
                self.angle_down += 1
                self.angle_sum = 0
                return -1
        else:
            if abs(self.angle_sum) < 360:
                logging.info("Did not found ore... Rotating Right")
                self.dispatcher.request_rotate(lambda: controller.LookRight(45))
            elif abs(self.angle_down) < 90:
                self.angle_sum = 0
                logging.info("Nothing in X axis trying to rotate Down for ore")
                self.dispatcher.request_rotate(lambda: controller.LookDown(rotation_angle))
                self.angle_down += 1
            else:
                logging.info("Nothing in X axis trying to rotate Up for ore")
                self.dispatcher.request_rotate(lambda: controller.LookUp(180))
                self.angle_down = 0
                self.angle_sum = 0

    def get_center_area(self, width=32, height=32):
        y, x = self.window.height, self.window.width
        startx = x // 2 - width // 2
        starty = y // 2 - height // 2
        return startx, starty, width, height

    def get_left_area(self, width=700):
        startx = 0
        starty = 0
        return startx, starty, width, self.window.height

    def get_right_area(self, width=700):
        startx = self.window.width - width
        starty = 0
        return startx, starty, width, self.window.height

    def get_top_area(self, width=300):
        startx = 300
        starty = 1
        return startx, starty, self.window.width - width, self.window.height / 2 - width

    def get_bottom_area(self, width=300):
        y, x = self.window.height, self.window.width
        startx = x // 2 - 800 // 2
        starty = y // 1.21 - width // 2
        return startx, starty, 800, width

    def get_warning_area(self):
        y, x = self.window.height, self.window.width
        startx = x // 2 - 500 // 2
        starty = y // 1.21 - 50 // 2
        return startx, starty, 500, 45

    def what_is_in_area(self, screen_region=None):
        """
        Returns type of ore ahead of player
        """
        image_path = "tmp.png"
        if screen_region is None:
            screen_region = self.get_center_area()
        pyautogui.screenshot(image_path, region=screen_region)
        ore_type, confidence = self.classifier.predict(image_path)
        os.remove(image_path)
        return ore_type, confidence

    def too_far_away(self):
        """
        Returns type of ore ahead of player
        """
        image_path = "tmp.png"
        pyautogui.screenshot(image_path, region=self.get_warning_area())
        a, x = self.classifier.predict(image_path)
        os.remove(image_path)
        logging.info("In warning area: " + a)
        if a == "warning" and x > 0.5:
            self.too_f_away_counter += 1
            return True
        self.too_f_away_counter = 0
        return False
