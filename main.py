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


def image_weight(screen_data: np.array, sample_data: np.array, rgb: int, chunk_no: int):
    chunk_weights = np.isin(screen_data[:, :, rgb],
                            np.array_split(sample_data[:, chunk_no:chunk_no + 4, rgb], 8))
    num_of_true = np.sum(chunk_weights)
    comp_size = np.size(chunk_weights)
    return num_of_true / comp_size


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
