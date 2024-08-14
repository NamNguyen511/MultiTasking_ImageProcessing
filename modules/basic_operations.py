import os
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel


# Load and Display image
def load_image(filepath, max_width=800, max_height=600):
    if os.path.exists(filepath) and isinstance(filepath, str):
        print(f"Loading Image from: {filepath}")
        image = cv2.imread(filepath)
        if image is None:
            raise ValueError(f"Failed to load image from {filepath}")
        return resize_for_display(image, max_width, max_height)
    else:
        raise ValueError(f"File does not exist {filepath}")


def resize_for_display(image, max_width=800, max_height=600):
    height, width = image.shape[:2]
    scaling_factor = min(max_width / width, max_height / height)

    if scaling_factor < 1:
        new_size = (int(scaling_factor * width), int(scaling_factor * height))
        resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        return resized_image
    return image


def display_image(image, label):
    if len(image.shape) == 2:
        q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)
    else:
        q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_RGB888).rgbSwapped()
    # height, width, channel = image.shape
    # bytes_per_line = 3 * width

    pixmap = QPixmap.fromImage(q_image)
    label.setPixmap(pixmap)
    label.setScaledContents(True)


# Resize image based on user input
def resize_image(image, width=None, height=None):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized


# Rotate Image
def rotate_image(image, angle):
    # Get the image dimensions
    (h, w) = image.shape[:2]

    # Calculate the center of the image
    center = (w // 2, h // 2)

    # Calculate the rotation of matrix
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Calculate the cosine and sine of rotation matrix
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])

    # Compute the new bounding dimensions of the image
    new_width = int((h * sin) + (w * cos))
    new_height = int((h * cos) + (w * sin))

    # Adjust the rotation of matrix to take into account the new dimension
    matrix[0, 2] += (new_width / 2) - center[0]
    matrix[1, 2] += (new_height / 2) - center[1]

    # Perform the actual rotation and return the image
    rotated_image = cv2.warpAffine(image, matrix, (new_width, new_height), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    # Find the bounding box of the non-black areas
    gray = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        cropped_image = rotated_image[y:y+h, x:x+w]
        return cropped_image
    else:
        return rotated_image
