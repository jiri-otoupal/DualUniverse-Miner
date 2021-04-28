import numpy as np
import tensorflow as tf
from keras.backend import expand_dims
from keras.models import load_model
from tensorflow import keras

model = load_model('ores')

img = keras.preprocessing.image.load_img(
    "samples/vrmvrmVrm.png", target_size=(32, 32)
)
img_array = keras.preprocessing.image.img_to_array(img)
img_array = expand_dims(img_array, 0)  # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

class_names = ['blue', 'hematite', 'lacobus']



def image_to_tiles(im):
    pass



for image in image_to_tiles(img_array, 4):
    pre = model.predict(image)
    scor = tf.nn.softmax(pre[0])
    print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
            .format(class_names[np.argmax(scor)], 100 * np.max(scor))
    )

print(
    "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(class_names[np.argmax(score)], 100 * np.max(score))
)
