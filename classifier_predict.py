import logging
import os
from time import time

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.python.keras.backend import expand_dims
from tensorflow.python.keras.models import load_model


class Classifier:

    def __init__(self, model):
        """

        :param model:
        """
        self.time = 0
        self.model = load_model(model)
        self.class_names = ['bauxite', 'coal', 'hematite', 'quartz', 'terrain', 'warning']

    def predict(self, path_to_img) -> [str, float]:
        """
        Will predict image class of image
        :param path_to_img: Path to image
        :rtype: str, float
        :return: class and percent confidence 0-1
        """
        t0 = time()
        img = keras.preprocessing.image.load_img(os.path.normpath(path_to_img), target_size=(32, 32))
        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = expand_dims(img_array, 0)  # Create a batch
        predictions = self.model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        logging.debug("Prediction took %.4f sec" % (time() - t0))
        self.time = (time() - t0)
        return self.class_names[np.argmax(score)], np.max(score)
