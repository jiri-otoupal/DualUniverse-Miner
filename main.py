import os
import struct

import PIL
import numba
import numpy
from numba.roc.decorators import autojit
from scipy.ndimage.morphology import grey_dilation, generate_binary_structure, iterate_structure, binary_dilation

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from PIL import Image


def image_to_matrix(path: str):
    img = Image.open(path)
    data = np.array(img)
    return data


def intersect_colors(red, green, blue):
    if not (red.shape == green.shape == blue.shape):
        return False

    mat_intersect = np.where((red == green), red, 0)
    mat_intersect = np.where((blue == mat_intersect), blue, 0)
    return mat_intersect


def image_recognize(screen_data: np.array, sample_data: np.array):
    ir = lambda rgb: image_recognize_by_color(screen_data, sample_data, rgb)
    return intersect_colors(ir(0), ir(1), ir(2))


def image_recognize_by_color(screen_data: np.array, sample_data: np.array, rgb: int):
    """

    :param screen_data: all data in screenshot
    :param sample_data: sample that we are comparing to
    :param rgb: number of index of color r=0 g=1 b=2
    :return:
    """
    chunks = []
    for chunk_no in range(0, 8):
        chunks.append(np.array_split(sample_data[:, chunk_no + chunk_no * 3:(chunk_no + 4) + chunk_no * 3, rgb], 8))
    chunk_weights = np.isin(screen_data[:, :, rgb], chunks)
    return chunk_weights


def findFirst_jit(a, b):
    for i in range( len(a) ):
        result = True
        for j in range(len(b)):
            result = result and (a[i+j] == b[j])
            if not result:
                break

        if result:
            return i
    return 0

def image_weight(screen_data: np.array, sample_data: np.array):
    chunk_weights = image_recognize(screen_data, sample_data)
    num_of_true = np.sum(chunk_weights)
    comp_size = np.size(chunk_weights)
    return num_of_true / comp_size


def image_weight_by_color(screen_data: np.array, sample_data: np.array, rgb: int):
    """

    :param screen_data: all data in screenshot
    :param sample_data: sample that we are comparing to
    :param rgb: number of index of color r=0 g=1 b=2
    :return:
    """
    chunk_weights = image_recognize_by_color(screen_data, sample_data, rgb)
    num_of_true = np.sum(chunk_weights)
    comp_size = np.size(chunk_weights)
    return num_of_true / comp_size


def compare_to_all_samples(screen_data: np.array):
    samples = os.listdir("../images/bauxite/")
    recognized = None
    for sample in samples:
        sample_mat = image_to_matrix("../images/bauxite/" + sample)
        if recognized is None:
            recognized = image_recognize(screen_data, sample_mat)
        else:
            recognized += image_recognize(screen_data, sample_mat)
    return recognized


def img_frombytes(data):
    """
    For debuging only graymap
    :param data:
    :return:
    """
    size = data.shape[::-1]
    databytes = np.packbits(data, axis=1)
    return Image.frombytes(mode='1', size=size, data=databytes)


def apply_filter(mat, confidence: int):
    """

    :param confidence: count of sample that matched ( put there number higher than 2 )
    :return: Filtered matrix
    """
    return np.greater(mat, confidence)


def apply_filter_dilation(mat, iterations):
    return binary_dilation(mat, iterations=iterations)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
