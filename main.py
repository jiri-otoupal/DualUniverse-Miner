"""


      @@@  @@@@@@  @@@@@@@  @@@  @@@ @@@@@@@@ @@@
      @@! @@!  @@@ @@!  @@@ @@!  @@@ @@!      @@!
      !!@ @!@  !@! @!@  !@! @!@  !@! @!!!:!   @!!
  .  .!!  !!:  !!! !!:  !!!  !: .:!  !!:      !!:
  ::.::    : :. :  :: :  :     ::    : :: ::  : ::.: :


Dual Universe Bot


Copyright Jiri Otoupal, Dominik Deak, Vojtech Sevcik

c 2021

"""
import logging
from time import sleep

import keyboard as keyboard
import pyautogui
import pygetwindow
from rich.console import Console
from silence_tensorflow import silence_tensorflow

import controller
from config import model_to_use_ores, log_level, full_auto, logo
from control_dispatcher import ControlDispatcher
from logger import config_logger


def activate_window(my):
    try:
        my.activate()
    except:
        pass
    if not my.isActive:
        sleep(0.5)
        activate_window(my)
    else:
        return True
    sleep(0.1)
    if not my.isActive:
        logging.fatal("Windows had problem activating window... Stopping")
        return False
    return True


if __name__ == "__main__":
    print(logo)
    pyautogui.FAILSAFE = False
    config_logger(log_level)
    logging.info("Starting JoDVel Bot !")
    logging.info("Loading Neural Net Model [" + model_to_use_ores + "]... Please Wait")
    silence_tensorflow()
    from classifier_predict import Classifier
    from vision import Vision

    try:
        classifier = Classifier(model_to_use_ores)
    except Exception as ex:
        logging.critical("Failed to load Model !")
        logging.debug(ex.__str__())
        exit(1)
    logging.info("Loaded Model Successfully !")
    logging.info("Warming Up Neural Net")
    console = Console()
    tasks = [f"Warming up Neural Net {n}" for n in range(1, 5)]
    with console.status("[bold green]Predicting... ") as status:
        while tasks:
            c, confidence = classifier.predict("samples/test_sample.png")
            if c != "ore":
                logging.fatal("Test Sample is incorrectly identified as " + c + " !")
            c, confidence = classifier.predict("samples/lacobus_test.png")
            if c != "terrain":
                logging.fatal("Test Sample is incorrectly identified as " + c + " !")
            tasks.pop(0)
    logging.info("Neural net Warmed Up")
    logging.info(
        "Current Time of Prediction: " + classifier.time.__str__() + " seconds"
    )
    logging.info("Launching Bot")
    windows = pygetwindow.getAllTitles()
    logging.info("Locating Dual Universe Window")
    dual_windows = [s for s in windows if "Dual Universe" in s]
    if dual_windows.__len__() == 0:
        logging.fatal("Dual Universe is not launched !")
        exit(1)
        logging.info("Using First Instance")
    for window in dual_windows:
        logging.info("Dual Universe instances: [" + window + "]")
    my = pygetwindow.getWindowsWithTitle(dual_windows[0])[0]
    my.maximize()
    if not activate_window(my):
        exit(1)
    dispatcher = ControlDispatcher(my)
    keyboard.hook(dispatcher.stop)
    # TODO: pass function that will be called if is too far away and if see ore
    vision = Vision(my, classifier, dispatcher)
    dispatcher.start()
    vision_thread = vision.start()
    sleep(0.1)
    controller.SwitchToHarvest(0.05)
    controller.SwitchToMining(0.05)
    logging.info("Maximizing Mining Circle")
    if full_auto:
        controller.maximize_mining_circle()
    logging.info("Maximized")
    vision_thread.join()
    # my.minimize()
    logging.info("Stopped")
