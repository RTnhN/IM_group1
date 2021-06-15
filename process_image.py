from skimage.io import imsave
import numpy as np
from skimage.transform import resize
from model import bce_dice_loss, iou, dice_coef
from read_one_image import read_one_image
from post_process_image import post_processing, colorize_image
from tensorflow.keras.models import  load_model
import tensorflow as tf
class predict:
    def __init__(self, mode:str):
        '''The mode can either be mem_save or time_save. The parameter mem_save only loads the models into the 
        memory when it is needed. This will make each of the prediction times longer. The mode time_save loads all 
        of the models into the memory at the start so that when the algorithm is predicting, it is much faster.
        In short, the mem_save mode is better if you are just going to run one or two predictions or if you are limited
        on computer memory while the time_save function is better if you are doing many predictions. '''

        mode_types = ["mem_save", "time_save"]
        if mode not in mode_types:
            raise ValueError("You are using a not correct mode type. Mode types must be either mem_save or time_save")
        
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
        if mode == "mem_save":
            self.unet_model = None
            self.unetpp_model = None
            self.fcn_model = None
            self.gan_model = None
        elif mode == "time_save":
            self.load_models()

    def load_models(self):
        self.unet_model = load_model("models/unet", custom_objects={"dice_coef": dice_coef})
        self.unetpp_model = load_model("models/unet++", custom_objects={'bce_dice_loss': bce_dice_loss, 'iou': iou})
        self.fcn_model = load_model("models/FCN", custom_objects={"dice_coef": dice_coef})
        self.gan_model = load_model("models/GAN")

    def process_image(self, folder,filename, model_name):
        IMG_WIDTH=256
        IMG_HEIGHT=256
        if model_name == "unet":
            if self.unet_model == None:
                model = load_model("models/unet", custom_objects={"dice_coef": dice_coef})
            else:
                model = self.unet_model
        elif model_name == "unetpp":    
            if self.unetpp_model == None:
                model = load_model("models/unet++", custom_objects={'bce_dice_loss': bce_dice_loss, 'iou': iou})
            else:
                model = self.unetpp_model
        elif model_name == "fcn":    
            if self.fcn_model == None:
                model = load_model("models/FCN", custom_objects={"dice_coef": dice_coef})
            else:
                model = self.fcn_model
        elif model_name == "gan":    
            if self.gan_model == None:
                model = load_model("models/GAN") 
            else:
                model = self.gan_model
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