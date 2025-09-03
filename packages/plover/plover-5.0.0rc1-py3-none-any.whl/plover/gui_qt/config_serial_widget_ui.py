# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'config_serial_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SerialWidget(object):
    def setupUi(self, SerialWidget):
        if not SerialWidget.objectName():
            SerialWidget.setObjectName(u"SerialWidget")
        SerialWidget.resize(314, 431)
        SerialWidget.setWindowTitle(u"")
        self.verticalLayout_3 = QVBoxLayout(SerialWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(SerialWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.port = QComboBox(self.groupBox)
        self.port.setObjectName(u"port")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.port.sizePolicy().hasHeightForWidth())
        self.port.setSizePolicy(sizePolicy2)
        self.port.setEditable(True)
        self.port.setInsertPolicy(QComboBox.InsertAtBottom)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.port)

        self.scan_button = QPushButton(self.groupBox)
        self.scan_button.setObjectName(u"scan_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.scan_button.sizePolicy().hasHeightForWidth())
        self.scan_button.setSizePolicy(sizePolicy3)
        self.scan_button.setMaximumSize(QSize(16777215, 16777215))

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.scan_button)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.baudrate = QComboBox(self.groupBox)
        self.baudrate.setObjectName(u"baudrate")
        sizePolicy2.setHeightForWidth(self.baudrate.sizePolicy().hasHeightForWidth())
        self.baudrate.setSizePolicy(sizePolicy2)

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.baudrate)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(SerialWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.bytesize = QComboBox(self.groupBox_2)
        self.bytesize.setObjectName(u"bytesize")
        sizePolicy2.setHeightForWidth(self.bytesize.sizePolicy().hasHeightForWidth())
        self.bytesize.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.bytesize)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.stopbits = QComboBox(self.groupBox_2)
        self.stopbits.setObjectName(u"stopbits")
        sizePolicy2.setHeightForWidth(self.stopbits.sizePolicy().hasHeightForWidth())
        self.stopbits.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.stopbits)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.parity = QComboBox(self.groupBox_2)
        self.parity.setObjectName(u"parity")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.parity)


        self.verticalLayout_3.addWidget(self.groupBox_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.groupBox_3 = QGroupBox(SerialWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy2.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy2)
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_6 = QLabel(self.groupBox_3)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.label_6, 0, 0, 1, 1)

        self.timeout = QDoubleSpinBox(self.groupBox_3)
        self.timeout.setObjectName(u"timeout")
        self.timeout.setEnabled(True)
        sizePolicy2.setHeightForWidth(self.timeout.sizePolicy().hasHeightForWidth())
        self.timeout.setSizePolicy(sizePolicy2)
        self.timeout.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.timeout, 0, 1, 1, 1)

        self.use_timeout = QCheckBox(self.groupBox_3)
        self.use_timeout.setObjectName(u"use_timeout")
        sizePolicy3.setHeightForWidth(self.use_timeout.sizePolicy().hasHeightForWidth())
        self.use_timeout.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.use_timeout, 1, 0, 1, 2)


        self.horizontalLayout_2.addWidget(self.groupBox_3)

        self.groupBox_4 = QGroupBox(SerialWidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.verticalLayout = QVBoxLayout(self.groupBox_4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.xonxoff = QCheckBox(self.groupBox_4)
        self.xonxoff.setObjectName(u"xonxoff")
        sizePolicy3.setHeightForWidth(self.xonxoff.sizePolicy().hasHeightForWidth())
        self.xonxoff.setSizePolicy(sizePolicy3)

        self.verticalLayout.addWidget(self.xonxoff)

        self.rtscts = QCheckBox(self.groupBox_4)
        self.rtscts.setObjectName(u"rtscts")
        sizePolicy3.setHeightForWidth(self.rtscts.sizePolicy().hasHeightForWidth())
        self.rtscts.setSizePolicy(sizePolicy3)

        self.verticalLayout.addWidget(self.rtscts)


        self.horizontalLayout_2.addWidget(self.groupBox_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.port)
        self.label_2.setBuddy(self.baudrate)
        self.label_3.setBuddy(self.bytesize)
        self.label_4.setBuddy(self.stopbits)
        self.label_5.setBuddy(self.parity)
        self.label_6.setBuddy(self.timeout)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(SerialWidget)
        self.scan_button.clicked.connect(SerialWidget.scan)
        self.baudrate.textActivated.connect(SerialWidget.update_baudrate)
        self.bytesize.textActivated.connect(SerialWidget.update_bytesize)
        self.parity.textActivated.connect(SerialWidget.update_parity)
        self.port.editTextChanged.connect(SerialWidget.update_port)
        self.stopbits.textActivated.connect(SerialWidget.update_stopbits)
        self.use_timeout.clicked["bool"].connect(SerialWidget.update_use_timeout)
        self.xonxoff.clicked["bool"].connect(SerialWidget.update_xonxoff)
        self.rtscts.clicked["bool"].connect(SerialWidget.update_rtscts)
        self.timeout.valueChanged.connect(SerialWidget.update_timeout)

        QMetaObject.connectSlotsByName(SerialWidget)
    # setupUi

    def retranslateUi(self, SerialWidget):
#if QT_CONFIG(accessibility)
        SerialWidget.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Serial", None))
#endif // QT_CONFIG(accessibility)
        self.groupBox.setTitle(QCoreApplication.translate("SerialWidget", u"Connection", None))
        self.label.setText(QCoreApplication.translate("SerialWidget", u"Port", None))
#if QT_CONFIG(accessibility)
        self.port.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Port", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.port.setAccessibleDescription(QCoreApplication.translate("SerialWidget", u"Serial port device name.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.scan_button.setAccessibleDescription(QCoreApplication.translate("SerialWidget", u"Reload all available serial ports.", None))
#endif // QT_CONFIG(accessibility)
        self.scan_button.setText(QCoreApplication.translate("SerialWidget", u"Refresh", None))
        self.label_2.setText(QCoreApplication.translate("SerialWidget", u"Baudrate", None))
#if QT_CONFIG(accessibility)
        self.baudrate.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Baudrate", None))
#endif // QT_CONFIG(accessibility)
        self.groupBox_2.setTitle(QCoreApplication.translate("SerialWidget", u"Data format", None))
        self.label_3.setText(QCoreApplication.translate("SerialWidget", u"Data bits", None))
#if QT_CONFIG(accessibility)
        self.bytesize.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Data bits", None))
#endif // QT_CONFIG(accessibility)
        self.label_4.setText(QCoreApplication.translate("SerialWidget", u"Stop bits", None))
#if QT_CONFIG(accessibility)
        self.stopbits.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Stop bits", None))
#endif // QT_CONFIG(accessibility)
        self.label_5.setText(QCoreApplication.translate("SerialWidget", u"Parity", None))
#if QT_CONFIG(accessibility)
        self.parity.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Parity", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.groupBox_3.setAccessibleName("")
#endif // QT_CONFIG(accessibility)
        self.groupBox_3.setTitle(QCoreApplication.translate("SerialWidget", u"Timeout", None))
        self.label_6.setText(QCoreApplication.translate("SerialWidget", u"Duration", None))
#if QT_CONFIG(accessibility)
        self.timeout.setAccessibleName(QCoreApplication.translate("SerialWidget", u"Duration", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.timeout.setAccessibleDescription(QCoreApplication.translate("SerialWidget", u"Timeout duration in seconds.", None))
#endif // QT_CONFIG(accessibility)
        self.use_timeout.setText(QCoreApplication.translate("SerialWidget", u"Use timeout", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("SerialWidget", u"Flow control", None))
        self.xonxoff.setText(QCoreApplication.translate("SerialWidget", u"Xon/Xoff", None))
        self.rtscts.setText(QCoreApplication.translate("SerialWidget", u"RTS/CTS", None))
    # retranslateUi

