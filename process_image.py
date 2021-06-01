#!/usr/bin/env python
# coding=utf-8
"""
python=3.5.2
"""

# from data_input import read_train_data, read_test_data, prob_to_rles, mask_to_rle, resize, np, read_one_image
from skimage.feature import canny
from skimage.io import imsave
import skimage
import numpy as np
from skimage.transform import resize
from skimage.morphology import binary_dilation
from model import dice_coef
from read_one_image import read_one_image
from post_process_image import post_processing
from tensorflow.keras.models import  load_model

# This code below is added to keep tensorflow from using GPU
# import tensorflow as tf
# import os
# try:
#     # Disable all GPUS
#     tf.config.set_visible_devices([], 'GPU')
#     visible_devices = tf.config.get_visible_devices()
#     for device in visible_devices:
#         assert device.device_type != 'GPU'
# except:
#     # Invalid device or cannot modify virtual devices once initialized.
#     pass
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def process_image(folder,filename):
    test_img, test_img_sizes = read_one_image(folder + "/" + filename)
    # model_name = 'model-0522-test.h5'
    # get u_net model
    u_net = load_model("mymodel", custom_objects={"dice_coef": dice_coef})
    # u_net.load_weights(model_name)

    # Predict on test data
    test_mask = u_net(test_img, training=False)
    test_mask = np.array(test_mask)
    test_mask = test_mask[0,:,:,:]
    test_img = test_img[0,:,:,:]

    # post processing
    edges_brightness = 200
    center_brightness = 100
    color_mask = [0, 1, 0]
    iterations = 2

    post_test_mask = post_processing(test_mask)
    post_test_mask = resize(post_test_mask, test_img_sizes, mode='constant', preserve_range=True,anti_aliasing=True).astype('bool')
    edges = canny(post_test_mask)
    for i in range(iterations):
        edges = binary_dilation(edges)
    center =  post_test_mask^edges # bitwise xor
    formattedMask = center * center_brightness +  edges * edges_brightness
    formattedMask = skimage.color.grey2rgb(formattedMask)
    coloredMask = color_mask * formattedMask
    coloredMask_int = np.copy(coloredMask).astype('uint8')
    test_img = resize(test_img, test_img_sizes, mode='constant', preserve_range=True,anti_aliasing=True)
    test_img_int = np.copy(test_img).astype('uint8')
    alpha = .7
    beta = 1

    fin = (coloredMask_int*alpha + test_img_int*(beta))
    fin = np.copy(fin).astype('uint8')
    processedFilename = "processed_" + filename
    processed_path = folder + "/" + processedFilename
    imsave(processed_path, fin)
    return "processed_" + filename

