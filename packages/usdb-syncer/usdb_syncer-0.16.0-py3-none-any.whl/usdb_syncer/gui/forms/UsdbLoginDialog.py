# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UsdbLoginDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QCommandLinkButton,
    QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(294, 214)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.line_edit_username = QLineEdit(Dialog)
        self.line_edit_username.setObjectName(u"line_edit_username")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_edit_username)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.line_edit_password = QLineEdit(Dialog)
        self.line_edit_password.setObjectName(u"line_edit_password")
        self.line_edit_password.setEchoMode(QLineEdit.Password)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.line_edit_password)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.combobox_browser = QComboBox(Dialog)
        self.combobox_browser.setObjectName(u"combobox_browser")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.combobox_browser)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.command_link_register = QCommandLinkButton(Dialog)
        self.command_link_register.setObjectName(u"command_link_register")

        self.horizontalLayout_2.addWidget(self.command_link_register)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_check_login = QPushButton(Dialog)
        self.button_check_login.setObjectName(u"button_check_login")

        self.horizontalLayout.addWidget(self.button_check_login)

        self.button_log_out = QPushButton(Dialog)
        self.button_log_out.setObjectName(u"button_log_out")

        self.horizontalLayout.addWidget(self.button_log_out)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Save)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"USDB Login", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Username:", None))
#if QT_CONFIG(tooltip)
        self.line_edit_username.setToolTip(QCoreApplication.translate("Dialog", u"Enter your USDB credentials to automatically log in if there is no existing session.", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Password:", None))
#if QT_CONFIG(tooltip)
        self.line_edit_password.setToolTip(QCoreApplication.translate("Dialog", u"Enter your USDB credentials to automatically log in if there is no existing session.", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Browser cookies:", None))
#if QT_CONFIG(tooltip)
        self.combobox_browser.setToolTip(QCoreApplication.translate("Dialog", u"Select your browser in order to reuse an existing USDB session.", None))
#endif // QT_CONFIG(tooltip)
        self.command_link_register.setText(QCoreApplication.translate("Dialog", u"No account?", None))
        self.command_link_register.setDescription(QCoreApplication.translate("Dialog", u"Register on USDB", None))
        self.button_check_login.setText(QCoreApplication.translate("Dialog", u"Check Login", None))
        self.button_log_out.setText(QCoreApplication.translate("Dialog", u"Log Out", None))
    # retranslateUi

