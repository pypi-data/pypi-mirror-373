# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'dictionary_editor.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QFrame,
    QGridLayout, QGroupBox, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableView,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_DictionaryEditor(object):
    def setupUi(self, DictionaryEditor):
        if not DictionaryEditor.objectName():
            DictionaryEditor.setObjectName(u"DictionaryEditor")
        DictionaryEditor.setWindowModality(Qt.WindowModal)
        DictionaryEditor.resize(658, 560)
        DictionaryEditor.setSizeGripEnabled(True)
        self.action_Delete = QAction(DictionaryEditor)
        self.action_Delete.setObjectName(u"action_Delete")
        icon = QIcon()
        icon.addFile(u":/resources/remove.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Delete.setIcon(icon)
        self.action_Undo = QAction(DictionaryEditor)
        self.action_Undo.setObjectName(u"action_Undo")
        icon1 = QIcon()
        icon1.addFile(u":/resources/undo.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_Undo.setIcon(icon1)
        self.action_New = QAction(DictionaryEditor)
        self.action_New.setObjectName(u"action_New")
        icon2 = QIcon()
        icon2.addFile(u":/resources/add.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_New.setIcon(icon2)
        self.verticalLayout = QVBoxLayout(DictionaryEditor)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(DictionaryEditor)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.strokes_filter = QLineEdit(self.groupBox)
        self.strokes_filter.setObjectName(u"strokes_filter")

        self.gridLayout.addWidget(self.strokes_filter, 0, 1, 1, 1)

        self.pushButton = QPushButton(self.groupBox)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.pushButton, 0, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.translation_filter = QLineEdit(self.groupBox)
        self.translation_filter.setObjectName(u"translation_filter")

        self.gridLayout.addWidget(self.translation_filter, 1, 1, 1, 1)

        self.pushButton_2 = QPushButton(self.groupBox)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.table = QTableView(DictionaryEditor)
        self.table.setObjectName(u"table")
        self.table.setFrameShape(QFrame.Box)
        self.table.setTabKeyNavigation(False)
        self.table.setProperty(u"showDropIndicator", True)
        self.table.setDragEnabled(True)
        self.table.setDragDropOverwriteMode(False)
        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setDefaultDropAction(Qt.IgnoreAction)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setTextElideMode(Qt.ElideMiddle)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setCascadingSectionResizes(True)

        self.verticalLayout.addWidget(self.table)

#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.strokes_filter)
        self.label_2.setBuddy(self.translation_filter)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.table, self.strokes_filter)
        QWidget.setTabOrder(self.strokes_filter, self.translation_filter)
        QWidget.setTabOrder(self.translation_filter, self.pushButton)
        QWidget.setTabOrder(self.pushButton, self.pushButton_2)

        self.retranslateUi(DictionaryEditor)
        self.action_Delete.triggered.connect(DictionaryEditor.delete_selected_row)
        self.action_Undo.triggered.connect(DictionaryEditor.undo)
        self.action_New.triggered.connect(DictionaryEditor.add_new_row)
        DictionaryEditor.finished.connect(DictionaryEditor.save_modified_dictionaries)
        self.pushButton.clicked.connect(DictionaryEditor.apply_filter)
        self.strokes_filter.returnPressed.connect(DictionaryEditor.apply_filter)
        self.translation_filter.returnPressed.connect(DictionaryEditor.apply_filter)
        self.pushButton_2.clicked.connect(DictionaryEditor.clear_filter)

        QMetaObject.connectSlotsByName(DictionaryEditor)
    # setupUi

    def retranslateUi(self, DictionaryEditor):
        DictionaryEditor.setWindowTitle(QCoreApplication.translate("DictionaryEditor", u"Plover: Dictionary Editor", None))
        self.action_Delete.setText(QCoreApplication.translate("DictionaryEditor", u"&Delete", None))
#if QT_CONFIG(tooltip)
        self.action_Delete.setToolTip(QCoreApplication.translate("DictionaryEditor", u"Delete selected entries.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_Delete.setShortcut(QCoreApplication.translate("DictionaryEditor", u"Del", None))
#endif // QT_CONFIG(shortcut)
        self.action_Undo.setText(QCoreApplication.translate("DictionaryEditor", u"&Undo", None))
#if QT_CONFIG(tooltip)
        self.action_Undo.setToolTip(QCoreApplication.translate("DictionaryEditor", u"Undo last add/delete/edit operation.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_Undo.setShortcut(QCoreApplication.translate("DictionaryEditor", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.action_New.setText(QCoreApplication.translate("DictionaryEditor", u"&New translation", None))
#if QT_CONFIG(tooltip)
        self.action_New.setToolTip(QCoreApplication.translate("DictionaryEditor", u"Add a new translation", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_New.setShortcut(QCoreApplication.translate("DictionaryEditor", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(accessibility)
        self.groupBox.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Filter", None))
#endif // QT_CONFIG(accessibility)
        self.groupBox.setTitle(QCoreApplication.translate("DictionaryEditor", u"Filter", None))
        self.label.setText(QCoreApplication.translate("DictionaryEditor", u"By strokes:", None))
#if QT_CONFIG(accessibility)
        self.strokes_filter.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Strokes filter", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pushButton.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Apply filter", None))
#endif // QT_CONFIG(accessibility)
        self.pushButton.setText(QCoreApplication.translate("DictionaryEditor", u"Apply", None))
        self.label_2.setText(QCoreApplication.translate("DictionaryEditor", u"By translation:", None))
#if QT_CONFIG(accessibility)
        self.translation_filter.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Translation filter", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pushButton_2.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Clear filter", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.pushButton_2.setAccessibleDescription("")
#endif // QT_CONFIG(accessibility)
        self.pushButton_2.setText(QCoreApplication.translate("DictionaryEditor", u"Clear", None))
#if QT_CONFIG(accessibility)
        self.table.setAccessibleName(QCoreApplication.translate("DictionaryEditor", u"Mappings", None))
#endif // QT_CONFIG(accessibility)
    # retranslateUi

