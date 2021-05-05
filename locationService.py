import os
from time import time

import cv2
import pytesseract


class LocationService:

    def __init__(self):
        if not os.path.isfile(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
            print("Tesseract is not installed !")
            print("Install from here and run again")
            print("https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20201127.exe")
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.speed = None
        self.height = None
        self.location_x = None
        self.location_y = None
        self.location_z = None
        self.time = None

    def predict_numbers(self, path):
        t0 = time()
        image = cv2.imread(os.path.normpath(path), 0)
        thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        result = 255 - close
        result = cv2.GaussianBlur(result, (5, 5), 0)
        data = pytesseract.image_to_string(result, lang='eng', config='--psm 10')
        processed_data = ''.join(char for char in data if char.isnumeric() or char == '.' or char == "-")
        self.time = time() - t0
        return processed_data

    def get_map_location(self):
        # TODO
        pass

    def get_speed(self):
        # TODO
        pass

    def get_height(self):
        # TODO
        pass
