import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit
from PyQt5 import uic


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_files/untitled.ui', self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wnd = Window()
    wnd.show()

    sys.excepthook = except_hook
    sys.exit(app.exec())
