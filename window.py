import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QThread
import libdalsa

# class Getting_Images(QThread):
#     def __init__(self):
#         QThread.__init__(self)
#
#     def __del__(self):
#         self.wait()
#
#     def initial(self):
#         self.cmrs = libdalsa.Camera()
#         self.flag_connect = False
#
#     def connect(self):
#         if self.flag_connect:
#             status = self.cmrs.disconnect()
#             print(status)
#             self.btn_connect.setText('Connect')
#             text_line = 'Disconnected'
#             self.text_connection.setText(text_line)
#             self.flag_connect = False
#         else:
#             status = self.cmrs.connect()
#             # self.btn_connect.setText('Disconnect')
#             # print(status)
#             self.flag_connect = True
#             # text_line = 'Connected to camera'
#             # self.text_connection.setText(text_line)
#             #
#
#     def run(self):



# your logic here

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'Определение содержания асбеста'
        # self.left = 10
        # self.top = 10
        # self.width = 1920
        # self.height = 1080
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        self.image = QLabel(self)
        self.image.move(500, 10)
        self.image.resize(1024, 840)

        self.flag_connect = False
        self.text_connection = QLabel(self)
        self.text_connection.setGeometry(10, 10, 300, 100)
        self.text_connection.move(250, 20)
        self.text_connection.setText('Disconnected')

        self.btn_init = QPushButton('Initialize', self)
        self.btn_init.setGeometry(10, 10, 200, 40)
        self.btn_init.setToolTip('Connect to camera')
        self.btn_init.move(10, 10)
        self.btn_init.clicked.connect(self.initialize)

        self.btn_connect = QPushButton('Connect', self)
        self.btn_connect.setGeometry(10, 10, 200, 40)
        self.btn_connect.setToolTip('Connect to camera')
        self.btn_connect.move(10, 70)
        self.btn_connect.clicked.connect(self.connect)

        self.btn_snap = QPushButton('Snap image', self)
        self.btn_snap.setGeometry(10, 10, 200, 40)
        self.btn_snap.setToolTip('Connect to camera')
        self.btn_snap.move(10, 130)
        self.btn_snap.clicked.connect(self.snap)

        self.btn_rt = QPushButton('Real-time START', self)
        self.btn_rt.setGeometry(10, 10, 200, 40)
        self.btn_rt.setToolTip('Connect to camera')
        self.btn_rt.move(10, 190)
        self.btn_rt.clicked.connect(self.realtime)

        self.btn_quit = QPushButton('Quit', self)
        self.btn_quit.setGeometry(10, 10, 200, 40)
        self.btn_quit.clicked.connect(QCoreApplication.quit)
        self.btn_quit.move(10, 800)

        # self.showMaximized()
        self.show()


    @pyqtSlot()
    def initialize(self):
        self.cmrs = libdalsa.Camera()
        text_line = str()
        if self.cmrs.ip_info:
            text_line += 'Found cameras:\n'
            for num_cmr in self.cmrs.ip_info.keys():
                text_line += 'Camera ' + str(num_cmr) + ': ' + self.cmrs.ip_info[num_cmr] + '\n'
        self.text_connection.setText(text_line)


    @pyqtSlot()
    def connect(self):
        if self.flag_connect:
            status = self.cmrs.disconnect()
            print(status)
            self.btn_connect.setText('Connect')
            text_line = 'Disconnected'
            self.text_connection.setText(text_line)
            self.flag_connect = False
        else:
            status = self.cmrs.connect()
            self.btn_connect.setText('Disconnect')
            print(status)
            self.flag_connect = True
            text_line = 'Connected to camera'
            self.text_connection.setText(text_line)


    @pyqtSlot()
    def snap(self):
        img = self.cmrs.get_image()
        height, width = img.shape
        bytesPerLine = 1 * width
        self.image.setPixmap(QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_Grayscale8)))


    @pyqtSlot()
    def realtime(self):
        self.btn_rt.setText('Real-time STOP')
        img = self.cmrs.get_image()
        height, width = img.shape
        bytesPerLine = 1 * width
        while True:
            img = self.cmrs.get_image()
            self.image.setPixmap(QPixmap(QImage(img, width, height, bytesPerLine, QImage.Format_Grayscale8)))
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())
