import sys
import cv2
import numpy as np

# Importing PyQt5 Libraries
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QGroupBox, QFrame, QSizePolicy, QMenuBar, QAction,
    QMessageBox, QToolBar, QStatusBar
)
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import Qt

# Importing Gui folders
from gui.button_panel import ButtonPanel
from gui.image_viewer import ImageViewer
from gui.histogram_window import HistogramWindow
from gui.dockable_panel import DockablePanel

# Importing modules folders
from modules.pipeline_manager import  (
    PipelineManager, HueSaturationOperation,
    ColorBalanceAdjustment, ResizeOperation,
    RotateOperation, MorphOperations,
    SobelEdgeDetectionOperation
)
from modules.basic_operations import load_image, resize_image, rotate_image
from modules.filtering import blur_images, canny_detect_edges, morphological_filters
from modules.color_processing import hue_saturation_adjustment, color_balance_adjustment

# Importing styles
from resources.styles import combined_styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tool_bar = None
        self.setWindowTitle("Image Multitask Processing.")
        self.setGeometry(100, 100, 1400, 1000)

        self.original_image = None # Store the original image
        self.current_image = None  # Store the current image
        self.total_angle = 0 # Store cumulative angle for rotation

        # Adding global styles
        self.setStyleSheet(combined_styles)

        # Pipeline Manager Reference
        self.pipeline_manager = None

        # Create the central widget
        self.image_viewer = ImageViewer(self)
        self.setCentralWidget(self.image_viewer)

        # Create and add the dockable panel
        self.dock_panel = DockablePanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_panel)

        # Create menu bar
        self.create_menus_and_toolbar()
        self.create_status_bar()

    # -------------------------------------------------
    # 1. MENUS & TOOLBAR
    # ------------------------------------------------
    def create_menus_and_toolbar(self):
        """Set up the main menu and a top toolbar with icons"""

        # --- MENUBAR ---
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        load_action = QAction(QIcon("icons/open.png"), "Load Image", self)
        load_action.triggered.connect(self.load_image)
        file_menu.addAction(load_action)

        # Save Action
        save_action = QAction(QIcon("icons/save.png"),"Save", self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction(QIcon("icons/undo.png"),"Undo", self)
        undo_action.triggered.connect(self.undo_operation)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon("icons/redo.png"), "Redo", self)
        redo_action.triggered.connect(self.redo_operation)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        reset_action = QAction("Reset Image", self)
        reset_action.triggered.connect(self.reset_image)
        edit_menu.addAction(reset_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")

        toggle_panel_action = QAction("Toggle Side Panel", self, checkable=True)
        toggle_panel_action.setChecked(True)
        toggle_panel_action.triggered.connect(self.toggle_side_panel)
        view_menu.addAction(toggle_panel_action)

        original_action = QAction("Show Original", self, checkable=True)
        original_action.triggered.connect(self.toggle_original)
        view_menu.addAction(original_action)

        histogram_action = QAction("Show Histogram", self)
        histogram_action.triggered.connect(self.show_histogram)
        view_menu.addAction(histogram_action)

        # --- TOOLBAR ---
        # Create a top toolbar and add selected actions
        self.tool_bar = QToolBar("Main Toolbar", self)
        # self.tool_bar.setIconSize(Qt.SizeMode)  # Example icon size
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        self.tool_bar.addAction(load_action)
        self.tool_bar.addAction(save_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(undo_action)
        self.tool_bar.addAction(redo_action)
        self.tool_bar.addSeparator()

    # -----------------------------------------------
    #  2. STATUS BAR
    # -----------------------------------------------
    def create_status_bar(self):
        """Creates a status bar at the bottom of the window."""
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def show_message_in_status_bar(self, message):
        """Helper to display a message in the status bar."""
        self.status_bar.showMessage(message, 5000)  # 5 seconds

    # -----------------------------------------------
    #  3. LOAD & SAVE
    # -----------------------------------------------
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            self.original_image = load_image(file_name)
            # Pipeline Instance with original image
            self.pipeline_manager = PipelineManager(self.original_image)
            self.current_image = self.original_image.copy()

            # Display the original image
            self.image_viewer.display_image(self.original_image, label_type="original")
            self.image_viewer.modified_image_label.clear()
            self.show_message_in_status_bar(f"Loaded Image: {file_name}")

    def save_image(self):
        if not self.check_image_loaded():
            return

        if self.current_image is not None:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;All Files (*)",
                options=options
            )
            if file_name:
                cv2.imwrite(file_name, self.current_image)
                QMessageBox.information(self, "Image Saved", "Your image has been saved successfully!")
                self.show_message_in_status_bar(f"Saved image to: {file_name}")
    def show_message(self, message):
        QMessageBox.warning(self, "Warning", message)

    # -----------------------------------------------
    #  4. EDIT METHODS (Undo, Redo, Reset, etc.)
    # -----------------------------------------------
    def undo_operation(self):
        if hasattr(self, 'pipeline_manager') and self.pipeline_manager:
            self.pipeline_manager.undo()
            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.show_message_in_status_bar("Undid last Operation")

    def redo_operation(self):
        if hasattr(self, 'pipeline_manager') and self.pipeline_manager:
            self.pipeline_manager.redo()
            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.show_message_in_status_bar("Redid last undone operation")

    def reset_image(self):
        """Clear all pipeline operations and revert to the original image"""
        if not self.check_image_loaded():
            return
        self.pipeline_manager.clear_operations()
        self.current_image = self.original_image.copy()
        self.image_viewer.display_image(self.current_image, label_type='modified')
        self.show_message_in_status_bar("Reset image to original")

    # -----------------------------------------------
    #  5. VIEW METHODS (Toggle Panel, Toggle Original, Show Histogram)
    # -----------------------------------------------
    def toggle_side_panel(self, checked):
        """Show or hide the side panel."""
        self.button_panel.setVisible(checked)
        self.show_message_in_status_bar("Side Panel Toggled")

    def toggle_original(self, checked):
        """Toggle between showing the original image and the processed image."""
        if not self.check_image_loaded():
            return

        if checked:
            # Show original
            self.image_viewer.display_image(self.original_image, label_type="modified")
            self.show_message_in_status_bar("Showing original image")
        else:
            # Show current (processed) image
            self.image_viewer.display_image(self.current_image, label_type="modified")
            self.show_message_in_status_bar("Showing processed image")

    def show_histogram(self):
        if not self.check_image_loaded():
            return
        histogram_window = HistogramWindow(self.current_image)
        histogram_window.show()
        self.show_message_in_status_bar("Displaying histogram")

    # -----------------------------------------------
    #  6. UTILITY
    # -----------------------------------------------

    def check_image_loaded(self):
        if self.original_image is None:
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return False
        return True

    # -----------------------------------
    # 7. METHODS CALLED BY DOCKABLE PANEL
    # -----------------------------------
    def resize_image(self):
        if not self.check_image_loaded():
            return
        width_str = self.dock_panel.width_input.text()
        height_str = self.dock_panel.height_input.text()
        if not width_str or not height_str:
            return

        width = int(width_str) if width_str else self.current_image.shape[1]
        height = int(height_str) if height_str else self.current_image.shape[0]

        # Remove any existing resize operations
        self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, ResizeOperation)]
        self.pipeline_manager.add_operation(ResizeOperation(width, height))

        self.current_image = self.pipeline_manager.current_image
        self.image_viewer.display_image(self.current_image, label_type='modified')
        self.show_message_in_status_bar(f"Resized to {width} x {height}")
    def rotate_image(self):
        if not self.check_image_loaded():
            return

        angle_str = self.dock_panel.angle_input.text()
        angle = int(angle_str) if angle_str else 90

        self.total_angle = (self.total_angle + angle) % 360

        self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, RotateOperation)]
        self.pipeline_manager.add_operation(RotateOperation(self.total_angle))

        self.current_image = self.pipeline_manager.current_image
        self.image_viewer.display_image(self.current_image, label_type='modified')
        self.show_message_in_status_bar(f"Rotated image by {angle} degrees")

    def blur_image(self):

        if not self.check_image_loaded():
            return
        kernel_str = self.dock_panel.blur_size_input.text()
        kernel_size = int(kernel_str) if kernel_str else 5
        kernel = (kernel_size, kernel_size)

        if self.current_image is not None:
            blurred_image = blur_images(self.current_image, kernel)
            self.current_image = blurred_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.show_message_in_status_bar(f"Blurred image with kernel {kernel_size} x {kernel_size}")

    def canny_edge(self):

        if not self.check_image_loaded():
            return
        low_str = self.dock_panel.low_threshold_input.text()
        high_str = self.dock_panel.high_threshold_input.text()

        low_threshold = int(low_str) if low_str else 50
        high_threshold = int(high_str) if high_str else 150

        if self.current_image is not None:
            self.current_image = canny_detect_edges(self.current_image, low_threshold, high_threshold)
            self.image_viewer.display_image(self.current_image, label_type='modified')

    def apply_color_from_palette(self, hue, saturation):

        if not self.check_image_loaded():
            return

        # Remove any previous hue/saturation operation
        self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, HueSaturationOperation)]
        # Add new hue/saturation
        self.pipeline_manager.add_operation(HueSaturationOperation(hue, saturation))
        # Update the displayed image
        self.current_image = self.pipeline_manager.current_image
        self.image_viewer.display_image(self.current_image, label_type='modified')
        self.show_message_in_status_bar(f"Applied hue={hue}, saturation={saturation}")

    def adjust_color_balance(self):

        if not self.check_image_loaded():
            return

        red_balance = self.button_panel.red_slider.value()
        green_balance = self.button_panel.green_slider.value()
        blue_balance = self.button_panel.blue_slider.value()

        self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if
                                            not isinstance(op, ColorBalanceAdjustment)]
        self.pipeline_manager.add_operation(ColorBalanceAdjustment(red_balance, blue_balance, green_balance))

        self.current_image = self.pipeline_manager.current_image
        self.image_viewer.display_image(self.current_image, label_type='modified')

    # Morphological Operations
    def morphological_filters(self):
        if not self.check_image_loaded():
            return

        kernel_shape = self.dock_panel.filter_shape_combo.currentData()
        operation_type = self.dock_panel.filter_type_combo.currentData()

        if self.original_image is not None:
            self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if
                                                not isinstance(op, MorphOperations)]
            self.pipeline_manager.add_operation(MorphOperations(kernel_shape, operation_type))
            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type="modified")
            self.show_message_in_status_bar("Applied morphological operation")

    def sobel_edge_detection(self):
        if not self.check_image_loaded():
            return
        model_index = self.dock_panel.sobel_combo.currentIndex()
        mode = "Vertical" if model_index == 0 else "Horizontal"

        self.pipeline_manager.add_operation(SobelEdgeDetectionOperation(mode=mode))
        self.current_image = self.pipeline_manager.current_image
        self.image_viewer.display_image(self.current_image, label_type="modified")
        self.show_message_in_status_bar(f"Sobel Edge Detection: {mode}")
    def run(self):
        self.show()
