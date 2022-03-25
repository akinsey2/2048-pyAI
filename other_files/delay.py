# importing libraries
from PyQt6 import QtWidgets, QtCore, QtGui
import sys


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Python ")

        # setting geometry
        self.setGeometry(100, 100, 500, 400)

        # calling method
        self.UiComponents()

        # showing all the widgets
        self.show()

    # method for components
    def UiComponents(self):
        # creating a command link button
        cl_button = QCommandLinkButton("Press", self)

        # setting geometry
        cl_button.setGeometry(250, 100, 200, 50)

        # setting auto repeat
        cl_button.setAutoRepeat(True)

        # setting delay time
        cl_button.setAutoRepeatDelay(1000)

        # creating label
        label = QLabel("GeeksforGeeks", self)

        # setting label geometry
        label.setGeometry(50, 100, 200, 40)

        # getting auto repeat delay time
        value = cl_button.autoRepeatDelay()

        # setting text to the label
        label.setText("Auto Repeat Delay (ms) : " + str(value))

        # counter
        self.counter = 0

        # adding action to the button
        cl_button.clicked.connect(lambda: update_label())

        # method for updating label text
        def update_label():
            # setting label text
            label.setText(str(self.counter))

            # incrementing the counter
            self.counter += 1


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())
