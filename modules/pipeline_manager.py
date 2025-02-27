from abc import ABC, abstractmethod
import cv2
import numpy as np

# Import existing processing functions from modules
from modules.basic_operations import resize_image, rotate_image
from modules.color_processing import hue_saturation_adjustment, color_balance_adjustment
from modules.filtering import blur_images, canny_detect_edges, morphological_filters


# Abstract base class for all operations
class Operation(ABC):
    @abstractmethod
    def apply(self, image):
        """Apply the operation on the given image
        and return the result"""
        pass

class ResizeOperation(Operation):
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def apply(self, image):
        return resize_image(image, width=self.width, height=self.height)

class RotateOperation(Operation):
    def __init__(self, angle):
        self.angle = angle

    def apply(self, image):
        return rotate_image(image, self.angle)

class HueSaturationOperation(Operation):
    def __init__(self, hue, saturation):
        self.hue = hue
        self.saturation = saturation

    def apply(self, image):
        return hue_saturation_adjustment(image, hue=self.hue, saturation=self.saturation)

class ColorBalanceAdjustment(Operation):
    def __init__(self, red_balance, blue_balance, green_balance):
        self.red_balance = red_balance
        self.blue_balance = blue_balance
        self.green_balance = green_balance

    def apply(self, image):
        return color_balance_adjustment(image, red_balance=self.red_balance, green_balance=self.green_balance, blue_balance=self.blue_balance)

class BlurOperation(Operation):
    def __init__(self, kernel_size=(5,5)):
        self.kernel_size = kernel_size

    def apply(self, image):
        return blur_images(image, kernel_size=self.kernel_size)

class MorphOperations(Operation):
    def __int__(self, kernel_shape, operation):
        self.kernel_shape = kernel_shape
        self.operation = operation

    def apply(self, image):
        return morphological_filters(image, kernel_shape=self.kernel_shape, operation=self.operation)

class SobelEdgeDetectionOperation(Operation):
    def __int__(self, mode="Vertical"):
        self.mode = mode

    def apply(self, image):
        image = cv2.GaussianBlur(image, (3, 3), 0)
        gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.mode.lower() == 'vertical':
            sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
        else:
            sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
        abs_sobel = cv2.convertScaleAbs(sobel)
        return abs_sobel

class GammaCorrectionOperation(Operation):
    def __init__(self, gamma=1.0):
        self.gamma = gamma

    def apply(self, image):
        # Build a lookup table mapping pixel values [0, 255] to their adjusted gamma values.
        invGamma = 1.0 / self.gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(256)]).astype("uint8")
        corrected = cv2.LUT(image, table)
        return corrected

class SharpenOperation(Operation):
    def __init__(self, kernel=None):
        # Default sharpening kernel if none provided
        if kernel is None:
            self.kernel = np.array([[0, -1, 0],
                                    [-1, 5, -1],
                                    [0, -1, 0]])
        else:
            self.kernel = kernel

    def apply(self, image):
        sharpened = cv2.filter2D(image, -1, self.kernel)
        return sharpened

class CropOperation(Operation):
    def __init__(self, x, y, width, height):
        """
        Crop the image to the rectangle starting at (x, y) with given width and height.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def apply(self, image):
        # Ensure crop coordinates are within image bounds
        h, w = image.shape[:2]
        x1 = max(0, self.x)
        y1 = max(0, self.y)
        x2 = min(w, self.x + self.width)
        y2 = min(h, self.y + self.height)
        return image[y1:y2, x1:x2]

# Pipeline Manager
class PipelineManager:
    def __init__(self, original_image):
        self.original_image = original_image # Keep the untouched image
        self.operations = []
        self.undo_stack = []
        self.redo_stack = []
        self.current_image = original_image.copy()

    def add_operation(self, operation):
        """Append operation and reprocess the image"""
        self.operations.append(operation)
        self.undo_stack.append(('add', operation))
        self.redo_stack.clear()
        self.reprocess()

    def remove_operation(self, index):
        """Remove an operation by index and reprocess"""
        if 0 <= index < len(self.operations):
            removed_op = self.operations.pop(index)
            self.undo_stack.append(('remove', index, removed_op))
            self.redo_stack.clear()
            self.reprocess()

    def update_operation(self, index, new_operation):
        """Update operation at a specific and reprocess"""
        if 0 <= index < len(self.operations):
            old_operation = self.operations[index]
            self.operations[index] = new_operation
            self.undo_stack.append(('update', index, old_operation))
            self.redo_stack.clear()
            self.reprocess()

    def clear_operation(self):
        """Clear all operations and reset image"""
        previous_ops = self.operations.copy()
        self.operations.clear()
        self.undo_stack.append(('clear', previous_ops))
        self.redo_stack.clear()
        self.operations = []
        self.current_image = self.original_image.copy()

    def undo(self):
        """Undo the last action in the pipeline"""
        if not self.undo_stack:
            return # Nothing to undo

        action = self.undo_stack.pop()
        action_type = action[0]

        if action_type == 'add':
            op = action[1]
            if self.operations and self.operations[-1] == op:
                self.operations.pop()
                self.redo_stack.append(('add', op))
        elif action_type == 'remove':
            index, op = action[1], action[2]
            self.operations.insert(index, op)
            self.redo_stack.append(('remove', index, op))
        elif action_type == 'update':
            index, old_op = action[1], action[2]
            new_op = self.operations[index]
            self.operations[index] = old_op
            self.redo_stack.append(('update', index, new_op))
        elif action_type == 'clear':
            previous_ops = action[1]
            self.operations = previous_ops
            self.redo_stack.append(('clear', None))
        self.reprocess()

    def redo(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return  # Nothing to redo

        action = self.redo_stack.pop()
        action_type = action[0]

        if action_type == 'add':
            op = action[1]
            self.operations.append(op)
            self.undo_stack.append(('add', op))
        elif action_type == 'remove':
            index, op = action[1], action[2]
            if 0 <= index < len(self.operations):
                self.operations.pop(index)
            self.undo_stack.append(('remove', index, op))
        elif action_type == 'update':
            index, new_op = action[1], action[2]
            old_op = self.operations[index]
            self.operations[index] = new_op
            self.undo_stack.append(('update', index, old_op))
        elif action_type == 'clear':
            previous_ops = self.operations.copy()
            self.operations.clear()
            self.undo_stack.append(('clear', previous_ops))
        self.reprocess()
    def reprocess(self):
        """Reaply all operations sequantially on the original image"""
        image = self.original_image.copy()
        for op in self.operations:
            image = op.apply(image)
        self.current_image = image
        return self.current_image