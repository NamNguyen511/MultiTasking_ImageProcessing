import sys
import cv2
import numpy as np

# Importing PyQt5 Libraries
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, \
    QLineEdit, QHBoxLayout, QGroupBox, QFrame, QSizePolicy, QMenuBar, QAction, QMessageBox
from PyQt5.QtGui import QPalette, QColor

# Importing Gui folders
from gui.button_panel import ButtonPanel
from gui.image_viewer import ImageViewer
from gui.histogram_window import HistogramWindow

# Importing modules folders
from modules.animation import animation_widget
from modules.basic_operations import load_image, resize_image, rotate_image
from modules.filtering import blur_images, canny_detect_edges, morphological_filters
from modules.color_processing import hue_saturation_adjustment, color_balance_adjustment

# Importing styles
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
        self.setGeometry(100, 100, 1400, 1000)
        self.original_image = None # Store the original image
        self.current_image = None  # Store the current image
        self.total_angle = 0 # Store cumulative angle for rotation

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

        # Image menu
        image_menu = menuBar.addMenu("Image")

        # Show histogram
        histogram_action = QAction("Show Histogram", self)
        histogram_action.triggered.connect(self.show_histogram)
        image_menu.addAction(histogram_action)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.original_image = load_image(file_name)
            self.current_image = self.original_image.copy()
            self.image_viewer.display_image(self.original_image, label_type="original")
            self.image_viewer.modified_image_label.clear()

    def show_message(self, message):
        QMessageBox.warning(self, "Warning", message)

    def check_image_loaded(self):
        if self.original_image is None:
            self.show_message("Please load an image first")
            return False
        return True

    def resize_image(self):
        if not self.check_image_loaded():
            return

        if self.current_image is not None:
            width = int(self.button_panel.width_input.text()) if self.button_panel.width_input.text() else self.current_image.shape[1]
            height = int(self.button_panel.height_input.text()) if self.button_panel.height_input.text() else self.current_image.shape[0]
            resized_image = resize_image(self.current_image, width, height)
            self.current_image = resized_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def rotate_image(self):
        if not self.check_image_loaded():
            return

        angle = int(self.button_panel.angle_input.text()) if self.button_panel.angle_input.text() else 90

        if self.original_image is not None:
            self.total_angle = (self.total_angle + angle) % 360
            rotated_image = rotate_image(self.current_image, self.total_angle)
            self.current_image = rotated_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def blur_image(self):

        if not self.check_image_loaded():
            return

        kernel_size = int(self.button_panel.blur_size_input.text()) if self.button_panel.blur_size_input.text() else 5
        kernel = (kernel_size, kernel_size)

        if self.current_image is not None:
            blurred_image = blur_images(self.current_image, kernel)
            self.current_image = blurred_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def canny_edge(self):

        if not self.check_image_loaded():
            return

        low_threshold = int(self.button_panel.low_threshold_input.text()) if self.button_panel.low_threshold_input.text() else 50
        high_threshold = int(self.button_panel.high_threshold_input.text()) if self.button_panel.high_threshold_input.text() else 150

        if self.current_image is not None:
            self.current_image = canny_detect_edges(self.current_image, low_threshold, high_threshold)
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def save_image(self):
        if not self.check_image_loaded():
            return

        if self.current_image is not None:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;All Files (*)", options=options)
            if file_name:
                cv2.imwrite(file_name, self.current_image)
                QMessageBox.information(self, "Image Saved", "Your image has been saved successfully!")

    def adjust_hue_saturation(self):

        if not self.check_image_loaded():
            return

        if self.original_image is not None:
            hue = self.button_panel.hue_slider.value()
            saturation = self.button_panel.saturation_slider.value()

            adjusted_image = hue_saturation_adjustment(self.original_image, hue, saturation)
            self.current_image = adjusted_image
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def adjust_color_balance(self):

        if not self.check_image_loaded():
            return

        red_balance = self.button_panel.red_slider.value()
        green_balance = self.button_panel.green_slider.value()
        blue_balance = self.button_panel.blue_slider.value()
        adjusted_image = color_balance_adjustment(self.original_image, red_balance, green_balance, blue_balance)
        self.current_image = adjusted_image
        self.image_viewer.display_image(self.current_image, label_type='modified')

    # Show Image Histogram
    def show_histogram(self):
        if not self.check_image_loaded():
            return

        histogramWindow = HistogramWindow(self.current_image)
        histogramWindow.show()

    # Morphological Operations
    def morphological_filters(self):
        if not self.check_image_loaded():
            return

        if self.original_image is not None:
            shape_index = self.button_panel.filter_shape_combo.currentIndex()
            operation_index = self.button_panel.filter_type_combo.currentIndex()

            kernel_shape = self.button_panel.filter_shape_combo.itemData(shape_index)
            operation_type = self.button_panel.filter_type_combo.itemData(operation_index)

            filtered_image = morphological_filters(self.original_image, kernel_shape, operation_type)
            self.image_viewer.display_image(filtered_image, label_type="modified")

    def run(self):
        self.show()
