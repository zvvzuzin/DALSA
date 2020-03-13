#!/usr/bin/env python3

import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QCheckBox, QTextEdit
from PyQt5.QtGui import QIcon, QPixmap, QImage
from time import sleep
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import libdalsa
import cv2


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=5, dpi=60):
        fig = Figure(figsize=(width, height), dpi=dpi)
        # self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        # self.plot()
    #
    def plot(self, img):
        # arr = np.random.randint(0, 100, 1000)
        # self.fig.cla()
        self.ax.cla()
        self.ax.hist(img.ravel()/255, bins=256, range=(0,1), density=True)
        self.draw()

class GettingImages(QThread):
    def __init__(self, img: QLabel, text: QLabel, full_size: QCheckBox, hist: Canvas):
        QThread.__init__(self)
        self.snap_image = None
        self.hist = hist
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
        self.hist.plot(self.snap_image)

    def run(self):
        self.camera.ctx.GevStartImageTransfer(-1)
        # it = 0
        while self.running:
            # self.camera.ctx.GevWaitForNextImage()
            self.snap_image = self.camera.get_image()
            img_resized = self.snap_image.copy()
            if self.full_size.isChecked():
                img_resized = cv2.resize(img_resized, (1024, 840))
            height, width = img_resized.shape
            bytes_per_line = 1 * width
            self.img.setPixmap(QPixmap(QImage(img_resized, width, height, bytes_per_line, QImage.Format_Grayscale8)))
            # it += 1
            # if it % 10 == 0:
            #     self.hist.plot(self.snap_image)
            sleep(1e-2)
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

        # fig = plt.figure(figsize=(5,4), dpi=100)

        self.hist = Canvas(self)
        self.hist.move(10, 450)
        # self.hist.setPa
        # self.hist.resize(1024, 840)

        self.text_connection = QLabel(self)
        self.text_connection.setGeometry(10, 10, 300, 50)
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

        self.text_1 = QLabel(self)
        self.text_1.setGeometry(10, 10, 200, 20)
        self.text_1.move(10, 180)
        self.text_1.setText('Number of frames for saving')

        self.textedit_1 = QTextEdit('1', self)
        self.textedit_1.setGeometry(10, 10, 100, 30)
        self.textedit_1.move(10, 200)

        self.text_2 = QLabel(self)
        self.text_2.setGeometry(10, 10, 200, 20)
        self.text_2.move(10, 240)
        self.text_2.setText('Number of batch. Previous was None')

        self.textedit_2 = QTextEdit('1', self)
        self.textedit_2.setGeometry(10, 10, 100, 30)
        self.textedit_2.move(10, 260)

        self.btn_save_img = QPushButton('Save Image', self)
        self.btn_save_img.setDisabled(True)
        self.btn_save_img.setGeometry(10, 10, 200, 40)
        self.btn_save_img.setToolTip('Save image')
        self.btn_save_img.move(10, 300)
        self.btn_save_img.clicked.connect(self.save_image)

        self.btn_rt = QPushButton('Real-time START', self)
        self.btn_rt.setDisabled(True)
        self.btn_rt.setGeometry(10, 10, 200, 40)
        self.btn_rt.setToolTip('Start/stop realtime')
        self.btn_rt.move(10, 360)
        self.btn_rt.clicked.connect(self.realtime)

        self.btn_quit = QPushButton('Quit', self)
        self.btn_quit.setGeometry(10, 10, 200, 40)
        self.btn_quit.clicked.connect(QCoreApplication.quit)
        self.btn_quit.move(10, 800)

        self.chk_img_size = QCheckBox('Full size in frame', self)
        # self.chk_img_size.setGeometry(10, 10, 100, 40)
        self.chk_img_size.move(10, 760)
        self.chk_img_size.setChecked(True)
        # self.showMaximized()

        self.show()

    @pyqtSlot()
    def initialize(self):
        print('Init')
        self.thread = GettingImages(self.image, self.text_connection, self.chk_img_size, self.hist)
        self.btn_connect.setEnabled(True)
        self.btn_save_img.setDisabled(True)

    @pyqtSlot()
    def connect(self):
        if self.btn_connect.text() == 'Disconnect':
            if self.thread.disconn():
                self.btn_connect.setText('Connect')
                self.btn_snap.setDisabled(True)
                self.btn_rt.setDisabled(True)
                self.btn_save_img.setDisabled(True)
        elif self.btn_connect.text() == 'Connect':
            if self.thread.connect():
                self.btn_connect.setText('Disconnect')
                self.btn_snap.setEnabled(True)
                self.btn_rt.setEnabled(True)
                self.btn_save_img.setEnabled(True)
                print("Initial image parameters:")
                print(self.thread.camera.image_params)
                # print("Initial image parameters:")
                # print(self.thread.camera.camera_options)


    @pyqtSlot()
    def snap(self):
        self.thread.snap()

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
        # if hasattr(self.thread.snap_image, 'shape'):
        self.thread.running = True
        self.thread.start()
        sleep(1)
        for it in range(int(self.textedit_1.toPlainText())):

            cv2.imwrite('images/' + self.textedit_2.toPlainText() + '_' + datetime.now().strftime("%H:%M:%S_%d-%m-%Y_") + str(it) + '.png', self.thread.snap_image)
            # print(datetime())
        self.thread.running = False
        text = self.text_2.text().split(' ')
        text[-1] = self.textedit_2.toPlainText()
        self.textedit_2.setText(str(int(text[-1]) + 1))
        text = ' '.join(text)
        # print(text)
        # text = sum(text, ' ')
        self.text_2.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
ex = App()
sys.exit(app.exec_())
