# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'CommentDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QGridLayout, QHBoxLayout, QLabel,
    QPlainTextEdit, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(425, 273)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.text_edit_comment = QPlainTextEdit(Dialog)
        self.text_edit_comment.setObjectName(u"text_edit_comment")

        self.verticalLayout.addWidget(self.text_edit_comment)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.rating_label = QLabel(Dialog)
        self.rating_label.setObjectName(u"rating_label")

        self.gridLayout.addWidget(self.rating_label, 0, 0, 1, 1)

        self.combobox_rating = QComboBox(Dialog)
        self.combobox_rating.setObjectName(u"combobox_rating")

        self.gridLayout.addWidget(self.combobox_rating, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(1, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Save)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Post a Comment", None))
#if QT_CONFIG(tooltip)
        self.text_edit_comment.setToolTip(QCoreApplication.translate("Dialog", u"Enter the comment you want to post on the song.", None))
#endif // QT_CONFIG(tooltip)
        self.rating_label.setText(QCoreApplication.translate("Dialog", u"Rating:", None))
#if QT_CONFIG(tooltip)
        self.combobox_rating.setToolTip(QCoreApplication.translate("Dialog", u"Please select a rating for this comment.", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

