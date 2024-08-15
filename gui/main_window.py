import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, \
    QLineEdit, QHBoxLayout, QGroupBox, QFrame
from PyQt5.QtGui import QPalette, QColor
from gui.button_panel import ButtonPanel
from gui.image_viewer import ImageViewer
from modules.animation import animation_widget
from modules.basic_operations import load_image, resize_image, rotate_image
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
        self.main_layout = QHBoxLayout()

        self.button_panel = ButtonPanel(self)
        self.main_layout.addWidget(self.button_panel)

        # Add line seperator
        line_seperator = QFrame()
        line_seperator.setFrameShape(QFrame.VLine)
        line_seperator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line_seperator)

        # Image Viewer
        self.image_viewer = ImageViewer(self)
        self.main_layout.addWidget(self.image_viewer)

        # Central widget and layout
        central_widget = QWidget(self)
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Animation button panel
        self.show()
        start_y_offset = self.height() + 50
        animation_widget(self.button_panel, start_y=start_y_offset, end_y=self.button_panel.y(), duration=3000)


    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.original_image = load_image(file_name)
            self.current_image = self.original_image.copy()
            self.image_viewer.display_image(self.original_image, label_type="original")
            self.image_viewer.modified_image_label.clear()

    def resize_image(self):
        if self.current_image is not None:
            width = int(self.button_panel.width_input.text()) if self.button_panel.width_input.text() else self.current_image.shape[1]
            height = int(self.button_panel.height_input.text()) if self.button_panel.height_input.text() else self.current_image.shape[0]
            resized_image = resize_image(self.current_image, width, height)
            self.current_image = resized_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def rotate_image(self):
        angle = int(self.button_panel.angle_input.text()) if self.button_panel.angle_input.text() else 0

        if self.current_image is not None:
            rotated_image = rotate_image(self.current_image, angle)
            self.current_image = rotated_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def blur_image(self):
        kernel_size = int(self.button_panel.blur_size_input.text()) if self.button_panel.blur_size_input.text() else 5
        kernel = (kernel_size, kernel_size)

        if self.current_image is not None:
            blurred_image = blur_images(self.current_image, kernel)
            self.current_image = blurred_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def canny_edge(self):
        low_threshold = int(self.button_panel.low_threshold_input.text()) if self.button_panel.low_threshold_input.text() else 50
        high_threshold = int(self.button_panel.high_threshold_input.text()) if self.button_panel.high_threshold_input.text() else 150

        if self.current_image is not None:
            self.current_image = canny_detect_edges(self.current_image, low_threshold, high_threshold)
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def run(self):
        self.show()
