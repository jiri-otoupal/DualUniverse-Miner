import ctypes
import logging
import time

import pyautogui
import pydirectinput as pydirectinput

from ControlDispatcher import ControlDispatcher
from config import rotation_angle, mining_time_sphere

SendInput = ctypes.windll.user32.SendInput

W = 0x11
A = 0x1E
S = 0x1F
D = 0x20

SPACE = 0x39

# Switching tools
harvest_tool = 0x02  # Slot 1
mining_tool = 0x03  # Slot 2
scanner_tool = 0x04  # Slot 3
detector_tool = 0x05  # Slot 4

# Misc
ctrl_key = 0x11
alt_key = 0x12

# Opening inventory
open_inventory = 0x17  # Slot i

# Bind these to Camera in Dual Universe XD
Down = 0x50
Left = 0x4B
Right = 0x4D
Up = 0x48

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


def maximize_mining_circle():
    pydirectinput.keyDown('ctrl')
    for s in range(100):
        pyautogui.scroll(10)
        time.sleep(0.01)
        pyautogui.scroll(10)
    pydirectinput.keyUp('ctrl')


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def MoveMouse(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def PressAndRelease(t: float, key: int):
    PressKey(key)
    time.sleep(t)
    ReleaseKey(key)


def Forward(t: float):
    PressAndRelease(t, W)


def Backward(t: float):
    PressAndRelease(t, S)


def GoLeft(t: float):
    PressAndRelease(t, A)


def GoRight(t: float):
    PressAndRelease(t, D)


def SwitchToHarvest(t: float):
    PressAndRelease(t, harvest_tool)


def SwitchToMining(t: float):
    PressAndRelease(t, mining_tool)


def SwitchToScanner(t: float):
    PressAndRelease(t, scanner_tool)


def SwitchToDetector(t: float):
    PressAndRelease(t, detector_tool)


def OpenInventory(t: float):
    PressAndRelease(t, open_inventory)


def LookLeft(dispatcher, angle: float = rotation_angle):
    logging.info("Rotating by " + rotation_angle.__str__() + " degrees")
    if dispatcher.mining:
        return
    dispatcher.mr_undergoing = True
    logging.info("Rotating Left Start")
    PressKey(Left)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Left)
    logging.info("Rotating Left Stop")
    dispatcher.mr_undergoing = False


def LookRight(dispatcher, angle: float = rotation_angle):
    logging.info("Rotating by " + rotation_angle.__str__() + " degrees")
    if dispatcher.mining:
        return
    dispatcher.mr_undergoing = True
    logging.info("Rotating Right Start")
    PressKey(Right)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Right)
    logging.info("Rotating Right Stop")
    dispatcher.mr_undergoing = False


def Jump(dispatcher):
    dispatcher.mr_undergoing = True
    PressAndRelease(1.2, SPACE)
    dispatcher.mr_undergoing = False


def Mine(dispatcher):
    # Mutex True
    dispatcher.clear_movement_rotation()
    dispatcher.mining = True
    logging.info("Mining...")
    pyautogui.mouseDown()
    time.sleep(mining_time_sphere)
    pyautogui.mouseUp()
    # Mutex False
    dispatcher.mining = False
    logging.info("Finished Mining")


def LookUp(dispatcher, angle: float = rotation_angle):
    logging.info("Rotating by " + rotation_angle.__str__() + " degrees")
    if dispatcher.mining:
        return
    dispatcher.mr_undergoing = True
    logging.info("Rotating Up Start")
    PressKey(Up)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Up)
    logging.info("Rotating Up Stop")
    dispatcher.mr_undergoing = False


def LookDown(dispatcher, angle: float = rotation_angle):
    logging.info("Rotating by " + rotation_angle.__str__() + " degrees")
    if dispatcher.mining:
        return
    dispatcher.mr_undergoing = True
    logging.info("Rotating Down Start")
    PressKey(Down)
    time.sleep((1.79 / 360) * rotation_angle)
    ReleaseKey(Down)
    logging.info("Rotating Down Stop")
    dispatcher.mr_undergoing = False


if __name__ == '__main__':
    disp = ControlDispatcher(None)
    time.sleep(3)
    print("Testing Sensitivity")
    for i in range(1, 10):
        LookLeft(disp, i / 3)
        print("Pressed " + (i / 3).__str__())
        time.sleep(3)