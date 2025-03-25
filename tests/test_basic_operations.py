import unittest
import numpy as np
import cv2
import os
import tempfile
from modules.basic_operations import (
    crop_image, flip_image, resize_image, rotate_image,
    save_image, validate_image, load_image
)
from modules.pipeline_manager import (
    PipelineManager, CropOperation, FlipOperation,
    OperationError
)

class TestBasicOperations(unittest.TestCase):
    def setUp(self):
        # Create a test image
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image[25:75, 25:75] = 255  # White square in the middle
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_validate_image(self):
        # Test valid image
        validate_image(self.test_image)
        
        # Test invalid inputs
        with self.assertRaises(ValueError):
            validate_image(None)
        with self.assertRaises(ValueError):
            validate_image([1, 2, 3])
        with self.assertRaises(ValueError):
            validate_image(np.array([1, 2, 3], dtype=np.float32))

    def test_crop_image(self):
        # Test valid crop
        cropped = crop_image(self.test_image, 25, 25, 50, 50)
        self.assertEqual(cropped.shape, (50, 50, 3))
        self.assertTrue(np.all(cropped == 255))

        # Test invalid crop parameters
        with self.assertRaises(ValueError):
            crop_image(self.test_image, -1, 25, 50, 50)
        with self.assertRaises(ValueError):
            crop_image(self.test_image, 25, 25, 100, 50)
        with self.assertRaises(TypeError):
            crop_image(self.test_image, "25", 25, 50, 50)

    def test_flip_image(self):
        # Test horizontal flip
        flipped_h = flip_image(self.test_image, 1)
        self.assertEqual(flipped_h.shape, self.test_image.shape)
        
        # Test vertical flip
        flipped_v = flip_image(self.test_image, 0)
        self.assertEqual(flipped_v.shape, self.test_image.shape)
        
        # Test both flips
        flipped_both = flip_image(self.test_image, -1)
        self.assertEqual(flipped_both.shape, self.test_image.shape)
        
        # Test invalid flip code
        with self.assertRaises(ValueError):
            flip_image(self.test_image, 2)
        with self.assertRaises(TypeError):
            flip_image(self.test_image, "1")

    def test_resize_image(self):
        # Test resize with width
        resized_w = resize_image(self.test_image, width=50)
        self.assertEqual(resized_w.shape[1], 50)
        
        # Test resize with height
        resized_h = resize_image(self.test_image, height=50)
        self.assertEqual(resized_h.shape[0], 50)
        
        # Test resize with both dimensions
        resized_both = resize_image(self.test_image, width=50, height=50)
        self.assertEqual(resized_both.shape, (50, 50, 3))
        
        # Test invalid parameters
        with self.assertRaises(ValueError):
            resize_image(self.test_image)
        with self.assertRaises(ValueError):
            resize_image(self.test_image, width=-1)

    def test_rotate_image(self):
        # Test rotation by 90 degrees
        rotated = rotate_image(self.test_image, 90)
        self.assertEqual(rotated.shape, (100, 100, 3))
        
        # Test rotation by 45 degrees
        rotated = rotate_image(self.test_image, 45)
        self.assertTrue(rotated.shape[0] > 100 or rotated.shape[1] > 100)
        
        # Test invalid angle
        with self.assertRaises(TypeError):
            rotate_image(self.test_image, "90")

    def test_save_and_load_image(self):
        # Test saving image
        temp_path = os.path.join(self.temp_dir, "test.png")
        self.assertTrue(save_image(self.test_image, temp_path))
        
        # Test loading image
        loaded = load_image(temp_path)
        self.assertEqual(loaded.shape, self.test_image.shape)
        np.testing.assert_array_equal(loaded, self.test_image)
        
        # Test invalid file path
        with self.assertRaises(FileNotFoundError):
            load_image("nonexistent.png")
        with self.assertRaises(TypeError):
            save_image(self.test_image, 123)

class TestPipelineManager(unittest.TestCase):
    def setUp(self):
        self.pipeline = PipelineManager()
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.test_image[25:75, 25:75] = 255
        self.pipeline.set_image(self.test_image)

    def test_add_operation(self):
        # Test adding crop operation
        crop_op = CropOperation(25, 25, 50, 50)
        self.pipeline.add_operation(crop_op)
        self.assertEqual(len(self.pipeline.operations), 1)
        self.assertEqual(self.pipeline.current_image.shape, (50, 50, 3))

        # Test adding flip operation
        flip_op = FlipOperation(1)
        self.pipeline.add_operation(flip_op)
        self.assertEqual(len(self.pipeline.operations), 2)

        # Test invalid operation
        with self.assertRaises(OperationError):
            self.pipeline.add_operation("invalid")

    def test_undo_redo(self):
        # Add operations
        crop_op = CropOperation(25, 25, 50, 50)
        self.pipeline.add_operation(crop_op)
        flip_op = FlipOperation(1)
        self.pipeline.add_operation(flip_op)

        # Test undo
        self.assertTrue(self.pipeline.undo())
        self.assertEqual(len(self.pipeline.operations), 1)
        self.assertEqual(self.pipeline.current_image.shape, (50, 50, 3))

        # Test redo
        self.assertTrue(self.pipeline.redo())
        self.assertEqual(len(self.pipeline.operations), 2)

        # Test undo limit
        for _ in range(22):  # More than max_undo_steps
            self.pipeline.add_operation(FlipOperation(1))
        self.assertEqual(len(self.pipeline.undo_stack), 20)

    def test_reset(self):
        # Add operations
        crop_op = CropOperation(25, 25, 50, 50)
        self.pipeline.add_operation(crop_op)
        flip_op = FlipOperation(1)
        self.pipeline.add_operation(flip_op)

        # Test reset
        self.assertTrue(self.pipeline.reset())
        self.assertEqual(len(self.pipeline.operations), 0)
        self.assertEqual(self.pipeline.current_image.shape, self.test_image.shape)

    def test_get_operation_history(self):
        # Add operations
        crop_op = CropOperation(25, 25, 50, 50)
        self.pipeline.add_operation(crop_op)
        flip_op = FlipOperation(1)
        self.pipeline.add_operation(flip_op)

        # Test operation history
        history = self.pipeline.get_operation_history()
        self.assertEqual(history, ['CropOperation', 'FlipOperation'])

    def test_get_current_state(self):
        # Add operation
        crop_op = CropOperation(25, 25, 50, 50)
        self.pipeline.add_operation(crop_op)

        # Test current state
        state = self.pipeline.get_current_state()
        self.assertEqual(len(state['operations']), 1)
        self.assertTrue(state['can_undo'])
        self.assertFalse(state['can_redo'])

if __name__ == '__main__':
    unittest.main()
