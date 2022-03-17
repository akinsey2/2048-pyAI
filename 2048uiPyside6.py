# -*- coding: utf-8 -*-

################################################################################
# Form generated from reading UI file '2048uipgeBYF.ui'
#
# Created by: Qt User Interface Compiler version 6.1.0
#
# WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")

        MainWindow.resize(499, 774)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.game_title = QLabel(self.centralwidget)
        self.game_title.setObjectName(u"game_title")
        self.game_title.setGeometry(QRect(180, 10, 121, 61))
        font = QFont()
        font.setPointSize(36)
        font.setBold(True)
        self.game_title.setFont(font)
        self.game_title.setMidLineWidth(0)
        self.game_title.setAlignment(Qt.AlignCenter)

        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setGeometry(QRect(25, 130, 450, 450))

        self.start_but = QPushButton(self.centralwidget)
        self.start_but.setObjectName(u"start_but")
        self.start_but.setGeometry(QRect(20, 610, 100, 100))
        font1 = QFont()
        font1.setPointSize(12)
        self.start_but.setFont(font1)

        self.save_button = QPushButton(self.centralwidget)
        self.save_button.setObjectName(u"save_button")
        self.save_button.setEnabled(False)
        self.save_button.setGeometry(QRect(140, 620, 100, 30))
        self.save_button.setFont(font1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(240, 600, 20, 131))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.load_but = QPushButton(self.centralwidget)
        self.load_but.setObjectName(u"load_but")
        self.load_but.setGeometry(QRect(140, 670, 100, 30))
        self.load_but.setFont(font1)

        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(50, 70, 99, 54))

        self.verticalLayout = QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.curr_score_label = QLabel(self.layoutWidget)
        self.curr_score_label.setObjectName(u"curr_score_label")
        self.curr_score_label.setFont(font1)

        self.verticalLayout.addWidget(self.curr_score_label)

        self.curr_score = QLabel(self.layoutWidget)
        self.curr_score.setObjectName(u"curr_score")
        font2 = QFont()
        font2.setPointSize(16)
        self.curr_score.setFont(font2)
        self.curr_score.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.curr_score)

        self.layoutWidget1 = QWidget(self.centralwidget)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(320, 70, 133, 54))

        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)

        self.record_score_label = QLabel(self.layoutWidget1)
        self.record_score_label.setObjectName(u"record_score_label")
        self.record_score_label.setFont(font1)

        self.verticalLayout_2.addWidget(self.record_score_label)

        self.record_score = QLabel(self.layoutWidget1)
        self.record_score.setObjectName(u"record_score")
        self.record_score.setFont(font2)
        self.record_score.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.record_score)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(260, 600, 211, 131))
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.ap_spd_label = QLabel(self.widget)
        self.ap_spd_label.setObjectName(u"ap_spd_label")
        self.ap_spd_label.setEnabled(False)
        font3 = QFont()
        font3.setPointSize(10)
        self.ap_spd_label.setFont(font3)
        self.ap_spd_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.ap_spd_label)

        self.horizontalSlider = QSlider(self.widget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setEnabled(False)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(40)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setValue(10)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(5)

        self.verticalLayout_3.addWidget(self.horizontalSlider)

        self.comboBox = QComboBox(self.widget)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setEnabled(False)

        self.verticalLayout_3.addWidget(self.comboBox)

        self.ap_start_button = QPushButton(self.widget)
        self.ap_start_button.setObjectName(u"ap_start_button")
        self.ap_start_button.setEnabled(False)
        font4 = QFont()
        font4.setFamilies([u"Tahoma"])
        font4.setPointSize(12)
        self.ap_start_button.setFont(font4)

        self.verticalLayout_3.addWidget(self.ap_start_button)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 499, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.game_title.setText(QCoreApplication.translate("MainWindow", u"2048", None))
        self.start_but.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.save_button.setText(QCoreApplication.translate("MainWindow", u"Save Game", None))
        self.load_but.setText(QCoreApplication.translate("MainWindow", u"Load Game", None))
        self.curr_score_label.setText(QCoreApplication.translate("MainWindow", u"Current Score", None))
        self.curr_score.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.record_score_label.setText(QCoreApplication.translate("MainWindow", u"Record High Score", None))
        self.record_score.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.ap_spd_label.setText(QCoreApplication.translate("MainWindow", u"Auto-Play Speed", None))
        self.ap_start_button.setText(QCoreApplication.translate("MainWindow", u"Start Auto-Play", None))
    # retranslateUi

