import ctypes
import time

SendInput = ctypes.windll.user32.SendInput

W = 0x11
A = 0x1E
S = 0x1F
D = 0x20

SPACE = 0x39

# Bind these to Camera in Dual Universe XD
Down = 0x50
Left = 0x4B
Right = 0x4D
Up = 0x48

# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


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


def LookLeft(angle: int = 45):
    PressKey(Left)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Left)


def LookRight(angle: int = 45):
    PressKey(Right)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Right)


def LookUp(angle: int = 30):
    PressKey(Up)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Up)


def LookDown(angle: int = 30):
    PressKey(Down)
    time.sleep((1.79 / 360) * angle)
    ReleaseKey(Down)


if __name__ == '__main__':
    time.sleep(3)
    LookUp()
    LookDown()
    LookLeft()
    LookRight()