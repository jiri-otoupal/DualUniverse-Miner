import unittest
from time import sleep, time

import cv2
import imutils
import numpy as np
import pydirectinput as pydirectinput
import pytesseract


class MyTestCase(unittest.TestCase):

    def unsharp_mask(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        # For details on unsharp masking, see:
        # https://en.wikipedia.org/wiki/Unsharp_masking
        # https://homepages.inf.ed.ac.uk/rbf/HIPR2/unsharp.htm
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    def test_something(self):
        # imgs = image_to_matrix("../images/samples/lacobus2.png")

        t0 = time()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        image = cv2.imread("../samples/height.png", 0)
        image = imutils.resize(image, width=143)
        thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        result = 255 - close
        result = cv2.GaussianBlur(result, (5, 5), 0)

        data = pytesseract.image_to_string(result, lang='eng', config='--psm 10')
        processed_data = ''.join(char for char in data if char.isnumeric() or char == '.' or char == "-")
        print(data)
        print(processed_data)

        cv2.imshow('thresh', thresh)
        cv2.imshow('close', close)
        cv2.imshow('result', result)
        print(time() - t0)
        # rec = compare_to_all_samples(imgs, False)
        # mat = apply_filter(rec, 100)
        # mat = blur(mat, 1)
        # c = unsharp_mask(mat, 5, 5, 1)
        ## c = apply_filter_dilation(mat, 2)
        # img_frombytes(c).show()

    def test_auto(self):
        sleep(5)
        pydirectinput.click(100, 100, duration=2)
        # color = (0, 188, 252)


#
# s = pyautogui.screenshot()
# for x in range(s.width):
#    for y in range(s.height):
#        if s.getpixel((x, y)) == color:
#            pyautogui.click(x, y)  # do something here


if __name__ == 'main':
    unittest.main()
