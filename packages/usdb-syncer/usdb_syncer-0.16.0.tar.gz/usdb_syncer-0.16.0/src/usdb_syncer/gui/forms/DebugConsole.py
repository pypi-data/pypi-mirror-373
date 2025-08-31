# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'DebugConsole.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPlainTextEdit, QSizePolicy,
    QSplitter, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(659, 664)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(Dialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(5)
        self.input = QPlainTextEdit(self.splitter)
        self.input.setObjectName(u"input")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.input.sizePolicy().hasHeightForWidth())
        self.input.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.input.setFont(font)
        self.input.setLineWidth(1)
        self.input.setPlaceholderText(u"This REPL lets you execute Python code at runtime.\n"
"\n"
"Actions\n"
"    Ctrl+Return         Execute\n"
"    Ctrl+Shift+Return   Execute and print current line\n"
"    Ctrl+L              Clear output\n"
"    Ctrl+Shift+L        Clear input\n"
"\n"
"Locals\n"
"    mw: usdb_syncer.gui.mw.MainWindow")
        self.splitter.addWidget(self.input)
        self.output = QPlainTextEdit(self.splitter)
        self.output.setObjectName(u"output")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(2)
        sizePolicy1.setHeightForWidth(self.output.sizePolicy().hasHeightForWidth())
        self.output.setSizePolicy(sizePolicy1)
        self.output.setFont(font)
        self.output.setReadOnly(True)
        self.splitter.addWidget(self.output)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Debug Console", None))
        self.input.setDocumentTitle("")
        self.input.setPlainText("")
    # retranslateUi

