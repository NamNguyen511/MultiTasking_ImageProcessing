import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy import ndimage

def watershed_segmentation(image, markers=None, connectivity=8):
    """Apply watershed segmentation to an image
    Args:
        image: Input image (color)
        markers: Pre-defined markers (None for automatic markers)
        connectivity: Connectivity for the watershed (4 or 8)
    
    Returns:
        Segmented image with markers
    """
    
    # Convert to grayscale if the image is color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create markers if not provided
    if markers is None:
        # Threshold the grayscale image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Noise removal with morphological operations
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)

        # Sure backkground area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)

        # Finding sure foreground area
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)

        # Finding unkown region
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)

        # Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)

        # Add one to all labels so that the background is not 0, but 1
        markers = markers + 1

        # Now, mark the unknown region as 0
        markers[unknown == 255] = 0

    # Apply Watershed
    if len(image.shape) == 2:
        # Convert grayscale to color for watershed
        color_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        markers = cv2.watershed(color_img, markers)
    else:
        # Color image can be used directly
        markers = cv2.watershed(image, markers)

    # Create a color map for visualization
    color_map = np.random.randint(0, 255, (np.max(markers) + 1, 3), dtype=np.uint8)
    color_map[0] = (0, 0, 0) # Background is black

    # Apply color map to markers
    segmented = color_map[markers]

    # Create a result with boundaries marked
    image_with_boundaries = image.copy() if len(image.shape) == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image_with_boundaries[markers == -1] = (0, 0, 255) # Mark boundaries in red
    
    return segmented, image_with_boundaries, markers


def kmeans_segmentation(image, k=3, attempts=10):
    """Apply K-means clustering for segmentation
    Args:
        image: Input image (color)
        k: Number of clusters (default=3)
        attempts: Number of K-means runs (default=10)
    Returns:
        Segmented image with k colors
    """

    # Reshape the image for k-means
    if len(image.shape) == 3:
        # For color images
        pixel_values = image.reshape((-1, 3)).astype(np.float32)
    else:
        # For grayscale images
        pixel_values = image.reshape((-1, 1)).astype(np.float32)

    # Define criteria and apply KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, attempts, cv2.KMEANS_PP_CENTERS)

    # Convert back to 8-bit values
    centers = np.uint8(centers)

    # Replace each pixel with its center value
    segmented_flat = centers[labels.flatten()]

    # Resahpe back to the original image shape
    segmented = segmented_flat.reshape(image.shape)

    # Create colored labels for visualization
    colored_labels = np.zeros((labels.shape[0], 3), dtype=np.uint8)
    
    # Generate random colors for each cluster
    colors = np.random.randint(0, 255, (k, 3), dtype=np.uint8)

    # Assign colors to each label
    for i in range(k):
        colored_labels[labels.flatten() == i] = colors[i]
    
    # Reshape colored labels to original image shape
    label_image = colored_labels.reshape(image.shape[0], image.shape[1], 3)

    return segmented, label_image, labels.reshape(image.shape[0], image.shape[1])

def grabcut_segmentation(image, rect=None, mask=None, iterCount=5):
    """Apply GrabCut algorithm for foreground extraction
    
    Args:
        image: Input color image
        rect: Rectangle containing the foreground object (x, y, width, height)
        mask: Optional mask for initialization (None for automatic)
        iterCount: Number of GrabCut iterations
        
    Returns:
        Foreground mask, foreground image
    """
    # Ensure we have a color image
    if len(image.shape) != 3:
        # Convert grayscale to color
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    # Create initial mask
    if mask is None:
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
    
    # Default rectangle if not provided (whole image with margin)
    if rect is None:
        height, width = image.shape[:2]
        margin = min(width, height) // 10
        rect = (margin, margin, width - 2*margin, height - 2*margin)
    
    # Initialize background and foreground models
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    # Apply GrabCut
    mask, bgd_model, fgd_model = cv2.grabCut(
        image, mask, rect, bgd_model, fgd_model, iterCount, cv2.GC_INIT_WITH_RECT
    )
    
    # Create mask where foreground (1) and probable foreground (3) are set to 1
    # and background (0) and probable background (2) are set to 0
    foreground_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype('uint8')
    
    # Apply the mask to extract foreground
    foreground = image * foreground_mask[:, :, np.newaxis]
    
    # Create a display mask (white for foreground, black for background)
    display_mask = foreground_mask * 255
    
    return display_mask, foreground, foreground_mask


def interactive_segmentation(image, seeds=None, threshold=0.1):
    """Apply interactive segmentation using region growing
    
    Args:
        image: Input image
        seeds: List of seed points (y, x)
        threshold: Threshold for region growing
        
    Returns:
        Segmented regions
    """
    # Convert to grayscale if color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create an empty mask to store the segmentation
    mask = np.zeros_like(gray, dtype=np.uint8)
    
    # Default seeds if not provided
    if seeds is None or len(seeds) == 0:
        seeds = [(gray.shape[0] // 2, gray.shape[1] // 2)]  # Center of the image
    
    # Process each seed point
    for i, seed in enumerate(seeds, 1):
        # Create a seed mask with only this seed point
        seed_mask = np.zeros_like(gray, dtype=np.uint8)
        seed_mask[seed[0], seed[1]] = 1
        
        # Region growing
        region = region_growing(gray, seed_mask, threshold)
        
        # Add to the final mask with a unique label
        mask[region > 0] = i
    
    # Create colored segmentation for display
    color_map = np.random.randint(0, 255, (len(seeds) + 1, 3), dtype=np.uint8)
    color_map[0] = [0, 0, 0]  # Background is black
    
    # Create segmented image
    segmented = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
    for i in range(1, len(seeds) + 1):
        segmented[mask == i] = color_map[i]
    
    # Create boundaries
    image_with_boundaries = image.copy() if len(image.shape) == 3 else cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # Mark boundaries of each region
    for i in range(1, len(seeds) + 1):
        region = (mask == i).astype(np.uint8)
        contours, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image_with_boundaries, contours, -1, (0, 255, 0), 2)
    
    return segmented, image_with_boundaries, mask


def region_growing(image, seed_mask, threshold):
    """Perform region growing from a seed mask
    
    Args:
        image: Grayscale image
        seed_mask: Binary mask with seed points
        threshold: Intensity threshold for growing
        
    Returns:
        Binary mask of the grown region
    """
    # Create markers for region
    markers = np.zeros_like(image, dtype=np.int32)
    markers[seed_mask > 0] = 1
    
    # Create a mask of processed pixels
    processed = seed_mask.copy()
    
    # Get seed values
    seed_points = np.where(seed_mask > 0)
    seed_values = image[seed_points]
    
    if len(seed_values) == 0:
        return np.zeros_like(image, dtype=np.uint8)
    
    # Calculate mean intensity of seeds
    mean_intensity = np.mean(seed_values)
    
    # Region growing by breadth-first search
    queue = list(zip(seed_points[0], seed_points[1]))
    while queue:
        y, x = queue.pop(0)
        
        # Check 4-connected neighbors
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            
            # Check if neighbor is within image bounds
            if 0 <= ny < image.shape[0] and 0 <= nx < image.shape[1]:
                # Check if neighbor is not processed and similar to seed intensity
                if processed[ny, nx] == 0 and abs(int(image[ny, nx]) - mean_intensity) <= threshold * 255:
                    # Add to region
                    markers[ny, nx] = 1
                    processed[ny, nx] = 1
                    queue.append((ny, nx))
    
    return markers 
    
