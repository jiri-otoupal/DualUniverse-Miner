import logging
import os
from time import time

import numpy as np
import tensorflow as tf
from tensorflow.python.keras.backend import expand_dims
from tensorflow.python.keras.models import load_model, Model
from tensorflow.python.keras.preprocessing.image import img_to_array, load_img


class Classifier:

    def __init__(self, model):
        """

        :param model:
        """
        self.time = 0
        self.model: Model = load_model(model)
        self.model.trainable = False
        self.class_names = ['hematite', 'terrain', 'warning']

    def predict(self, path_to_img) -> [str, float]:
        """
        Will predict image class of image
        :param path_to_img: Path to image
        :rtype: str, float
        :return: class and percent confidence 0-1
        """
        t0 = time()
        img = load_img(os.path.normpath(path_to_img), target_size=(32, 32))
        img_array = img_to_array(img)
        img_array = expand_dims(img_array, 0)  # Create a batch
        predictions = self.model.predict(img_array)
        score = tf.nn.softmax(predictions[0])
        logging.debug("Prediction took %.4f sec" % (time() - t0))
        self.time = (time() - t0)
        return self.class_names[np.argmax(score)], np.max(score)
