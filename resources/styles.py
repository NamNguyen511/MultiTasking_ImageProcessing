# styles.py

# General Application Styles
general_style = """
    QWidget {
        background-color: #f0f0f0;  /* Light grey background */
        font-family: Arial, sans-serif;
        font-size: 18px;
    }
"""

# Button Styles
button_style = """
    QPushButton {
        background-color: #4CAF50;  /* Green background */
        color: white;                /* White text */
        border-radius: 10px;         /* Rounded corners */
        padding: 8px 12px;
        font-size: 16px;
        min-width: 150px;
        margin-bottom: 10px;
    }
    QPushButton:hover {
        background-color: #45a049;  /* Darker green on hover */
    }
"""

# Input Field Styles
input_style = """
    QLineEdit {
        border: 2px solid #ccc;
        border-radius: 5px;
        padding: 5px;
        font-size: 14px;
        min-width: 150px:
        margin-bottom: 10px
    }
"""

# Group Box Styles
groupbox_style = """
    QGroupBox {
        margin-top: 20px;
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 5px;
        font-weight: bold;
        color: #333;
    }
"""

# QTabWidget Styles
tabWidget_style = """
    QTabWidget::pane {
        border: 1px solid #ccc;
        background: #e6e6e6;
    }
    QTabBar::tab {
        background: #d9d9d9;
        border: 1px solid #ccc;
        padding: 8px;
        margin-left: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background: #eeeeee;
    }
"""

# QToolBox Styles
toolbox_style = """
    QToolBox::tab {
        background: #d9d9d9;
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 8px;
        margin-top: 2px;
        min-width: 200px;
    }
    QToolBox::tab:selected {
        background: #ffffff;
        font-weight: bold;
        color: #4CAF50;
    }
    QToolBox::tab:hover {
        background: #eeeeee;
    }
"""

# Label Styles
label_style = """
    QLabel {
        color: #333;
        font-weight: normal;
    }
"""

# Combine all styles into one stylesheet
combined_styles = general_style + button_style + input_style + groupbox_style + tabWidget_style + toolbox_style + label_style
