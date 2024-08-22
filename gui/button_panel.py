import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QSlider, QGroupBox, QSizePolicy, QTabWidget, \
    QToolBox, QLabel, QComboBox
from PyQt5.QtCore import Qt
from modules.animation import animation_group_widgets
from resources import styles

class ButtonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.tab_widget = QTabWidget()
        button_layout = QVBoxLayout()

        # Load Image Button
        load_group = QGroupBox("Image Loading")
        load_layout = QVBoxLayout()

        load_button = QPushButton("Load Image")
        load_button.clicked.connect(self.parent().load_image)
        load_layout.addWidget(load_button)

        load_group.setLayout(load_layout)
        button_layout.addWidget(load_group)

        # Basic Operations Tab
        basic_operations_tab = QWidget()
        basic_operations_layout = QVBoxLayout()

        # Resize Image Group
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

        # Adding Groups to Basic Operations Tab
        basic_operations_layout.addWidget(resize_group)
        basic_operations_layout.addWidget(rotate_group)
        basic_operations_tab.setLayout(basic_operations_layout)
        self.tab_widget.addTab(basic_operations_tab, "Basic Operations")

        # Image Operations Tab (using QtoolBox for collapsible sections)
        image_operations_tab = QWidget()
        image_operations_layout = QVBoxLayout()

        operations_toolbox = QToolBox(self)

        # Blurring Image Controls
        blur_group = QWidget()
        blur_layout = QVBoxLayout()
        self.blur_size_input = QLineEdit(self)
        self.blur_size_input.setPlaceholderText("Kernel Size")
        blur_layout.addWidget(self.blur_size_input)
        blur_button = QPushButton("Blurred Image", self)
        blur_button.clicked.connect(self.parent().blur_image)
        blur_layout.addWidget(blur_button)
        blur_group.setLayout(blur_layout)
        operations_toolbox.addItem(blur_group, "Blurring Image")

        # Edge Detection Controls
        canny_group = QWidget()
        canny_layout = QVBoxLayout()
        self.low_threshold_input = QLineEdit(self)
        self.low_threshold_input.setPlaceholderText("Low Threshold")
        canny_layout.addWidget(self.low_threshold_input)
        self.high_threshold_input = QLineEdit(self)
        self.high_threshold_input.setPlaceholderText("High Threshold")
        canny_layout.addWidget(self.high_threshold_input)
        canny_button = QPushButton("Canny Edge Detection", self)
        canny_button.clicked.connect(self.parent().canny_edge)
        canny_layout.addWidget(canny_button)
        canny_group.setLayout(canny_layout)
        operations_toolbox.addItem(canny_group, "Canny Edge Detection")

        # Morphological Operations
        morph_group = QWidget()
        morph_layout = QVBoxLayout()
        self.filter_shape_combo = QComboBox(self)
        self.filter_shape_combo.addItem("Rectangle", cv2.MORPH_RECT)
        self.filter_shape_combo.addItem("Ellipse", cv2.MORPH_ELLIPSE)
        self.filter_shape_combo.addItem("Cross", cv2.MORPH_CROSS)
        self.filter_shape_combo.setToolTip("Select the shape of the morphological filter")

        self.filter_type_combo = QComboBox(self)
        self.filter_type_combo.addItem("Dilation", cv2.MORPH_DILATE)
        self.filter_type_combo.addItem("Erosion", cv2.MORPH_ERODE)
        self.filter_type_combo.addItem("Open", cv2.MORPH_OPEN)
        self.filter_type_combo.addItem("Closing", cv2.MORPH_CLOSE)
        self.filter_type_combo.addItem("Gradient", cv2.MORPH_GRADIENT)
        self.filter_type_combo.setToolTip("Select the type of morphological operation")

        apply_filter_button = QPushButton("Apply Filter", self)
        apply_filter_button.setToolTip("Apply the selected filter to the image")
        apply_filter_button.clicked.connect(self.parent().morphological_filters)

        morph_layout.addWidget(QLabel("Kernel Shape"))
        morph_layout.addWidget(self.filter_shape_combo)
        morph_layout.addWidget(QLabel("Filter Type"))
        morph_layout.addWidget(self.filter_type_combo)
        morph_layout.addWidget(apply_filter_button)
        morph_group.setLayout(morph_layout)
        operations_toolbox.addItem(morph_group, "Morphological Operation")

        image_operations_layout.addWidget(operations_toolbox)
        image_operations_tab.setLayout(image_operations_layout)
        self.tab_widget.addTab(image_operations_tab, "Image Operations")

        # Color Adjustments Group
        color_adjustments_group = QGroupBox("Color Adjustments")
        color_adjustments_layout = QVBoxLayout()

        # Hue Slider
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(-180)
        self.hue_slider.setMaximum(180)
        self.hue_slider.setValue(0)
        self.hue_slider_label = QLabel("Hue")
        color_adjustments_layout.addWidget(self.hue_slider)
        color_adjustments_layout.addWidget(self.hue_slider_label)

        # Saturation Slider
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider_label = QLabel("Saturation")
        color_adjustments_layout.addWidget(self.saturation_slider)
        color_adjustments_layout.addWidget(self.saturation_slider_label)

        # Color Balance Sliders
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setMinimum(-100)
        self.red_slider.setMaximum(100)
        self.red_slider.setValue(0)
        self.red_slider_label = QLabel("Red")
        color_adjustments_layout.addWidget(self.red_slider)
        color_adjustments_layout.addWidget(self.red_slider_label)

        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setMinimum(-100)
        self.blue_slider.setMaximum(100)
        self.blue_slider.setValue(0)
        self.blue_slider_label = QLabel("Blue")
        color_adjustments_layout.addWidget(self.blue_slider)
        color_adjustments_layout.addWidget(self.blue_slider_label)

        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setMinimum(-100)
        self.green_slider.setMaximum(100)
        self.green_slider.setValue(0)
        self.green_slider_label = QLabel("Green")
        color_adjustments_layout.addWidget(self.green_slider)
        color_adjustments_layout.addWidget(self.green_slider_label)

        color_adjustments_group.setLayout(color_adjustments_layout)
        button_layout.addWidget(color_adjustments_group)

        button_layout.addWidget(self.tab_widget)
        button_layout.addStretch(1)  # Push buttons to the top

        # Set size policies to allow resizing
        resize_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        rotate_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        color_adjustments_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        image_operations_tab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setLayout(button_layout)

