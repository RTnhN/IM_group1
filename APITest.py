from skimage.io import imread
import matplotlib.pyplot as plt
import requests
import json

# Load file code
DIR = "tmp/"
filename = "test1.jpg"
with open(DIR+filename, "rb") as f:
    img = imread(f)
    f.seek(0)
    imgData = f.read()
plt.imshow(img)
plt.show()

# Make API request code
# Note: this goes out to the website. I have been trying to save resources, so this website is not running
# all the time. To use with the local flask, just change the base_url to the same that the local flask uses.
API_path = "API"
base_URL = "http://www.imsp21g1.online"
url = base_URL + "/" + API_path
model = {"model":"unet"} # Must be unet, unetpp, or fcn
files = {"json":(None, json.dumps(model)),  "file": (filename,imgData)}
r = requests.post(url,files=files)

# Receive API code
print(r)
print(r.json())
path = r.json()["processed_file"]
processed_image = imread(base_URL + "/" + path)
plt.imshow(processed_image)
plt.show()
r = requests.get(base_URL + "/" + path)
with open("processed_image.jpg", "wb") as f:
    f.write(r.content)



