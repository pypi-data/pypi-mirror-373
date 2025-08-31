# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'WebserverDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(348, 322)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_status = QLabel(Dialog)
        self.label_status.setObjectName(u"label_status")
        self.label_status.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.label_status)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.box_port = QSpinBox(Dialog)
        self.box_port.setObjectName(u"box_port")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.box_port.sizePolicy().hasHeightForWidth())
        self.box_port.setSizePolicy(sizePolicy)
        self.box_port.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.box_port.setMaximum(65535)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.box_port)

        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.edit_title = QLineEdit(Dialog)
        self.edit_title.setObjectName(u"edit_title")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.edit_title)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.label_qrcode = QLabel(Dialog)
        self.label_qrcode.setObjectName(u"label_qrcode")
        self.label_qrcode.setMinimumSize(QSize(150, 150))
        self.label_qrcode.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_qrcode)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_start = QPushButton(Dialog)
        self.button_start.setObjectName(u"button_start")

        self.horizontalLayout.addWidget(self.button_start)

        self.button_stop = QPushButton(Dialog)
        self.button_stop.setObjectName(u"button_stop")

        self.horizontalLayout.addWidget(self.button_stop)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Webserver", None))
        self.label_status.setText(QCoreApplication.translate("Dialog", u"The webserver is not currently running.", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Port:", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Title:", None))
        self.label_qrcode.setText("")
        self.button_start.setText(QCoreApplication.translate("Dialog", u"Start", None))
        self.button_stop.setText(QCoreApplication.translate("Dialog", u"Stop", None))
    # retranslateUi

