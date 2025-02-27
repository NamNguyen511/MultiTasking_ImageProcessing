import cv2
from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QToolBox, QLabel, QComboBox, QPushButton, QLineEdit,
    QTabWidget, QColorDialog, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class DockablePanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Image Operations", parent)

        # Allow docking on left or right side
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Make the dock wider & Stylish
        self.setMinimumWidth(400)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)


        # Create an internal widget that holds all panels/tabs
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(5,5,5,5)

        # Tabs for Basic Operations & Advanced Operations
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.addTab(self.create_basic_operations_tab(), "Basic Operations")
        self.tab_widget.addTab(self.create_image_operations_tab(), "Filters / Advanced")
        container_layout.addWidget(self.tab_widget)

        # Color Adjustment
        container_layout.addWidget(self.create_color_adjustments_group())

        container_layout.addStretch(1)
        self.setWidget(container_widget)
    # -----------------------------------
    # BASIC OPERATIONS TAB
    # -----------------------------------
    def create_basic_operations_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5,5,5,5)

        # Resize Group
        resize_group = QGroupBox("Resizing Image")
        resize_layout = QVBoxLayout()
        self.width_input = QLineEdit(self)
        self.width_input.setPlaceholderText("Width")
        resize_layout.addWidget(self.width_input)

        self.height_input = QLineEdit(self)
        self.height_input.setPlaceholderText("Height")
        resize_layout.addWidget(self.height_input)

        resize_button = QPushButton("Resize Image", self)
        resize_button.setToolTip("Resize Image")
        resize_button.clicked.connect(self.parent().resize_image)
        resize_layout.addWidget(resize_button)
        resize_group.setLayout(resize_layout)

        # Rotate Group
        rotate_group = QGroupBox("Rotating Image")
        rotate_layout = QVBoxLayout()
        self.angle_input = QLineEdit(self)
        self.angle_input.setPlaceholderText("Angle (Degrees)")
        rotate_layout.addWidget(self.angle_input)

        rotate_button = QPushButton("Rotate Image", self)
        rotate_button.clicked.connect(self.parent().rotate_image)
        rotate_layout.addWidget(rotate_button)
        rotate_group.setLayout(rotate_layout)

        layout.addWidget(resize_group)
        layout.addWidget(rotate_group)

        return widget
    # ----------------------------------
    # FILTER / ADVANCED TABS
    # ----------------------------------
    def create_image_operations_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        toolbox = QToolBox()
        toolbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbox.addItem(self.create_blur_group(), "Blurring Image")
        toolbox.addItem(self.create_canny_group(), "Canny Edge Detection")
        toolbox.addItem(self.create_sobel_group(), "Sobel Edge Detection")
        toolbox.addItem(self.create_morph_group(), "Morphological Operation")

        layout.addWidget(toolbox)

        return widget

    def create_blur_group(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.blur_size_input = QLineEdit(self)
        self.blur_size_input.setPlaceholderText("Kernel Size")
        layout.addWidget(self.blur_size_input)

        blur_button = QPushButton("Blurred Image")
        blur_button.clicked.connect(self.parent().blur_image)
        layout.addWidget(blur_button)

        return widget

    def create_canny_group(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.low_threshold_input = QLineEdit(self)
        self.low_threshold_input.setPlaceholderText("Low Threshold")
        layout.addWidget(self.low_threshold_input)

        self.high_threshold_input = QLineEdit(self)
        self.high_threshold_input.setPlaceholderText("High Threshold")
        layout.addWidget(self.high_threshold_input)

        canny_button = QPushButton("Canny Edge Detection", self)
        canny_button.clicked.connect(self.parent().canny_edge)
        layout.addWidget(canny_button)

        return widget

    def create_sobel_group(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.sobel_combo = QComboBox(self)
        self.sobel_combo.addItem("Vertical Gradient")
        self.sobel_combo.addItem("Horizontal Gradient")
        layout.addWidget(self.sobel_combo)

        apply_sobel_button = QPushButton("Sobel Edge Detection", self)

        apply_sobel_button.clicked.connect(self.parent().sobel_edge_detection)
        layout.addWidget(apply_sobel_button)

        return widget

    def create_morph_group(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.filter_shape_combo = QComboBox(self)
        self.filter_shape_combo.addItem("Rectangle", cv2.MORPH_RECT)
        self.filter_shape_combo.addItem("Ellipse", cv2.MORPH_ELLIPSE)
        self.filter_shape_combo.addItem("Cross", cv2.MORPH_CROSS)
        self.filter_shape_combo.setToolTip("Select kernel shape")
        layout.addWidget(QLabel("Kernel Shape"))
        layout.addWidget(self.filter_shape_combo)

        self.filter_type_combo = QComboBox(self)
        self.filter_type_combo.addItem("Dilation", cv2.MORPH_DILATE)
        self.filter_type_combo.addItem("Erosion", cv2.MORPH_ERODE)
        self.filter_type_combo.addItem("Open", cv2.MORPH_OPEN)
        self.filter_type_combo.addItem("Closing", cv2.MORPH_CLOSE)
        self.filter_type_combo.addItem("Gradient", cv2.MORPH_GRADIENT)
        self.filter_type_combo.setToolTip("Select morphological operation")
        layout.addWidget(QLabel("Filter Type"))
        layout.addWidget(self.filter_type_combo)

        apply_filter_button = QPushButton("Apply Filter", self)
        apply_filter_button.setToolTip("Apply selected morphological filter")
        apply_filter_button.clicked.connect(self.parent().morphological_filters)
        layout.addWidget(apply_filter_button)

        return widget
    # ----------------------------
    #  COLOR ADJUSTMENTS
    # ----------------------------
    def create_color_adjustments_group(self):
        group = QGroupBox("Color Adjustments")
        layout = QVBoxLayout()

        # Instead of Hue/Sat sliders, use a "Pick Color" approach
        self.pick_color_button = QPushButton("Pick Color")
        self.pick_color_button.clicked.connect(self.pick_color_from_palette)
        layout.addWidget(self.pick_color_button)

        # You could add a label or preview of the chosen color
        self.color_label = QLabel("No color selected")
        layout.addWidget(self.color_label)

        group.setLayout(layout)
        return group

    def pick_color_from_palette(self):
        """Open a color dialog and adjust the image hue/sat based on the chosen color."""
        chosen_color = QColorDialog.getColor(initial=QColor(255, 255, 255), parent=self)
        if chosen_color.isValid():
            # Update label to show chosen color code
            self.color_label.setText(chosen_color.name())

            # Convert the chosen color's hue and saturation to the pipeline's expected range
            # QColor.hue() -> [0..359], QColor.saturation() -> [0..255]
            # Original sliders were -180..180 for hue, -100..100 for saturation
            hue = chosen_color.hue() - 180  # shift range to [-180..180]
            saturation = int(chosen_color.saturation() / 255.0 * 200) - 100  # map [0..255] -> [-100..100]

            # Call a method in the main window to apply a hue/sat operation
            self.parent().apply_color_from_palette(hue, saturation)