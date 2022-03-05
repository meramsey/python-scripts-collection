import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QApplication, QSplashScreen
from PyQt5.QtCore import QTimer


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        self.b1 = QPushButton('Display screensaver')
        self.b1.clicked.connect(self.flash_splash)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.b1)

    def flash_splash(self):
        self.splash = QSplashScreen(QPixmap('/home/user/PycharmProjects/WizardAssistant/src/main/icons/Icon.png'))

        # By default, SplashScreen will be in the center of the screen.
        # You can move it to a specific location if you want:
        # self.splash.move(10,10)

        self.splash.show()

        # Close SplashScreen after 2 seconds (2000 ms)
        QTimer.singleShot(20000, self.splash.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Dialog()
    main.show()
    sys.exit(app.exec_())
