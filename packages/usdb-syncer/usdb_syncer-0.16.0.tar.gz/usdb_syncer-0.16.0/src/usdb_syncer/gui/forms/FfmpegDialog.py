# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FfmpegDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        Dialog.resize(631, 180)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_ffmpeg = QLabel(Dialog)
        self.label_ffmpeg.setObjectName(u"label_ffmpeg")
        self.label_ffmpeg.setTextFormat(Qt.TextFormat.RichText)
        self.label_ffmpeg.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_ffmpeg)

        self.label_windows = QLabel(Dialog)
        self.label_windows.setObjectName(u"label_windows")
        self.label_windows.setEnabled(True)
        self.label_windows.setTextFormat(Qt.TextFormat.RichText)
        self.label_windows.setWordWrap(True)
        self.label_windows.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.label_windows)

        self.label_macos = QLabel(Dialog)
        self.label_macos.setObjectName(u"label_macos")
        self.label_macos.setEnabled(True)
        self.label_macos.setTextFormat(Qt.TextFormat.RichText)
        self.label_macos.setWordWrap(True)
        self.label_macos.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.label_macos)

        self.label_linux = QLabel(Dialog)
        self.label_linux.setObjectName(u"label_linux")
        self.label_linux.setEnabled(True)
        self.label_linux.setTextFormat(Qt.TextFormat.RichText)
        self.label_linux.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_linux)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.set_location = QPushButton(Dialog)
        self.set_location.setObjectName(u"set_location")

        self.horizontalLayout.addWidget(self.set_location)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.horizontalLayout.addWidget(self.buttonBox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"FFmpeg not found", None))
        self.label_ffmpeg.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">FFmpeg</span> and ffprobe are required to proceed!</p></body></html>", None))
        self.label_windows.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>The recommended way to install FFmpeg is to use a package manager such as <a href=\"https://chocolatey.org/\"><span style=\" text-decoration: underline; color:#2e54ff;\">Chocolatey</span></a> (<span style=\" font-family:'Courier New';\">choco install ffmpeg</span>) or <a href=\"https://learn.microsoft.com/en-us/windows/package-manager/winget/\"><span style=\" text-decoration: underline; color:#2e54ff;\">winget</span></a> (<span style=\" font-family:'Courier New';\">winget install --id=Gyan.FFmpeg -e</span>).</p><p>Alternatively, download the FFmpeg binaries from <a href=\"https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z\"><span style=\" text-decoration: underline; color:#2e54ff;\">https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z</span></a>, extract the archive and then set the location with the button below. </p></body></html>", None))
        self.label_macos.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>The recommended way to install FFmpeg is via <a href=\"https://brew.sh/\"><span style=\" text-decoration: underline; color:#2e54ff;\">Homebrew</span></a> (<span style=\" font-family:'Courier New';\">brew install ffmpeg</span>).</p></body></html>", None))
        self.label_linux.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Please install the FFmpeg package through your distribution\u2019s package manager.</p></body></html>", None))
        self.set_location.setText(QCoreApplication.translate("Dialog", u"Set Location...", None))
    # retranslateUi

