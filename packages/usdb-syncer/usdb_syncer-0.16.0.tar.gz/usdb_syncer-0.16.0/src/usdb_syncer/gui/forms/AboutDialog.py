# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AboutDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QSizePolicy, QTextBrowser, QWidget)
from usdb_syncer.gui.resources.qt import resources as resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 300)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(500, 300))
        Dialog.setMaximumSize(QSize(500, 300))
        Dialog.setStyleSheet(u"background-image: url(:/splash/splash.png);")
        self.credits = QTextBrowser(Dialog)
        self.credits.setObjectName(u"credits")
        self.credits.setGeometry(QRect(20, 20, 211, 201))
        sizePolicy.setHeightForWidth(self.credits.sizePolicy().hasHeightForWidth())
        self.credits.setSizePolicy(sizePolicy)
        self.credits.setStyleSheet(u"background-image: url();\n"
"background-color: rgba(255, 255, 255, 20);\n"
"color: rgb(255, 255, 255);\n"
"border-radius: 8px;\n"
"padding: 10px;")
        self.credits.setFrameShape(QFrame.Shape.NoFrame)
        self.credits.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.credits.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.credits.setOpenExternalLinks(True)
        self.label_version = QLabel(Dialog)
        self.label_version.setObjectName(u"label_version")
        self.label_version.setGeometry(QRect(0, 0, 431, 151))
        self.label_version.setStyleSheet(u"background-image: url(); \n"
"color: rgb(0, 174, 238);\n"
"font: 24pt \"Kozuka Gothic Pro\";")
        self.label_version.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"USDB Syncer", None))
        self.credits.setMarkdown(QCoreApplication.translate("Dialog", u"\n"
"\n"
"\n"
"**Thank you** for using USDB Syncer!\n"
"\n"
"Keep your karaoke song collection up to\n"
"date at the click of a button.\n"
"\n"
"***\n"
"\n"
"Licensed under the \n"
"[MIT License](https://mit-license.org/).\n"
"Find the source code on \n"
"[GitHub](https://github.com/bohning/usdb_syncer/).\n"
"\n"
"\n"
"***\n"
"\n"
"\n"
"**More info**\n"
"[USDB Syncer Wiki](https://github.com/bohning/usdb_syncer/wiki)\n"
"\n"
"\n"
"\n"
"\\***\n"
"\n"
"**Support**\n"
"You can support the developers by buying them some \n"
"[vegan pizza!](https://www.buymeacoffee.com/usdbsyncer)\n"
"\n"
"\n"
"\\***\n"
"\n"
"**Main Programmers**\n"
"bohning\n"
"RumovZ\n"
"\n"
"**Contributing Programmers**\n"
"mjhalwa\n"
"g3n35i5\n"
"BWagener\n"
"\n"
"***\n"
"\n"
"**\n"
"Application Icon**\n"
"rawpixel.com on Freepik\n"
"Website: \n"
"[freepik.com](https://www.freepik.com/free-vector/pink-neon-cloud-icon-digital-networking-system_16406257.htm)\n"
"**Fugue Icons**\n"
"\u00a9 2021 Yusuke Kamiyamane\n"
"Website: \n"
"[p.yusukekamiyama"
                        "ne.com/](https://p.yusukekamiyamane.com/)\n"
"License: \n"
"[CC Attribution 3.0 Unported](http://creativecommons.org/licenses/by/3.0)\n"
"\n"
"\\***\n"
"\n"
"**Testers**\n"
"Rakuri\n"
"Hoanzl\n"
"Gr\u00fcneNeun\n"
"\n"
"\n"
"\n"
"\n"
"**Copyright \u00a9 2023**\n"
"\n"
"", None))
        self.credits.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /><br /><br /><span style=\" font-weight:700;\">Thank you</span> for using USDB Syncer!<br /><br />Keep your karaoke song collection up to date at the click of a button.<br /><br />***<br /><br />Licensed under the <a href=\"https://mit-license.org/\"><span style=\" text-decoration: underline; color:#00aeef;\">MIT License</span></a>.<br />Find the source code on <a href=\"https://"
                        "github.com/bohning/usdb_syncer/\"><span style=\" text-decoration: underline; color:#00aeef;\">GitHub</span></a>.<br /><br /><br />***</p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /><span style=\" font-weight:700;\">More info</span><br /><a href=\"https://github.com/bohning/usdb_syncer/wiki\"><span style=\" text-decoration: underline; color:#00aeef;\">USDB Syncer Wiki</span></a><br /></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br />***<br /><br /><span style=\" font-weight:700;\">Support</span><br />You can support the developers by buying them some <a href=\"https://www.buymeacoffee.com/usdbsyncer\"><span style=\" text-decoration: underline; color:#00aeef;\">vegan pizza!</span></a><br /><br /><br />***<br /><br /><span style=\" font-weight:700;\">Main Programmers</span><br />bohning<br />RumovZ<br /><br /"
                        "><span style=\" font-weight:700;\">Contributing Programmers</span><br />mjhalwa<br />g3n35i5<br />BWagener<br /><br />***<br /><br /><span style=\" font-weight:700;\">Application Icon</span><br />rawpixel.com on Freepik<br />Website: <a href=\"https://www.freepik.com/free-vector/pink-neon-cloud-icon-digital-networking-system_16406257.htm\"><span style=\" text-decoration: underline; color:#00aeef;\">freepik.com</span></a><br /><br /><span style=\" font-weight:700;\">Fugue Icons</span><br />\u00a9 2021 Yusuke Kamiyamane<br />Website: <a href=\"https://p.yusukekamiyamane.com/\"><span style=\" text-decoration: underline; color:#00aeef;\">p.yusukekamiyamane.com/</span></a><br />License: <a href=\"http://creativecommons.org/licenses/by/3.0\"><span style=\" text-decoration: underline; color:#00aeef;\">CC Attribution 3.0 Unported</span></a><br /><br />***<br /><br /><span style=\" font-weight:700;\">Testers</span><br />Rakuri<br />Hoanzl<br />Gr\u00fcneNeun<br /><br /><br /><br /><br /><span style=\" font-weight:700;\""
                        ">Copyright \u00a9 2023</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'.AppleSystemUIFont'; font-size:13pt;\"><br /></p></body></html>", None))
        self.label_version.setText(QCoreApplication.translate("Dialog", u"VERSION", None))
    # retranslateUi

