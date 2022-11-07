from time import sleep

import pydirectinput

if __name__ == "__main__":
    sleep(5)
    pydirectinput.keyDown("space")
    while True:
        pydirectinput.press("F4")
        sleep(5)
        pydirectinput.keyDown("space")
