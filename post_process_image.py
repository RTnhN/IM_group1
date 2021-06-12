import numpy as np
import scipy.ndimage as ndi
from skimage.color.colorconv import gray2rgb
from skimage.measure import regionprops
from skimage.morphology import label,binary_dilation
from skimage import img_as_bool, img_as_float
import cv2
from skimage.feature import canny

def post_processing(mask):
    mask = np.squeeze(mask * 255).astype(np.uint8)
    mask = process(mask)
    labeled_mask, labels_num = ndi.label(mask)
    post_mask = []
    if labels_num < 2:
        return mask

    for i in range(labels_num + 1):
        # 分割出n个mask
        if i == 0:  # id = 0 is for background
            continue
        mask_i = (labeled_mask == i).astype(np.uint8)
        props = regionprops(mask_i, cache=False)
        if len(props) > 0:
            prop = props[0]
            if prop.convex_area / prop.filled_area > 1.1:
                mask_i = split_mask_v1(mask_i)
        post_mask.append(mask_i)
    post_mask = np.array(post_mask)
    post_mask_combined = np.amax(post_mask, axis=0)
    labels = label(post_mask_combined)
    post_mask = labels > 0
    return post_mask

def process(img_gray):
    # green channel happends to produce slightly better results
    # than the grayscale image and other channels
    #     img_gray=img_rgb[:,:,1]#cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # morphological opening (size tuned on training data)
    circle7 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    img_open = cv2.morphologyEx(img_gray, cv2.MORPH_OPEN, circle7)
    # Otsu thresholding
    img_th = cv2.threshold(img_open, 0, 255, cv2.THRESH_OTSU)[1]
    # Invert the image in case the objects of interest are in the dark side
    if (np.sum(img_th == 255) > np.sum(img_th == 0)):
        img_th = cv2.bitwise_not(img_th)
    # second morphological opening (on binary image this time)
    bin_open = cv2.morphologyEx(img_th, cv2.MORPH_OPEN, circle7)
    # connected components
    cc = cv2.connectedComponents(bin_open)[1]
    # cc=segment_on_dt(bin_open,20)
    return cc

def split_mask_v1(mask):
    thresh = mask.copy().astype(np.uint8)
    contours, hierarchy = cv2.findContours(thresh, 2, 1)
    i = 0
    for contour in contours:
        if cv2.contourArea(contour) > 20:
            hull = cv2.convexHull(contour, returnPoints=False)
            defects = cv2.convexityDefects(contour, hull)
            if defects is None:
                continue
            points = []
            dd = []

            # In this loop we gather all defect points
            # so that they can be filtered later on.
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                d = d / 256
                dd.append(d)

            for i in range(len(dd)):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                if dd[i] > 1.0 and dd[i] / np.max(dd) > 0.2:
                    points.append(f)

            i = i + 1
            if len(points) >= 2:
                for i in range(len(points)):
                    f1 = points[i]
                    p1 = tuple(contour[f1][0])
                    nearest = None
                    min_dist = np.inf
                    for j in range(len(points)):
                        if i != j:
                            f2 = points[j]
                            p2 = tuple(contour[f2][0])
                            dist = (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])
                            if dist < min_dist:
                                min_dist = dist
                                nearest = p2

                    cv2.line(thresh, p1, nearest, [0, 0, 0], 2)
    return thresh

def colorize_image(mask, image):
    colorized = image
    image_width = image.shape[0]
    iterations = int(round(2*image_width/255))
    mask_edges = canny(mask)
    for i in range(iterations):
        mask_edges = binary_dilation(mask_edges)
    mask_edges = mask_edges*np.invert(mask)
    mask_edges_and_nuclei = mask_edges|mask
    background = np.invert(mask_edges_and_nuclei)
    image_nuclei = img_as_float(np.multiply(img_as_bool(gray2rgb(mask)),colorized))
    image_edges = img_as_float(gray2rgb(mask_edges))*255
    image_background = img_as_float(np.multiply(img_as_bool(gray2rgb(background)),colorized))
    colorized = [1,1,1]*image_nuclei + [0,1,0]*image_edges + [.5,.5,.5]*image_background
    return colorized.astype(np.uint8)




    
