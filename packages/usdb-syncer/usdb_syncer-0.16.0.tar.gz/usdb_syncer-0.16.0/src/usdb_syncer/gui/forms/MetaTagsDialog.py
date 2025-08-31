# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MetaTagsDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(861, 868)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(0, 0))
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(Dialog)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QFrame.Shadow.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 843, 850))
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.audio = QGroupBox(self.scrollAreaWidgetContents)
        self.audio.setObjectName(u"audio")
        self.verticalLayout_5 = QVBoxLayout(self.audio)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(4, 4, 4, 4)
        self.audio_layout = QHBoxLayout()
        self.audio_layout.setObjectName(u"audio_layout")
        self.audio_label = QLabel(self.audio)
        self.audio_label.setObjectName(u"audio_label")

        self.audio_layout.addWidget(self.audio_label)

        self.audio_url = QLineEdit(self.audio)
        self.audio_url.setObjectName(u"audio_url")

        self.audio_layout.addWidget(self.audio_url)


        self.verticalLayout_5.addLayout(self.audio_layout)


        self.verticalLayout_2.addWidget(self.audio)

        self.video = QGroupBox(self.scrollAreaWidgetContents)
        self.video.setObjectName(u"video")
        self.verticalLayout_4 = QVBoxLayout(self.video)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.video_layout = QHBoxLayout()
        self.video_layout.setObjectName(u"video_layout")
        self.video_label = QLabel(self.video)
        self.video_label.setObjectName(u"video_label")

        self.video_layout.addWidget(self.video_label)

        self.video_url = QLineEdit(self.video)
        self.video_url.setObjectName(u"video_url")

        self.video_layout.addWidget(self.video_url)


        self.verticalLayout_4.addLayout(self.video_layout)


        self.verticalLayout_2.addWidget(self.video)

        self.cover = QGroupBox(self.scrollAreaWidgetContents)
        self.cover.setObjectName(u"cover")
        self.verticalLayout_6 = QVBoxLayout(self.cover)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(4, 4, 4, 4)
        self.cover_url_layout = QHBoxLayout()
        self.cover_url_layout.setObjectName(u"cover_url_layout")
        self.cover_label = QLabel(self.cover)
        self.cover_label.setObjectName(u"cover_label")

        self.cover_url_layout.addWidget(self.cover_label)

        self.cover_url = QLineEdit(self.cover)
        self.cover_url.setObjectName(u"cover_url")

        self.cover_url_layout.addWidget(self.cover_url)


        self.verticalLayout_6.addLayout(self.cover_url_layout)

        self.cover_rotate_contrast_resize_layout = QHBoxLayout()
        self.cover_rotate_contrast_resize_layout.setObjectName(u"cover_rotate_contrast_resize_layout")
        self.cover_rotate_contrast_resize_layout.setContentsMargins(-1, -1, -1, 0)
        self.groupBox_12 = QGroupBox(self.cover)
        self.groupBox_12.setObjectName(u"groupBox_12")
        self.horizontalLayout_15 = QHBoxLayout(self.groupBox_12)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(4, 4, 4, 4)
        self.rotation_label = QLabel(self.groupBox_12)
        self.rotation_label.setObjectName(u"rotation_label")

        self.horizontalLayout_15.addWidget(self.rotation_label)

        self.cover_rotation = QDoubleSpinBox(self.groupBox_12)
        self.cover_rotation.setObjectName(u"cover_rotation")
        self.cover_rotation.setMinimum(-360.000000000000000)
        self.cover_rotation.setMaximum(360.000000000000000)
        self.cover_rotation.setSingleStep(0.100000000000000)

        self.horizontalLayout_15.addWidget(self.cover_rotation)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_10)


        self.cover_rotate_contrast_resize_layout.addWidget(self.groupBox_12)

        self.groupBox_14 = QGroupBox(self.cover)
        self.groupBox_14.setObjectName(u"groupBox_14")
        self.horizontalLayout_19 = QHBoxLayout(self.groupBox_14)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(4, 4, 4, 4)
        self.contrast_label = QLabel(self.groupBox_14)
        self.contrast_label.setObjectName(u"contrast_label")

        self.horizontalLayout_19.addWidget(self.contrast_label)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.cover_contrast_auto = QCheckBox(self.groupBox_14)
        self.cover_contrast_auto.setObjectName(u"cover_contrast_auto")

        self.horizontalLayout_3.addWidget(self.cover_contrast_auto)

        self.cover_contrast = QDoubleSpinBox(self.groupBox_14)
        self.cover_contrast.setObjectName(u"cover_contrast")
        self.cover_contrast.setSingleStep(0.100000000000000)
        self.cover_contrast.setValue(1.000000000000000)

        self.horizontalLayout_3.addWidget(self.cover_contrast)


        self.horizontalLayout_19.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_12)


        self.cover_rotate_contrast_resize_layout.addWidget(self.groupBox_14)

        self.groupBox_13 = QGroupBox(self.cover)
        self.groupBox_13.setObjectName(u"groupBox_13")
        self.horizontalLayout_16 = QHBoxLayout(self.groupBox_13)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(4, 4, 4, 4)
        self.resize_label = QLabel(self.groupBox_13)
        self.resize_label.setObjectName(u"resize_label")

        self.horizontalLayout_16.addWidget(self.resize_label)

        self.cover_resize = QSpinBox(self.groupBox_13)
        self.cover_resize.setObjectName(u"cover_resize")
        self.cover_resize.setMinimum(0)
        self.cover_resize.setMaximum(1920)
        self.cover_resize.setValue(0)

        self.horizontalLayout_16.addWidget(self.cover_resize)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_11)


        self.cover_rotate_contrast_resize_layout.addWidget(self.groupBox_13)


        self.verticalLayout_6.addLayout(self.cover_rotate_contrast_resize_layout)

        self.cover_crop_group = QGroupBox(self.cover)
        self.cover_crop_group.setObjectName(u"cover_crop_group")
        self.horizontalLayout_2 = QHBoxLayout(self.cover_crop_group)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.cover_crop_left_label = QLabel(self.cover_crop_group)
        self.cover_crop_left_label.setObjectName(u"cover_crop_left_label")
        sizePolicy1.setHeightForWidth(self.cover_crop_left_label.sizePolicy().hasHeightForWidth())
        self.cover_crop_left_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.cover_crop_left_label)

        self.cover_crop_left = QSpinBox(self.cover_crop_group)
        self.cover_crop_left.setObjectName(u"cover_crop_left")
        self.cover_crop_left.setMaximum(9999)

        self.horizontalLayout_2.addWidget(self.cover_crop_left)

        self.cover_crop_top_label = QLabel(self.cover_crop_group)
        self.cover_crop_top_label.setObjectName(u"cover_crop_top_label")

        self.horizontalLayout_2.addWidget(self.cover_crop_top_label)

        self.cover_crop_top = QSpinBox(self.cover_crop_group)
        self.cover_crop_top.setObjectName(u"cover_crop_top")
        self.cover_crop_top.setMaximum(9999)

        self.horizontalLayout_2.addWidget(self.cover_crop_top)

        self.cover_crop_width_label = QLabel(self.cover_crop_group)
        self.cover_crop_width_label.setObjectName(u"cover_crop_width_label")

        self.horizontalLayout_2.addWidget(self.cover_crop_width_label)

        self.cover_crop_width = QSpinBox(self.cover_crop_group)
        self.cover_crop_width.setObjectName(u"cover_crop_width")
        self.cover_crop_width.setMaximum(9999)

        self.horizontalLayout_2.addWidget(self.cover_crop_width)

        self.cover_crop_height_label = QLabel(self.cover_crop_group)
        self.cover_crop_height_label.setObjectName(u"cover_crop_height_label")

        self.horizontalLayout_2.addWidget(self.cover_crop_height_label)

        self.cover_crop_height = QSpinBox(self.cover_crop_group)
        self.cover_crop_height.setObjectName(u"cover_crop_height")
        self.cover_crop_height.setMaximum(9999)

        self.horizontalLayout_2.addWidget(self.cover_crop_height)

        self.horizontalSpacer_4 = QSpacerItem(0, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_6.addWidget(self.cover_crop_group)


        self.verticalLayout_2.addWidget(self.cover)

        self.background = QGroupBox(self.scrollAreaWidgetContents)
        self.background.setObjectName(u"background")
        self.verticalLayout_7 = QVBoxLayout(self.background)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(4, 4, 4, 4)
        self.background_url_layout = QHBoxLayout()
        self.background_url_layout.setObjectName(u"background_url_layout")
        self.background_label = QLabel(self.background)
        self.background_label.setObjectName(u"background_label")

        self.background_url_layout.addWidget(self.background_label)

        self.background_url = QLineEdit(self.background)
        self.background_url.setObjectName(u"background_url")

        self.background_url_layout.addWidget(self.background_url)


        self.verticalLayout_7.addLayout(self.background_url_layout)

        self.background_resize_group = QGroupBox(self.background)
        self.background_resize_group.setObjectName(u"background_resize_group")
        self.horizontalLayout_9 = QHBoxLayout(self.background_resize_group)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(4, 4, 4, 4)
        self.background_resize_width_label = QLabel(self.background_resize_group)
        self.background_resize_width_label.setObjectName(u"background_resize_width_label")

        self.horizontalLayout_9.addWidget(self.background_resize_width_label)

        self.background_resize_width = QSpinBox(self.background_resize_group)
        self.background_resize_width.setObjectName(u"background_resize_width")
        self.background_resize_width.setMaximum(9999)

        self.horizontalLayout_9.addWidget(self.background_resize_width)

        self.label_22background_resize_height_label = QLabel(self.background_resize_group)
        self.label_22background_resize_height_label.setObjectName(u"label_22background_resize_height_label")

        self.horizontalLayout_9.addWidget(self.label_22background_resize_height_label)

        self.background_resize_height = QSpinBox(self.background_resize_group)
        self.background_resize_height.setObjectName(u"background_resize_height")
        self.background_resize_height.setMaximum(9999)

        self.horizontalLayout_9.addWidget(self.background_resize_height)

        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_9)


        self.verticalLayout_7.addWidget(self.background_resize_group)

        self.background_crop_group = QGroupBox(self.background)
        self.background_crop_group.setObjectName(u"background_crop_group")
        self.horizontalLayout_4 = QHBoxLayout(self.background_crop_group)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.background_crop_left_label = QLabel(self.background_crop_group)
        self.background_crop_left_label.setObjectName(u"background_crop_left_label")
        sizePolicy1.setHeightForWidth(self.background_crop_left_label.sizePolicy().hasHeightForWidth())
        self.background_crop_left_label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_4.addWidget(self.background_crop_left_label)

        self.background_crop_left = QSpinBox(self.background_crop_group)
        self.background_crop_left.setObjectName(u"background_crop_left")
        self.background_crop_left.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.background_crop_left)

        self.background_crop_top_label = QLabel(self.background_crop_group)
        self.background_crop_top_label.setObjectName(u"background_crop_top_label")

        self.horizontalLayout_4.addWidget(self.background_crop_top_label)

        self.background_crop_top = QSpinBox(self.background_crop_group)
        self.background_crop_top.setObjectName(u"background_crop_top")
        self.background_crop_top.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.background_crop_top)

        self.background_crop_width_label = QLabel(self.background_crop_group)
        self.background_crop_width_label.setObjectName(u"background_crop_width_label")

        self.horizontalLayout_4.addWidget(self.background_crop_width_label)

        self.background_crop_width = QSpinBox(self.background_crop_group)
        self.background_crop_width.setObjectName(u"background_crop_width")
        self.background_crop_width.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.background_crop_width)

        self.background_crop_height_label = QLabel(self.background_crop_group)
        self.background_crop_height_label.setObjectName(u"background_crop_height_label")

        self.horizontalLayout_4.addWidget(self.background_crop_height_label)

        self.background_crop_height = QSpinBox(self.background_crop_group)
        self.background_crop_height.setObjectName(u"background_crop_height")
        self.background_crop_height.setMaximum(9999)

        self.horizontalLayout_4.addWidget(self.background_crop_height)

        self.horizontalSpacer_8 = QSpacerItem(385, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.verticalLayout_7.addWidget(self.background_crop_group)


        self.verticalLayout_2.addWidget(self.background)

        self.duet = QGroupBox(self.scrollAreaWidgetContents)
        self.duet.setObjectName(u"duet")
        sizePolicy1.setHeightForWidth(self.duet.sizePolicy().hasHeightForWidth())
        self.duet.setSizePolicy(sizePolicy1)
        self.duet.setCheckable(True)
        self.duet.setChecked(False)
        self.horizontalLayout_6 = QHBoxLayout(self.duet)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(4, 4, 4, 4)
        self.duet_p1_label = QLabel(self.duet)
        self.duet_p1_label.setObjectName(u"duet_p1_label")
        sizePolicy1.setHeightForWidth(self.duet_p1_label.sizePolicy().hasHeightForWidth())
        self.duet_p1_label.setSizePolicy(sizePolicy1)
        self.duet_p1_label.setMaximumSize(QSize(16777215, 26))

        self.horizontalLayout_6.addWidget(self.duet_p1_label)

        self.duet_p1 = QLineEdit(self.duet)
        self.duet_p1.setObjectName(u"duet_p1")

        self.horizontalLayout_6.addWidget(self.duet_p1)

        self.duet_p2_label = QLabel(self.duet)
        self.duet_p2_label.setObjectName(u"duet_p2_label")
        sizePolicy1.setHeightForWidth(self.duet_p2_label.sizePolicy().hasHeightForWidth())
        self.duet_p2_label.setSizePolicy(sizePolicy1)
        self.duet_p2_label.setMaximumSize(QSize(16777215, 26))

        self.horizontalLayout_6.addWidget(self.duet_p2_label)

        self.duet_p2 = QLineEdit(self.duet)
        self.duet_p2.setObjectName(u"duet_p2")

        self.horizontalLayout_6.addWidget(self.duet_p2)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addWidget(self.duet)

        self.preview_medley = QHBoxLayout()
        self.preview_medley.setObjectName(u"preview_medley")
        self.preview = QGroupBox(self.scrollAreaWidgetContents)
        self.preview.setObjectName(u"preview")
        self.horizontalLayout_7 = QHBoxLayout(self.preview)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.preview_start_label = QLabel(self.preview)
        self.preview_start_label.setObjectName(u"preview_start_label")

        self.horizontalLayout_7.addWidget(self.preview_start_label)

        self.preview_start = QDoubleSpinBox(self.preview)
        self.preview_start.setObjectName(u"preview_start")
        self.preview_start.setDecimals(3)
        self.preview_start.setMaximum(999.990000000000009)

        self.horizontalLayout_7.addWidget(self.preview_start)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_2)


        self.preview_medley.addWidget(self.preview)

        self.medley = QGroupBox(self.scrollAreaWidgetContents)
        self.medley.setObjectName(u"medley")
        self.horizontalLayout_11 = QHBoxLayout(self.medley)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.medley_start_label = QLabel(self.medley)
        self.medley_start_label.setObjectName(u"medley_start_label")

        self.horizontalLayout_11.addWidget(self.medley_start_label)

        self.medley_start = QSpinBox(self.medley)
        self.medley_start.setObjectName(u"medley_start")
        self.medley_start.setMaximum(99999)

        self.horizontalLayout_11.addWidget(self.medley_start)

        self.medley_end_label = QLabel(self.medley)
        self.medley_end_label.setObjectName(u"medley_end_label")

        self.horizontalLayout_11.addWidget(self.medley_end_label)

        self.medley_end = QSpinBox(self.medley)
        self.medley_end.setObjectName(u"medley_end")
        self.medley_end.setMaximum(99999)

        self.horizontalLayout_11.addWidget(self.medley_end)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_5)


        self.preview_medley.addWidget(self.medley)


        self.verticalLayout_2.addLayout(self.preview_medley)

        self.tags_2 = QGroupBox(self.scrollAreaWidgetContents)
        self.tags_2.setObjectName(u"tags_2")
        self.verticalLayout_3 = QVBoxLayout(self.tags_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.tags_layout = QHBoxLayout()
        self.tags_layout.setObjectName(u"tags_layout")
        self.tags_label = QLabel(self.tags_2)
        self.tags_label.setObjectName(u"tags_label")

        self.tags_layout.addWidget(self.tags_label)

        self.tags = QLineEdit(self.tags_2)
        self.tags.setObjectName(u"tags")

        self.tags_layout.addWidget(self.tags)


        self.verticalLayout_3.addLayout(self.tags_layout)


        self.verticalLayout_2.addWidget(self.tags_2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.meta_tags = QHBoxLayout()
        self.meta_tags.setObjectName(u"meta_tags")
        self.output = QLineEdit(self.scrollAreaWidgetContents)
        self.output.setObjectName(u"output")
        self.output.setReadOnly(True)

        self.meta_tags.addWidget(self.output)

        self.button_copy_to_clipboard = QPushButton(self.scrollAreaWidgetContents)
        self.button_copy_to_clipboard.setObjectName(u"button_copy_to_clipboard")

        self.meta_tags.addWidget(self.button_copy_to_clipboard)


        self.verticalLayout_2.addLayout(self.meta_tags)

        self.buttonBox = QDialogButtonBox(self.scrollAreaWidgetContents)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Meta Tags", None))
        self.audio.setTitle(QCoreApplication.translate("Dialog", u"Audio (a)", None))
        self.audio_label.setText(QCoreApplication.translate("Dialog", u"URL:", None))
        self.video.setTitle(QCoreApplication.translate("Dialog", u"Video (v)", None))
        self.video_label.setText(QCoreApplication.translate("Dialog", u"URL:", None))
        self.cover.setTitle(QCoreApplication.translate("Dialog", u"Cover (co)", None))
        self.cover_label.setText(QCoreApplication.translate("Dialog", u"URL:", None))
        self.groupBox_12.setTitle(QCoreApplication.translate("Dialog", u"Rotation (co-rotate)", None))
        self.rotation_label.setText(QCoreApplication.translate("Dialog", u"Angle (ccw):", None))
        self.cover_rotation.setSuffix(QCoreApplication.translate("Dialog", u"\u00b0", None))
        self.groupBox_14.setTitle(QCoreApplication.translate("Dialog", u"Contrast (co-contrast)", None))
        self.contrast_label.setText(QCoreApplication.translate("Dialog", u"Value:", None))
        self.cover_contrast_auto.setText(QCoreApplication.translate("Dialog", u"Auto", None))
        self.groupBox_13.setTitle(QCoreApplication.translate("Dialog", u"Resize (co-resize)", None))
        self.resize_label.setText(QCoreApplication.translate("Dialog", u"Width/Height:", None))
        self.cover_resize.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.cover_crop_group.setTitle(QCoreApplication.translate("Dialog", u"Crop (co-crop)", None))
        self.cover_crop_left_label.setText(QCoreApplication.translate("Dialog", u"Left:", None))
        self.cover_crop_left.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.cover_crop_top_label.setText(QCoreApplication.translate("Dialog", u"Top:", None))
        self.cover_crop_top.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.cover_crop_width_label.setText(QCoreApplication.translate("Dialog", u"Width:", None))
        self.cover_crop_width.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.cover_crop_height_label.setText(QCoreApplication.translate("Dialog", u"Height:", None))
        self.cover_crop_height.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.background.setTitle(QCoreApplication.translate("Dialog", u"Background (bg)", None))
        self.background_label.setText(QCoreApplication.translate("Dialog", u"URL:", None))
        self.background_resize_group.setTitle(QCoreApplication.translate("Dialog", u"Resize (bg-resize)", None))
        self.background_resize_width_label.setText(QCoreApplication.translate("Dialog", u"Width:", None))
        self.background_resize_width.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.label_22background_resize_height_label.setText(QCoreApplication.translate("Dialog", u"Height:", None))
        self.background_resize_height.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.background_crop_group.setTitle(QCoreApplication.translate("Dialog", u"Crop (bg-crop)", None))
        self.background_crop_left_label.setText(QCoreApplication.translate("Dialog", u"Left:", None))
        self.background_crop_left.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.background_crop_top_label.setText(QCoreApplication.translate("Dialog", u"Top:", None))
        self.background_crop_top.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.background_crop_width_label.setText(QCoreApplication.translate("Dialog", u"Width:", None))
        self.background_crop_width.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.background_crop_height_label.setText(QCoreApplication.translate("Dialog", u"Height:", None))
        self.background_crop_height.setSuffix(QCoreApplication.translate("Dialog", u" px", None))
        self.duet.setTitle(QCoreApplication.translate("Dialog", u"Duet (p1, p2)", None))
        self.duet_p1_label.setText(QCoreApplication.translate("Dialog", u"Player 1:", None))
        self.duet_p1.setText(QCoreApplication.translate("Dialog", u"P1", None))
        self.duet_p2_label.setText(QCoreApplication.translate("Dialog", u"Player 2:", None))
        self.duet_p2.setText(QCoreApplication.translate("Dialog", u"P2", None))
        self.preview.setTitle(QCoreApplication.translate("Dialog", u"Preview (preview)", None))
        self.preview_start_label.setText(QCoreApplication.translate("Dialog", u"Preview start:", None))
        self.preview_start.setPrefix("")
        self.preview_start.setSuffix(QCoreApplication.translate("Dialog", u" s", None))
        self.medley.setTitle(QCoreApplication.translate("Dialog", u"Medley (medley)", None))
        self.medley_start_label.setText(QCoreApplication.translate("Dialog", u"Start:", None))
        self.medley_start.setSuffix("")
        self.medley_start.setPrefix(QCoreApplication.translate("Dialog", u"beat ", None))
        self.medley_end_label.setText(QCoreApplication.translate("Dialog", u"End:", None))
        self.medley_end.setPrefix(QCoreApplication.translate("Dialog", u"beat ", None))
        self.tags_2.setTitle(QCoreApplication.translate("Dialog", u"Tags (tags)", None))
        self.tags_label.setText(QCoreApplication.translate("Dialog", u"Tags:", None))
        self.output.setText(QCoreApplication.translate("Dialog", u"#VIDEO:", None))
        self.button_copy_to_clipboard.setText(QCoreApplication.translate("Dialog", u"Copy to Clipboard", None))
    # retranslateUi

