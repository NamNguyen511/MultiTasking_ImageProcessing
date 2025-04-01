from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QVBoxLayout, 
                           QScrollArea, QSlider, QFrame, QToolBar, QAction)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon, QColor, QFont
from PyQt5.QtCore import Qt, QPoint, QSize, QRect


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create title bar
        self.title_bar = QFrame()
        self.title_bar.setFrameStyle(QFrame.StyledPanel)
        self.title_bar.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                padding: 5px;
                border-bottom: 1px solid #cccccc;
            }
            QLabel {
                font-weight: bold;
                color: #333333;
            }
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Image title
        self.image_title = QLabel("No Image Loaded")
        title_layout.addWidget(self.image_title)
        
        # Zoom display
        self.zoom_label = QLabel("100%")
        self.zoom_label.setStyleSheet("color: #666666;")
        title_layout.addWidget(self.zoom_label)
        
        # Add title bar to main layout
        self.layout.addWidget(self.title_bar)
        
        # Create mini-toolbar
        self.mini_toolbar = QToolBar()
        self.mini_toolbar.setIconSize(QSize(16, 16))
        self.mini_toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #cccccc;
                spacing: 5px;
                padding: 2px;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 2px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
            }
        """)
        
        # Add toolbar actions
        self.zoom_in_action = QAction(QIcon("icons/zoom_in.png"), "Zoom In", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.mini_toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction(QIcon("icons/zoom_out.png"), "Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.mini_toolbar.addAction(self.zoom_out_action)
        
        self.mini_toolbar.addSeparator()
        
        self.fit_action = QAction(QIcon("icons/fit.png"), "Fit to Window", self)
        self.fit_action.triggered.connect(self.fit_to_window)
        self.mini_toolbar.addAction(self.fit_action)
        
        self.original_size_action = QAction(QIcon("icons/original.png"), "Original Size", self)
        self.original_size_action.triggered.connect(self.original_size)
        self.mini_toolbar.addAction(self.original_size_action)
        
        # Add mini-toolbar to main layout
        self.layout.addWidget(self.mini_toolbar)
        
        # Create slider container with padding
        slider_container = QFrame()
        slider_container.setFrameStyle(QFrame.StyledPanel)
        slider_container.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                padding: 5px;
                border-top: 1px solid #cccccc;
                border-bottom: 1px solid #cccccc;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
                margin: 0 5px;
            }
            QSlider {
                margin: 0 10px;
            }
        """)
        slider_layout = QHBoxLayout(slider_container)
        slider_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add comparison mode label
        self.comparison_label = QLabel("Before")
        self.comparison_label.setVisible(False)
        slider_layout.addWidget(self.comparison_label)
        
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
        
        # Add "After" label
        self.after_label = QLabel("After")
        self.after_label.setVisible(False)
        slider_layout.addWidget(self.after_label)
        
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
        self.current_image_name = None
        
    def set_image_name(self, name):
        """Set the current image name in the title bar"""
        self.current_image_name = name
        self.image_title.setText(name if name else "No Image Loaded")
        
    def zoom_in(self):
        """Zoom in the image"""
        self.zoom_factor *= 1.2
        self.update_zoom()
        
    def zoom_out(self):
        """Zoom out the image"""
        self.zoom_factor /= 1.2
        self.zoom_factor = max(0.1, self.zoom_factor)
        self.update_zoom()
        
    def fit_to_window(self):
        """Fit image to window size"""
        if self.modified_pixmap:
            self.zoom_factor = 1.0
            self.update_zoom()
            
    def original_size(self):
        """Show image at original size"""
        if self.modified_pixmap:
            self.zoom_factor = 2.0  # Show at 100% of original size
            self.update_zoom()
            
    def update_zoom(self):
        """Update zoom for both images"""
        # Update zoom label
        zoom_percentage = int(self.zoom_factor * 100)
        self.zoom_label.setText(f"{zoom_percentage}%")
        
        if self.comparison_mode:
            self.update_comparison()
        elif self.modified_pixmap:
            scaled_pixmap = self.modified_pixmap.scaled(
                self.scroll.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
    def toggle_comparison_mode(self, enabled=True):
        """Toggle split view comparison mode"""
        self.comparison_mode = enabled
        self.comparison_slider.setVisible(enabled)
        self.comparison_label.setVisible(enabled)
        self.after_label.setVisible(enabled)
        
        if enabled and self.original_pixmap and self.modified_pixmap:
            self.update_comparison()
        elif not enabled and self.modified_pixmap:
            scaled_pixmap = self.modified_pixmap.scaled(
                self.scroll.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
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
        
        # Calculate positions to center images
        orig_x = (size.width() - scaled_original.width()) // 2
        orig_y = (size.height() - scaled_original.height()) // 2
        mod_x = (size.width() - scaled_modified.width()) // 2
        mod_y = (size.height() - scaled_modified.height()) // 2
        
        # Draw original image on the left side
        painter.drawPixmap(
            QRect(orig_x, orig_y, split_x - orig_x, scaled_original.height()),
            scaled_original,
            QRect(0, 0, split_x - orig_x, scaled_original.height())
        )
        
        # Draw modified image on the right side
        painter.drawPixmap(
            QRect(split_x, mod_y, scaled_modified.width() - (split_x - mod_x), scaled_modified.height()),
            scaled_modified,
            QRect(split_x - mod_x, 0, scaled_modified.width() - (split_x - mod_x), scaled_modified.height())
        )
        
        # Draw split line with highlighting
        pen = painter.pen()
        pen.setColor(QColor(76, 175, 80))  # Green color
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(split_x, 0, split_x, result.height())
        
        painter.end()
        
        # Display the result
        self.image_label.setPixmap(result)
        
    def resizeEvent(self, event):
        """Handle resize events to maintain image scaling"""
        super().resizeEvent(event)
        self.update_zoom()
        


