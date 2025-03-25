import sys
import cv2
import numpy as np

# Importing PyQt5 Libraries
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QGroupBox, QFrame, QSizePolicy, QMenuBar, QAction,
    QMessageBox, QToolBar, QStatusBar, QLabel, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt5.QtGui import QPalette, QColor, QIcon, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut

# Importing Gui folders
from gui.button_panel import ButtonPanel
from gui.image_viewer import ImageViewer
from gui.histogram_window import HistogramWindow
from gui.dockable_panel import DockablePanel
from gui.operation_dialog import OperationDialog

# Importing modules folders
from modules.pipeline_manager import  (
    PipelineManager, HueSaturationOperation,
    ColorBalanceAdjustment, ResizeOperation,
    RotateOperation, MorphOperations,
    SobelEdgeDetectionOperation
)
from modules.basic_operations import load_image, resize_image, rotate_image, save_image
from modules.filtering import blur_images, canny_detect_edges, morphological_filters
from modules.color_processing import hue_saturation_adjustment, color_balance_adjustment

# Importing styles
from resources.styles import combined_styles

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tool_bar = None
        self.setWindowTitle("Image Multitask Processing")
        self.setGeometry(100, 100, 1400, 1000)

        self.original_image = None  # Store the original image
        self.current_image = None   # Store the current image
        self.total_angle = 0        # Store cumulative angle for rotation
        self.operation_count = 0    # Track number of operations
        self.pipeline_manager = PipelineManager()

        # Adding global styles
        self.setStyleSheet(combined_styles)

        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create left panel for image display
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Initialize image viewer with proper settings
        self.image_viewer = ImageViewer(self)
        self.image_viewer.zoom_factor = 1.0  # Initialize zoom factor
        left_layout.addWidget(self.image_viewer)

        # Create operation history panel
        history_panel = QFrame()
        history_panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        history_layout = QVBoxLayout(history_panel)

        history_label = QLabel("Operation History")
        history_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        history_layout.addWidget(history_label)

        self.operation_list = QListWidget()
        self.operation_list.setMinimumWidth(250)
        self.operation_list.itemClicked.connect(self.on_operation_selected)
        history_layout.addWidget(self.operation_list)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(history_panel)

        # Create and add the dockable panel
        self.dock_panel = DockablePanel(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_panel)

        # Create menu bar and status bar
        self.create_menus_and_toolbar()
        self.create_status_bar()

        # Initialize operation history
        self.operation_history = []

        # Create shortcuts
        self.create_shortcuts()

        # Initialize the operation history display
        self.update_operation_history()

    def run(self):
        self.show()
        
    # -------------------------------------------------
    # 1. MENUS & TOOLBAR
    # ------------------------------------------------
    def show_operation_history(self):
        """Show the operation history panel"""
        if not self.pipeline_manager or not self.pipeline_manager.operations:
            QMessageBox.information(self, "Operation History", "No operations performed yet.")
            return
        self.update_operation_history()

    def on_operation_selected(self, item):
        """Handle operation selection from history"""
        try:
            index = item.data(Qt.UserRole)
            operation = self.pipeline_manager.operations[index]
            dialog = OperationDialog(operation, self)
            if dialog.exec_():
                new_operation = dialog.get_updated_operation()
                self.pipeline_manager.update_operation(index, new_operation)
                self.current_image = self.pipeline_manager.current_image
                self.image_viewer.display_image(self.current_image, label_type="modified")
                self.update_operation_history()  # Update history after editing
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update operation: {str(e)}")
    
    def create_shortcuts(self):
        """Create keyboard shortcuts for common operations"""
        # File operations
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.load_image)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_image)
        
        # Edit operations
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_operation)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.redo_operation)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.reset_image)
        
        # View operations
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.show_histogram)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self.zoom_out)
        
        # Operation shortcuts
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self.blur_image)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.canny_edge)
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(self.morphological_filters)
        QShortcut(QKeySequence("Ctrl+G"), self).activated.connect(self.adjust_color_balance)
    
    def zoom_in(self):
        """Zoom in the image"""
        if self.current_image is not None and hasattr(self.image_viewer, 'zoom_factor'):
            self.image_viewer.zoom_factor *= 1.2
            self.image_viewer.update_zoom()
            self.update_status_bar()
    
    def zoom_out(self):
        """Zoom out the image"""
        if self.current_image is not None and hasattr(self.image_viewer, 'zoom_factor'):
            self.image_viewer.zoom_factor /= 1.2
            self.image_viewer.zoom_factor = max(0.1, self.image_viewer.zoom_factor)  # Prevent too small zoom
            self.image_viewer.update_zoom()
            self.update_status_bar()


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

        # History Menu
        history_menu = menu_bar.addMenu("History")
        
        show_history_action = QAction("Show Operation History", self)
        show_history_action.triggered.connect(self.show_operation_history)
        history_menu.addAction(show_history_action)

        # --- TOOLBAR ---
        # Create a top toolbar and add selected actions
        self.tool_bar = QToolBar("Main Toolbar", self)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        self.tool_bar.addAction(load_action)
        self.tool_bar.addAction(save_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(undo_action)
        self.tool_bar.addAction(redo_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(show_history_action)
    

    # -----------------------------------------------
    #  2. STATUS BAR
    # -----------------------------------------------
    def create_status_bar(self):
        """Creates a status bar at the bottom of the window."""
        self.status_bar = self.statusBar()
        
        # Image info panel
        self.image_info_label = QLabel()
        self.status_bar.addPermanentWidget(self.image_info_label)
        
        # Operation count panel
        self.operation_count_label = QLabel()
        self.status_bar.addPermanentWidget(self.operation_count_label)
        
        # Memory usage panel
        self.memory_usage_label = QLabel()
        self.status_bar.addPermanentWidget(self.memory_usage_label)
        
        # Initialize status bar
        self.update_status_bar()
        
    def update_status_bar(self, message=None):
        """Update status bar with information"""
        if self.current_image is not None:
            # Update image info
            height, width = self.current_image.shape[:2]
            channels = self.current_image.shape[2] if len(self.current_image.shape) == 3 else 1
            self.image_info_label.setText(f"Size: {width}x{height} | Channels: {channels}")
            
            # Update operation count
            operation_count = len(self.pipeline_manager.operations) if self.pipeline_manager else 0
            self.operation_count_label.setText(f"Operations: {operation_count}")
            
            # Update memory usage
            memory_bytes = self.current_image.nbytes
            memory_mb = memory_bytes / (1024 * 1024)
            self.memory_usage_label.setText(f"Memory: {memory_mb:.2f} MB")
        else:
            self.image_info_label.setText("No image loaded")
            self.operation_count_label.setText("Operations: 0")
            self.memory_usage_label.setText("Memory: 0.00 MB")
            
        # Show temporary message if provided
        if message:
            self.status_bar.showMessage(message, 5000)  # Show for 5 seconds

    # -----------------------------------------------
    #  3. LOAD & SAVE
    # -----------------------------------------------
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_name:
            try:
                self.original_image = load_image(file_name)
                # Pipeline Instance
                self.pipeline_manager = PipelineManager()
                self.pipeline_manager.set_image(self.original_image)
                self.current_image = self.original_image.copy()

                # Reset operation tracking
                self.operation_count = 0
                self.operation_history = []

                # Display the original image
                self.image_viewer.display_image(self.original_image, label_type="original")
                self.image_viewer.modified_image_label.clear()
                self.update_status_bar()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def save_image(self):
        if not self.check_image_loaded():
            return

        if self.current_image is not None:
            try:
                options = QFileDialog.Options()
                file_name, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Image",
                    "",
                    "PNG Files (*.png);;JPEG Files (*.jpg);;BMP Files (*.bmp);;All Files (*)",
                    options=options
                )
                if file_name:
                    save_image(self.current_image, file_name)
                    QMessageBox.information(self, "Success", "Image saved successfully!")
                    self.update_status_bar()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")

    def show_message(self, message):
        QMessageBox.warning(self, "Warning", message)

    # -----------------------------------------------
    #  4. EDIT METHODS (Undo, Redo, Reset, etc.)
    # -----------------------------------------------
    def undo_operation(self):
        """Undo the last operation"""
        try:
            if self.pipeline_manager.undo():
                self.current_image = self.pipeline_manager.current_image
                self.image_viewer.display_image(self.current_image, label_type="modified")
                self.update_operation_history()  # Update history after undo
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to undo: {str(e)}")

    def redo_operation(self):
        """Redo the last undone operation"""
        try:
            if self.pipeline_manager.redo():
                self.current_image = self.pipeline_manager.current_image
                self.image_viewer.display_image(self.current_image, label_type="modified")
                self.update_operation_history()  # Update history after redo
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to redo: {str(e)}")

    def reset_image(self):
        """Reset image to original state"""
        try:
            if self.pipeline_manager.reset():
                self.current_image = self.pipeline_manager.current_image
                self.image_viewer.display_image(self.current_image, label_type="modified")
                self.update_operation_history()  # Update history after reset
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset image: {str(e)}")

    def show_operation_history(self):
        """Show a dialog with operation history"""
        if not self.operation_history:
            QMessageBox.information(self, "Operation History", "No operations performed yet.")
            return

        history_text = "Operation History:\n\n"
        for i, op in enumerate(self.operation_history, 1):
            history_text += f"{i}. {op}\n"

        msg = QMessageBox(self)
        msg.setWindowTitle("Operation History")
        msg.setText(history_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    # -----------------------------------------------
    #  5. VIEW METHODS (Toggle Panel, Toggle Original, Show Histogram)
    # -----------------------------------------------
    def toggle_side_panel(self, checked):
        """Show or hide the side panel."""
        self.button_panel.setVisible(checked)
        self.update_status_bar("Side Panel Toggled")

    def toggle_original(self, checked):
        """Toggle between showing the original image and the processed image."""
        if not self.check_image_loaded():
            return

        if checked:
            # Show original
            self.image_viewer.display_image(self.original_image, label_type="modified")
            self.update_status_bar("Showing original image")
        else:
            # Show current (processed) image
            self.image_viewer.display_image(self.current_image, label_type="modified")
            self.update_status_bar("Showing processed image")

    def show_histogram(self):
        if not self.check_image_loaded():
            return
        histogram_window = HistogramWindow(self.current_image)
        histogram_window.show()
        self.update_status_bar("Displaying histogram")

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

        try:
            width = int(width_str) if width_str else self.current_image.shape[1]
            height = int(height_str) if height_str else self.current_image.shape[0]

            # Remove any existing resize operations
            self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, ResizeOperation)]
            self.pipeline_manager.add_operation(ResizeOperation(width, height))

            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.update_operation_history()
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to resize image: {str(e)}")

    def rotate_image(self):
        if not self.check_image_loaded():
            return

        try:
            angle_str = self.dock_panel.angle_input.text()
            angle = int(angle_str) if angle_str else 90

            self.total_angle = (self.total_angle + angle) % 360

            self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, RotateOperation)]
            self.pipeline_manager.add_operation(RotateOperation(self.total_angle))

            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.update_operation_history()
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rotate image: {str(e)}")

    def blur_image(self):
        if not self.check_image_loaded():
            return
        try:
            kernel_str = self.dock_panel.blur_size_input.text()
            kernel_size = int(kernel_str) if kernel_str else 5
            kernel = (kernel_size, kernel_size)

            if self.current_image is not None:
                blurred_image = blur_images(self.current_image, kernel)
                self.current_image = blurred_image
                self.image_viewer.display_image(self.current_image, label_type='modified')
                self.update_operation_history()
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to blur image: {str(e)}")

    def canny_edge(self):
        if not self.check_image_loaded():
            return
        try:
            low_str = self.dock_panel.low_threshold_input.text()
            high_str = self.dock_panel.high_threshold_input.text()

            low_threshold = int(low_str) if low_str else 50
            high_threshold = int(high_str) if high_str else 150

            if self.current_image is not None:
                self.current_image = canny_detect_edges(self.current_image, low_threshold, high_threshold)
                self.image_viewer.display_image(self.current_image, label_type='modified')
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply Canny edge detection: {str(e)}")

    def apply_color_from_palette(self, hue, saturation):
        if not self.check_image_loaded():
            return
        try:
            # Remove any previous hue/saturation operation
            self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if not isinstance(op, HueSaturationOperation)]
            # Add new hue/saturation
            self.pipeline_manager.add_operation(HueSaturationOperation(hue, saturation))
            # Update the displayed image
            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.update_operation_history()
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to adjust color: {str(e)}")

    def adjust_color_balance(self):
        if not self.check_image_loaded():
            return
        try:
            red_balance = self.button_panel.red_slider.value()
            green_balance = self.button_panel.green_slider.value()
            blue_balance = self.button_panel.blue_slider.value()

            self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if
                                                not isinstance(op, ColorBalanceAdjustment)]
            self.pipeline_manager.add_operation(ColorBalanceAdjustment(red_balance, blue_balance, green_balance))

            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type='modified')
            self.update_operation_history()
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to adjust color balance: {str(e)}")

    def morphological_filters(self):
        if not self.check_image_loaded():
            return
        try:
            kernel_shape = self.dock_panel.filter_shape_combo.currentData()
            operation_type = self.dock_panel.filter_type_combo.currentData()

            if self.original_image is not None:
                self.pipeline_manager.operations = [op for op in self.pipeline_manager.operations if
                                                    not isinstance(op, MorphOperations)]
                self.pipeline_manager.add_operation(MorphOperations(kernel_shape, operation_type))
                self.current_image = self.pipeline_manager.current_image
                self.image_viewer.display_image(self.current_image, label_type="modified")
                self.update_operation_history()  # Update history after operation
                self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply morphological operation: {str(e)}")

    def sobel_edge_detection(self):
        if not self.check_image_loaded():
            return
        try:
            model_index = self.dock_panel.sobel_combo.currentIndex()
            mode = "Vertical" if model_index == 0 else "Horizontal"

            self.pipeline_manager.add_operation(SobelEdgeDetectionOperation(mode=mode))
            self.current_image = self.pipeline_manager.current_image
            self.image_viewer.display_image(self.current_image, label_type="modified")
            self.update_operation_history()  # Update history after operation
            self.update_status_bar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply Sobel edge detection: {str(e)}")

    def update_operation_history(self):
        """Update the operation history list widget with current operations"""
        self.operation_list.clear()
        if self.pipeline_manager:
            operations = self.pipeline_manager.get_operation_history()
            for i, op in enumerate(operations):
                item = QListWidgetItem(f"{i+1}. {op}")
                item.setData(Qt.UserRole, i)
                self.operation_list.addItem(item)
                
    
