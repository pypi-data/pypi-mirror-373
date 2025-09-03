# -*- coding: utf-8 -*-
_ = __import__(__package__.split(".", 1)[0])._

################################################################################
## Form generated from reading UI file 'plugins_manager.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QFrame,
    QHBoxLayout, QHeaderView, QProgressBar, QPushButton,
    QSizePolicy, QSplitter, QTableWidget, QTableWidgetItem,
    QToolButton, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_PluginsManager(object):
    def setupUi(self, PluginsManager):
        if not PluginsManager.objectName():
            PluginsManager.setObjectName(u"PluginsManager")
        PluginsManager.resize(800, 600)
        self.verticalLayout = QVBoxLayout(PluginsManager)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(PluginsManager)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.table = QTableWidget(self.frame)
        if (self.table.columnCount() < 4):
            self.table.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.table.setObjectName(u"table")
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.table)

        self.splitter.addWidget(self.frame)
        self.info_frame = QFrame(self.splitter)
        self.info_frame.setObjectName(u"info_frame")
        self.info_frame.setFrameShape(QFrame.StyledPanel)
        self.info_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.info_frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.restart_button = QPushButton(self.info_frame)
        self.restart_button.setObjectName(u"restart_button")

        self.horizontalLayout.addWidget(self.restart_button)

        self.progress = QProgressBar(self.info_frame)
        self.progress.setObjectName(u"progress")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress.sizePolicy().hasHeightForWidth())
        self.progress.setSizePolicy(sizePolicy)
        self.progress.setMaximum(0)
        self.progress.setValue(-1)

        self.horizontalLayout.addWidget(self.progress)

        self.refresh_button = QPushButton(self.info_frame)
        self.refresh_button.setObjectName(u"refresh_button")

        self.horizontalLayout.addWidget(self.refresh_button)

        self.uninstall_button = QPushButton(self.info_frame)
        self.uninstall_button.setObjectName(u"uninstall_button")

        self.horizontalLayout.addWidget(self.uninstall_button)

        self.install_button = QPushButton(self.info_frame)
        self.install_button.setObjectName(u"install_button")

        self.horizontalLayout.addWidget(self.install_button)

        self.install_git_button = QToolButton(self.info_frame)
        self.install_git_button.setObjectName(u"install_git_button")
        icon = QIcon()
        icon.addFile(u":/resources/git.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.install_git_button.setIcon(icon)

        self.horizontalLayout.addWidget(self.install_git_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.splitter.addWidget(self.info_frame)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(PluginsManager)
        self.table.itemSelectionChanged.connect(PluginsManager.handle_selection_change)
        self.install_button.clicked.connect(PluginsManager.install_selected_package)
        self.restart_button.clicked.connect(PluginsManager.restart)
        self.uninstall_button.clicked.connect(PluginsManager.uninstall_selected_package)
        self.refresh_button.clicked.connect(PluginsManager.refresh)
        self.install_git_button.clicked.connect(PluginsManager.install_from_git)

        QMetaObject.connectSlotsByName(PluginsManager)
    # setupUi

    def retranslateUi(self, PluginsManager):
        PluginsManager.setWindowTitle(QCoreApplication.translate("PluginsManager", u"Dialog", None))
        ___qtablewidgetitem = self.table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("PluginsManager", u"State", None));
        ___qtablewidgetitem1 = self.table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("PluginsManager", u"Name", None));
        ___qtablewidgetitem2 = self.table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("PluginsManager", u"Version", None));
        ___qtablewidgetitem3 = self.table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("PluginsManager", u"Summary", None));
        self.restart_button.setText(QCoreApplication.translate("PluginsManager", u"Restart", None))
        self.refresh_button.setText(QCoreApplication.translate("PluginsManager", u"Refresh", None))
        self.uninstall_button.setText(QCoreApplication.translate("PluginsManager", u"Uninstall", None))
        self.install_button.setText(QCoreApplication.translate("PluginsManager", u"Install/Update", None))
        self.install_git_button.setText(QCoreApplication.translate("PluginsManager", u"...", None))
    # retranslateUi

