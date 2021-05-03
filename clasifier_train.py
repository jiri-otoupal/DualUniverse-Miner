import numpy as np
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

model_name = "models/ores_a_v3_soft"
epochs = 10
batch_size = 32
img_height = 32
img_width = 32
data_dir = "images"

train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    seed=4621301,
    subset="training",
    image_size=(img_height, img_width),
    batch_size=batch_size)

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    seed=1231657,
    subset="validation",
    image_size=(img_height, img_width),
    batch_size=batch_size)

train_datagen = ImageDataGenerator(
    rescale=1. / 255, zoom_range=[0.2, 1], rotation_range=90,
    brightness_range=[0.8, 1.2], width_shift_range=0.2, height_shift_range=0.2, channel_shift_range=0.1)

test_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_directory(
    data_dir,
    target_size=(32, 32), color_mode='rgb', shuffle=True,
    seed=42, class_mode="sparse",
    batch_size=32)

validation_generator = test_datagen.flow_from_directory(
    data_dir,
    target_size=(32, 32), color_mode='rgb', shuffle=True,
    seed=12, class_mode="sparse",
    batch_size=32)

AUTOTUNE = tf.data.AUTOTUNE
print(train_ds.class_names)
num_classes = train_ds.class_names.__len__()
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
normalization_layer = layers.experimental.preprocessing.Rescaling(1. / 255)
normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_ds))
first_image = image_batch[0]
# Notice the pixels values are now in `[0,1]`.
print(np.min(first_image), np.max(first_image))

data_augmentation = keras.Sequential(
    [
        layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical",
                                                     input_shape=(img_height,
                                                                  img_width,
                                                                  3)),
        layers.experimental.preprocessing.RandomRotation(0.5),
        layers.experimental.preprocessing.RandomContrast(0.2),
        layers.experimental.preprocessing.RandomZoom(0.5)
    ]
)
model = Sequential([
    data_augmentation,
    layers.experimental.preprocessing.Rescaling(1. / 255),
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(64, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Conv2D(128, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.1),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    # layers.Dense(num_classes, "softmax")
    layers.Dense(num_classes)
])

model.compile(optimizer='adam',
              #loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
model.summary()

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs, use_multiprocessing=True
)
model.save(model_name)


model.fit(
    train_generator, validation_data=val_ds,
    epochs=epochs)
model.save(model_name + "_aug")
