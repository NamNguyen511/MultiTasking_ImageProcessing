from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QSlider, QGroupBox
from PyQt5.QtCore import Qt
from modules.animation import animation_group_widgets


class ButtonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        button_layout = QVBoxLayout()

        # Store GroupBoxes for animation
        self.groupBoxes = []
        self.animations = None

        # Load Image Button
        load_group = QGroupBox("Image Loading")
        load_layout = QVBoxLayout()

        load_button = QPushButton("Load Image")
        load_button.clicked.connect(self.parent().load_image)
        load_layout.addWidget(load_button)

        load_group.setLayout(load_layout)
        button_layout.addWidget(load_group)
        self.groupBoxes.append(load_group)

        # Resize Image Controls
        resize_group = QGroupBox("Resizing Image")
        resize_layout = QVBoxLayout()
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText("Width")
        resize_layout.addWidget(self.width_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height")
        resize_layout.addWidget(self.height_input)

        resize_button = QPushButton("Resize Image", self)
        resize_button.clicked.connect(self.parent().resize_image)
        resize_layout.addWidget(resize_button)

        resize_group.setLayout(resize_layout)
        button_layout.addWidget(resize_group)
        self.groupBoxes.append(resize_group)

        # Rotate Image Controls
        rotate_group = QGroupBox("Rotating Image")
        rotate_layout = QVBoxLayout()

        self.angle_input = QLineEdit(self)
        self.angle_input.setPlaceholderText("Angle (Degrees)")
        rotate_layout.addWidget(self.angle_input)

        rotate_button = QPushButton("Rotate Image", self)
        rotate_button.clicked.connect(self.parent().rotate_image)
        rotate_layout.addWidget(rotate_button)

        rotate_group.setLayout(rotate_layout)
        button_layout.addWidget(rotate_group)
        self.groupBoxes.append(rotate_group)

        # Blurring Image Controls
        operations_group = QGroupBox("Image Operations")
        operations_layout = QVBoxLayout()

        self.blur_size_input = QLineEdit(self)
        self.blur_size_input.setPlaceholderText("Kernel Size")
        operations_layout.addWidget(self.blur_size_input)

        blur_button = QPushButton("Blurred Image", self)
        blur_button.clicked.connect(self.parent().blur_image)
        operations_layout.addWidget(blur_button)

        # Edge Detection Controls
        self.low_threshold_input = QLineEdit(self)
        self.low_threshold_input.setPlaceholderText("Low Threshold")
        operations_layout.addWidget(self.low_threshold_input)

        self.high_threshold_input = QLineEdit(self)
        self.high_threshold_input.setPlaceholderText("High Threshold")
        operations_layout.addWidget(self.high_threshold_input)

        canny_button = QPushButton("Canny Edge Detection", self)
        canny_button.clicked.connect(self.parent().canny_edge)
        operations_layout.addWidget(canny_button)

        operations_group.setLayout(operations_layout)
        button_layout.addWidget(operations_group)
        self.groupBoxes.append(operations_group)

        button_layout.addStretch(1)  # Push buttons to the top
        self.setLayout(button_layout)

        # Animation groupBoxes after initialization
        self.animations = animation_group_widgets(self.groupBoxes, start_y_offset=300, duration=2000)