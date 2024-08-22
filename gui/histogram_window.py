from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout
import matplotlib.pyplot as plt
import cv2


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
        color = ('b', 'r', 'g')
        plt.figure('Histogram')
        plt.title("Color Histogram")
        plt.xlabel("Bins")
        plt.ylabel("Number of Pixels")
        for i, col in enumerate(color):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
            plt.xlim([0, 256])
        plt.show()