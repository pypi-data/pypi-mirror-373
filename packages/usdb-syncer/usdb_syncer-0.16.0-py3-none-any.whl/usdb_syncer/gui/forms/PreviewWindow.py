# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PreviewWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QSizePolicy, QSlider,
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)
from usdb_syncer.gui.resources.qt import resources as resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1198, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.layout_main = QVBoxLayout()
        self.layout_main.setObjectName(u"layout_main")
        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.setObjectName(u"layout_buttons")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_buttons.addItem(self.horizontalSpacer)

        self.button_to_start = QToolButton(self.centralwidget)
        self.button_to_start.setObjectName(u"button_to_start")
        icon = QIcon()
        icon.addFile(u":/icons/control-skip-180.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_to_start.setIcon(icon)
        self.button_to_start.setIconSize(QSize(20, 20))

        self.layout_buttons.addWidget(self.button_to_start)

        self.button_backward = QToolButton(self.centralwidget)
        self.button_backward.setObjectName(u"button_backward")
        icon1 = QIcon()
        icon1.addFile(u":/icons/control-double-180.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_backward.setIcon(icon1)
        self.button_backward.setIconSize(QSize(20, 20))

        self.layout_buttons.addWidget(self.button_backward)

        self.button_pause = QToolButton(self.centralwidget)
        self.button_pause.setObjectName(u"button_pause")
        icon2 = QIcon()
        icon2.addFile(u":/icons/control-pause.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_pause.setIcon(icon2)
        self.button_pause.setIconSize(QSize(20, 20))
        self.button_pause.setCheckable(True)

        self.layout_buttons.addWidget(self.button_pause)

        self.button_forward = QToolButton(self.centralwidget)
        self.button_forward.setObjectName(u"button_forward")
        icon3 = QIcon()
        icon3.addFile(u":/icons/control-double.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_forward.setIcon(icon3)
        self.button_forward.setIconSize(QSize(20, 20))

        self.layout_buttons.addWidget(self.button_forward)

        self.button_to_end = QToolButton(self.centralwidget)
        self.button_to_end.setObjectName(u"button_to_end")
        icon4 = QIcon()
        icon4.addFile(u":/icons/control-skip.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_to_end.setIcon(icon4)
        self.button_to_end.setIconSize(QSize(20, 20))

        self.layout_buttons.addWidget(self.button_to_end)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.layout_buttons.addItem(self.horizontalSpacer_2)


        self.layout_main.addLayout(self.layout_buttons)


        self.horizontalLayout.addLayout(self.layout_main)

        self.horizontalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.layout_extra = QVBoxLayout()
        self.layout_extra.setObjectName(u"layout_extra")
        self.label_time = QLabel(self.centralwidget)
        self.label_time.setObjectName(u"label_time")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_time.setFont(font)
        self.label_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout_extra.addWidget(self.label_time)

        self.label_bpm = QLabel(self.centralwidget)
        self.label_bpm.setObjectName(u"label_bpm")

        self.layout_extra.addWidget(self.label_bpm)

        self.label_gap = QLabel(self.centralwidget)
        self.label_gap.setObjectName(u"label_gap")

        self.layout_extra.addWidget(self.label_gap)

        self.label_start = QLabel(self.centralwidget)
        self.label_start.setObjectName(u"label_start")

        self.layout_extra.addWidget(self.label_start)

        self.label_end = QLabel(self.centralwidget)
        self.label_end.setObjectName(u"label_end")

        self.layout_extra.addWidget(self.label_end)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_extra.addItem(self.verticalSpacer)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_ticks_volume = QLabel(self.centralwidget)
        self.label_ticks_volume.setObjectName(u"label_ticks_volume")
        self.label_ticks_volume.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_ticks_volume, 2, 2, 1, 1)

        self.label_voice = QLabel(self.centralwidget)
        self.label_voice.setObjectName(u"label_voice")

        self.gridLayout.addWidget(self.label_voice, 0, 0, 1, 1)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.slider_source = QSlider(self.centralwidget)
        self.slider_source.setObjectName(u"slider_source")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slider_source.sizePolicy().hasHeightForWidth())
        self.slider_source.setSizePolicy(sizePolicy)
        self.slider_source.setMaximum(10)
        self.slider_source.setSingleStep(1)
        self.slider_source.setPageStep(1)
        self.slider_source.setValue(10)
        self.slider_source.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.slider_source, 1, 1, 1, 1)

        self.label_source_volume = QLabel(self.centralwidget)
        self.label_source_volume.setObjectName(u"label_source_volume")
        self.label_source_volume.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_source_volume, 1, 2, 1, 1)

        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_pitch_volume = QLabel(self.centralwidget)
        self.label_pitch_volume.setObjectName(u"label_pitch_volume")
        self.label_pitch_volume.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.label_pitch_volume, 3, 2, 1, 1)

        self.slider_ticks = QSlider(self.centralwidget)
        self.slider_ticks.setObjectName(u"slider_ticks")
        sizePolicy.setHeightForWidth(self.slider_ticks.sizePolicy().hasHeightForWidth())
        self.slider_ticks.setSizePolicy(sizePolicy)
        self.slider_ticks.setMaximum(10)
        self.slider_ticks.setSingleStep(1)
        self.slider_ticks.setPageStep(1)
        self.slider_ticks.setValue(10)
        self.slider_ticks.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.slider_ticks, 2, 1, 1, 1)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.comboBox_voice = QComboBox(self.centralwidget)
        self.comboBox_voice.setObjectName(u"comboBox_voice")

        self.gridLayout.addWidget(self.comboBox_voice, 0, 1, 1, 2)

        self.slider_pitch = QSlider(self.centralwidget)
        self.slider_pitch.setObjectName(u"slider_pitch")
        sizePolicy.setHeightForWidth(self.slider_pitch.sizePolicy().hasHeightForWidth())
        self.slider_pitch.setSizePolicy(sizePolicy)
        self.slider_pitch.setMaximum(10)
        self.slider_pitch.setPageStep(1)
        self.slider_pitch.setValue(0)
        self.slider_pitch.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.slider_pitch, 3, 1, 1, 1)


        self.layout_extra.addLayout(self.gridLayout)


        self.horizontalLayout.addLayout(self.layout_extra)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.button_to_start.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.button_backward.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.button_pause.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.button_forward.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.button_to_end.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.label_time.setText(QCoreApplication.translate("MainWindow", u"00:00 / 02:30", None))
        self.label_bpm.setText(QCoreApplication.translate("MainWindow", u"#BPM: ", None))
        self.label_gap.setText(QCoreApplication.translate("MainWindow", u"#GAP: ", None))
        self.label_start.setText(QCoreApplication.translate("MainWindow", u"#START:", None))
        self.label_end.setText(QCoreApplication.translate("MainWindow", u"#END:", None))
        self.label_ticks_volume.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.label_voice.setText(QCoreApplication.translate("MainWindow", u"Voice:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Source:", None))
        self.label_source_volume.setText(QCoreApplication.translate("MainWindow", u"100", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Pitch:", None))
        self.label_pitch_volume.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Ticks:", None))
    # retranslateUi

