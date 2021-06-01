from skimage.io import imread
import matplotlib.pyplot as plt
import requests
import base64

dir = "tmp/"
filename = "test1.jpg"

with open(dir+filename, "rb") as f:
    img = imread(f)
    f.seek(0)
    imgData = f.read()

plt.imshow(img)
plt.show()

API_path = "API"

baseURL = "http://www.imsp21g1.online"

url = baseURL + "/" + API_path

files = {"file": (filename,imgData)}

r = requests.post(url,files=files)

print(r)

print(r.json())

path = r.json()["processedFile"]

processedImg = imread(baseURL + "/" + path)

plt.imshow(processedImg)
plt.show()

r = requests.get(baseURL + "/" + path)

with open("processedImg.jpg", "wb") as f:
    f.write(r.content)



