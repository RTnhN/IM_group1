from skimage.io import imsave
import numpy as np
from skimage.transform import resize
from model import bce_dice_loss, iou, dice_coef
from read_one_image import read_one_image
from post_process_image import post_processing, colorize_image
from tensorflow.keras.models import  load_model
import tensorflow as tf

USE_GPU = False
if USE_GPU:
    # This code is required if I want tensorflow to use the GPU
    physical_devices = tf.config.list_physical_devices('GPU') 
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
else: 
    # This code below is added to keep tensorflow from using GPU
    import os
    try:
        # Disable all GPUS
        tf.config.set_visible_devices([], 'GPU')
        visible_devices = tf.config.get_visible_devices()
        for device in visible_devices:
            assert device.device_type != 'GPU'
    except:
        # Invalid device or cannot modify virtual devices once initialized.
        pass
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def process_image(folder,filename, model_name):
    IMG_WIDTH=256
    IMG_HEIGHT=256
    if model_name == "unet":
        model = load_model("models/unet", custom_objects={"dice_coef": dice_coef})
    elif model_name == "unetpp":    
        model = load_model("models/unet++", custom_objects={'bce_dice_loss': bce_dice_loss, 'iou': iou})
    elif model_name == "fcn":    
        model = load_model("models/FCN", custom_objects={"dice_coef": dice_coef})
    elif model_name == "gan":    
        model = load_model("models/GAN")
        IMG_WIDTH=128
        IMG_HEIGHT=128

   
    input_image, input_image_sizes = read_one_image(folder + "/" + filename, IMG_WIDTH, IMG_HEIGHT)

    # Predict on test data
    predicted_mask = model(input_image, training=False)
    predicted_mask = np.array(predicted_mask)
    predicted_mask = predicted_mask[0,:,:,:]
    input_image = input_image[0,:,:,:]

    # post processing
    predicted_mask_processed = post_processing(predicted_mask)
    predicted_mask_processed = resize(predicted_mask_processed, input_image_sizes, mode='constant', preserve_range=True).astype('bool')
    input_image = resize(input_image, input_image_sizes, mode='constant', preserve_range=True,anti_aliasing=True)
    colorized_image = colorize_image(predicted_mask_processed,input_image)
    colorized_image_filename = "processed_" + filename
    colorized_image_path = folder + "/" + colorized_image_filename
    imsave(colorized_image_path, colorized_image)
    return "processed_" + filename