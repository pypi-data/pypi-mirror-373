# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'config_keyboard_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QSizePolicy,
    QWidget)

class Ui_KeyboardWidget(object):
    def setupUi(self, KeyboardWidget):
        if not KeyboardWidget.objectName():
            KeyboardWidget.setObjectName(u"KeyboardWidget")
        KeyboardWidget.resize(159, 66)
        KeyboardWidget.setWindowTitle(u"")
        self.gridLayout = QGridLayout(KeyboardWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.first_up_chord_send = QCheckBox(KeyboardWidget)
        self.first_up_chord_send.setObjectName(u"first_up_chord_send")

        self.gridLayout.addWidget(self.first_up_chord_send, 1, 0, 1, 1)

        self.arpeggiate = QCheckBox(KeyboardWidget)
        self.arpeggiate.setObjectName(u"arpeggiate")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.arpeggiate.sizePolicy().hasHeightForWidth())
        self.arpeggiate.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.arpeggiate, 0, 0, 1, 1)


        self.retranslateUi(KeyboardWidget)
        self.arpeggiate.clicked["bool"].connect(KeyboardWidget.update_arpeggiate)
        self.first_up_chord_send.clicked["bool"].connect(KeyboardWidget.update_first_up_chord_send)

        QMetaObject.connectSlotsByName(KeyboardWidget)
    # setupUi

    def retranslateUi(self, KeyboardWidget):
#if QT_CONFIG(tooltip)
        self.first_up_chord_send.setToolTip(QCoreApplication.translate("KeyboardWidget", u"When the first key in a chord is released, the chord is sent.\n"
"If the key is pressed and released again, another chord is sent.", None))
#endif // QT_CONFIG(tooltip)
        self.first_up_chord_send.setText(QCoreApplication.translate("KeyboardWidget", u"First-up chord send", None))
        self.arpeggiate.setText(QCoreApplication.translate("KeyboardWidget", u"Arpeggiate", None))
        pass
    # retranslateUi

