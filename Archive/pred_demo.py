
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt
from skimage.io import imread
from skimage.transform import resize

model = load_model('nuclei_model.h5')
# test file
print("\n data preparation")
TEST_PATH = 'test/'
IMG_WIDTH = 128
IMG_HEIGHT = 128
IMG_CHANNELS = 3

X_test = np.zeros((66, IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dtype=np.uint8)

for i in range(1,66):
    j = i-1
    img = imread(TEST_PATH + '%d.png' % j)[:,:,:IMG_CHANNELS]
    img = resize(img, (IMG_HEIGHT, IMG_WIDTH), mode='constant', preserve_range=True)
    X_test[i] = img

print("\n prediction")
# predict
preds_test = model.predict(X_test, verbose=1)
preds_test_t = (preds_test > 0.5).astype(np.uint8)

# plot
fig, axes = plt.subplots(1, 10, figsize=(20,3))
fig.suptitle('Images', fontsize=15)
axes = axes.flatten()
for img, ax in zip(X_test[1:10], axes[:10]): # here can change the scale
    ax.imshow(img)
    ax.axis('off')
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 10, figsize=(20,3))
fig.suptitle('Predicted Masks', fontsize=15)
axes = axes.flatten()
for img, ax in zip(preds_test[1:10], axes[:10]): # here can change the scale
    ax.imshow(np.squeeze(img, -1), cmap='gray')
    ax.axis('off')
plt.tight_layout()
plt.show()