import datetime
import logging
import os
import shutil
import stat
from itertools import product
from pathlib import Path
from random import randint

import cv2
import tensorflow as tf
from PIL import Image
from tensorflow.python.keras.models import load_model, Model


class SelfTrain:
    def __init__(self, classifier):
        self.model: Model = classifier.model
        self.classifier = classifier

    @staticmethod
    def tile(filename, dir_in, dir_out, d):
        name, ext = os.path.splitext(filename)
        img = Image.open(os.path.join(dir_in, filename))
        img = img.convert("RGB")
        w, h = img.size
        ran = randint(-1212464564, 9999999999)

        grid = list(product(range(0, h - h % d, d), range(0, w - w % d, d)))
        for i, j in grid:
            box = (j, i, j + d, i + d)
            out = os.path.join(dir_out, f"out_{i}_{j}{ran}.jpg")
            img.crop(box).save(out)

    def crop_images(self, type):
        logging.info("Cropping sample")
        for file in os.listdir("tmp"):
            self.tile(file, "tmp", Path("selftrain") / type, 32)
            os.remove("tmp/" + file)
        logging.info("Removing wrong tiles")
        for imgy in os.listdir("tmp"):
            if os.stat(imgy).st_size == 0:
                os.chmod(imgy, stat.S_IWRITE)
                os.remove(imgy)
                continue
            img = cv2.imread(imgy, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            h, w = img.shape
            if not (h == 32 and w == 32):
                os.remove(imgy)

    def gather_sample(self, surf_type, image_path):
        if not any(map(surf_type.__contains__, ["ore", "terrain"])):
            return
        new_path = f"{surf_type}{datetime.datetime.now().timestamp()}.png"
        os.rename(image_path, new_path)
        logging.info(f"Found Sample to learn for {surf_type} with too little confidence")
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        shutil.move(new_path, str(Path(__file__).resolve().parent / "tmp" / new_path))
        self.crop_images(surf_type)
        if (
                os.listdir("selftrain/ore").__len__()
                and os.listdir("selftrain/terrain").__len__()
        ):
            logging.info("Training model with new samples")
            self.train()
        else:
            logging.info("Cant Train model waiting for more samples")

    def train(self):
        data_dir = "selftrain"
        epochs = 2
        batch_size = 1
        img_height = 32
        img_width = 32
        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            seed=4621301,
            subset="training",
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )

        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            validation_split=0.2,
            seed=1231657,
            subset="validation",
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )
        history = self.model.fit(
            train_ds, validation_data=val_ds, epochs=epochs, use_multiprocessing=True
        )
        learned_model_path = "models/ores_v1_selftrain"
        self.model.save(learned_model_path)
        self.classifier.bin_model = load_model(learned_model_path)
