#!/usr/bin/env python
# coding=utf-8
"""
python=3.5.2
"""

# from data_input import read_train_data, read_test_data, prob_to_rles, mask_to_rle, resize, np, read_one_image
from skimage.io import imsave
import numpy as np
from skimage.transform import resize
from model import dice_loss, bce_dice_loss, iou, dice_coef
from read_one_image import read_one_image
from post_process_image import post_processing, colorize_image
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

def process_image(folder,filename, model):
    test_img, test_img_sizes = read_one_image(folder + "/" + filename)
    # model_name = 'model-0522-test.h5'
    # get u_net model
    if model == "unet":
        u_net = load_model("unet", custom_objects={"dice_coef": dice_coef})
    elif model == "unetpp":    
        u_net = load_model("unet++", custom_objects={'bce_dice_loss': bce_dice_loss, 'iou': iou})

    # u_net.load_weights(model_name)

    # Predict on test data
    test_mask = u_net(test_img, training=False)
    test_mask = np.array(test_mask)
    test_mask = test_mask[0,:,:,:]
    test_img = test_img[0,:,:,:]

    # post processing
    post_test_mask = post_processing(test_mask)
    post_test_mask = resize(post_test_mask, test_img_sizes, mode='constant', preserve_range=True).astype('bool')
    test_img = resize(test_img, test_img_sizes, mode='constant', preserve_range=True,anti_aliasing=True)
    colorized_image = colorize_image(post_test_mask,test_img)
    processed_filename = "processed_" + filename
    processed_path = folder + "/" + processed_filename
    imsave(processed_path, colorized_image)
    return "processed_" + filename