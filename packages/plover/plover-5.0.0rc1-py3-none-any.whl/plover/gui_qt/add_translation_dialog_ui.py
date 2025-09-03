# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'add_translation_dialog.ui'
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
    QSizePolicy, QVBoxLayout, QWidget)

from plover.gui_qt.add_translation_widget import AddTranslationWidget

class Ui_AddTranslationDialog(object):
    def setupUi(self, AddTranslationDialog):
        if not AddTranslationDialog.objectName():
            AddTranslationDialog.setObjectName(u"AddTranslationDialog")
        AddTranslationDialog.resize(299, 255)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddTranslationDialog.sizePolicy().hasHeightForWidth())
        AddTranslationDialog.setSizePolicy(sizePolicy)
        AddTranslationDialog.setWindowTitle(u"")
        AddTranslationDialog.setSizeGripEnabled(True)
        self.verticalLayout = QVBoxLayout(AddTranslationDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.add_translation = AddTranslationWidget(AddTranslationDialog)
        self.add_translation.setObjectName(u"add_translation")

        self.verticalLayout.addWidget(self.add_translation)

        self.buttonBox = QDialogButtonBox(AddTranslationDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AddTranslationDialog)
        self.buttonBox.accepted.connect(AddTranslationDialog.accept)
        self.buttonBox.rejected.connect(AddTranslationDialog.reject)

        QMetaObject.connectSlotsByName(AddTranslationDialog)
    # setupUi

    def retranslateUi(self, AddTranslationDialog):
        pass
    # retranslateUi

