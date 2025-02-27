import cv2
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QSlider,
    QGroupBox, QSizePolicy, QTabWidget, QToolBox, QLabel, QComboBox
)
from PyQt5.QtCore import Qt
from modules.animation import animation_group_widgets
from resources import styles


class ButtonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.main_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_basic_operations_tab(), "Basic Operations")
        self.tab_widget.addTab(self.create_image_operations_tab(), "Image Operations")
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addWidget(self.create_color_adjustments_group())

        self.main_layout.addStretch(1)  # Push everything up

        self.setLayout(self.main_layout)


    def create_color_adjustments_group(self):
        group = QGroupBox("Color Adjustments")
        layout = QVBoxLayout()

        # Hue Slider
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(-180)
        self.hue_slider.setMaximum(180)
        self.hue_slider.setValue(0)
        self.hue_slider_label = QLabel("Hue")
        layout.addWidget(self.hue_slider)
        layout.addWidget(self.hue_slider_label)

        # Saturation Slider
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider_label = QLabel("Saturation")
        layout.addWidget(self.saturation_slider)
        layout.addWidget(self.saturation_slider_label)

        # Red Balance Slider
        self.red_slider = QSlider(Qt.Horizontal)
        self.red_slider.setMinimum(-100)
        self.red_slider.setMaximum(100)
        self.red_slider.setValue(0)
        self.red_slider_label = QLabel("Red")
        layout.addWidget(self.red_slider)
        layout.addWidget(self.red_slider_label)

        # Blue Balance Slider
        self.blue_slider = QSlider(Qt.Horizontal)
        self.blue_slider.setMinimum(-100)
        self.blue_slider.setMaximum(100)
        self.blue_slider.setValue(0)
        self.blue_slider_label = QLabel("Blue")
        layout.addWidget(self.blue_slider)
        layout.addWidget(self.blue_slider_label)

        # Green Balance Slider
        self.green_slider = QSlider(Qt.Horizontal)
        self.green_slider.setMinimum(-100)
        self.green_slider.setMaximum(100)
        self.green_slider.setValue(0)
        self.green_slider_label = QLabel("Green")
        layout.addWidget(self.green_slider)
        layout.addWidget(self.green_slider_label)

        group.setLayout(layout)
        return group
