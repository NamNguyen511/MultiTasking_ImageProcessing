import cv2
import numpy as np

# Blur Images
def blur_images(image, kernel_size=(5, 5)):
    blurred = cv2.GaussianBlur(image, kernel_size, 0)
    return blurred


# Canny Edges Detection
def canny_detect_edges(image, low_threshold=50, high_threshold=150):
    edges = cv2.Canny(image, low_threshold, high_threshold)
    return edges


def morphological_filters(image, kernel_shape, operation):
    kernel_size = (5, 5)

    # Initialize Structuring Element
    kernel = cv2.getStructuringElement(kernel_shape, kernel_size)
    filtered_image = cv2.morphologyEx(image, operation, kernel)
    return filtered_image
