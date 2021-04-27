import os

from scipy.ndimage.morphology import grey_dilation, generate_binary_structure, iterate_structure, binary_dilation

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
from PIL import Image

dir_scanned = "bauxite"

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
        cropped_screen = image_crop_center(screen_data[:, :, rgb], 500, 500)
    else:
        cropped_screen = screen_data[:, :, rgb]
    chunk_weights = np.isin(cropped_screen, sample, assume_unique=True)
    return chunk_weights


def blur(img, radius):
    orig = np.zeros_like(img, dtype='int32')
    np.copyto(orig, img, casting='unsafe')

    d = 2 * radius - 1
    avg = np.zeros_like(orig)
    for i in range(d):
        for j in range(d):
            avg += np.pad(orig[i: _omit_zero(i - d + 1), j: _omit_zero(j - d + 1)],
                          _get_pad_tuple(len(img.shape), d, i, j), 'edge')
    avg = avg // (d ** 2)

    avg = avg.clip(0, 255)
    res = np.empty_like(img)

    np.copyto(res, avg, casting='unsafe')
    return res


def unsharp_mask(img, amount, radius, threshold):
    orig = np.zeros_like(img, dtype='int32')
    np.copyto(orig, img, casting='unsafe')

    d = 2 * radius - 1

    lowpass = np.zeros_like(orig)
    for i in range(d):
        for j in range(d):
            lowpass += np.pad(orig[i: _omit_zero(i - d + 1), j: _omit_zero(j - d + 1)],
                              _get_pad_tuple(len(img.shape), d, i, j), 'edge')
    lowpass = lowpass // (d ** 2)

    highpass = orig - lowpass

    tmp = orig + (amount / 100.) * highpass

    tmp = tmp.clip(0, 255)
    res = np.zeros_like(img)
    np.copyto(res, tmp, casting='unsafe')

    res = np.where(np.abs(img^res) < threshold, img, res)
    return res


def _omit_zero(x):
    if x == 0:
        return None
    return x


def _get_pad_tuple(dim, d, i, j):
    if dim == 2:  # greyscale
        return (d - i - 1, i), (d - j - 1, j)
    else:   # color (and alpha) channels
        return (d - i - 1, i), (d - j - 1, j), (0, 0)

def isin_try(screen_data, sample_data, rgb):
    chunks = []
    for chunk_no in range(0, 8):
        chunks.append(np.array_split(sample_data[:, chunk_no + chunk_no * 3:(chunk_no + 4) + chunk_no * 3, rgb], 8))
    res = np.zeros(screen_data[:, :, rgb].shape, dtype=bool)
    for y in range(0, np.size(screen_data[:, :, rgb], axis=0)):
        for x in range(0, np.size(screen_data[:, :, rgb], axis=1)):
            for chunky in chunks:
                if not np.all(res[x:x + 3, y:y + 3]):
                    for chunkx in chunky:
                        res[x:x + 3, y:y + 3] = chunkx == screen_data[x:x + 3, y:y + 3, rgb]
        print(y)
    return res


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
    samples = os.listdir("../images/"+dir_scanned+"/")
    recognized = None
    for sample in samples:
        sample_mat = image_to_matrix("../images/"+dir_scanned+"/" + sample)
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
