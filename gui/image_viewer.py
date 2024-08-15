from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap

class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()

        # Labels to display images
        self.original_image_label = QLabel(self)
        self.modified_image_label = QLabel(self)

        # Add Labels to the image layout
        layout.addWidget(self.original_image_label)
        layout.addWidget(self.modified_image_label)
        self.setLayout(layout)

    def display_image(self, image, label_type='modified'):
        label = self.modified_image_label if label_type == 'modified' else self.original_image_label
        if len(image.shape) == 2:
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_Grayscale8)
        else:
            q_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0],
                             QImage.Format_RGB888).rgbSwapped()

        pixmap = QPixmap.fromImage(q_image)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
