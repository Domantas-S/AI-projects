import tensorflow as tf
import numpy as np
#import cv2
import matplotlib as mpl

def main():
    model = tf.keras.models.load_model('cnndigits.model')
    mnist = tf.keras.datasets.mnist

    (x_train, y_train), (x_test, y_test) = mnist.load_data()  # (pixel input, classification), images are 28x28px
    x_test = tf.keras.utils.normalize(x_test, axis=1)

    loss, accuracy = model.evaluate(x_test, y_test)
    print(loss)
    print(accuracy)

if __name__ == '__main__':
    main()