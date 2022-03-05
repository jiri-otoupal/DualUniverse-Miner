import logging
import os
from time import time

import numpy as np

from config import prediction_batch_size, cloud


class Classifier:
    def __init__(self, model, bin_model="models/ores_v1_selftrain"):
        """

        :param model:
        """
        from tensorflow.python.keras.models import load_model, Model

        self.time = 0
        self.model: Model = load_model(model)
        if os.path.isfile(bin_model):
            self.bin_model: Model = load_model(bin_model)
        else:
            self.bin_model = None
        self.class_names = ["ore", "signal", "terrain", "warning"]

    def predict(self, path_to_img, learned: bool = False) -> [str, float]:
        """
        Will predict image class of image
        :param learned: Extension for self learning module
        :param path_to_img: Path to image
        :rtype: str, float
        :return: class and percent confidence 0-1
        """
        t0 = time()
        if cloud:
            from predict_cloud import get_prediction

            prediction = get_prediction(path_to_img)
            logging.debug("Prediction took %.4f sec" % (time() - t0))
            self.time = time() - t0
            return (
                prediction.payload.pb[0].display_name,
                prediction.payload.pb[0].classification.score,
            )
        else:
            import tensorflow as tf
            from tensorflow.python.keras.backend import expand_dims

            from tensorflow.python.keras.preprocessing.image import (
                img_to_array,
                load_img,
            )

            img = load_img(os.path.normpath(path_to_img), target_size=(32, 32))
            img_array = img_to_array(img)
            img_array = expand_dims(img_array, 0)  # Create a batch
            if not learned:
                predictions = self.model.predict(
                    img_array, batch_size=prediction_batch_size
                )
            else:
                if self.bin_model is None:
                    return None, None
                predictions = self.bin_model.predict(
                    img_array, batch_size=prediction_batch_size
                )
            score = tf.nn.softmax(predictions[0])
            logging.debug("Prediction took %.4f sec" % (time() - t0))
            self.time = time() - t0
            return self.class_names[np.argmax(score)], np.max(score)
