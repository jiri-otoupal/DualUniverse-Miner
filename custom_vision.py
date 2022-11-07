import time
from pathlib import Path

import numpy as np
from PIL import Image

dir_scanned = "ores"
sample_count_use = 20


def get_sample_count():
    count = 0

    for path in (Path("images").resolve() / dir_scanned).iterdir():

        if path.is_file():
            count += 1
    return count


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


def image_recognize_by_color(screen_data: np.array, sample_data: np.array, rgb: int,
                             small_area=True):
    """

    :param small_area: cropped at center of screen
    :param screen_data: all data in screenshot
    :param sample_data: sample that we are comparing to
    :param rgb: number of index of color r=0 g=1 b=2
    :return:
    """
    sample = np.unique(sample_data[:, :, rgb])
    if small_area:
        cropped_screen = image_crop_center(screen_data[:, :, rgb], 500, 500)
    else:
        cropped_screen = screen_data[:, :, rgb]

    # chunk_weights = isin_nb(cropped_screen, sample)

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

    res = np.where(np.abs(img ^ res) < threshold, img, res)
    return res


def _omit_zero(x):
    if x == 0:
        return None
    return x


def _get_pad_tuple(dim, d, i, j):
    if dim == 2:  # greyscale
        return (d - i - 1, i), (d - j - 1, j)
    else:  # color (and alpha) channels
        return (d - i - 1, i), (d - j - 1, j), (0, 0)


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


def cache_pattern(kind):
    cached = []
    images_dir = Path("images").resolve() / kind
    for i, sample in enumerate(images_dir.iterdir()):
        if i > sample_count_use:
            break
        sample_mat = image_to_matrix(str(sample))
        cached.append(sample_mat)
    return np.unique(cached, axis=3)


def compare_to_all_samples(screen_data: np.array, cached, cropped=True, debug=False):
    images_dir = Path("images").resolve() / dir_scanned
    recognized = None
    for i, sample in enumerate(cached):
        sample_mat = sample
        if recognized is None:
            # For getting the first matrix
            recognized = image_recognize(screen_data, sample_mat, cropped)
        else:
            recognized += image_recognize(screen_data, sample_mat, cropped)
        img_frombytes(recognized, "LA").save(f"images/tmp/sample{i}.png")
    img_frombytes(recognized, "LA").save(f"images/tmp/final.png")
    return recognized


def img_frombytes(data, mode="1"):
    """
    For debuging only graymap
    :param data:
    :return:
    """
    size = data.shape[::-1]
    databytes = np.packbits(data, axis=1)
    if mode == "1":
        return Image.frombytes("1", size=size, data=databytes)
    else:
        return Image.fromarray(mode="L", obj=np.uint8((data / sample_count_use) * 255))


def apply_filter(mat, confidence: float):
    """

    :param confidence: count of sample that matched ( put there number higher than 2 )
    :return: Filtered matrix
    """
    return np.greater(mat, confidence)


def circle_matrix(width, height):
    z = np.zeros((width, height))

    # specify circle parameters: centre ij and radius
    ci, cj = width / 2, height / 2
    cr = width / 2 + 1

    # Create index arrays to z
    I, J = np.meshgrid(np.arange(z.shape[0]), np.arange(z.shape[1]))

    # calculate distance of all points to centre
    dist = np.sqrt((I - ci) ** 2 + (J - cj) ** 2)

    # Assign value of 1 to those points where dist<cr:
    z[np.where(dist < cr)] = 1
    return z


def stamp_filter(screen, radius=256, granularity=16):
    cir = circle_matrix(radius, radius)
    wx, hx = np.shape(screen)
    scr_copy = np.copy(screen)
    for w in range(radius, wx, granularity):
        for h in range(radius, hx, granularity):
            scope = screen[w - radius:w, h - radius:h]
            circle_inner = np.multiply(scope, cir)
            circle_outer = np.equal(cir, 0)

            if (np.sum(circle_inner) / np.sum(cir)) < 0.2:
                scr_copy[w - radius:w, h - radius:h] = np.add(
                    np.multiply(scope, circle_outer), circle_inner * 0)
            else:
                scr_copy[w - radius:w, h - radius:h] = np.add(
                    np.multiply(scope, circle_outer), circle_inner * 1)

    return scr_copy.astype(bool)


if __name__ == "__main__":
    print("Resolving")
    out = cache_pattern(dir_scanned)

    sample_count = np.shape(out)[0]
    i = 2
    img = image_to_matrix(str(Path("samples") / f"lacobus{i}.png"))
    # img = blur(img, 3)

    start_time = time.time()
    arr = compare_to_all_samples(img, out, cropped=False)

    mean = np.mean(arr)
    confidence = 0.1

    bin_arr = (arr - (mean + mean * confidence)) > 0
    for s in range(8, 64, 8):
        bin_arr = stamp_filter(bin_arr, 64, s)

    print("---NB %s seconds ---" % (time.time() - start_time))
    # bin_arr = apply_filter(arr, confidence)
    img_frombytes(bin_arr.astype(bool)).save(f"test{i}.png")
