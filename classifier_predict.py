import os
from itertools import product
from time import time

import numpy as np
import tensorflow as tf
from PIL import Image
from keras.backend import expand_dims, clear_session
from keras.models import load_model
from tensorflow import keras

model = load_model('ores')
class_names = ['bauxite', 'blue', 'coal', 'hematite', 'lacobus', 'quartz', 'warning']

img = keras.preprocessing.image.load_img(
    "samples/vrmvrmVrm.png", target_size=(32, 32)
)
img_array = keras.preprocessing.image.img_to_array(img)
img_array = expand_dims(img_array, 0)  # Create a batch
t0 = time()
print("Warmup Predicting")
predictions = model.predict(img_array, use_multiprocessing=True, batch_size=1024, workers=8)
print("%.4f sec" % (time() - t0))
t0 = time()
print("Started Predicting")
predictions = model.predict(img_array, use_multiprocessing=True, batch_size=1024, workers=8)
print("%.4f sec" % (time() - t0))
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
)
