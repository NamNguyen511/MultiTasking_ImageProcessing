import sys
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.segmentation import (
    watershed_segmentation,
    kmeans_segmentation,
    grabcut_segmentation,
    interactive_segmentation
)

def display_results(images, titles, figsize=(15, 10)):
    """Display multiple images with titles"""
    fig, axes = plt.subplots(1, len(images), figsize=figsize)
    for i, (image, title) in enumerate(zip(images, titles)):
        if len(image.shape) == 2:
            axes[i].imshow(image, cmap='gray')
        else:
            # OpenCV uses BGR, matplotlib uses RGB
            if image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            axes[i].imshow(image)
        axes[i].set_title(title)
        axes[i].axis('off')
    plt.tight_layout()
    plt.show()

def main():
    # Check if an image path was provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a default image if none provided
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, 'sample.jpg')
        
        # If the sample image doesn't exist, create a synthetic one
        if not os.path.exists(image_path):
            print(f"Sample image not found at {image_path}")
            print("Creating a synthetic test image instead...")
            
            # Create a simple test image with shapes
            image = np.zeros((300, 300, 3), dtype=np.uint8)
            # Background
            image[:, :] = (200, 200, 200)
            # Draw a green circle
            cv2.circle(image, (150, 150), 60, (0, 255, 0), -1)
            # Draw a blue rectangle
            cv2.rectangle(image, (50, 50), (100, 100), (255, 0, 0), -1)
            # Draw a red rectangle
            cv2.rectangle(image, (200, 200), (250, 250), (0, 0, 255), -1)
            # Save the image
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            cv2.imwrite(image_path, image)
    
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    # Display the original image
    display_results([image], ["Original Image"])
    
    # 1. Watershed Segmentation
    print("Applying Watershed Segmentation...")
    segmented, image_with_boundaries, _ = watershed_segmentation(image)
    display_results(
        [image, segmented, image_with_boundaries], 
        ["Original", "Watershed Segmentation", "Watershed Boundaries"]
    )
    
    # 2. K-means Segmentation
    print("Applying K-means Segmentation...")
    segmented, label_image, _ = kmeans_segmentation(image, k=4)
    display_results(
        [image, segmented, label_image], 
        ["Original", "K-means Segmentation (k=4)", "K-means Labels"]
    )
    
    # 3. GrabCut Segmentation
    print("Applying GrabCut Segmentation...")
    # Define a rectangle in the center of the image
    h, w = image.shape[:2]
    rect = (w//4, h//4, w//2, h//2)
    mask, foreground, _ = grabcut_segmentation(image, rect=rect)
    display_results(
        [image, mask, foreground], 
        ["Original", "GrabCut Mask", "GrabCut Foreground"]
    )
    
    # 4. Interactive Segmentation
    print("Applying Interactive Segmentation...")
    # Define seed points (center and each quadrant)
    h, w = image.shape[:2]
    seeds = [
        (h//2, w//2),              # Center
        (h//4, w//4),              # Top-left
        (h//4, 3*w//4),            # Top-right
        (3*h//4, w//4),            # Bottom-left
        (3*h//4, 3*w//4)           # Bottom-right
    ]
    segmented, image_with_boundaries, _ = interactive_segmentation(image, seeds=seeds, threshold=0.2)
    display_results(
        [image, segmented, image_with_boundaries], 
        ["Original", "Interactive Segmentation", "Interactive Boundaries"]
    )
    
    print("Demo completed successfully!")

if __name__ == "__main__":
    main() 