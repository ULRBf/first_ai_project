# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './search_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(424, 554)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.second_page = QtWidgets.QWidget()
        self.second_page.setObjectName("second_page")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.second_page)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(self.second_page)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.le_car_plate_info = QtWidgets.QLineEdit(self.widget)
        self.le_car_plate_info.setText("")
        self.le_car_plate_info.setObjectName("le_car_plate_info")
        self.horizontalLayout.addWidget(self.le_car_plate_info)
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.second_page)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget_6 = QtWidgets.QWidget(self.widget_2)
        self.widget_6.setMinimumSize(QtCore.QSize(40, 0))
        self.widget_6.setMaximumSize(QtCore.QSize(40, 16777215))
        self.widget_6.setObjectName("widget_6")
        self.label_2 = QtWidgets.QLabel(self.widget_6)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 40, 72))
        self.label_2.setMinimumSize(QtCore.QSize(40, 0))
        self.label_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.widget_6)
        self.widget_5 = QtWidgets.QWidget(self.widget_2)
        self.widget_5.setObjectName("widget_5")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.le_first_time = QtWidgets.QLineEdit(self.widget_5)
        self.le_first_time.setObjectName("le_first_time")
        self.verticalLayout_3.addWidget(self.le_first_time)
        self.le_second_time = QtWidgets.QLineEdit(self.widget_5)
        self.le_second_time.setText("")
        self.le_second_time.setObjectName("le_second_time")
        self.verticalLayout_3.addWidget(self.le_second_time)
        self.horizontalLayout_2.addWidget(self.widget_5)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.widget_3 = QtWidgets.QWidget(self.second_page)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_search = QtWidgets.QPushButton(self.widget_3)
        self.btn_search.setObjectName("btn_search")
        self.horizontalLayout_3.addWidget(self.btn_search)
        self.verticalLayout_2.addWidget(self.widget_3)
        self.widget_7 = QtWidgets.QWidget(self.second_page)
        self.widget_7.setObjectName("widget_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_7)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget_8 = QtWidgets.QWidget(self.widget_7)
        self.widget_8.setMinimumSize(QtCore.QSize(60, 0))
        self.widget_8.setMaximumSize(QtCore.QSize(60, 16777215))
        self.widget_8.setObjectName("widget_8")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_8)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_4 = QtWidgets.QLabel(self.widget_8)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_6.addWidget(self.label_4)
        self.horizontalLayout_4.addWidget(self.widget_8)
        self.widget_9 = QtWidgets.QWidget(self.widget_7)
        self.widget_9.setObjectName("widget_9")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget_9)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.le_car_type = QtWidgets.QLineEdit(self.widget_9)
        self.le_car_type.setText("")
        self.le_car_type.setObjectName("le_car_type")
        self.verticalLayout_5.addWidget(self.le_car_type)
        self.horizontalLayout_4.addWidget(self.widget_9)
        self.verticalLayout_2.addWidget(self.widget_7)
        self.widget_4 = QtWidgets.QWidget(self.second_page)
        self.widget_4.setObjectName("widget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.widget_4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tableWidget = QtWidgets.QTableWidget(self.widget_4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.verticalLayout_4.addWidget(self.tableWidget)
        self.verticalLayout_2.addWidget(self.widget_4)
        self.stackedWidget.addWidget(self.second_page)
        self.fisrt_page = QtWidgets.QWidget()
        self.fisrt_page.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.fisrt_page.setObjectName("fisrt_page")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.fisrt_page)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.widget_10 = QtWidgets.QWidget(self.fisrt_page)
        self.widget_10.setObjectName("widget_10")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.widget_10)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.first_page_label = QtWidgets.QLabel(self.widget_10)
        self.first_page_label.setText("")
        self.first_page_label.setPixmap(QtGui.QPixmap(".\\search_img.png"))
        self.first_page_label.setAlignment(QtCore.Qt.AlignCenter)
        self.first_page_label.setObjectName("first_page_label")
        self.verticalLayout_7.addWidget(self.first_page_label)
        self.verticalLayout_8.addWidget(self.widget_10)
        self.stackedWidget.addWidget(self.fisrt_page)
        self.verticalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "차 번호"))
        self.le_car_plate_info.setPlaceholderText(_translate("MainWindow", "123가 5678"))
        self.label_2.setText(_translate("MainWindow", "시간"))
        self.le_first_time.setPlaceholderText(_translate("MainWindow", "20230101 23:30"))
        self.le_second_time.setPlaceholderText(_translate("MainWindow", "20230102 01:30"))
        self.btn_search.setText(_translate("MainWindow", "조회"))
        self.label_4.setText(_translate("MainWindow", "용도"))
        self.le_car_type.setPlaceholderText(_translate("MainWindow", "용도 출력"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "index"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "전송자ID"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "시각"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "위치"))