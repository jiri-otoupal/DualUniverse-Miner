import os
from itertools import product
from time import time

import numpy as np
import tensorflow as tf
from PIL import Image
from keras.backend import expand_dims, clear_session
from keras.models import load_model
from tensorflow import keras
from tensorflow.python.framework.ops import reset_default_graph

model = load_model('ores')
class_names = ['bauxite', 'blue', 'coal', 'hematite', 'lacobus', 'quartz', 'warning']


img = keras.preprocessing.image.load_img(
    "samples/vrmvrmVrm.png", target_size=(32, 32)
)
img_array = keras.preprocessing.image.img_to_array(img)
img_array = expand_dims(img_array, 0)  # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
)
