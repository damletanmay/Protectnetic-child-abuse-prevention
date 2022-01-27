import os
import json
import numpy as np
from os import listdir
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
from os.path import isfile, join, exists, isdir, abspath,dirname, join


def load_images(image_paths, image_size, verbose=True):

    loaded_images = []
    loaded_image_paths = []

    if isdir(image_paths):
        parent = abspath(image_paths)
        image_paths = [join(parent, f) for f in listdir(image_paths) if isfile(join(parent, f))]
    elif isfile(image_paths):
        image_paths = [image_paths]

    for img_path in image_paths:
        try:
            if verbose:
                print(img_path)
            image = keras.preprocessing.image.load_img(img_path, target_size=image_size)
            image = keras.preprocessing.image.img_to_array(image)
            image /= 255
            loaded_images.append(image)
            loaded_image_paths.append(img_path)
        except Exception as ex:
            print("Image Load Failure: ", img_path, ex)

    return np.asarray(loaded_images), loaded_image_paths

def load_model(model_path):
    if model_path is None or not exists(model_path):
    	raise ValueError("saved_model_path must be the valid directory of a saved model to load.")

    # model = tf.keras.models.load_model(model_path)
    model = tf.keras.models.load_model(model_path, custom_objects={'KerasLayer':hub.KerasLayer})
    # model.summary()
    #print(model.summary())
    return model

def classify(model, input_paths, image_dim):
    """ Classify given a model, input paths (could be single string), and image dimensionality...."""
    images, image_paths = load_images(input_paths, (image_dim, image_dim))
    probs = classify_nd(model, images)
    return dict(zip(image_paths, probs))

def classify_nd(model, nd_images):
    """ Classify given a model, image array (numpy)...."""

    model_preds = model.predict(nd_images)
    # preds = np.argsort(model_preds, axis = 1).tolist()

    categories = ['drawings', 'hentai', 'neutral', 'porn', 'sexy']

    probs = []
    for i, single_preds in enumerate(model_preds):
        single_probs = {}
        for j, pred in enumerate(single_preds):
            single_probs[categories[j]] = float(pred)
        probs.append(single_probs)
    return probs

# function to detect p content
def p_detect(path):
    IMAGE_DIM = 224   # required/default image dimensionality
    predictions = []
    model_path = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'PDetector.h5')
    model = load_model(model_path)
    image_preds = classify(model,path, IMAGE_DIM)
    predictions.append(image_preds)

    return predictions
