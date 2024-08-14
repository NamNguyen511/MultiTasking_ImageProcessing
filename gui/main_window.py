import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, \
    QLineEdit, QHBoxLayout, QGroupBox, QFrame
from PyQt5.QtGui import QPalette, QColor
from modules.basic_operations import load_image, display_image, resize_image, rotate_image
from modules.filtering import blur_images, canny_detect_edges



class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Multitask Processing.")
        self.setGeometry(100, 100, 1200, 600)
        self.original_image = None # Store the original image
        self.current_image = None  # Store the current image

        # Main Layout
        main_layout = QHBoxLayout()

        # Left side layout for button
        button_layout = QVBoxLayout()

        # Set the fixed width for button layout
        button_container = QWidget()
        button_container.setLayout(button_layout)
        button_container.setFixedWidth(200)

        # Load Image Button
        load_group = QGroupBox("Image Loading")
        load_layout = QVBoxLayout()

        load_button = QPushButton("Load Image")
        load_button.clicked.connect(self.load_image)
        load_layout.addWidget(load_button)

        load_group.setLayout(load_layout)
        button_layout.addWidget(load_group)

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
        resize_button.clicked.connect(self.resize_image)
        resize_layout.addWidget(resize_button)

        resize_group.setLayout(resize_layout)
        button_layout.addWidget(resize_group)

        # Rotate Image Controls
        rotate_group = QGroupBox("Rotating Image")
        rotate_layout = QVBoxLayout()

        self.angle_input = QLineEdit(self)
        self.angle_input.setPlaceholderText("Angle (Degrees)")
        rotate_layout.addWidget(self.angle_input)

        rotate_button = QPushButton("Rotate Image", self)
        rotate_button.clicked.connect(self.rotate_image)
        rotate_layout.addWidget(rotate_button)

        rotate_group.setLayout(rotate_layout)
        button_layout.addWidget(rotate_group)

        # Blurring Image Controls
        operations_group = QGroupBox("Image Operations")
        operations_layout = QVBoxLayout()

        self.blur_size_input = QLineEdit(self)
        self.blur_size_input.setPlaceholderText("Kernel Size")
        operations_layout.addWidget(self.blur_size_input)

        blur_button = QPushButton("Blurred Image", self)
        blur_button.clicked.connect(self.blur_image)
        operations_layout.addWidget(blur_button)

        # Edge Detection Controls
        self.low_threshold_input = QLineEdit(self)
        self.low_threshold_input.setPlaceholderText("Low Threshold")
        operations_layout.addWidget(self.low_threshold_input)

        self.high_threshold_input = QLineEdit(self)
        self.high_threshold_input.setPlaceholderText("High Threshold")
        operations_layout.addWidget(self.high_threshold_input)

        canny_button = QPushButton("Canny Edge Detection", self)
        canny_button.clicked.connect(self.canny_edge)
        operations_layout.addWidget(canny_button)

        operations_group.setLayout(operations_layout)
        button_layout.addWidget(operations_group)

        button_layout.addStretch(1) # Push buttons to the top

        # Add button layout to the main layout
        main_layout.addWidget(button_container)

        # Add line seperator
        line_seperator = QFrame()
        line_seperator.setFrameShape(QFrame.VLine)
        line_seperator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line_seperator)

        # Right side layout for displaying images
        image_layout = QHBoxLayout()

        # Labels to display images
        self.original_image_label = QLabel(self)
        self.modified_image_label = QLabel(self)

        # Add Labels to the image layout
        image_layout.addWidget(self.original_image_label)
        image_layout.addWidget(self.modified_image_label)

        # Add Image layout to the main layout
        main_layout.addLayout(image_layout)

        # Central widget and layout
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # layout.addWidget(Color('red'))

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.original_image = load_image(file_name)
            self.current_image = self.original_image.copy()
            display_image(self.original_image, self.original_image_label)
            self.modified_image_label.clear()

    def resize_image(self):
        if self.current_image is not None:
            width = int(self.width_input.text()) if self.width_input.text() else self.current_image.shape[1]
            height = int(self.height_input.text()) if self.height_input.text() else self.current_image.shape[0]
            resized_image = resize_image(self.current_image, width, height)
            self.current_image = resized_image
            self.display_images(self.original_image, self.current_image)

    def rotate_image(self):
        angle = int(self.angle_input.text()) if self.angle_input.text() else 0

        if self.current_image is not None:
            rotated_image = rotate_image(self.current_image, angle)
            self.current_image = rotated_image
            self.display_images(self.original_image, self.current_image)

    def blur_image(self):
        kernel_size = int(self.blur_size_input.text()) if self.blur_size_input.text() else 5
        kernel = (kernel_size, kernel_size)

        if self.current_image is not None:
            blurred_image = blur_images(self.current_image, kernel)
            self.current_image = blurred_image
            self.display_images(self.original_image, self.current_image)

    def canny_edge(self):
        low_threshold = int(self.low_threshold_input.text()) if self.low_threshold_input.text() else 50
        high_threshold = int(self.high_threshold_input.text()) if self.high_threshold_input.text() else 150

        if self.current_image is not None:
            self.current_image = canny_detect_edges(self.current_image, low_threshold, high_threshold)
            self.display_images(self.original_image, self.current_image)

    def display_images(self, original_image, modified_image):
        # Display the original image
        display_image(original_image, self.original_image_label)

        # Display the modified image
        display_image(modified_image, self.modified_image_label)

    def run(self):
        self.show()
