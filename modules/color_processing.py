import cv2
import numpy as np


def hue_saturation_adjustment(image, hue, saturation):
    # Convert image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Adjust hue and saturation
    hsv_image = np.float32(hsv_image)
    hsv_image[..., 0] += hue
    hsv_image[..., 1] += np.clip(hsv_image[..., 1] + saturation, 0, 255)

    # Convert back to BGR color space
    hsv_image = np.uint8(hsv_image)
    adjusted_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    return adjusted_image


def color_balance_adjustment(image, red_balance, green_balance, blue_balance):
    # Split the image into RGB components
    b, g, r = cv2.split(image)

    # Adjust the balance for each channel
    r = np.clip(r + red_balance, 0, 255)
    g = np.clip(g + green_balance, 0, 255)
    b = np.clip(b + blue_balance, 0, 255)

    # Merge the channels back to one image
    adjusted_image = cv2.merge([b, g, r])
    return adjusted_image
