# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'config_file_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_FileWidget(object):
    def setupUi(self, FileWidget):
        if not FileWidget.objectName():
            FileWidget.setObjectName(u"FileWidget")
        FileWidget.resize(166, 78)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FileWidget.sizePolicy().hasHeightForWidth())
        FileWidget.setSizePolicy(sizePolicy)
        FileWidget.setWindowTitle(u"")
        self.verticalLayout = QVBoxLayout(FileWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.path = QLineEdit(FileWidget)
        self.path.setObjectName(u"path")

        self.verticalLayout.addWidget(self.path)

        self.pushButton = QPushButton(FileWidget)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.pushButton)


        self.retranslateUi(FileWidget)
        self.pushButton.clicked.connect(FileWidget.open_file_dialog)
        self.path.editingFinished.connect(FileWidget.handle_edited_path)

        QMetaObject.connectSlotsByName(FileWidget)
    # setupUi

    def retranslateUi(self, FileWidget):
#if QT_CONFIG(accessibility)
        self.path.setAccessibleName(QCoreApplication.translate("FileWidget", u"Log file path.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.path.setAccessibleDescription(QCoreApplication.translate("FileWidget", u"Path to the log file.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pushButton.setAccessibleName(QCoreApplication.translate("FileWidget", u"Browse.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pushButton.setAccessibleDescription(QCoreApplication.translate("FileWidget", u"Open a file picker to select the log file.", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton.setText(QCoreApplication.translate("FileWidget", u"Browse", None))
        pass
    # retranslateUi

