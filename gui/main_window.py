import sys
import cv2
import numpy as np

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, \
    QLineEdit, QHBoxLayout, QGroupBox, QFrame, QSizePolicy, QMenuBar, QAction, QMessageBox
from PyQt5.QtGui import QPalette, QColor
from gui.button_panel import ButtonPanel
from gui.image_viewer import ImageViewer

from modules.animation import animation_widget
from modules.basic_operations import load_image, resize_image, rotate_image
from modules.filtering import blur_images, canny_detect_edges
from resources.styles import combined_styles


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
        self.setGeometry(100, 100, 1200, 800)
        self.original_image = None # Store the original image
        self.current_image = None  # Store the current image

        # Main Layout
        self.main_layout = QHBoxLayout()

        # Button Panel
        self.button_panel = ButtonPanel(self)
        self.button_panel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.button_panel)

        # Add line seperator
        line_seperator = QFrame()
        line_seperator.setFrameShape(QFrame.VLine)
        line_seperator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(line_seperator)

        # Image Viewer
        self.image_viewer = ImageViewer(self)
        self.image_viewer.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.image_viewer)

        # Central widget and layout
        central_widget = QWidget(self)
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # Styling
        self.setStyleSheet(combined_styles)

        # Create menu bar
        self.create_menu_bar()

        # Connect slider to their respective handlers
        self.button_panel.hue_slider.valueChanged.connect(self.adjust_hue_saturation)
        self.button_panel.saturation_slider.valueChanged.connect(self.adjust_hue_saturation)
        self.button_panel.red_slider.valueChanged.connect(self.adjust_color_balance)
        self.button_panel.blue_slider.valueChanged.connect(self.adjust_color_balance)
        self.button_panel.green_slider.valueChanged.connect(self.adjust_color_balance)

    def create_menu_bar(self):
        menuBar = self.menuBar()

        # File menu
        file_menu = menuBar.addMenu("File")

        # Save Action
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        # Export action
        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)

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

    def save_image(self):
        if self.current_image is not None:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;All Files (*)", options=options)
            if file_name:
                cv2.imwrite(file_name, self.current_image)
                QMessageBox.information(self, "Image Saved", "Your image has been saved successfully!")

    def export_image(self):
        pass

    def adjust_hue_saturation(self):
        if self.original_image is not None:
            hue = self.button_panel.hue_slider.value()
            saturation = self.button_panel.saturation_slider.value()

            hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            hsv_image = np.float32(hsv_image)
            hsv_image[..., 0] += hue
            hsv_image[..., 1] += np.clip(hsv_image[..., 1] + saturation, 0, 255)
            hsv_image = np.uint8(hsv_image)
            adjusted_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            self.current_image = adjusted_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def adjust_color_balance(self):
        red_balance = self.button_panel.red_slider.value()
        green_balance = self.button_panel.green_slider.value()
        blue_balance = self.button_panel.blue_slider.value()
        b, g, r =  cv2.split(self.original_image)
        r = np.clip(r + red_balance, 0, 255)
        g = np.clip(g + green_balance, 0, 255)
        b = np.clip(b + blue_balance, 0, 255)
        adjusted_image = cv2.merge([b, g, r])
        self.current_image = adjusted_image
        self.image_viewer.display_image(self.current_image, label_type='modified')


    def run(self):
        self.show()
