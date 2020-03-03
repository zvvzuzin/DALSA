#!/usr/bin/env python3

import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap, QImage
from time import sleep
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QThread

import libdalsa
import cv2


class GettingImages(QThread):
    def __init__(self, img: QLabel, text: QLabel, full_size: QCheckBox):
        QThread.__init__(self)
        self.snap_image = None
        self.img = img
        self.text = text
        self.full_size = full_size
        self.running = True
        self.camera = libdalsa.Camera()

        text_line = str()
        if self.camera.ip_info:
           text_line += 'Found cameras:\n'
           for num_cmr in self.camera.ip_info.keys():
               text_line += 'Camera ' + str(num_cmr) + ': ' + self.camera.ip_info[num_cmr] + '\n'
        self.text.setText(text_line)


    def connect(self):
        if self.camera.connect() == 'OK':
            text_line = 'Connected to camera'
            self.text.setText(text_line)
            return True
        else:
            return False


    def disconn(self):
        if self.camera.disconnect() == 'OK':
            text_line = 'Disconnected'
            self.text.setText(text_line)
            return True
        else:
            return False

    def snap(self):
        self.camera.ctx.GevStartImageTransfer(0)
        self.snap_image = self.camera.get_image()
        img_resized = self.snap_image.copy()
        if self.full_size.isChecked():
            img_resized = cv2.resize(img_resized, (1024, 840))
        height, width = img_resized.shape
        bytes_per_line = 1 * width
        self.img.setPixmap(QPixmap(QImage(img_resized, width, height, bytes_per_line, QImage.Format_Grayscale8)))

    def run(self):
        self.camera.ctx.GevStartImageTransfer(-1)
        while self.running:
            self.snap_image = self.camera.get_image()
            img_resized = self.snap_image.copy()
            if self.full_size.isChecked():
                img_resized = cv2.resize(img_resized, (1024, 840))
            height, width = img_resized.shape
            bytes_per_line = 1 * width
            self.img.setPixmap(QPixmap(QImage(img_resized, width, height, bytes_per_line, QImage.Format_Grayscale8)))
            sleep(5e-3)
        self.camera.ctx.GevStopImageTransfer()


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.title = 'Определение содержания асбеста'

        self.thread = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top, self.width, self.height)

        self.image = QLabel(self)
        self.image.move(500, 10)
        self.image.resize(1024, 840)

        self.text_connection = QLabel(self)
        self.text_connection.setGeometry(10, 10, 300, 100)
        self.text_connection.move(250, 10)
        self.text_connection.setText('Disconnected')

        self.btn_init = QPushButton('Initialize', self)
        self.btn_init.setGeometry(10, 10, 200, 40)
        self.btn_init.setToolTip('Connect to camera')
        self.btn_init.move(10, 10)
        self.btn_init.clicked.connect(self.initialize)

        self.btn_connect = QPushButton('Connect', self)
        self.btn_connect.setDisabled(True)
        self.btn_connect.setGeometry(10, 10, 200, 40)
        self.btn_connect.setToolTip('Connect to camera')
        self.btn_connect.move(10, 70)
        self.btn_connect.clicked.connect(self.connect)

        self.btn_snap = QPushButton('Snap image', self)
        self.btn_snap.setDisabled(True)
        self.btn_snap.setGeometry(10, 10, 200, 40)
        self.btn_snap.setToolTip('Snap image')
        self.btn_snap.move(10, 130)
        self.btn_snap.clicked.connect(self.snap)

        self.btn_rt = QPushButton('Real-time START', self)
        self.btn_rt.setDisabled(True)
        self.btn_rt.setGeometry(10, 10, 200, 40)
        self.btn_rt.setToolTip('Start/stop realtime')
        self.btn_rt.move(10, 190)
        self.btn_rt.clicked.connect(self.realtime)

        self.btn_save_img = QPushButton('Save Image', self)
        self.btn_save_img.setDisabled(True)
        self.btn_save_img.setGeometry(10, 10, 200, 40)
        self.btn_save_img.setToolTip('Save image')
        self.btn_save_img.move(10, 250)
        self.btn_save_img.clicked.connect(self.save_image)

        self.btn_quit = QPushButton('Quit', self)
        self.btn_quit.setGeometry(10, 10, 200, 40)
        self.btn_quit.clicked.connect(QCoreApplication.quit)
        self.btn_quit.move(10, 800)

        self.chk_img_size = QCheckBox('Full size in frame', self)
        # self.chk_img_size.setGeometry(10, 10, 100, 40)
        self.chk_img_size.move(10, 750)
        # self.showMaximized()

        self.show()

    @pyqtSlot()
    def initialize(self):
        print('Init')
        self.thread = GettingImages(self.image, self.text_connection, self.chk_img_size)
        self.btn_connect.setEnabled(True)
        self.btn_save_img.setDisabled(True)

    @pyqtSlot()
    def connect(self):
        if self.btn_connect.text() == 'Disconnect':
            if self.thread.disconn():
                self.btn_connect.setText('Connect')
                self.btn_snap.setDisabled(True)
                self.btn_rt.setDisabled(True)
        elif self.btn_connect.text() == 'Connect':
            if self.thread.connect():
                self.btn_connect.setText('Disconnect')
                self.btn_snap.setEnabled(True)
                self.btn_rt.setEnabled(True)

    @pyqtSlot()
    def snap(self):
        self.thread.snap()
        self.btn_save_img.setEnabled(True)

    @pyqtSlot()
    def realtime(self):
        if self.btn_rt.text().endswith('START'):
            self.thread.running = True
            self.thread.start()
            self.btn_rt.setText('Real-time STOP')
        elif self.btn_rt.text().endswith('STOP'):
            self.thread.running = False
            self.btn_rt.setText('Real-time START')
        self.btn_save_img.setEnabled(True)

    def save_image(self):
        if hasattr(self.thread.snap_image, 'shape'):
            cv2.imwrite('images/' + datetime.now().strftime("%H:%M:%S %d-%m-%Y") + '.png', self.thread.snap_image)
            # print(datetime())


if __name__ == '__main__':
    app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())
