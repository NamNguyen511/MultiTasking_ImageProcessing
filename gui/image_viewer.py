from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QScrollArea, QSlider, QFrame
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QPoint


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)  # Remove spacing between widgets
        
        # Create slider container with padding
        slider_container = QFrame()
        slider_container.setFrameStyle(QFrame.StyledPanel)
        slider_container.setStyleSheet("QFrame { background-color: #f0f0f0; padding: 5px; }")
        slider_layout = QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create comparison slider
        self.comparison_slider = QSlider(Qt.Horizontal)
        self.comparison_slider.setRange(0, 100)
        self.comparison_slider.setValue(50)
        self.comparison_slider.setVisible(False)
        self.comparison_slider.setFixedHeight(20)
        self.comparison_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #ffffff;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #5c9f5f;
                border: 1px solid #5c9f5f;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.comparison_slider.valueChanged.connect(self.update_comparison)
        
        # Add slider to container
        slider_layout.addWidget(self.comparison_slider)
        
        # Add slider container to main layout
        self.layout.addWidget(slider_container)
        
        # Create scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setMinimumSize(400, 400)
        
        # Create container for image
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignCenter)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Add image label to container layout
        self.container_layout.addWidget(self.image_label)
        
        # Set container as widget for scroll area
        self.scroll.setWidget(self.container)
        
        # Add scroll area to main layout
        self.layout.addWidget(self.scroll)
        
        # Initialize variables
        self.zoom_factor = 1.0
        self.original_pixmap = None
        self.modified_pixmap = None
        self.comparison_mode = False
        
    def display_image(self, image, label_type='modified'):
        """Display an image in the specified label"""
        if image is None:
            return
            
        # Convert image to QPixmap
        if len(image.shape) == 2:  # Grayscale image
            height, width = image.shape
            bytes_per_line = width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:  # Color image
            height, width = image.shape[:2]
            bytes_per_line = width * 3
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            
        pixmap = QPixmap.fromImage(q_image)
        
        # Store pixmaps for comparison
        if label_type == 'original':
            self.original_pixmap = pixmap
        else:
            self.modified_pixmap = pixmap
        
        # Scale pixmap
        scaled_pixmap = pixmap.scaled(
            self.scroll.size() * self.zoom_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Update display based on mode
        if self.comparison_mode and self.original_pixmap and self.modified_pixmap:
            self.update_comparison()
        else:
            self.image_label.setPixmap(scaled_pixmap)
            
    def toggle_comparison(self, show_comparison=True):
        """Toggle between side-by-side and single image view"""
        self.scroll.setVisible(show_comparison)
        if not show_comparison:
            self.image_label.clear()  # Use image_label instead of modified_image_label
        
    def toggle_comparison_mode(self, enabled=True):
        """Toggle split view comparison mode"""
        self.comparison_mode = enabled
        self.comparison_slider.setVisible(enabled)
        if enabled and self.original_pixmap and self.modified_pixmap:
            self.update_comparison()
        elif not enabled and self.modified_pixmap:
            scaled_pixmap = self.modified_pixmap.scaled(
                self.scroll.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def update_comparison(self):
        """Update the split view comparison"""
        if not self.comparison_mode or not self.original_pixmap or not self.modified_pixmap:
            return
            
        # Create a new pixmap for the combined view
        size = self.scroll.size() * self.zoom_factor
        result = QPixmap(size)
        result.fill(Qt.transparent)
        
        # Calculate split position
        split_x = (result.width() * self.comparison_slider.value()) // 100
        
        # Draw the comparison view
        painter = QPainter(result)
        
        # Scale pixmaps
        scaled_original = self.original_pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaled_modified = self.modified_pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Draw original image on the left side
        painter.drawPixmap(QPoint(0, 0), scaled_original)
        
        # Draw modified image on the right side
        painter.drawPixmap(QPoint(split_x, 0), scaled_modified,
                         scaled_modified.rect().adjusted(split_x, 0, 0, 0))
        
        # Draw split line
        painter.setPen(Qt.white)
        painter.drawLine(split_x, 0, split_x, result.height())
        
        painter.end()
        
        # Display the result
        self.image_label.setPixmap(result)
        
    def update_zoom(self):
        """Update zoom for both images"""
        if self.comparison_mode:
            self.update_comparison()
        elif self.modified_pixmap:
            scaled_pixmap = self.modified_pixmap.scaled(
                self.scroll.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def resizeEvent(self, event):
        """Handle resize events to maintain image scaling"""
        super().resizeEvent(event)
        self.update_zoom()
        


