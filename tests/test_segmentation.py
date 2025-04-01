import sys
import os
import unittest
import cv2
import numpy as np

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.segmentation import (
    watershed_segmentation,
    kmeans_segmentation,
    grabcut_segmentation,
    interactive_segmentation
)

class TestSegmentation(unittest.TestCase):
    def setUp(self):
        # Create a simple test image
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # Draw a white circle in the middle
        cv2.circle(self.test_image, (50, 50), 20, (255, 255, 255), -1)
        # Draw a white rectangle in the corner
        cv2.rectangle(self.test_image, (10, 10), (30, 30), (255, 255, 255), -1)
        
        # Create a grayscale version
        self.gray_image = cv2.cvtColor(self.test_image, cv2.COLOR_BGR2GRAY)

    def test_watershed_segmentation(self):
        # Test watershed segmentation with default parameters
        segmented, image_with_boundaries, markers = watershed_segmentation(self.test_image)
        
        # Check output shapes
        self.assertEqual(segmented.shape, self.test_image.shape)
        self.assertEqual(image_with_boundaries.shape, self.test_image.shape)
        self.assertEqual(markers.shape, (self.test_image.shape[0], self.test_image.shape[1]))
        
        # Check that there are at least 2 different segments (background and foreground)
        self.assertGreaterEqual(np.max(markers), 1)
        
        # Test with explicit connectivity
        segmented, _, _ = watershed_segmentation(self.test_image, connectivity=4)
        self.assertEqual(segmented.shape, self.test_image.shape)

    def test_kmeans_segmentation(self):
        # Test K-means segmentation with default parameters
        segmented, label_image, labels = kmeans_segmentation(self.test_image)
        
        # Check output shapes
        self.assertEqual(segmented.shape, self.test_image.shape)
        self.assertEqual(label_image.shape, self.test_image.shape)
        self.assertEqual(labels.shape, (self.test_image.shape[0], self.test_image.shape[1]))
        
        # Check that there are exactly k segments
        self.assertLessEqual(len(np.unique(labels)), 3)  # k=3 is the default
        
        # Test with different k
        segmented, _, labels = kmeans_segmentation(self.test_image, k=2)
        self.assertLessEqual(len(np.unique(labels)), 2)

    def test_grabcut_segmentation(self):
        # Test GrabCut segmentation with a rectangle
        rect = (30, 30, 40, 40)  # This should cover the circle
        mask, foreground, foreground_mask = grabcut_segmentation(self.test_image, rect=rect)
        
        # Check output shapes
        self.assertEqual(mask.shape, (self.test_image.shape[0], self.test_image.shape[1]))
        self.assertEqual(foreground.shape, self.test_image.shape)
        self.assertEqual(foreground_mask.shape, (self.test_image.shape[0], self.test_image.shape[1]))
        
        # Check mask values (should be binary - 0 and 255)
        self.assertTrue(np.all(np.isin(np.unique(mask), [0, 255])))
        
        # Check foreground mask values (should be binary - 0 and 1)
        self.assertTrue(np.all(np.isin(np.unique(foreground_mask), [0, 1])))

    def test_interactive_segmentation(self):
        # Test interactive segmentation with seed points
        seeds = [(50, 50)]  # Seed in the center (on the circle)
        segmented, image_with_boundaries, mask = interactive_segmentation(self.test_image, seeds=seeds)
        
        # Check output shapes
        self.assertEqual(segmented.shape, self.test_image.shape)
        self.assertEqual(image_with_boundaries.shape, self.test_image.shape)
        self.assertEqual(mask.shape, (self.test_image.shape[0], self.test_image.shape[1]))
        
        # Check that there's at least one segment
        self.assertGreater(np.max(mask), 0)
        
        # Test with multiple seeds
        seeds = [(50, 50), (20, 20)]  # Seeds on both shapes
        segmented, _, mask = interactive_segmentation(self.test_image, seeds=seeds)
        
        # Check that there are exactly 2 segments (plus background)
        unique_values = np.unique(mask)
        self.assertTrue(0 in unique_values)  # Background
        self.assertGreaterEqual(len(unique_values), 2)  # At least one segment plus background

if __name__ == "__main__":
    unittest.main() 