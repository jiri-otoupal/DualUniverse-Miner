import logging
import os
import random
from shutil import copyfile
from threading import Thread
from time import time, sleep

import numpy as np
import pyautogui
import tensorflow as tf

import controller
from config import ore_list, rotation_angle, forward_time, ore_threshold, circle_index_tempo, circle_index_loop

direction_left = -1
direction_right = 1
direction_top = 2
direction_bottom = -2


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

    def _recognize_in_loop_center(self):
        while not self.dispatcher.stopped:
            if self.dispatcher.tool_control_queue.empty() and self.dispatcher.movement_queue.empty() and self.dispatcher.camera_queue.empty():
                warning_tfa = self.too_far_away()
                ore_type, confidence = self.what_is_in_area()
                logging.info("Ahead of me is " + ore_type + " Confidence " + confidence.__str__())
                is_ore = ore_type in ore_list
                if is_ore and confidence > 0.5 and not warning_tfa:
                    logging.info("Requesting Mine of " + ore_type)
                    self.dispatcher.request_tool_event(lambda: controller.Mine(self.dispatcher))
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

    def train_model_realtime(self):
        data_dir = "selftrain"
        self.dispatcher.request_tool_event(lambda: controller.SwitchToDetector(0.1))
        sleep(3)
        # TODO: Scan area for blue thing
        # TODO: if blue do below
        self._save_area_self_train()
        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            seed=4621301,
            subset="training",
            image_size=(32, 32),
            batch_size=32)

        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            "images",
            validation_split=0.2,
            seed=1231657,
            subset="validation",
            image_size=(32, 32),
            batch_size=32)
        self.classifier.model.fit(train_ds, val_ds, epochs=1)
        self.dispatcher.request_rotate(lambda: controller.LookRight(10))

    def evaluate_area(self):
        circle_index = 0
        by_confidence = None
        for i in range(0, circle_index_loop):
            t0 = time()
            left = np.array(self.what_is_in_area(self.get_left_area(circle_index)) + ("left",), dtype=object)
            right = np.array(self.what_is_in_area(self.get_right_area(circle_index)) + ("right",), dtype=object)
            top = np.array(self.what_is_in_area(self.get_top_area(circle_index)) + ("top",), dtype=object)
            bottom = np.array(self.what_is_in_area(self.get_bottom_area(circle_index)) + ("bottom",),
                              dtype=object)
            zipped = np.vstack([left, right, top, bottom])
            by_confidence = np.flip(zipped[np.argsort(zipped[:, 1])])
            logging.info("Area for Evaluation: \n" + np.array_str(by_confidence))
            by_confidence[:, 2] = np.isin(by_confidence[:, 2], ore_list)
            logging.info("Area Evaluated: \n" + np.array_str(by_confidence))
            by_confidence = np.delete(by_confidence, np.where(by_confidence[:, 2] == False)[0], 0)
            time_took = (time() - t0)
            logging.info("Screen Prediction took " + time_took.__str__() + " s")
            if np.size(by_confidence) > 0:
                logging.info("Output " + np.array_str(by_confidence[0]))
                break
            circle_index += circle_index_tempo
            logging.info("Did not found ore -> decreasing circle")
        return by_confidence

    def request_blind_search(self):
        logging.info("Did not found Closest ore... requesting blind search")
        if abs(self.angle_sum) < 360:
            logging.info("Did not found ore... Rotating Right")
            self.dispatcher.request_rotate(lambda: controller.LookRight(45))
        elif abs(self.angle_down) < 45:
            self.angle_sum = 0
            logging.info("Nothing in X axis trying to rotate Down for ore")
            self.dispatcher.request_rotate(lambda: controller.LookDown(rotation_angle))
            self.angle_down += 1
        else:
            logging.info("Nothing in X axis trying to rotate Up for ore")
            self.dispatcher.request_rotate(lambda: controller.LookUp(90))
            self.angle_down = 0
            self.angle_sum = 0

    def rotate_to_closest_ore(self):
        """
        Will rotate to closest ore
        :return:
        """
        if self.dispatcher.mining:
            logging.info("Currently Mining ignoring requests")
            return
        by_confidence = self.evaluate_area()

        logging.info("Angle on X axis Sum " + self.angle_sum.__str__())
        logging.info("Angle on Y axis Sum " + self.angle_down.__str__())
        if by_confidence is not None and np.size(by_confidence) > 0:
            highest = by_confidence[0]
            logging.info("Best now: " + highest[0] + " Ore: " + str(highest[2]))

            if abs(self.angle_sum) > 30:
                self.angle_sum = 0
                logging.info("Angle in X is higher than 30 -> Reset")

            if highest[0] == "left" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Left")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(controller.LookLeft)
                self.angle_sum -= 1
                return direction_left
            elif highest[0] == "right" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Right")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(controller.LookRight)
                self.angle_sum += 1
                return direction_right
            elif highest[0] == "top" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Up")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(controller.LookUp)
                self.angle_sum = 0
                self.angle_down -= 1
                return direction_top
            elif highest[0] == "bottom" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Down")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(controller.LookDown)
                self.angle_down += 1
                self.angle_sum = 0
                return direction_bottom
        else:
            self.request_blind_search()

    def get_center_area(self, width=32, height=32):
        xcenter = self.window.width / 2
        ycenter = self.window.height / 2
        x = xcenter - (width / 2)
        y = ycenter - (height / 2)
        return x, y, width, height

    def get_left_area(self, circle_index=0):
        """

        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * (0.01 + circle_index)
        starty = 0
        return startx, starty, self.window.width * (0.4 - circle_index), self.window.height

    def get_right_area(self, circle_index=0):
        """

        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * (0.6 + circle_index)
        starty = 0
        return startx, starty, self.window.width * (0.35 - circle_index), self.window.height

    def get_top_area(self, circle_index=0):
        """
        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * 0.35
        starty = 1 + self.window.height * circle_index
        return startx, starty, self.window.width - (self.window.width * 0.35 * 2), self.window.height * (
                0.35 - circle_index)

    def get_bottom_area(self, circle_index=0):
        """
        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * 0.35
        starty = self.window.height // 1.23 - self.window.height * (0.36 - circle_index)
        return startx, starty, self.window.width - (self.window.width * 0.35 * 2), self.window.height * (
                0.38 - circle_index)

    def get_warning_area(self):
        y, x = self.window.height, self.window.width
        startx = x // 2 - self.window.width * 0.47 // 2
        starty = y // 1.21 - 50 // 2
        return startx, starty, self.window.height * 0.26, 45

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

    def _save_area_self_train(self, screen_region=None, path="selftrain/terrain"):
        """
        Returns type of ore ahead of player
        """
        if not os.path.exists(path):
            os.mkdir(path)
        img = random.randint(0, 999999999).__str__() + "-self_train.jpg"
        image_path = path + "/" + img
        if screen_region is None:
            screen_region = self.get_center_area()
        pyautogui.screenshot(image_path, region=screen_region)
        copyfile(path, "images/terrain/" + img)

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
