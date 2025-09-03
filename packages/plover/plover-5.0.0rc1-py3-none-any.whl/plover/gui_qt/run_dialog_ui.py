# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'run_dialog.ui'
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
    QGridLayout, QSizePolicy, QWidget)

class Ui_RunDialog(object):
    def setupUi(self, RunDialog):
        if not RunDialog.objectName():
            RunDialog.setObjectName(u"RunDialog")
        RunDialog.resize(400, 300)
        self.gridLayout = QGridLayout(RunDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.console = QWidget(RunDialog)
        self.console.setObjectName(u"console")

        self.gridLayout.addWidget(self.console, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(RunDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Close)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)


        self.retranslateUi(RunDialog)
        self.buttonBox.accepted.connect(RunDialog.accept)
        self.buttonBox.rejected.connect(RunDialog.reject)

        QMetaObject.connectSlotsByName(RunDialog)
    # setupUi

    def retranslateUi(self, RunDialog):
        RunDialog.setWindowTitle(QCoreApplication.translate("RunDialog", u"Dialog", None))
    # retranslateUi

