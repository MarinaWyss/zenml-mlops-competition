import logging
import numpy as np

from tensorflow.keras import Sequential
from tensorflow.keras.layers import (
    Dense,
    Dropout,
    Flatten,
    Conv2D,
    MaxPooling2D,
    BatchNormalization
)

import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import AUC, Precision, Recall

logging.basicConfig(level=logging.DEBUG)


class CatClassifier:
    def __init__(self, args):
        self.args = args

    def train(self,
              X_train: np.array,
              y_train: np.array):
        """Train model.

        Heavily inspired by
        https://github.com/rpeden/cat-or-not/blob/master/train.py

        Args:
            X_train (np.array): Array of train images
            y_train (np.array): Array of training labels

        Returns:
            (tf.Keras.model): Trained model
        """
        logging.info("Constructing model...")

        cnn2d = Sequential()
        cnn2d.add(
            Conv2D(
                filters=self.args['conv_1_filters'],
                kernel_size=(self.args['kernel_size'], self.args['kernel_size']),
                activation='relu',
                input_shape=(self.args['image_size'], self.args['image_size'], 1)))
        cnn2d.add(MaxPooling2D(
            pool_size=(self.args['max_pool'], self.args['max_pool'])))
        cnn2d.add(BatchNormalization())
        cnn2d.add(Conv2D(
            filters=self.args['conv_2_filters'],
            kernel_size=(self.args['kernel_size'], self.args['kernel_size']),
            activation='relu'))
        cnn2d.add(MaxPooling2D(
            pool_size=(self.args['max_pool'], self.args['max_pool'])))
        cnn2d.add(BatchNormalization())
        cnn2d.add(Conv2D(
            filters=self.args['conv_3_filters'],
            kernel_size=(self.args['kernel_size'], self.args['kernel_size']),
            activation='relu'))
        cnn2d.add(MaxPooling2D(
            pool_size=(self.args['max_pool'], self.args['max_pool'])))
        cnn2d.add(BatchNormalization())
        cnn2d.add(Conv2D(
            filters=self.args['conv_4_filters'],
            kernel_size=(self.args['kernel_size'], self.args['kernel_size']),
            activation='relu'))
        cnn2d.add(MaxPooling2D(
            pool_size=(self.args['max_pool'], self.args['max_pool'])))
        cnn2d.add(BatchNormalization())
        cnn2d.add(Conv2D(
            filters=self.args['conv_5_filters'],
            kernel_size=(self.args['kernel_size'], self.args['kernel_size']),
            activation='relu'))
        cnn2d.add(MaxPooling2D(
            pool_size=(self.args['max_pool'], self.args['max_pool'])))
        cnn2d.add(BatchNormalization())
        cnn2d.add(Dropout(
            self.args['dropout']))
        cnn2d.add(Flatten())
        cnn2d.add(Dense(
            units=self.args['dense_1_units'],
            activation='relu'))
        cnn2d.add(Dropout(
            self.args['dropout']))
        cnn2d.add(Dense(
            units=self.args['dense_2_units'],
            activation='relu'))
        cnn2d.add(Dense(
            units=self.args['dense_3_units'],
            activation='sigmoid'))

        # TODO from_logits
        cnn2d.compile(loss='binary_crossentropy',
                      optimizer=Adam(learning_rate=self.args['learning_rate']),
                      metrics=[AUC(), Precision(), Recall()])
        logging.info("Model compiled.")

        logging.info("Fitting model...")
        cnn2d.fit(x=X_train,
                  y=y_train,
                  epochs=self.args['num_epochs'],
                  batch_size=self.args['batch_size'],
                  validation_split=self.args['val_split'],
                  seed=self.args['random_seed'],
                  shuffle=True)

        logging.info("Model successfully fit.")
        return cnn2d

    def save(self, model):
        """Save model.

        Args:
            model: Trained tf.keras.model
        """
        tf.keras.models.save_model(
            model,
            filepath=self.args['output_path'],
            save_format='h5'
        )
        logging.info("Model saved.")