"""

Dual Universe Bot


Copyright Jiri Otoupal, Dominik Deak

c 2021

"""

import logging
import os
import sys

import pyautogui
import pygetwindow
from rich.console import Console
from silence_tensorflow import silence_tensorflow

from logger import config_logger

"""
Config

"""

model_to_use = "ores"


def get_center_area(window_area, width=500, height=500):
    y, x = window_area.top, window_area.left
    startx = x // 2 - width // 2
    starty = y // 2 - height // 2
    return startx, starty, width, height


def get_warning_area(window_area):
    y, x = window_area.top, window_area.left
    startx = x // 2 - 500 // 2
    return startx, 720, 500, 50


if __name__ == '__main__':
    windows = pygetwindow.getAllTitles()
    logging.info("Locating Dual Universe Window")
    dual_windows = [s for s in windows if "Dual Universe" in s]
    if dual_windows.__len__() == 0:
        logging.fatal("Dual Universe is not launched !")
        exit(1)
    for window in dual_windows:
        logging.info("Dual Universe instances: [" + window + "]")
    logging.info("Using First Instance")
    my = pygetwindow.getWindowsWithTitle(dual_windows[0])[0]
    my.activate()
    pyautogui.screenshot("warning.png", get_center_area(my.box))

    config_logger()
    logging.info("Starting Dual TTB Bot !")
    logging.info("Loading Neural Net Model [" + model_to_use + "]... Please Wait")
    silence_tensorflow()
    from classifier_predict import Classifier

    try:
        classifier = Classifier(model_to_use)
    except:
        logging.critical("Failed to load Model !")
        exit(1)
    logging.info("Loaded Model Successfully !")
    console = Console()
    tasks = [f"Warming up Neural Net {n}" for n in range(1, 5)]
    with console.status("[bold green]Predicting... ") as status:
        while tasks:
            c, confidence = classifier.predict("samples/test_sample.png")
            tasks.pop(0)
    logging.info("Neural net Warmed Up !")
    logging.info("Current Time of Prediction: " + classifier.time.__str__() + " seconds")
    logging.info("Launching Bot")
    windows = pygetwindow.getAllTitles()
    logging.info("Locating Dual Universe Window")
    dual_windows = [s for s in windows if "dual" in s]
    if dual_windows.__len__() == 0:
        logging.fatal("Dual Universe is not launched !")
        exit(1)
    for window in dual_windows:
        logging.info("Dual Universe instances: [" + window + "]")
    logging.info("Using First Instance")
    my = pygetwindow.getWindowsWithTitle(dual_windows[0])[0]
    my.activate()
    pyautogui.screenshot("tmp.jpg", my.box)
    pyautogui.screenshot()
