from skimage.io import imread
from skimage.color import grey2rgb
from skimage.transform import resize
import numpy as np

def read_one_image(image_path, IMG_WIDTH=256, IMG_HEIGHT=256, IMG_CHANNELS=3):
    X_test = np.zeros((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dtype=np.uint8)
    image = imread(image_path)
    if len(image.shape) == 2:
        image = grey2rgb(image)
    image = image[:, :, :IMG_CHANNELS]
    image_size = [image.shape[0], image.shape[1]]
    image = resize(image, (IMG_HEIGHT, IMG_WIDTH), mode='constant', preserve_range=True, anti_aliasing=True)
    image = np.expand_dims(image, axis=0)
    return image, image_size