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


def sobel_edge_detection(image, operation):
    # Smooth an image with Gaussian Blur
    image = cv2.GaussianBlur(image, (3, 3), 0)

    # Convert color image to gray
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    
# Advanced Filters for Phase 2

def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """Apply bilateral filter for edge-preserving noise reduction
    
    Args:
        image: Input image
        d: Diameter of each pixel neighborhood
        sigma_color: Filter sigma in the color space
        sigma_space: Filter sigma in the coordinate space
        
    Returns:
        Filtered image
    """
    filtered = cv2.bilateralFilter(image, d, sigma_color, sigma_space)
    return filtered


def median_filter(image, kernel_size=5):
    """Apply median filter for salt-and-pepper noise removal
    
    Args:
        image: Input image
        kernel_size: Size of the median filter kernel
        
    Returns:
        Filtered image
    """
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
        
    filtered = cv2.medianBlur(image, kernel_size)
    return filtered


def nlm_denoise(image, h=10, template_window_size=7, search_window_size=21):
    """Apply Non-Local Means denoising algorithm
    
    Args:
        image: Input image
        h: Filter strength (higher h removes more noise but also more details)
        template_window_size: Size of template patch for similarity evaluation
        search_window_size: Size of window for searching similar patches
        
    Returns:
        Denoised image
    """
    # Handle grayscale vs color images differently
    if len(image.shape) == 2:
        # Grayscale image
        filtered = cv2.fastNlMeansDenoising(
            image, 
            None, 
            h=h, 
            templateWindowSize=template_window_size,
            searchWindowSize=search_window_size
        )
    else:
        # Color image
        filtered = cv2.fastNlMeansDenoisingColored(
            image, 
            None, 
            h=h, 
            hColor=h, 
            templateWindowSize=template_window_size,
            searchWindowSize=search_window_size
        )
    return filtered


def custom_kernel_filter(image, kernel):
    """Apply a custom filter kernel to an image
    
    Args:
        image: Input image
        kernel: Custom filter kernel as numpy array
        
    Returns:
        Filtered image
    """
    # Ensure kernel is properly normalized
    kernel = np.array(kernel, dtype=np.float32)
    kernel_sum = np.sum(kernel)
    
    # Normalize the kernel if it's not already normalized
    if abs(kernel_sum) > 1e-10 and abs(kernel_sum - 1.0) > 1e-10:
        kernel = kernel / kernel_sum
        
    # Apply the filter
    filtered = cv2.filter2D(image, -1, kernel)
    return filtered


