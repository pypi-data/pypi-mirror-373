# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'config_window.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QGridLayout, QSizePolicy, QTabWidget, QWidget)
from . import resources_rc

class Ui_ConfigWindow(object):
    def setupUi(self, ConfigWindow):
        if not ConfigWindow.objectName():
            ConfigWindow.setObjectName(u"ConfigWindow")
        ConfigWindow.resize(471, 480)
        icon = QIcon()
        icon.addFile(u":/resources/plover.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ConfigWindow.setWindowIcon(icon)
        ConfigWindow.setSizeGripEnabled(True)
        self.gridLayout = QGridLayout(ConfigWindow)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabs = QTabWidget(ConfigWindow)
        self.tabs.setObjectName(u"tabs")

        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)

        self.buttons = QDialogButtonBox(ConfigWindow)
        self.buttons.setObjectName(u"buttons")
        self.buttons.setOrientation(Qt.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttons, 1, 0, 1, 1)


        self.retranslateUi(ConfigWindow)
        self.buttons.accepted.connect(ConfigWindow.accept)
        self.buttons.rejected.connect(ConfigWindow.reject)

        self.tabs.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(ConfigWindow)
    # setupUi

    def retranslateUi(self, ConfigWindow):
        ConfigWindow.setWindowTitle(QCoreApplication.translate("ConfigWindow", u"Plover: Configuration", None))
    # retranslateUi

