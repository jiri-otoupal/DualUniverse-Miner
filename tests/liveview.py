import os
import sys
from threading import Thread

import numpy as np
import pyautogui
from PIL import Image
from matplotlib import pyplot as plt, animation
from matplotlib.pyplot import draw
from scipy.ndimage import binary_dilation


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


def image_recognize(screen_data: np.array, sample_data: np.array, cropped=True):
    ir = lambda rgb: image_recognize_by_color(screen_data, sample_data, rgb, cropped)
    return intersect_colors(ir(0), ir(1), ir(2))


def image_crop_center(img, width, height):
    y, x = img.shape
    startx = x // 2 - width // 2
    starty = y // 2 - height // 2
    return img[starty:starty + height, startx:startx + width]


def image_recognize_by_color(screen_data: np.array, sample_data: np.array, rgb: int, small_area=True):
    """

    :param small_area: cropped at center of screen
    :param screen_data: all data in screenshot
    :param sample_data: sample that we are comparing to
    :param rgb: number of index of color r=0 g=1 b=2
    :return:
    """
    # TODO: Rewrite slow
    # chunk_weights = isin_try(screen_data, sample_data, rgb)
    sample = np.unique(sample_data[:, :, rgb]).flatten()
    if small_area:
        cropped_screen = image_crop_center(screen_data[:, :, rgb], 600, 600)
    else:
        cropped_screen = screen_data[:, :, rgb]
    chunk_weights = np.isin(cropped_screen, sample, assume_unique=True)
    return chunk_weights



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


def compare_to_all_samples(screen_data: np.array, cropped=True):
    samples = os.listdir("../images/bauxite/")
    recognized = None
    for sample in samples:
        sample_mat = image_to_matrix("../images/bauxite/" + sample)
        if recognized is None:
            recognized = image_recognize(screen_data, sample_mat, cropped)
        else:
            recognized += image_recognize(screen_data, sample_mat, cropped)
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


def get_pic():
    return pyautogui.screenshot()


def grab_frame():
    image = np.array(get_pic())
    rec = compare_to_all_samples(image, sys.argv[3] == "True")
    mat = apply_filter(rec, int(sys.argv[1]))
    return apply_filter_dilation(mat, int(sys.argv[2]))


fig = plt.figure()
data = img_frombytes(grab_frame())
im = plt.imshow(data, cmap='gist_gray_r', vmin=0, vmax=1)


def init():
    im.set_data(img_frombytes(grab_frame()))


def animate(i):
    im.set_data(img_frombytes(grab_frame()))
    return im


anim = animation.FuncAnimation(fig, animate, init_func=init, interval=500)
plt.show()
