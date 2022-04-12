import tensorflow as tf
import numpy as np
#import cv2
import matplotlib as mpl


def main():
    mnist = tf.keras.datasets.mnist  # get mnist dataset from module, training and test data are already split up

    (x_train, y_train), (x_test, y_test) = mnist.load_data()  # (pixel input, classification), images are 28x28px

    x_train = tf.keras.utils.normalize(x_train, axis=1)  # normalise pixel data to [0,1] rather than [0..255]
    x_test = tf.keras.utils.normalize(x_test, axis=1)

    model = tf.keras.models.Sequential()  # basic NN, one layer passes values to next layer
    model.add(tf.keras.layers.Flatten(input_shape=(28, 28)))  # 2d-array to 1d
    model.add(tf.keras.layers.Dense(128, activation='relu'))  # layer of 128 processing neurons
    model.add(tf.keras.layers.Dense(128, activation='relu'))  # using rectified units
    model.add(tf.keras.layers.Dense(10, activation='softmax'))  # output layer, each neuron will output a confidence
    # value, summing all confidence values will add to 1

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=10)  # train the model using the training data
    model.save('digits.model')


if __name__ == '__main__':
    main()
