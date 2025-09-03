# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'lookup_dialog.ui'
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
    QGridLayout, QLineEdit, QSizePolicy, QWidget)

from plover.gui_qt.suggestions_widget import SuggestionsWidget

class Ui_LookupDialog(object):
    def setupUi(self, LookupDialog):
        if not LookupDialog.objectName():
            LookupDialog.setObjectName(u"LookupDialog")
        LookupDialog.resize(274, 272)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LookupDialog.sizePolicy().hasHeightForWidth())
        LookupDialog.setSizePolicy(sizePolicy)
        LookupDialog.setSizeGripEnabled(True)
        self.gridLayout = QGridLayout(LookupDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(LookupDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)

        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.pattern = QLineEdit(LookupDialog)
        self.pattern.setObjectName(u"pattern")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.pattern.sizePolicy().hasHeightForWidth())
        self.pattern.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.pattern, 0, 0, 1, 1)

        self.suggestions = SuggestionsWidget(LookupDialog)
        self.suggestions.setObjectName(u"suggestions")
        sizePolicy.setHeightForWidth(self.suggestions.sizePolicy().hasHeightForWidth())
        self.suggestions.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.suggestions, 1, 0, 1, 1)


        self.retranslateUi(LookupDialog)
        self.buttonBox.accepted.connect(LookupDialog.accept)
        self.buttonBox.rejected.connect(LookupDialog.reject)
        self.pattern.textEdited.connect(LookupDialog.lookup)

        QMetaObject.connectSlotsByName(LookupDialog)
    # setupUi

    def retranslateUi(self, LookupDialog):
        LookupDialog.setWindowTitle(QCoreApplication.translate("LookupDialog", u"Plover: Dictionary Lookup", None))
#if QT_CONFIG(accessibility)
        self.pattern.setAccessibleName(QCoreApplication.translate("LookupDialog", u"Pattern", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pattern.setAccessibleDescription(QCoreApplication.translate("LookupDialog", u"Translation pattern to lookup.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.suggestions.setAccessibleName(QCoreApplication.translate("LookupDialog", u"Results", None))
#endif // QT_CONFIG(accessibility)
    # retranslateUi

