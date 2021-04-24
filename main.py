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


def image_weight(screen_data: np.array, sample_data: np.array, rgb: int):
    """

    :param screen_data: all data in screenshot
    :param sample_data: sample that we are comparing to
    :param rgb: number of index of color r=0 g=1 b=2
    :return:
    """
    chunks = []
    for chunk_no in range(0, 8):
        chunks.append(np.array_split(sample_data[:, chunk_no+chunk_no*3:(chunk_no + 4)+chunk_no*3, rgb], 8))
    chunk_weights = np.isin(screen_data[:, :, rgb],
                            chunks)
    num_of_true = np.sum(chunk_weights)
    comp_size = np.size(chunk_weights)
    return num_of_true / comp_size


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
