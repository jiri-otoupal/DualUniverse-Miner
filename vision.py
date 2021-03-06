import datetime
import logging
import os
import random
from shutil import copyfile
from threading import Thread
from time import time, sleep
from typing import Tuple

import numpy as np
import pyautogui

import controller
from config import (
    ore_list,
    rotation_angle,
    forward_time,
    ore_threshold,
    circle_index_tempo,
    circle_index_loop,
    failsafe_timeout,
    machine_learning,
)
from self_train import SelfTrain

direction_left = -1
direction_right = 1
direction_top = 2
direction_bottom = -2


class Vision:
    from classifier_predict import Classifier

    from control_dispatcher import ControlDispatcher

    def __init__(self, window, classifier: Classifier, dispatcher: ControlDispatcher):
        self.window = window
        self.classifier = classifier
        self.dispatcher = dispatcher
        self.too_f_away_counter = 0
        self.angle_sum = 0
        self.angle_down = 0
        self.mined = 0
        self.sum_mined = 0
        self.last_scan = datetime.datetime.now()
        self.learn_client = SelfTrain(classifier)

    def start(self):
        thread = Thread(target=self._recognize_in_loop_center)
        thread.start()
        return thread

    def fail_safe(self):
        if self.angle_down > 0:
            self.angle_down = -1
            self.dispatcher.request_rotate(
                lambda: controller.LookUp(self.dispatcher, 30)
            )
        else:
            self.angle_down = 1
            self.dispatcher.request_rotate(
                lambda: controller.LookDown(self.dispatcher, 30)
            )
        for _ in range(0, random.randint(1, 10)):
            self.dispatcher.request_jump(lambda: controller.Jump(self.dispatcher))
            self.dispatcher.request_movement(lambda: controller.Forward(forward_time))
        self.mined = 0

    def _recognize_in_loop_center(self):
        while not self.dispatcher.stopped:
            while (
                    not (
                            self.dispatcher.tool_control_queue.empty()
                            and self.dispatcher.movement_queue.empty()
                            and self.dispatcher.camera_queue.empty()
                            and not self.dispatcher.mr_undergoing
                    )
                    and not self.dispatcher.stopped
            ):
                logging.info("Waiting for Clearing Request Queue")
                sleep(0.1)

            if self.mined > failsafe_timeout:
                self.fail_safe()
            logging.info(
                "Failsafe Activation at "
                + (self.mined / failsafe_timeout * 100).__str__()
                + " %"
            )
            warning_tfa = self.too_far_away()
            surf_type, confidence = self.what_is_in_area()
            logging.info(
                "Ahead of me is " + surf_type + " Confidence " + confidence.__str__()
            )
            is_ore = surf_type in ore_list
            if is_ore and not warning_tfa:
                logging.info("Requesting Mine of " + surf_type)
                self.dispatcher.request_tool_event(
                    lambda: controller.Mine(self.dispatcher)
                )
                logging.debug("Clearing Movement and Rotation")
                self.dispatcher.clear_movement_rotation()
                self.mined = 0
                self.sum_mined += random.randint(5, 58)
                if (
                        datetime.timedelta(
                            self.last_scan.second, datetime.datetime.now().second
                        ).seconds
                        > 3
                        and machine_learning
                        and confidence < 0.8
                        and any(map(surf_type.__contains__, ["ore", "terrain"]))
                ):
                    self.last_scan = datetime.datetime.now()
                    # Need to make timeout scanning too often
                    _surf_type, _confidence = self.classifier.predict("tmp.png", True)
                    if _surf_type is not None:
                        surf_type = _surf_type
                    logging.info("Sampling not confident surface")
                    self.dispatcher.clear_movement_rotation()
                    self.dispatcher.tool_control_queue.get()
                    self.dispatcher.request_tool_event(
                        lambda: controller.SwitchToDetector(0.1)
                    )
                    while not self.dispatcher.tool_control_queue.empty():
                        sleep(0.1)
                    self.dispatcher.block = True
                    sleep(3)
                    verify_is_ore = self.is_it_ore()
                    self.learn_client.gather_sample(surf_type, "tmp.png")
                    self.dispatcher.block = False
                    self.dispatcher.request_tool_event(
                        lambda: controller.SwitchToMining(0.05)
                    )

            elif warning_tfa and self.too_f_away_counter > 1:
                if not self.rotate_to_closest_ore():
                    logging.info("Too Far Away ! => Requesting Jump and Movement")
                    self.dispatcher.request_jump(
                        lambda: controller.Jump(self.dispatcher)
                    )
                    self.dispatcher.request_movement(
                        lambda: controller.Forward(forward_time + random.randint(0, 5))
                    )
            elif warning_tfa:

                logging.info("Too Far Away ! => Requesting Movement")
                self.dispatcher.request_movement(
                    lambda: controller.Forward(forward_time)
                )
            else:
                self.too_f_away_counter = 0
                logging.info("Rotating to closest ore")
                self.rotate_to_closest_ore()
            self.mined += 1

            logging.info(
                "$$$ Mined so far "
                + (self.sum_mined * 25 * 1.3 / 1000000).__str__()
                + " USD"
            )

    def evaluate_area(self):
        circle_index = 0
        by_confidence = None
        for i in range(0, circle_index_loop):
            t0 = time()
            left = np.array(
                self.what_is_in_area(self.get_left_area(circle_index)) + ("left",),
                dtype=object,
            )
            right = np.array(
                self.what_is_in_area(self.get_right_area(circle_index)) + ("right",),
                dtype=object,
            )
            top = np.array(
                self.what_is_in_area(self.get_top_area(circle_index)) + ("top",),
                dtype=object,
            )
            bottom = np.array(
                self.what_is_in_area(self.get_bottom_area(circle_index)) + ("bottom",),
                dtype=object,
            )
            zipped = np.vstack([left, right, top, bottom])
            by_confidence = np.flip(zipped[np.argsort(zipped[:, 1])])
            logging.info("Area for Evaluation: \n" + np.array_str(by_confidence))
            by_confidence[:, 2] = np.isin(by_confidence[:, 2], ore_list)
            logging.info("Area Evaluated: \n" + np.array_str(by_confidence))
            by_confidence = np.delete(
                by_confidence, np.where(by_confidence[:, 2] == False)[0], 0
            )
            time_took = time() - t0
            logging.info("Screen Prediction took " + time_took.__str__() + " s")
            if np.size(by_confidence) > 0:
                logging.info("Output " + np.array_str(by_confidence[0]))
                break
            circle_index += circle_index_tempo
            logging.info("Did not found ore -> decreasing circle")
        return by_confidence, (circle_index + 1) * 10

    def request_blind_search(self):
        logging.info("Did not found Closest ore... requesting blind search")
        if abs(self.angle_sum) < 360:
            logging.info("Did not found ore... Rotating Right")
            self.dispatcher.request_rotate(
                lambda: controller.LookRight(self.dispatcher, 45)
            )
        elif abs(self.angle_down) < 45:
            self.angle_sum = 0
            logging.info("Nothing in X axis trying to rotate Down for ore")
            self.dispatcher.request_rotate(
                lambda: controller.LookDown(self.dispatcher, rotation_angle)
            )
            self.angle_down += 1
        else:
            logging.info("Nothing in X axis trying to rotate Up for ore")
            self.dispatcher.request_rotate(
                lambda: controller.LookUp(self.dispatcher, 90)
            )
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
        by_confidence, circle_index = self.evaluate_area()

        logging.info("Angle on X axis Sum " + self.angle_sum.__str__())
        logging.info("Angle on Y axis Sum " + self.angle_down.__str__())
        if by_confidence is not None and np.size(by_confidence) > 0:
            highest = by_confidence[0]
            logging.info("Best now: " + highest[0] + " Ore: " + str(highest[2]))

            if abs(self.angle_sum) > 30:
                self.angle_sum = 0
                logging.info("Angle in X is higher than 30 -> Reset")
            elif abs(self.angle_down) > 90:
                self.angle_down = 0
                if self.angle_down > 0:
                    self.dispatcher.request_rotate(
                        lambda: controller.LookUp(self.dispatcher, 30)
                    )
                else:
                    self.dispatcher.request_rotate(
                        lambda: controller.LookDown(self.dispatcher, 30)
                    )

            if highest[0] == "left" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Left")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(
                    lambda: controller.LookLeft(
                        self.dispatcher, rotation_angle * circle_index
                    )
                )
                self.angle_sum -= 1
                return direction_left
            elif highest[0] == "right" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Right")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(
                    lambda: controller.LookRight(
                        self.dispatcher, rotation_angle * circle_index
                    )
                )
                self.angle_sum += 1
                return direction_right
            elif highest[0] == "top" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Up")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(
                    lambda: controller.LookUp(
                        self.dispatcher, rotation_angle * circle_index
                    )
                )
                self.angle_sum = 0
                self.angle_down -= 1
                return direction_top
            elif highest[0] == "bottom" and highest[2] and highest[1] > ore_threshold:
                logging.info("Requesting Rotation Down")
                self.dispatcher.clear_movement_rotation()
                self.dispatcher.request_rotate(
                    lambda: controller.LookDown(
                        self.dispatcher, rotation_angle * circle_index
                    )
                )
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
        return (
            startx,
            starty,
            self.window.width * (0.4 - circle_index),
            self.window.height,
        )

    def get_right_area(self, circle_index=0):
        """

        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * (0.6 + circle_index)
        starty = 0
        return (
            startx,
            starty,
            self.window.width * (0.35 - circle_index),
            self.window.height,
        )

    def get_top_area(self, circle_index=0):
        """
        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * 0.35
        starty = 1 + self.window.height * circle_index
        return (
            startx,
            starty,
            self.window.width - (self.window.width * 0.35 * 2),
            self.window.height * (0.35 - circle_index),
        )

    def get_bottom_area(self, circle_index=0):
        """
        :param circle_index: 0 - 0.3
        :return:
        """
        startx = self.window.width * 0.35
        starty = self.window.height // 1.23 - self.window.height * (0.36 - circle_index)
        return (
            startx,
            starty,
            self.window.width - (self.window.width * 0.35 * 2),
            self.window.height * (0.38 - circle_index),
        )

    def get_ore_area(self):
        startx = self.window.width * 0.5
        starty = self.window.height - self.window.height * 0.375
        return startx, starty, 32, self.window.height * (0.15)

    def get_warning_area(self):
        y, x = self.window.height, self.window.width
        startx = x // 2 - self.window.width * 0.47 // 2
        starty = y // 1.21 - 50 // 2
        return startx, starty, self.window.height * 0.26, 45

    def get_signal_area(self):
        y, x = self.window.height, self.window.width
        startx = x // 2 - self.window.width * 0.01 // 2
        starty = y // 1.57
        return startx, starty, self.window.height * 0.1, 150

    def what_is_in_area(self, screen_region=None) -> Tuple[str, float]:
        """
        Returns type of ore ahead of player
        """
        image_path = "tmp.png"
        if os.path.isfile(image_path):
            os.remove(image_path)
        if screen_region is None:
            screen_region = self.get_center_area()
        pyautogui.screenshot(image_path, region=screen_region)
        ore_type, confidence = self.classifier.predict(image_path)
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

    def is_it_ore(self):
        """
        Returns if surface contains ore from detector *used for machine learning*
        """
        image_path = "tmp_sig.png"
        pyautogui.screenshot(image_path, region=self.get_signal_area())
        a, x = self.classifier.predict(image_path)
        os.remove(image_path)
        return a == "signal"

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
