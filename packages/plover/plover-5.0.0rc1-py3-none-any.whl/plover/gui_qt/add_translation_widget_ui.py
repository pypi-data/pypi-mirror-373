# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'add_translation_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QLabel, QLineEdit, QSizePolicy, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_AddTranslationWidget(object):
    def setupUi(self, AddTranslationWidget):
        if not AddTranslationWidget.objectName():
            AddTranslationWidget.setObjectName(u"AddTranslationWidget")
        AddTranslationWidget.resize(299, 255)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddTranslationWidget.sizePolicy().hasHeightForWidth())
        AddTranslationWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(AddTranslationWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_3 = QLabel(AddTranslationWidget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label = QLabel(AddTranslationWidget)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.strokes = QLineEdit(AddTranslationWidget)
        self.strokes.setObjectName(u"strokes")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.strokes.sizePolicy().hasHeightForWidth())
        self.strokes.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.strokes)

        self.label_2 = QLabel(AddTranslationWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.translation = QLineEdit(AddTranslationWidget)
        self.translation.setObjectName(u"translation")
        sizePolicy2.setHeightForWidth(self.translation.sizePolicy().hasHeightForWidth())
        self.translation.setSizePolicy(sizePolicy2)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.translation)

        self.dictionary = QComboBox(AddTranslationWidget)
        self.dictionary.setObjectName(u"dictionary")
        self.dictionary.setEditable(False)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.dictionary)


        self.verticalLayout.addLayout(self.formLayout)

        self.strokes_info = QTextEdit(AddTranslationWidget)
        self.strokes_info.setObjectName(u"strokes_info")
        sizePolicy.setHeightForWidth(self.strokes_info.sizePolicy().hasHeightForWidth())
        self.strokes_info.setSizePolicy(sizePolicy)
        self.strokes_info.setFrameShape(QFrame.Box)
        self.strokes_info.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.strokes_info)

        self.translation_info = QTextEdit(AddTranslationWidget)
        self.translation_info.setObjectName(u"translation_info")
        sizePolicy.setHeightForWidth(self.translation_info.sizePolicy().hasHeightForWidth())
        self.translation_info.setSizePolicy(sizePolicy)
        self.translation_info.setFrameShape(QFrame.Box)
        self.translation_info.setTextInteractionFlags(Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.translation_info)

#if QT_CONFIG(shortcut)
        self.label_3.setBuddy(self.dictionary)
        self.label.setBuddy(self.strokes)
        self.label_2.setBuddy(self.translation)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.strokes, self.translation)
        QWidget.setTabOrder(self.translation, self.strokes_info)
        QWidget.setTabOrder(self.strokes_info, self.translation_info)
        QWidget.setTabOrder(self.translation_info, self.dictionary)

        self.retranslateUi(AddTranslationWidget)
        self.strokes.textEdited.connect(AddTranslationWidget.handle_stroke_input_change)
        self.translation.textEdited.connect(AddTranslationWidget.handle_translation_input_change)
        self.dictionary.activated.connect(AddTranslationWidget.update_selected_dictionary)

        QMetaObject.connectSlotsByName(AddTranslationWidget)
    # setupUi

    def retranslateUi(self, AddTranslationWidget):
        self.label_3.setText(QCoreApplication.translate("AddTranslationWidget", u"Dictionary:", None))
        self.label.setText(QCoreApplication.translate("AddTranslationWidget", u"Strokes:", None))
#if QT_CONFIG(accessibility)
        self.strokes.setAccessibleName(QCoreApplication.translate("AddTranslationWidget", u"Strokes", None))
#endif // QT_CONFIG(accessibility)
        self.label_2.setText(QCoreApplication.translate("AddTranslationWidget", u"Translation:", None))
#if QT_CONFIG(accessibility)
        self.translation.setAccessibleName(QCoreApplication.translate("AddTranslationWidget", u"Translation", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.dictionary.setAccessibleName(QCoreApplication.translate("AddTranslationWidget", u"Dictionary", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.dictionary.setAccessibleDescription(QCoreApplication.translate("AddTranslationWidget", u"Select the target dictionary for the new translation.", None))
#endif // QT_CONFIG(accessibility)
#if QT_CONFIG(accessibility)
        self.strokes_info.setAccessibleName(QCoreApplication.translate("AddTranslationWidget", u"Existing mappings (strokes)", None))
#endif // QT_CONFIG(accessibility)
        self.strokes_info.setProperty(u"text", "")
#if QT_CONFIG(accessibility)
        self.translation_info.setAccessibleName(QCoreApplication.translate("AddTranslationWidget", u"Existing mappings (translations)", None))
#endif // QT_CONFIG(accessibility)
        self.translation_info.setProperty(u"text", "")
        pass
    # retranslateUi

