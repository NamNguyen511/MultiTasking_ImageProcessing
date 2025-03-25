import os
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel
import logging

logger = logging.getLogger(__name__)

def validate_image(image):
    """Validate input image"""
    if image is None:
        raise ValueError("Input image is None")
    if not isinstance(image, np.ndarray):
        raise ValueError("Input must be a numpy array")
    if len(image.shape) not in [2, 3]:
        raise ValueError("Image must be 2D or 3D array")
    if image.dtype != np.uint8:
        raise ValueError("Image must be uint8 type")

def load_image(filepath, max_width=800, max_height=600):
    """Load and display image with error handling"""
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File does not exist: {filepath}")
        if not isinstance(filepath, str):
            raise TypeError("Filepath must be a string")

        logger.info(f"Loading Image from: {filepath}")
        image = cv2.imread(filepath)
        if image is None:
            raise ValueError(f"Failed to load image from {filepath}")

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return resize_for_display(image, max_width, max_height)
    except Exception as e:
        logger.error(f"Error loading image: {str(e)}")
        raise

def resize_for_display(image, max_width=800, max_height=600):
    """Resize image for display while maintaining aspect ratio"""
    try:
        validate_image(image)
        height, width = image.shape[:2]
        scaling_factor = min(max_width / width, max_height / height)

        if scaling_factor < 1:
            new_size = (int(scaling_factor * width), int(scaling_factor * height))
            resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
            logger.info(f"Image resized from {width}x{height} to {new_size[0]}x{new_size[1]}")
            return resized_image
        return image
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise

def resize_image(image, width=None, height=None):
    """Resize image to specified dimensions"""
    try:
        validate_image(image)
        if width is None and height is None:
            raise ValueError("Either width or height must be specified")

        h, w = image.shape[:2]
        if width is None:
            scaling_factor = height / h
            width = int(w * scaling_factor)
        elif height is None:
            scaling_factor = width / w
            height = int(h * scaling_factor)

        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")

        new_size = (width, height)
        resized_image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        logger.info(f"Image resized to {width}x{height}")
        return resized_image
    except Exception as e:
        logger.error(f"Error resizing image: {str(e)}")
        raise

def rotate_image(image, angle):
    """Rotate image by specified angle"""
    try:
        validate_image(image)
        if not isinstance(angle, (int, float)):
            raise TypeError("Angle must be a number")

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new image size
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        
        # Adjust translation
        matrix[0, 2] += (new_w / 2) - center[0]
        matrix[1, 2] += (new_h / 2) - center[1]
        
        rotated_image = cv2.warpAffine(image, matrix, (new_w, new_h))
        logger.info(f"Image rotated by {angle} degrees")
        return rotated_image
    except Exception as e:
        logger.error(f"Error rotating image: {str(e)}")
        raise

def crop_image(image, x, y, width, height):
    """Crop an image to the specified dimensions"""
    try:
        validate_image(image)
        if not all(isinstance(v, (int, float)) for v in [x, y, width, height]):
            raise TypeError("All crop parameters must be numbers")
        
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid crop parameters")
        
        h, w = image.shape[:2]
        if x + width > w or y + height > h:
            raise ValueError("Crop dimensions exceed image size")
        
        cropped = image[y:y+height, x:x+width]
        logger.info(f"Image cropped to {width}x{height} at position ({x}, {y})")
        return cropped
    except Exception as e:
        logger.error(f"Error cropping image: {str(e)}")
        raise

def flip_image(image, flip_code):
    """Flip an image horizontally, vertically, or both"""
    try:
        validate_image(image)
        if not isinstance(flip_code, int):
            raise TypeError("Flip code must be an integer")
        
        if flip_code not in [-1, 0, 1]:
            raise ValueError("Invalid flip code. Use 0 for vertical, 1 for horizontal, or -1 for both")
        
        flipped = cv2.flip(image, flip_code)
        logger.info(f"Image flipped with code {flip_code}")
        return flipped
    except Exception as e:
        logger.error(f"Error flipping image: {str(e)}")
        raise

def save_image(image, filepath):
    """Save image to file"""
    try:
        validate_image(image)
        if not isinstance(filepath, str):
            raise TypeError("Filepath must be a string")

        # Convert RGB to BGR for OpenCV
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        success = cv2.imwrite(filepath, image)
        if not success:
            raise ValueError(f"Failed to save image to {filepath}")
        
        logger.info(f"Image saved successfully to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")
        raise
