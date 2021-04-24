import PIL
import numpy

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from PIL import Image


def image_to_matrix(path: str):
    img = Image.open(path)
    data = np.array(img)
    return data



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
