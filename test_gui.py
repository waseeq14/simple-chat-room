from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QTextEdit, QMenu, QAction, QFileDialog
import sys
import socket
import threading
import json
import base64
from PyQt5.QtGui import QPixmap


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 593)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.chat_textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.chat_textEdit.setGeometry(QtCore.QRect(10, 0, 601, 461))
        self.chat_textEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.chat_textEdit.setReadOnly(True)
        self.chat_textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chat_textEdit.setObjectName("chat_textEdit")
        self.input_lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.input_lineEdit.setGeometry(QtCore.QRect(10, 470, 481, 61))
        self.input_lineEdit.setObjectName("input_lineEdit")
        self.send_btn = QtWidgets.QPushButton(self.centralwidget)
        self.send_btn.setGeometry(QtCore.QRect(500, 470, 111, 31))
        self.send_btn.setObjectName("send_btn")
        self.sendImg_btn = QtWidgets.QPushButton(self.centralwidget)
        self.sendImg_btn.setGeometry(QtCore.QRect(500, 500, 111, 28))
        self.sendImg_btn.setObjectName("sendImg_btn")
        self.changeColor_btn = QtWidgets.QPushButton(self.centralwidget)
        self.changeColor_btn.setGeometry(QtCore.QRect(500, 530, 111, 28))
        self.changeColor_btn.setObjectName("changeColor_btn")
        self.changeColor_btn.setText("Change Border Color")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setStyleSheet("")
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.actionBackground_Color = QtWidgets.QAction(MainWindow)
        self.actionBackground_Color.setObjectName("actionBackground_Color")
        self.actionBackground_Color.setText("Background Color")
        self.menuSettings.addAction(self.actionBackground_Color)
        self.profile_label = QtWidgets.QLabel(self.centralwidget)
        self.profile_label.setGeometry(QtCore.QRect(10, 530, 48, 50))
        self.profile_label.setObjectName("profile_label")
        # Load profile picture
        profile_pixmap = QPixmap("dp2.png")  # Replace "profile_picture.png" with the actual file path
        profile_pixmap = profile_pixmap.scaled(48, 48, QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                               QtCore.Qt.TransformationMode.SmoothTransformation)
        self.profile_label.setPixmap(profile_pixmap)
        self.menubar.addMenu(self.menuSettings)
        MainWindow.setMenuBar(self.menubar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.send_btn.clicked.connect(self.handle_send_btn)
        self.sendImg_btn.clicked.connect(self.handle_imagebtn)
        self.changeColor_btn.clicked.connect(self.handle_color_change)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Chat Room"))
        self.send_btn.setText(_translate("MainWindow", "Send"))
        self.sendImg_btn.setText(_translate("MainWindow", "Upload"))
        name, ok = QtWidgets.QInputDialog.getText(MainWindow, "Enter Name", "Please enter your name:")
        if ok:
            self.username = name
            self.connection()
        else:
            sys.exit()

    def connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 4444))
        except:
            app = QApplication([])
            QtWidgets.QMessageBox.critical(None, "Error", "Connection Could Not Be Established!")
            sys.exit()

    def receive(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('ascii')
                if message == 'Name:':
                    self.client_socket.send(self.username.encode('ascii'))
                else:
                    QtCore.QMetaObject.invokeMethod(self.chat_textEdit, "append", QtCore.Qt.QueuedConnection,
                                                    QtCore.Q_ARG(str, message))
                    QtCore.QMetaObject.invokeMethod(self.chat_textEdit.verticalScrollBar(), "setValue",
                                                    QtCore.Qt.QueuedConnection,
                                                    QtCore.Q_ARG(int, self.chat_textEdit.verticalScrollBar().maximum()))
            except Exception as e:
                print(e)
                app = QApplication([])
                QtWidgets.QMessageBox.critical(None, "Error", "Connection Dropped!")
                self.client_socket.close()
                sys.exit()

    def handle_send_btn(self):
        message = {
            'username': self.username,
            'text': self.input_lineEdit.text(),
            'type': 'text'
        }
        self.input_lineEdit.setText("")
        self.client_socket.send(json.dumps(message).encode('ascii'))

    def closeEvent(self, event):
        self.client_socket.close()
        event.accept()
        sys.exit()

    def handle_imagebtn(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('Images (*.png *.xpm *.jpg *.bmp)')
        if file_dialog.exec_() == QFileDialog.Accepted:
            self.image_path = file_dialog.selectedFiles()[0]
            self.send_image()

    def send_image(self):
        try:
            with open(self.image_path, 'rb') as file:
                image_data = file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            message = {
                'username': self.username,
                'type': 'image',
                'data': image_base64
            }
            self.client_socket.send(json.dumps(message).encode('ascii'))
        except Exception as e:
            print(f"Error sending image: {e}")

    def handle_color_change(self):
        menu = QMenu(self.centralwidget)
        red_action = QAction("Red", self.centralwidget)
        black_action = QAction("Black", self.centralwidget)
        blue_action = QAction("Blue", self.centralwidget)
        white_action = QAction("White", self.centralwidget)

        red_action.triggered.connect(lambda: self.set_border_color("red"))
        black_action.triggered.connect(lambda: self.set_border_color("black"))
        blue_action.triggered.connect(lambda: self.set_border_color("blue"))
        white_action.triggered.connect(lambda: self.set_border_color("white"))

        menu.addAction(red_action)
        menu.addAction(black_action)
        menu.addAction(blue_action)
        menu.addAction(white_action)

        self.changeColor_btn.setMenu(menu)

    def set_border_color(self, color):
        self.centralwidget.setStyleSheet(f"border: 2px solid {color};")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    threading.Thread(target=ui.receive).start()
    app.aboutToQuit.connect(ui.closeEvent)

    sys.exit(app.exec_())
