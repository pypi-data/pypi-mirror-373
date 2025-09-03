# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'suggestions_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QSizePolicy, QVBoxLayout,
    QWidget)

from plover.gui_qt.suggestions_widget import SuggestionsWidget
from . import resources_rc

class Ui_SuggestionsDialog(object):
    def setupUi(self, SuggestionsDialog):
        if not SuggestionsDialog.objectName():
            SuggestionsDialog.setObjectName(u"SuggestionsDialog")
        SuggestionsDialog.resize(247, 430)
        font = QFont()
        font.setFamilies([u"Monospace"])
        SuggestionsDialog.setFont(font)
        SuggestionsDialog.setWindowTitle(u"")
        SuggestionsDialog.setSizeGripEnabled(True)
        self.action_Clear = QAction(SuggestionsDialog)
        self.action_Clear.setObjectName(u"action_Clear")
        icon = QIcon()
        icon.addFile(u":/resources/trash.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Clear.setIcon(icon)
        self.action_ToggleOnTop = QAction(SuggestionsDialog)
        self.action_ToggleOnTop.setObjectName(u"action_ToggleOnTop")
        self.action_ToggleOnTop.setCheckable(True)
        icon1 = QIcon()
        icon1.addFile(u":/resources/pin.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_ToggleOnTop.setIcon(icon1)
        self.action_SelectFont = QAction(SuggestionsDialog)
        self.action_SelectFont.setObjectName(u"action_SelectFont")
        icon2 = QIcon()
        icon2.addFile(u":/resources/font_selector.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_SelectFont.setIcon(icon2)
        self.verticalLayout = QVBoxLayout(SuggestionsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.suggestions = SuggestionsWidget(SuggestionsDialog)
        self.suggestions.setObjectName(u"suggestions")

        self.verticalLayout.addWidget(self.suggestions)


        self.retranslateUi(SuggestionsDialog)
        self.action_Clear.triggered.connect(SuggestionsDialog.clear)
        self.action_ToggleOnTop.triggered["bool"].connect(SuggestionsDialog.toggle_ontop)
        self.action_SelectFont.triggered.connect(SuggestionsDialog.select_font)

        QMetaObject.connectSlotsByName(SuggestionsDialog)
    # setupUi

    def retranslateUi(self, SuggestionsDialog):
        self.action_Clear.setText(QCoreApplication.translate("SuggestionsDialog", u"&Clear", None))
#if QT_CONFIG(tooltip)
        self.action_Clear.setToolTip(QCoreApplication.translate("SuggestionsDialog", u"Clear the history.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_Clear.setShortcut(QCoreApplication.translate("SuggestionsDialog", u"Ctrl+L", None))
#endif // QT_CONFIG(shortcut)
        self.action_ToggleOnTop.setText(QCoreApplication.translate("SuggestionsDialog", u"&Toggle \"always on top\"", None))
#if QT_CONFIG(tooltip)
        self.action_ToggleOnTop.setToolTip(QCoreApplication.translate("SuggestionsDialog", u"Toggle \"always on top\".", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_ToggleOnTop.setShortcut(QCoreApplication.translate("SuggestionsDialog", u"Ctrl+T", None))
#endif // QT_CONFIG(shortcut)
        self.action_SelectFont.setText(QCoreApplication.translate("SuggestionsDialog", u"Select &font", None))
#if QT_CONFIG(tooltip)
        self.action_SelectFont.setToolTip(QCoreApplication.translate("SuggestionsDialog", u"Open font selection dialog.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(accessibility)
        self.suggestions.setAccessibleName(QCoreApplication.translate("SuggestionsDialog", u"Suggestions", None))
#endif // QT_CONFIG(accessibility)
        pass
    # retranslateUi

