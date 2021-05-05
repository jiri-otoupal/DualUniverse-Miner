import os

import cv2
import pytesseract


class LocationService:

    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def predict_numbers(self, path):
        image = cv2.imread(os.path.normpath(path), 0)
        thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        result = 255 - close
        result = cv2.GaussianBlur(result, (5, 5), 0)
        data = pytesseract.image_to_string(result, lang='eng', config='--psm 10')
        processed_data = ''.join(char for char in data if char.isnumeric() or char == '.' or char == "-")
        return processed_data
