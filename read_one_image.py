from skimage.io import imread
from skimage.color import grey2rgb
from skimage.transform import resize
import numpy as np

def read_one_image(imagePath, IMG_WIDTH=256, IMG_HEIGHT=256, IMG_CHANNELS=3):
    X_test = np.zeros((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dtype=np.uint8)
    img = imread(imagePath)
    if len(img.shape) == 2:
        img = grey2rgb(img)
    img = img[:, :, :IMG_CHANNELS]
    imSize = [img.shape[0], img.shape[1]]
    img = resize(img, (IMG_HEIGHT, IMG_WIDTH), mode='constant', preserve_range=True,anti_aliasing=True)
    img = np.expand_dims(img, axis=0)
    return img, imSize