# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'paper_tape.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QDialog,
    QFormLayout, QFrame, QLabel, QListView,
    QSizePolicy, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_PaperTape(object):
    def setupUi(self, PaperTape):
        if not PaperTape.objectName():
            PaperTape.setObjectName(u"PaperTape")
        PaperTape.resize(247, 430)
        PaperTape.setWindowTitle(u"")
        PaperTape.setSizeGripEnabled(True)
        self.action_Clear = QAction(PaperTape)
        self.action_Clear.setObjectName(u"action_Clear")
        icon = QIcon()
        icon.addFile(u":/resources/trash.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Clear.setIcon(icon)
        self.action_Save = QAction(PaperTape)
        self.action_Save.setObjectName(u"action_Save")
        icon1 = QIcon()
        icon1.addFile(u":/resources/save.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Save.setIcon(icon1)
        self.action_ToggleOnTop = QAction(PaperTape)
        self.action_ToggleOnTop.setObjectName(u"action_ToggleOnTop")
        self.action_ToggleOnTop.setCheckable(True)
        icon2 = QIcon()
        icon2.addFile(u":/resources/pin.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_ToggleOnTop.setIcon(icon2)
        self.action_SelectFont = QAction(PaperTape)
        self.action_SelectFont.setObjectName(u"action_SelectFont")
        icon3 = QIcon()
        icon3.addFile(u":/resources/font_selector.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_SelectFont.setIcon(icon3)
        self.verticalLayout = QVBoxLayout(PaperTape)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(PaperTape)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.styles = QComboBox(PaperTape)
        self.styles.setObjectName(u"styles")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.styles.sizePolicy().hasHeightForWidth())
        self.styles.setSizePolicy(sizePolicy)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.styles)


        self.verticalLayout.addLayout(self.formLayout)

        self.header = QLabel(PaperTape)
        self.header.setObjectName(u"header")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy1)
        self.header.setText(u"#STKPWHRAO*EUFRPBLGTSDZ")

        self.verticalLayout.addWidget(self.header)

        self.tape = QListView(PaperTape)
        self.tape.setObjectName(u"tape")
        self.tape.setFrameShape(QFrame.Panel)
        self.tape.setTabKeyNavigation(False)
        self.tape.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tape.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tape.setUniformItemSizes(True)

        self.verticalLayout.addWidget(self.tape)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.styles)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(PaperTape)
        self.styles.textActivated.connect(PaperTape.change_style)
        self.action_Clear.triggered.connect(PaperTape.clear)
        self.action_Save.triggered.connect(PaperTape.save)
        self.action_ToggleOnTop.triggered["bool"].connect(PaperTape.toggle_ontop)
        self.action_SelectFont.triggered.connect(PaperTape.select_font)

        QMetaObject.connectSlotsByName(PaperTape)
    # setupUi

    def retranslateUi(self, PaperTape):
        self.action_Clear.setText(QCoreApplication.translate("PaperTape", u"&Clear", None))
#if QT_CONFIG(tooltip)
        self.action_Clear.setToolTip(QCoreApplication.translate("PaperTape", u"Clear paper tape.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_Clear.setShortcut(QCoreApplication.translate("PaperTape", u"Ctrl+L", None))
#endif // QT_CONFIG(shortcut)
        self.action_Save.setText(QCoreApplication.translate("PaperTape", u"&Save", None))
#if QT_CONFIG(tooltip)
        self.action_Save.setToolTip(QCoreApplication.translate("PaperTape", u"Save paper tape to file.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_Save.setShortcut(QCoreApplication.translate("PaperTape", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.action_ToggleOnTop.setText(QCoreApplication.translate("PaperTape", u"&Toggle \"always on top\"", None))
#if QT_CONFIG(tooltip)
        self.action_ToggleOnTop.setToolTip(QCoreApplication.translate("PaperTape", u"Toggle \"always on top\".", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_ToggleOnTop.setShortcut(QCoreApplication.translate("PaperTape", u"Ctrl+T", None))
#endif // QT_CONFIG(shortcut)
        self.action_SelectFont.setText(QCoreApplication.translate("PaperTape", u"Select &font", None))
#if QT_CONFIG(tooltip)
        self.action_SelectFont.setToolTip(QCoreApplication.translate("PaperTape", u"Open font selection dialog.", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("PaperTape", u"Mode:", None))
#if QT_CONFIG(accessibility)
        self.styles.setAccessibleName(QCoreApplication.translate("PaperTape", u"Mode", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.styles.setAccessibleDescription(QCoreApplication.translate("PaperTape", u"Select paper tape display mode.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.tape.setAccessibleName(QCoreApplication.translate("PaperTape", u"Tape", None))
#endif // QT_CONFIG(accessibility)
        pass
    # retranslateUi

