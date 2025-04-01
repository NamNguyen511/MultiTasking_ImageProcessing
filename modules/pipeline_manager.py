import logging
from abc import ABC, abstractmethod
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import existing processing functions from modules
from modules.basic_operations import resize_image, rotate_image, crop_image, flip_image
from modules.color_processing import hue_saturation_adjustment, color_balance_adjustment
from modules.filtering import (blur_images, canny_detect_edges, morphological_filters, 
                              bilateral_filter, median_filter, nlm_denoise, 
                              custom_kernel_filter)
from modules.segmentation import (watershed_segmentation, kmeans_segmentation, 
                                 grabcut_segmentation, interactive_segmentation)

class OperationError(Exception):
    """Custom exception for operation-related errors"""
    pass

# Abstract base class for all operations
class Operation(ABC):
    @abstractmethod
    def apply(self, image):
        """Apply the operation on the given image and return the result"""
        pass

    def validate_image(self, image):
        """Validate input image"""
        if image is None:
            raise OperationError("Input image is None")
        if not isinstance(image, np.ndarray):
            raise OperationError("Input must be a numpy array")
        if len(image.shape) not in [2, 3]:
            raise OperationError("Image must be 2D or 3D array")
        if image.dtype != np.uint8:
            raise OperationError("Image must be uint8 type")

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
        try:
            # Validate input
            self.validate_image(image)
            
            # Ensure angle is within valid range
            self.angle = self.angle % 360
            
            # Get image dimensions
            height, width = image.shape[:2]
            
            # Get rotation matrix
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, self.angle, 1.0)
            
            # Calculate new dimensions
            cos = np.abs(rotation_matrix[0, 0])
            sin = np.abs(rotation_matrix[0, 1])
            new_width = int((height * sin) + (width * cos))
            new_height = int((height * cos) + (width * sin))
            
            # Adjust rotation matrix
            rotation_matrix[0, 2] += (new_width / 2) - center[0]
            rotation_matrix[1, 2] += (new_height / 2) - center[1]
            
            # Perform rotation
            rotated = cv2.warpAffine(
                image,
                rotation_matrix,
                (new_width, new_height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(255, 255, 255) if len(image.shape) == 3 else 255
            )
            
            return rotated
            
        except Exception as e:
            logger.error(f"Error in rotation operation: {str(e)}")
            raise OperationError(f"Failed to rotate image: {str(e)}")

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
    def __init__(self, kernel_shape, operation):
        self.kernel_shape = kernel_shape
        self.operation = operation

    def apply(self, image):
        # Convert to grayscale if input is color
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return morphological_filters(image, kernel_shape=self.kernel_shape, operation=self.operation)

class SobelEdgeDetectionOperation(Operation):
    def __init__(self, mode="Vertical"):
        self.mode = mode

    def apply(self, image):
        # Convert to grayscale if input is color
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply Sobel operator
        if self.mode.lower() == 'vertical':
            sobel = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        else:
            sobel = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
            
        # Convert back to uint8
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
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def apply(self, image):
        return crop_image(image, self.x, self.y, self.width, self.height)

class FlipOperation(Operation):
    def __init__(self, flip_code):
        self.flip_code = flip_code

    def apply(self, image):
        return flip_image(image, self.flip_code)

# Advanced Filter Operations for Phase 2
class BilateralFilterOperation(Operation):
    """Advanced edge-preserving smoothing filter operation"""
    def __init__(self, d=9, sigma_color=75, sigma_space=75):
        self.d = d  # Diameter of each pixel neighborhood
        self.sigma_color = sigma_color  # Filter sigma in the color space
        self.sigma_space = sigma_space  # Filter sigma in the coordinate space
        
    def apply(self, image):
        try:
            self.validate_image(image)
            return bilateral_filter(image, self.d, self.sigma_color, self.sigma_space)
        except Exception as e:
            logger.error(f"Error in bilateral filter operation: {str(e)}")
            raise OperationError(f"Failed to apply bilateral filter: {str(e)}")
            
    def __str__(self):
        return f"Bilateral Filter (d={self.d}, color={self.sigma_color}, space={self.sigma_space})"

class MedianFilterOperation(Operation):
    """Median filter for salt-and-pepper noise removal"""
    def __init__(self, kernel_size=5):
        self.kernel_size = kernel_size
        
    def apply(self, image):
        try:
            self.validate_image(image)
            # Ensure kernel size is odd
            if self.kernel_size % 2 == 0:
                self.kernel_size += 1
            return median_filter(image, self.kernel_size)
        except Exception as e:
            logger.error(f"Error in median filter operation: {str(e)}")
            raise OperationError(f"Failed to apply median filter: {str(e)}")
            
    def __str__(self):
        return f"Median Filter (kernel size={self.kernel_size})"

class NLMDenoiseOperation(Operation):
    """Non-Local Means denoising algorithm for advanced noise removal"""
    def __init__(self, h=10, template_window_size=7, search_window_size=21):
        self.h = h  # Filter strength
        self.template_window_size = template_window_size
        self.search_window_size = search_window_size
        
    def apply(self, image):
        try:
            self.validate_image(image)
            return nlm_denoise(
                image, 
                self.h, 
                self.template_window_size, 
                self.search_window_size
            )
        except Exception as e:
            logger.error(f"Error in NLM denoise operation: {str(e)}")
            raise OperationError(f"Failed to apply NLM denoising: {str(e)}")
            
    def __str__(self):
        return f"NLM Denoising (h={self.h}, template={self.template_window_size}, search={self.search_window_size})"

class CustomKernelOperation(Operation):
    """Apply a custom filter kernel to an image"""
    def __init__(self, kernel):
        self.kernel = np.array(kernel, dtype=np.float32)
        
    def apply(self, image):
        try:
            self.validate_image(image)
            return custom_kernel_filter(image, self.kernel)
        except Exception as e:
            logger.error(f"Error in custom kernel operation: {str(e)}")
            raise OperationError(f"Failed to apply custom kernel: {str(e)}")
            
    def __str__(self):
        # Format kernel for display, truncate if too large
        if self.kernel.size > 9:
            kernel_str = "custom matrix"
        else:
            kernel_str = str(self.kernel).replace('\n', '')
        return f"Custom Kernel Filter ({kernel_str})"

# Image Segmentation Operations for Phase 2
class WatershedSegmentationOperation(Operation):
    """Watershed algorithm for image segmentation"""
    def __init__(self, connectivity=8):
        self.connectivity = connectivity
        
    def apply(self, image):
        try:
            self.validate_image(image)
            segmented, image_with_boundaries, _ = watershed_segmentation(image, connectivity=self.connectivity)
            # Return the image with boundaries for display
            return image_with_boundaries
        except Exception as e:
            logger.error(f"Error in watershed segmentation: {str(e)}")
            raise OperationError(f"Failed to apply watershed segmentation: {str(e)}")
            
    def __str__(self):
        return f"Watershed Segmentation (connectivity={self.connectivity})"

class KMeansSegmentationOperation(Operation):
    """K-means clustering for color-based segmentation"""
    def __init__(self, k=3, attempts=10, use_labels=False):
        self.k = k
        self.attempts = attempts
        self.use_labels = use_labels  # Whether to use colored labels or segmented image
        
    def apply(self, image):
        try:
            self.validate_image(image)
            segmented, label_image, _ = kmeans_segmentation(image, k=self.k, attempts=self.attempts)
            # Return either the segmented image or the colored labels
            return label_image if self.use_labels else segmented
        except Exception as e:
            logger.error(f"Error in k-means segmentation: {str(e)}")
            raise OperationError(f"Failed to apply k-means segmentation: {str(e)}")
            
    def __str__(self):
        return f"K-Means Segmentation (k={self.k}, attempts={self.attempts})"

class GrabCutSegmentationOperation(Operation):
    """GrabCut algorithm for foreground extraction"""
    def __init__(self, rect=None, iter_count=5, extract_foreground=True):
        self.rect = rect  # Tuple (x, y, width, height) or None for auto
        self.iter_count = iter_count
        self.extract_foreground = extract_foreground  # Whether to return mask or foreground
        
    def apply(self, image):
        try:
            self.validate_image(image)
            # Ensure the image is color (required for GrabCut)
            if len(image.shape) != 3:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                
            display_mask, foreground, _ = grabcut_segmentation(
                image, rect=self.rect, iterCount=self.iter_count
            )
            
            # Return either the foreground extraction or the binary mask
            return foreground if self.extract_foreground else display_mask
        except Exception as e:
            logger.error(f"Error in GrabCut segmentation: {str(e)}")
            raise OperationError(f"Failed to apply GrabCut segmentation: {str(e)}")
            
    def __str__(self):
        rect_str = str(self.rect) if self.rect else "auto"
        return f"GrabCut Foreground Extraction (rect={rect_str}, iterations={self.iter_count})"

class InteractiveSegmentationOperation(Operation):
    """Interactive segmentation using region growing"""
    def __init__(self, seeds=None, threshold=0.1):
        self.seeds = seeds
        self.threshold = threshold
        
    def apply(self, image):
        try:
            self.validate_image(image)
            segmented, image_with_boundaries, _ = interactive_segmentation(
                image, seeds=self.seeds, threshold=self.threshold
            )
            return image_with_boundaries
        except Exception as e:
            logger.error(f"Error in interactive segmentation: {str(e)}")
            raise OperationError(f"Failed to apply interactive segmentation: {str(e)}")
            
    def __str__(self):
        seed_count = len(self.seeds) if self.seeds else 0
        return f"Interactive Segmentation (seeds={seed_count}, threshold={self.threshold})"

# Pipeline Manager
class PipelineManager:
    def __init__(self):
        self.operations = []
        self.undo_stack = []
        self.redo_stack = []
        self.current_image = None
        self.original_image = None
        self.max_undo_steps = 20
        self.presets = {}  # Store operation presets
        logger.info("PipelineManager initialized")

    def set_image(self, image):
        """Set the current image and store it as the original"""
        try:
            if image is None:
                raise ValueError("Cannot set None as image")
            
            # Validate image
            if not isinstance(image, np.ndarray):
                raise ValueError("Image must be a numpy array")
            if len(image.shape) not in [2, 3]:
                raise ValueError("Image must be 2D or 3D array")
            if image.dtype != np.uint8:
                raise ValueError("Image must be uint8 type")

            self.current_image = image.copy()
            self.original_image = image.copy()
            self.operations = []
            self.undo_stack = []
            self.redo_stack = []
            logger.info(f"Image set successfully. Shape: {image.shape}")
        except Exception as e:
            logger.error(f"Error setting image: {str(e)}")
            raise

    def add_operation(self, operation):
        """Add an operation to the pipeline and apply it"""
        try:
            if self.current_image is None:
                raise OperationError("No image loaded")
            
            # Validate operation
            if not isinstance(operation, Operation):
                raise OperationError("Invalid operation type")
            
            # Store current state for undo
            self.undo_stack.append((self.current_image.copy(), self.operations.copy()))
            if len(self.undo_stack) > self.max_undo_steps:
                self.undo_stack.pop(0)  # Remove oldest state
            
            self.redo_stack = []  # Clear redo stack when new operation is added
            
            # Apply operation
            self.current_image = operation.apply(self.current_image)
            self.operations.append(operation)
            logger.info(f"Operation {operation.__class__.__name__} added successfully")
        except Exception as e:
            logger.error(f"Error adding operation: {str(e)}")
            raise

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
        """Undo the last operation"""
        try:
            if not self.undo_stack:
                logger.warning("Nothing to undo")
                return False
            
            # Store current state for redo
            self.redo_stack.append((self.current_image.copy(), self.operations.copy()))
            
            # Restore previous state
            self.current_image, self.operations = self.undo_stack.pop()
            logger.info("Operation undone successfully")
            return True
        except Exception as e:
            logger.error(f"Error during undo: {str(e)}")
            return False

    def redo(self):
        """Redo the last undone operation"""
        try:
            if not self.redo_stack:
                logger.warning("Nothing to redo")
                return False
            
            # Store current state for undo
            self.undo_stack.append((self.current_image.copy(), self.operations.copy()))
            
            # Restore next state
            self.current_image, self.operations = self.redo_stack.pop()
            logger.info("Operation redone successfully")
            return True
        except Exception as e:
            logger.error(f"Error during redo: {str(e)}")
            return False

    def reset(self):
        """Reset the pipeline to its original state"""
        try:
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.operations = []
                self.undo_stack = []
                self.redo_stack = []
                logger.info("Pipeline reset to original state")
                return True
            logger.warning("No original image to reset to")
            return False
        except Exception as e:
            logger.error(f"Error during reset: {str(e)}")
            return False

    def reprocess(self):
        """Reaply all operations sequantially on the original image"""
        image = self.original_image.copy()
        for op in self.operations:
            image = op.apply(image)
        self.current_image = image
        return self.current_image

    def get_operation_history(self):
        """Get the list of operations in the pipeline"""
        return [op.__class__.__name__ for op in self.operations]

    def get_current_state(self):
        """Get the current state of the pipeline"""
        return {
            'current_image': self.current_image,
            'operations': self.get_operation_history(),
            'can_undo': len(self.undo_stack) > 0,
            'can_redo': len(self.redo_stack) > 0
        }

    def save_preset(self, name, operations):
        """Save a set of operations as a preset"""
        try:
            preset_data = []
            for op in operations:
                preset_data.append({
                    'type': op.__class__.__name__,
                    'params': op.__dict__
                })
            self.presets[name] = preset_data
            logger.info(f"Saved preset: {name}")
            return True
        except Exception as e:
            logger.error(f"Error saving preset: {str(e)}")
            return False

    def load_preset(self, name):
        """Load a preset by name"""
        try:
            if name not in self.presets:
                raise ValueError(f"Preset {name} not found")
            
            preset_data = self.presets[name]
            operations = []
            
            for op_data in preset_data:
                op_type = op_data['type']
                params = op_data['params']
                
                # Create operation instance based on type
                if op_type == 'ResizeOperation':
                    op = ResizeOperation(params.get('width'), params.get('height'))
                elif op_type == 'RotateOperation':
                    op = RotateOperation(params.get('angle'))
                elif op_type == 'HueSaturationOperation':
                    op = HueSaturationOperation(params.get('hue'), params.get('saturation'))
                elif op_type == 'ColorBalanceAdjustment':
                    op = ColorBalanceAdjustment(
                        params.get('red_balance'),
                        params.get('blue_balance'),
                        params.get('green_balance')
                    )
                elif op_type == 'BlurOperation':
                    op = BlurOperation(params.get('kernel_size'))
                elif op_type == 'MorphOperations':
                    op = MorphOperations(params.get('kernel_shape'), params.get('operation'))
                elif op_type == 'SobelEdgeDetectionOperation':
                    op = SobelEdgeDetectionOperation(params.get('mode'))
                elif op_type == 'GammaCorrectionOperation':
                    op = GammaCorrectionOperation(params.get('gamma'))
                elif op_type == 'BilateralFilterOperation':
                    op = BilateralFilterOperation(params.get('d'), params.get('sigma_color'), params.get('sigma_space'))
                elif op_type == 'MedianFilterOperation':
                    op = MedianFilterOperation(params.get('kernel_size'))
                elif op_type == 'NLMDenoiseOperation':
                    op = NLMDenoiseOperation(params.get('h'), params.get('template_window_size'), params.get('search_window_size'))
                elif op_type == 'CustomKernelOperation':
                    op = CustomKernelOperation(params.get('kernel'))
                elif op_type == 'WatershedSegmentationOperation':
                    op = WatershedSegmentationOperation(params.get('connectivity'))
                elif op_type == 'KMeansSegmentationOperation':
                    op = KMeansSegmentationOperation(params.get('k'), params.get('attempts'), params.get('use_labels'))
                elif op_type == 'GrabCutSegmentationOperation':
                    op = GrabCutSegmentationOperation(params.get('rect'), params.get('iter_count'), params.get('extract_foreground'))
                elif op_type == 'InteractiveSegmentationOperation':
                    op = InteractiveSegmentationOperation(params.get('seeds'), params.get('threshold'))
                else:
                    logger.warning(f"Unknown operation type: {op_type}")
                    continue
                    
                operations.append(op)
            
            # Apply the preset operations
            self.operations = operations
            self.reprocess()
            logger.info(f"Loaded preset: {name}")
            return True
        except Exception as e:
            logger.error(f"Error loading preset: {str(e)}")
            return False

    def get_presets(self):
        """Get list of available presets"""
        return list(self.presets.keys())

    def delete_preset(self, name):
        """Delete a preset"""
        try:
            if name in self.presets:
                del self.presets[name]
                logger.info(f"Deleted preset: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting preset: {str(e)}")
            return False