from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout
import matplotlib.pyplot as plt
import cv2
import numpy as np


class HistogramWindow(QMainWindow):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Histogram")
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Display histogram
        self.display_histogram(image)

    def display_histogram(self, image):
        plt.figure('Histogram')
        
        if len(image.shape) == 3:  # Color image
            plt.title("Color Image Histogram")
            color = ('b', 'g', 'r')
            labels = ['Blue', 'Green', 'Red']
            for i, (col, label) in enumerate(zip(color, labels)):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                plt.plot(hist, color=col, label=label)
        else:  # Grayscale image
            plt.title("Grayscale Image Histogram")
            hist = cv2.calcHist([image], [0], None, [256], [0, 256])
            plt.plot(hist, color='gray', label='Intensity')

        plt.xlabel("Pixel Intensity")
        plt.ylabel("Number of Pixels")
        plt.xlim([0, 256])
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.show()