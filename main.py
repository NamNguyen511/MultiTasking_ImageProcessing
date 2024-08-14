import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.run()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
