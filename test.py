import sys
import datetime as dt

print(dt.date.today().strftime('%Y.%m.%d'))

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLineEdit, QPushButton

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class WordShifter(QWidget):
    def __init__(self):
        super().__init__()
        self.unitUI()
        self.i = 0

    def unitUI(self):
        self.setFixedSize(400, 400)
        self.setWindowTitle('Перекидыватель слов')

        self.le = QLineEdit(self)
        self.le.resize(100, 20)
        self.le.move(150, 190)
        self.le.setInputMask('0000.00.00')
        self.le.returnPressed.connect(self.pressedKeys)
        self.le.textChanged.connect(self.value)

        self.show()

    def pressedKeys(self):
        print(self.le.text())
        self.lbl.setText(self.le.text())

    def value(self):
        first_part, second_part, third_part = self.le.text().split('.')
        if len(first_part) == 4:
            first_part = str(min(int(first_part), 2350))
        if len(second_part) == 2:
            print(second_part, 'aaa')
            second_part = str(min(int(second_part), 12)).rjust(2, '0')
        if len(third_part) == 2:
            third_part = str(min(int(third_part), 31)).rjust(2, '0')

        date = first_part + '.' + second_part + '.' + third_part
        print(date)

        print(self.le.cursorPosition())
        pos = self.le.cursorPosition()
        self.le.setText(date)
        self.le.setCursorPosition(pos)
        print(self.le.cursorPosition(), len(date) - 2 + int(len(first_part) == 4))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    shifter = WordShifter()
    shifter.show()

    sys.exit(app.exec())
