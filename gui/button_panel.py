from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QSlider, QGroupBox, QSizePolicy, QTabWidget, QToolBox
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
        # load_group.setStyleSheet(styles.groupbox_style)
        load_layout = QVBoxLayout()

        load_button = QPushButton("Load Image")
        # load_button.setStyleSheet(styles.button_style)
        load_button.clicked.connect(self.parent().load_image)
        load_layout.addWidget(load_button)

        load_group.setLayout(load_layout)
        button_layout.addWidget(load_group)

        # Basic Operations Tab
        basic_operations_tab = QWidget()
        basic_operations_layout = QVBoxLayout()

        # Resize Image Group
        resize_group = QGroupBox("Resizing Image")
        # resize_group.setStyleSheet(styles.groupbox_style)
        resize_layout = QVBoxLayout()
        self.width_input = QLineEdit(self)
        # self.width_input.setStyleSheet(styles.input_style)
        self.width_input.setPlaceholderText("Width")
        resize_layout.addWidget(self.width_input)
        self.height_input = QLineEdit(self)
        # self.height_input.setStyleSheet(styles.input_style)
        self.height_input.setPlaceholderText("Height")
        resize_layout.addWidget(self.height_input)
        resize_button = QPushButton("Resize Image", self)
        # resize_button.setStyleSheet(styles.button_style)
        resize_button.clicked.connect(self.parent().resize_image)
        resize_layout.addWidget(resize_button)
        resize_group.setLayout(resize_layout)

        # Rotate Image Controls
        rotate_group = QGroupBox("Rotating Image")
        # rotate_group.setStyleSheet(styles.groupbox_style)
        rotate_layout = QVBoxLayout()
        self.angle_input = QLineEdit(self)
        # self.angle_input.setStyleSheet(styles.input_style)
        self.angle_input.setPlaceholderText("Angle (Degrees)")
        rotate_layout.addWidget(self.angle_input)
        rotate_button = QPushButton("Rotate Image", self)
        # rotate_button.setStyleSheet(styles.button_style)
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
        # self.blur_size_input.setStyleSheet(styles.input_style)
        self.blur_size_input.setPlaceholderText("Kernel Size")
        blur_layout.addWidget(self.blur_size_input)
        blur_button = QPushButton("Blurred Image", self)
        # blur_button.setStyleSheet(styles.button_style)
        blur_button.clicked.connect(self.parent().blur_image)
        blur_layout.addWidget(blur_button)
        blur_group.setLayout(blur_layout)
        operations_toolbox.addItem(blur_group, "Blurring Image")

        # Edge Detection Controls
        canny_group = QWidget()
        canny_layout = QVBoxLayout()
        self.low_threshold_input = QLineEdit(self)
        # self.low_threshold_input.setStyleSheet(styles.input_style)
        self.low_threshold_input.setPlaceholderText("Low Threshold")
        canny_layout.addWidget(self.low_threshold_input)
        self.high_threshold_input = QLineEdit(self)
        # self.high_threshold_input.setStyleSheet(styles.input_style)
        self.high_threshold_input.setPlaceholderText("High Threshold")
        canny_layout.addWidget(self.high_threshold_input)
        canny_button = QPushButton("Canny Edge Detection", self)
        # canny_button.setStyleSheet(styles.button_style)
        canny_button.clicked.connect(self.parent().canny_edge)
        canny_layout.addWidget(canny_button)
        canny_group.setLayout(canny_layout)
        operations_toolbox.addItem(canny_group, "Canny Edge Detection")

        image_operations_layout.addWidget(operations_toolbox)
        image_operations_tab.setLayout(image_operations_layout)
        self.tab_widget.addTab(image_operations_tab, "Image Operations")

        button_layout.addWidget(self.tab_widget)
        button_layout.addStretch(1)  # Push buttons to the top

        # Set size policies to allow resizing
        resize_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        rotate_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.setLayout(button_layout)

