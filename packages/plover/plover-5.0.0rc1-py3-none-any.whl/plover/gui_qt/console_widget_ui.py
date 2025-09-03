# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'console_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QTextEdit,
    QWidget)

class Ui_ConsoleWidget(object):
    def setupUi(self, ConsoleWidget):
        if not ConsoleWidget.objectName():
            ConsoleWidget.setObjectName(u"ConsoleWidget")
        ConsoleWidget.resize(321, 240)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConsoleWidget.sizePolicy().hasHeightForWidth())
        ConsoleWidget.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(ConsoleWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.output = QTextEdit(ConsoleWidget)
        self.output.setObjectName(u"output")
        self.output.setLineWrapMode(QTextEdit.NoWrap)
        self.output.setReadOnly(True)

        self.gridLayout.addWidget(self.output, 1, 0, 1, 1)


        self.retranslateUi(ConsoleWidget)

        QMetaObject.connectSlotsByName(ConsoleWidget)
    # setupUi

    def retranslateUi(self, ConsoleWidget):
        ConsoleWidget.setWindowTitle(QCoreApplication.translate("ConsoleWidget", u"Form", None))
    # retranslateUi

