from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
                             QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt
from modules.pipeline_manager import *

class OperationDialog(QDialog):
    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation
        self.setWindowTitle(f"Edit {operation.__class__.__name__}")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Create form for operation parameters
        form = QFormLayout()
        
        if isinstance(operation, ResizeOperation):
            self.width_spin = QSpinBox()
            self.width_spin.setRange(1, 10000)
            self.width_spin.setValue(operation.width or 800)
            self.height_spin = QSpinBox()
            self.height_spin.setRange(1, 10000)
            self.height_spin.setValue(operation.height or 600)
            
            form.addRow("Width:", self.width_spin)
            form.addRow("Height:", self.height_spin)
            
        elif isinstance(operation, RotateOperation):
            self.angle_spin = QSpinBox()
            self.angle_spin.setRange(-360, 360)
            self.angle_spin.setValue(operation.angle)
            form.addRow("Angle:", self.angle_spin)
            
        elif isinstance(operation, HueSaturationOperation):
            self.hue_spin = QSpinBox()
            self.hue_spin.setRange(-180, 180)
            self.hue_spin.setValue(operation.hue)
            self.saturation_spin = QSpinBox()
            self.saturation_spin.setRange(-100, 100)
            self.saturation_spin.setValue(operation.saturation)
            
            form.addRow("Hue:", self.hue_spin)
            form.addRow("Saturation:", self.saturation_spin)
            
        elif isinstance(operation, BlurOperation):
            self.kernel_size_spin = QSpinBox()
            self.kernel_size_spin.setRange(3, 31)
            self.kernel_size_spin.setValue(operation.kernel_size[0])
            self.kernel_size_spin.setSingleStep(2)
            form.addRow("Kernel Size:", self.kernel_size_spin)
            
        elif isinstance(operation, MorphOperations):
            self.kernel_shape_combo = QComboBox()
            self.kernel_shape_combo.addItems(['rect', 'ellipse', 'cross'])
            self.kernel_shape_combo.setCurrentText(operation.kernel_shape)
            
            self.operation_combo = QComboBox()
            self.operation_combo.addItems(['erode', 'dilate', 'open', 'close'])
            self.operation_combo.setCurrentText(operation.operation)
            
            form.addRow("Kernel Shape:", self.kernel_shape_combo)
            form.addRow("Operation:", self.operation_combo)
            
        elif isinstance(operation, SobelEdgeDetectionOperation):
            self.mode_combo = QComboBox()
            self.mode_combo.addItems(['Vertical', 'Horizontal'])
            self.mode_combo.setCurrentText(operation.mode)
            form.addRow("Mode:", self.mode_combo)
            
        elif isinstance(operation, GammaCorrectionOperation):
            self.gamma_spin = QDoubleSpinBox()
            self.gamma_spin.setRange(0.1, 10.0)
            self.gamma_spin.setValue(operation.gamma)
            self.gamma_spin.setSingleStep(0.1)
            form.addRow("Gamma:", self.gamma_spin)
            
        layout.addLayout(form)
        
        # Add buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def get_updated_operation(self):
        """Create and return a new operation with updated parameters"""
        if isinstance(self.operation, ResizeOperation):
            return ResizeOperation(self.width_spin.value(), self.height_spin.value())
        elif isinstance(self.operation, RotateOperation):
            return RotateOperation(self.angle_spin.value())
        elif isinstance(self.operation, HueSaturationOperation):
            return HueSaturationOperation(self.hue_spin.value(), self.saturation_spin.value())
        elif isinstance(self.operation, BlurOperation):
            size = self.kernel_size_spin.value()
            return BlurOperation((size, size))
        elif isinstance(self.operation, MorphOperations):
            return MorphOperations(self.kernel_shape_combo.currentText(),
                                 self.operation_combo.currentText())
        elif isinstance(self.operation, SobelEdgeDetectionOperation):
            return SobelEdgeDetectionOperation(self.mode_combo.currentText())
        elif isinstance(self.operation, GammaCorrectionOperation):
            return GammaCorrectionOperation(self.gamma_spin.value())
        return self.operation 