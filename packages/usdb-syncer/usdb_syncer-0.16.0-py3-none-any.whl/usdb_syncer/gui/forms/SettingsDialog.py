# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingsDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QVBoxLayout, QWidget)
from usdb_syncer.gui.resources.qt import resources as resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(673, 828)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_6 = QVBoxLayout(self.tab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_theme = QLabel(self.tab)
        self.label_theme.setObjectName(u"label_theme")

        self.horizontalLayout_11.addWidget(self.label_theme)

        self.comboBox_theme = QComboBox(self.tab)
        self.comboBox_theme.setObjectName(u"comboBox_theme")

        self.horizontalLayout_11.addWidget(self.comboBox_theme)


        self.verticalLayout_6.addLayout(self.horizontalLayout_11)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_primary_color = QLabel(self.tab)
        self.label_primary_color.setObjectName(u"label_primary_color")

        self.horizontalLayout_14.addWidget(self.label_primary_color)

        self.comboBox_primary_color = QComboBox(self.tab)
        self.comboBox_primary_color.setObjectName(u"comboBox_primary_color")

        self.horizontalLayout_14.addWidget(self.comboBox_primary_color)


        self.verticalLayout_6.addLayout(self.horizontalLayout_14)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_12.addWidget(self.label_3)

        self.checkBox_colored_background = QCheckBox(self.tab)
        self.checkBox_colored_background.setObjectName(u"checkBox_colored_background")

        self.horizontalLayout_12.addWidget(self.checkBox_colored_background)


        self.verticalLayout_6.addLayout(self.horizontalLayout_12)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.tabWidget.addTab(self.tab, "")
        self.tabDownload = QWidget()
        self.tabDownload.setObjectName(u"tabDownload")
        self.horizontalLayout = QHBoxLayout(self.tabDownload)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(20, -1, -1, -1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.checkBox_auto_update = QCheckBox(self.tabDownload)
        self.checkBox_auto_update.setObjectName(u"checkBox_auto_update")

        self.verticalLayout.addWidget(self.checkBox_auto_update)

        self.groupBox_login = QGroupBox(self.tabDownload)
        self.groupBox_login.setObjectName(u"groupBox_login")
        self.gridLayout_3 = QGridLayout(self.groupBox_login)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_login_cookies = QLabel(self.groupBox_login)
        self.label_login_cookies.setObjectName(u"label_login_cookies")

        self.gridLayout_3.addWidget(self.label_login_cookies, 0, 0, 1, 1)

        self.comboBox_browser = QComboBox(self.groupBox_login)
        self.comboBox_browser.setObjectName(u"comboBox_browser")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_browser.sizePolicy().hasHeightForWidth())
        self.comboBox_browser.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.comboBox_browser, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_login)

        self.groupBox_songfile = QGroupBox(self.tabDownload)
        self.groupBox_songfile.setObjectName(u"groupBox_songfile")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_songfile.sizePolicy().hasHeightForWidth())
        self.groupBox_songfile.setSizePolicy(sizePolicy1)
        self.groupBox_songfile.setCheckable(True)
        self.gridLayout_2 = QGridLayout(self.groupBox_songfile)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_song_file_encoding = QLabel(self.groupBox_songfile)
        self.label_song_file_encoding.setObjectName(u"label_song_file_encoding")

        self.gridLayout_2.addWidget(self.label_song_file_encoding, 0, 0, 1, 1)

        self.label_song_file_line_endings = QLabel(self.groupBox_songfile)
        self.label_song_file_line_endings.setObjectName(u"label_song_file_line_endings")

        self.gridLayout_2.addWidget(self.label_song_file_line_endings, 1, 0, 1, 1)

        self.comboBox_encoding = QComboBox(self.groupBox_songfile)
        self.comboBox_encoding.setObjectName(u"comboBox_encoding")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBox_encoding.sizePolicy().hasHeightForWidth())
        self.comboBox_encoding.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.comboBox_encoding, 0, 1, 1, 1)

        self.comboBox_line_endings = QComboBox(self.groupBox_songfile)
        self.comboBox_line_endings.setObjectName(u"comboBox_line_endings")
        sizePolicy2.setHeightForWidth(self.comboBox_line_endings.sizePolicy().hasHeightForWidth())
        self.comboBox_line_endings.setSizePolicy(sizePolicy2)

        self.gridLayout_2.addWidget(self.comboBox_line_endings, 1, 1, 1, 1)

        self.label_song_file_format_version = QLabel(self.groupBox_songfile)
        self.label_song_file_format_version.setObjectName(u"label_song_file_format_version")

        self.gridLayout_2.addWidget(self.label_song_file_format_version, 2, 0, 1, 1)

        self.comboBox_format_version = QComboBox(self.groupBox_songfile)
        self.comboBox_format_version.setObjectName(u"comboBox_format_version")

        self.gridLayout_2.addWidget(self.comboBox_format_version, 2, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_songfile)

        self.groupBox_fixes = QGroupBox(self.tabDownload)
        self.groupBox_fixes.setObjectName(u"groupBox_fixes")
        self.gridLayout_9 = QGridLayout(self.groupBox_fixes)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_song_file_fix_linebreaks = QLabel(self.groupBox_fixes)
        self.label_song_file_fix_linebreaks.setObjectName(u"label_song_file_fix_linebreaks")

        self.gridLayout_9.addWidget(self.label_song_file_fix_linebreaks, 0, 0, 1, 1)

        self.comboBox_fix_linebreaks = QComboBox(self.groupBox_fixes)
        self.comboBox_fix_linebreaks.setObjectName(u"comboBox_fix_linebreaks")

        self.gridLayout_9.addWidget(self.comboBox_fix_linebreaks, 0, 1, 1, 1)

        self.label_song_file_fix_first_words_capitalization = QLabel(self.groupBox_fixes)
        self.label_song_file_fix_first_words_capitalization.setObjectName(u"label_song_file_fix_first_words_capitalization")

        self.gridLayout_9.addWidget(self.label_song_file_fix_first_words_capitalization, 1, 0, 1, 1)

        self.checkBox_fix_first_words_capitalization = QCheckBox(self.groupBox_fixes)
        self.checkBox_fix_first_words_capitalization.setObjectName(u"checkBox_fix_first_words_capitalization")

        self.gridLayout_9.addWidget(self.checkBox_fix_first_words_capitalization, 1, 1, 1, 1)

        self.label_song_file_fix_spaces = QLabel(self.groupBox_fixes)
        self.label_song_file_fix_spaces.setObjectName(u"label_song_file_fix_spaces")

        self.gridLayout_9.addWidget(self.label_song_file_fix_spaces, 2, 0, 1, 1)

        self.comboBox_fix_spaces = QComboBox(self.groupBox_fixes)
        self.comboBox_fix_spaces.setObjectName(u"comboBox_fix_spaces")

        self.gridLayout_9.addWidget(self.comboBox_fix_spaces, 2, 1, 1, 1)

        self.label_song_file_fix_quotation_marks = QLabel(self.groupBox_fixes)
        self.label_song_file_fix_quotation_marks.setObjectName(u"label_song_file_fix_quotation_marks")

        self.gridLayout_9.addWidget(self.label_song_file_fix_quotation_marks, 3, 0, 1, 1)

        self.checkBox_fix_quotation_marks = QCheckBox(self.groupBox_fixes)
        self.checkBox_fix_quotation_marks.setObjectName(u"checkBox_fix_quotation_marks")

        self.gridLayout_9.addWidget(self.checkBox_fix_quotation_marks, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_fixes)

        self.groupBox_cover = QGroupBox(self.tabDownload)
        self.groupBox_cover.setObjectName(u"groupBox_cover")
        sizePolicy1.setHeightForWidth(self.groupBox_cover.sizePolicy().hasHeightForWidth())
        self.groupBox_cover.setSizePolicy(sizePolicy1)
        self.groupBox_cover.setCheckable(True)
        self.gridLayout_4 = QGridLayout(self.groupBox_cover)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_cover_max_size = QLabel(self.groupBox_cover)
        self.label_cover_max_size.setObjectName(u"label_cover_max_size")

        self.gridLayout_4.addWidget(self.label_cover_max_size, 0, 0, 1, 1)

        self.comboBox_cover_max_size = QComboBox(self.groupBox_cover)
        self.comboBox_cover_max_size.setObjectName(u"comboBox_cover_max_size")

        self.gridLayout_4.addWidget(self.comboBox_cover_max_size, 0, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_cover)

        self.groupBox_background = QGroupBox(self.tabDownload)
        self.groupBox_background.setObjectName(u"groupBox_background")
        sizePolicy1.setHeightForWidth(self.groupBox_background.sizePolicy().hasHeightForWidth())
        self.groupBox_background.setSizePolicy(sizePolicy1)
        self.groupBox_background.setCheckable(True)
        self.gridLayout_8 = QGridLayout(self.groupBox_background)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.checkBox_background_always = QCheckBox(self.groupBox_background)
        self.checkBox_background_always.setObjectName(u"checkBox_background_always")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.checkBox_background_always.sizePolicy().hasHeightForWidth())
        self.checkBox_background_always.setSizePolicy(sizePolicy3)
        self.checkBox_background_always.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.checkBox_background_always.setChecked(True)

        self.gridLayout_8.addWidget(self.checkBox_background_always, 0, 1, 1, 1)

        self.label_background_always = QLabel(self.groupBox_background)
        self.label_background_always.setObjectName(u"label_background_always")

        self.gridLayout_8.addWidget(self.label_background_always, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_background)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox_2 = QGroupBox(self.tabDownload)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_10 = QGridLayout(self.groupBox_2)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.label_ytdlp_rate_limit = QLabel(self.groupBox_2)
        self.label_ytdlp_rate_limit.setObjectName(u"label_ytdlp_rate_limit")

        self.gridLayout_10.addWidget(self.label_ytdlp_rate_limit, 1, 0, 1, 1)

        self.comboBox_ytdlp_rate_limit = QComboBox(self.groupBox_2)
        self.comboBox_ytdlp_rate_limit.setObjectName(u"comboBox_ytdlp_rate_limit")

        self.gridLayout_10.addWidget(self.comboBox_ytdlp_rate_limit, 1, 1, 1, 1)

        self.label_throttling_threads = QLabel(self.groupBox_2)
        self.label_throttling_threads.setObjectName(u"label_throttling_threads")

        self.gridLayout_10.addWidget(self.label_throttling_threads, 0, 0, 1, 1)

        self.spinBox_throttling_threads = QSpinBox(self.groupBox_2)
        self.spinBox_throttling_threads.setObjectName(u"spinBox_throttling_threads")
        self.spinBox_throttling_threads.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.spinBox_throttling_threads.setMinimum(0)
        self.spinBox_throttling_threads.setMaximum(32)

        self.gridLayout_10.addWidget(self.spinBox_throttling_threads, 0, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_2)

        self.groupBox_audio = QGroupBox(self.tabDownload)
        self.groupBox_audio.setObjectName(u"groupBox_audio")
        sizePolicy1.setHeightForWidth(self.groupBox_audio.sizePolicy().hasHeightForWidth())
        self.groupBox_audio.setSizePolicy(sizePolicy1)
        self.groupBox_audio.setCheckable(True)
        self.gridLayout_5 = QGridLayout(self.groupBox_audio)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.checkBox_audio_embed_artwork = QCheckBox(self.groupBox_audio)
        self.checkBox_audio_embed_artwork.setObjectName(u"checkBox_audio_embed_artwork")

        self.gridLayout_5.addWidget(self.checkBox_audio_embed_artwork, 3, 3, 1, 1)

        self.label_audio_embed_artwork = QLabel(self.groupBox_audio)
        self.label_audio_embed_artwork.setObjectName(u"label_audio_embed_artwork")

        self.gridLayout_5.addWidget(self.label_audio_embed_artwork, 3, 0, 1, 1)

        self.label_audio_bitrate = QLabel(self.groupBox_audio)
        self.label_audio_bitrate.setObjectName(u"label_audio_bitrate")

        self.gridLayout_5.addWidget(self.label_audio_bitrate, 1, 0, 1, 1)

        self.comboBox_audio_bitrate = QComboBox(self.groupBox_audio)
        self.comboBox_audio_bitrate.setObjectName(u"comboBox_audio_bitrate")

        self.gridLayout_5.addWidget(self.comboBox_audio_bitrate, 1, 3, 1, 1)

        self.label_audio_normalize = QLabel(self.groupBox_audio)
        self.label_audio_normalize.setObjectName(u"label_audio_normalize")

        self.gridLayout_5.addWidget(self.label_audio_normalize, 2, 0, 1, 1)

        self.label_audio_format = QLabel(self.groupBox_audio)
        self.label_audio_format.setObjectName(u"label_audio_format")

        self.gridLayout_5.addWidget(self.label_audio_format, 0, 0, 1, 1)

        self.comboBox_audio_format = QComboBox(self.groupBox_audio)
        self.comboBox_audio_format.setObjectName(u"comboBox_audio_format")
        sizePolicy.setHeightForWidth(self.comboBox_audio_format.sizePolicy().hasHeightForWidth())
        self.comboBox_audio_format.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.comboBox_audio_format, 0, 3, 1, 1)

        self.comboBox_audio_normalization = QComboBox(self.groupBox_audio)
        self.comboBox_audio_normalization.setObjectName(u"comboBox_audio_normalization")

        self.gridLayout_5.addWidget(self.comboBox_audio_normalization, 2, 3, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_audio)

        self.groupBox_video = QGroupBox(self.tabDownload)
        self.groupBox_video.setObjectName(u"groupBox_video")
        sizePolicy1.setHeightForWidth(self.groupBox_video.sizePolicy().hasHeightForWidth())
        self.groupBox_video.setSizePolicy(sizePolicy1)
        self.groupBox_video.setCheckable(True)
        self.gridLayout_6 = QGridLayout(self.groupBox_video)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.groupBox_reencode_video = QGroupBox(self.groupBox_video)
        self.groupBox_reencode_video.setObjectName(u"groupBox_reencode_video")
        sizePolicy1.setHeightForWidth(self.groupBox_reencode_video.sizePolicy().hasHeightForWidth())
        self.groupBox_reencode_video.setSizePolicy(sizePolicy1)
        self.groupBox_reencode_video.setCheckable(True)
        self.groupBox_reencode_video.setChecked(False)
        self.gridLayout_7 = QGridLayout(self.groupBox_reencode_video)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_18 = QLabel(self.groupBox_reencode_video)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_7.addWidget(self.label_18, 0, 0, 1, 1)

        self.comboBox_videoencoder = QComboBox(self.groupBox_reencode_video)
        self.comboBox_videoencoder.setObjectName(u"comboBox_videoencoder")
        sizePolicy2.setHeightForWidth(self.comboBox_videoencoder.sizePolicy().hasHeightForWidth())
        self.comboBox_videoencoder.setSizePolicy(sizePolicy2)

        self.gridLayout_7.addWidget(self.comboBox_videoencoder, 0, 1, 1, 1)


        self.gridLayout_6.addWidget(self.groupBox_reencode_video, 4, 0, 1, 2)

        self.comboBox_fps = QComboBox(self.groupBox_video)
        self.comboBox_fps.setObjectName(u"comboBox_fps")
        sizePolicy2.setHeightForWidth(self.comboBox_fps.sizePolicy().hasHeightForWidth())
        self.comboBox_fps.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_fps, 2, 1, 1, 1)

        self.checkBox_video_embed_artwork = QCheckBox(self.groupBox_video)
        self.checkBox_video_embed_artwork.setObjectName(u"checkBox_video_embed_artwork")

        self.gridLayout_6.addWidget(self.checkBox_video_embed_artwork, 3, 1, 1, 1)

        self.label_video_container = QLabel(self.groupBox_video)
        self.label_video_container.setObjectName(u"label_video_container")

        self.gridLayout_6.addWidget(self.label_video_container, 0, 0, 1, 1)

        self.comboBox_videocontainer = QComboBox(self.groupBox_video)
        self.comboBox_videocontainer.setObjectName(u"comboBox_videocontainer")
        sizePolicy2.setHeightForWidth(self.comboBox_videocontainer.sizePolicy().hasHeightForWidth())
        self.comboBox_videocontainer.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_videocontainer, 0, 1, 1, 1)

        self.label_video_max_fps = QLabel(self.groupBox_video)
        self.label_video_max_fps.setObjectName(u"label_video_max_fps")

        self.gridLayout_6.addWidget(self.label_video_max_fps, 2, 0, 1, 1)

        self.label_video_embed_artwork = QLabel(self.groupBox_video)
        self.label_video_embed_artwork.setObjectName(u"label_video_embed_artwork")

        self.gridLayout_6.addWidget(self.label_video_embed_artwork, 3, 0, 1, 1)

        self.label_video_max_resolution = QLabel(self.groupBox_video)
        self.label_video_max_resolution.setObjectName(u"label_video_max_resolution")

        self.gridLayout_6.addWidget(self.label_video_max_resolution, 1, 0, 1, 1)

        self.comboBox_videoresolution = QComboBox(self.groupBox_video)
        self.comboBox_videoresolution.setObjectName(u"comboBox_videoresolution")
        sizePolicy2.setHeightForWidth(self.comboBox_videoresolution.sizePolicy().hasHeightForWidth())
        self.comboBox_videoresolution.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_videoresolution, 1, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_video)

        self.groupBox_3 = QGroupBox(self.tabDownload)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.groupBox_3.setMinimumSize(QSize(0, 80))
        self.gridLayout_11 = QGridLayout(self.groupBox_3)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.label_discord = QLabel(self.groupBox_3)
        self.label_discord.setObjectName(u"label_discord")

        self.gridLayout_11.addWidget(self.label_discord, 0, 0, 1, 1)

        self.checkBox_discord_allowed = QCheckBox(self.groupBox_3)
        self.checkBox_discord_allowed.setObjectName(u"checkBox_discord_allowed")

        self.gridLayout_11.addWidget(self.checkBox_discord_allowed, 0, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.tabWidget.addTab(self.tabDownload, "")
        self.tabFiles = QWidget()
        self.tabFiles.setObjectName(u"tabFiles")
        self.verticalLayout_4 = QVBoxLayout(self.tabFiles)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox = QGroupBox(self.tabFiles)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.edit_path_template = QLineEdit(self.groupBox)
        self.edit_path_template.setObjectName(u"edit_path_template")
        self.edit_path_template.setMaxLength(100)

        self.horizontalLayout_3.addWidget(self.edit_path_template)

        self.button_default_path_template = QPushButton(self.groupBox)
        self.button_default_path_template.setObjectName(u"button_default_path_template")

        self.horizontalLayout_3.addWidget(self.button_default_path_template)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.comboBox_placeholder = QComboBox(self.groupBox)
        self.comboBox_placeholder.setObjectName(u"comboBox_placeholder")

        self.horizontalLayout_2.addWidget(self.comboBox_placeholder)

        self.button_insert_placeholder = QPushButton(self.groupBox)
        self.button_insert_placeholder.setObjectName(u"button_insert_placeholder")

        self.horizontalLayout_2.addWidget(self.button_insert_placeholder)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout_4.addWidget(self.label)

        self.edit_path_template_result = QLineEdit(self.groupBox)
        self.edit_path_template_result.setObjectName(u"edit_path_template_result")
        self.edit_path_template_result.setReadOnly(True)

        self.horizontalLayout_4.addWidget(self.edit_path_template_result)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.groupBox_4 = QGroupBox(self.tabFiles)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(0, 0))
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.checkBox_trash_files = QCheckBox(self.groupBox_4)
        self.checkBox_trash_files.setObjectName(u"checkBox_trash_files")
        self.checkBox_trash_files.setChecked(True)

        self.verticalLayout_7.addWidget(self.checkBox_trash_files)

        self.checkBox_trash_remotely_deleted_songs = QCheckBox(self.groupBox_4)
        self.checkBox_trash_remotely_deleted_songs.setObjectName(u"checkBox_trash_remotely_deleted_songs")

        self.verticalLayout_7.addWidget(self.checkBox_trash_remotely_deleted_songs)


        self.verticalLayout_4.addWidget(self.groupBox_4)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.tabFiles, "")
        self.tabPaths = QWidget()
        self.tabPaths.setObjectName(u"tabPaths")
        self.verticalLayout_5 = QVBoxLayout(self.tabPaths)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_usdx = QGroupBox(self.tabPaths)
        self.groupBox_usdx.setObjectName(u"groupBox_usdx")
        self.horizontalLayout_5 = QHBoxLayout(self.groupBox_usdx)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(6, 6, 6, 6)
        self.label_usdx = QLabel(self.groupBox_usdx)
        self.label_usdx.setObjectName(u"label_usdx")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_usdx.sizePolicy().hasHeightForWidth())
        self.label_usdx.setSizePolicy(sizePolicy4)
        self.label_usdx.setMinimumSize(QSize(32, 32))
        self.label_usdx.setMaximumSize(QSize(32, 32))
        self.label_usdx.setPixmap(QPixmap(u":/icons/usdx.png"))
        self.label_usdx.setScaledContents(True)

        self.horizontalLayout_5.addWidget(self.label_usdx)

        self.lineEdit_path_usdx = QLineEdit(self.groupBox_usdx)
        self.lineEdit_path_usdx.setObjectName(u"lineEdit_path_usdx")
        self.lineEdit_path_usdx.setReadOnly(True)

        self.horizontalLayout_5.addWidget(self.lineEdit_path_usdx)

        self.pushButton_browse_usdx = QPushButton(self.groupBox_usdx)
        self.pushButton_browse_usdx.setObjectName(u"pushButton_browse_usdx")

        self.horizontalLayout_5.addWidget(self.pushButton_browse_usdx)


        self.verticalLayout_5.addWidget(self.groupBox_usdx)

        self.groupBox_vocaluxe = QGroupBox(self.tabPaths)
        self.groupBox_vocaluxe.setObjectName(u"groupBox_vocaluxe")
        self.horizontalLayout_8 = QHBoxLayout(self.groupBox_vocaluxe)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(6, 6, 6, 6)
        self.label_vocaluxe = QLabel(self.groupBox_vocaluxe)
        self.label_vocaluxe.setObjectName(u"label_vocaluxe")
        sizePolicy4.setHeightForWidth(self.label_vocaluxe.sizePolicy().hasHeightForWidth())
        self.label_vocaluxe.setSizePolicy(sizePolicy4)
        self.label_vocaluxe.setMinimumSize(QSize(32, 32))
        self.label_vocaluxe.setMaximumSize(QSize(32, 32))
        self.label_vocaluxe.setPixmap(QPixmap(u":/icons/vocaluxe.png"))
        self.label_vocaluxe.setScaledContents(True)

        self.horizontalLayout_8.addWidget(self.label_vocaluxe)

        self.lineEdit_path_vocaluxe = QLineEdit(self.groupBox_vocaluxe)
        self.lineEdit_path_vocaluxe.setObjectName(u"lineEdit_path_vocaluxe")
        self.lineEdit_path_vocaluxe.setReadOnly(True)

        self.horizontalLayout_8.addWidget(self.lineEdit_path_vocaluxe)

        self.pushButton_browse_vocaluxe = QPushButton(self.groupBox_vocaluxe)
        self.pushButton_browse_vocaluxe.setObjectName(u"pushButton_browse_vocaluxe")

        self.horizontalLayout_8.addWidget(self.pushButton_browse_vocaluxe)


        self.verticalLayout_5.addWidget(self.groupBox_vocaluxe)

        self.groupBox_performous = QGroupBox(self.tabPaths)
        self.groupBox_performous.setObjectName(u"groupBox_performous")
        self.horizontalLayout_10 = QHBoxLayout(self.groupBox_performous)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(6, 6, 6, 6)
        self.label_performous = QLabel(self.groupBox_performous)
        self.label_performous.setObjectName(u"label_performous")
        sizePolicy4.setHeightForWidth(self.label_performous.sizePolicy().hasHeightForWidth())
        self.label_performous.setSizePolicy(sizePolicy4)
        self.label_performous.setMinimumSize(QSize(32, 32))
        self.label_performous.setMaximumSize(QSize(32, 32))
        self.label_performous.setPixmap(QPixmap(u":/icons/performous.png"))
        self.label_performous.setScaledContents(True)

        self.horizontalLayout_10.addWidget(self.label_performous)

        self.lineEdit_path_performous = QLineEdit(self.groupBox_performous)
        self.lineEdit_path_performous.setObjectName(u"lineEdit_path_performous")
        self.lineEdit_path_performous.setReadOnly(True)

        self.horizontalLayout_10.addWidget(self.lineEdit_path_performous)

        self.pushButton_browse_performous = QPushButton(self.groupBox_performous)
        self.pushButton_browse_performous.setObjectName(u"pushButton_browse_performous")

        self.horizontalLayout_10.addWidget(self.pushButton_browse_performous)


        self.verticalLayout_5.addWidget(self.groupBox_performous)

        self.groupBox_tune_perfect = QGroupBox(self.tabPaths)
        self.groupBox_tune_perfect.setObjectName(u"groupBox_tune_perfect")
        self.horizontalLayout_13 = QHBoxLayout(self.groupBox_tune_perfect)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(6, 6, 6, 6)
        self.label_tune_perfect = QLabel(self.groupBox_tune_perfect)
        self.label_tune_perfect.setObjectName(u"label_tune_perfect")
        sizePolicy4.setHeightForWidth(self.label_tune_perfect.sizePolicy().hasHeightForWidth())
        self.label_tune_perfect.setSizePolicy(sizePolicy4)
        self.label_tune_perfect.setMinimumSize(QSize(32, 32))
        self.label_tune_perfect.setMaximumSize(QSize(32, 32))
        self.label_tune_perfect.setPixmap(QPixmap(u":/icons/tune-perfect.png"))
        self.label_tune_perfect.setScaledContents(True)

        self.horizontalLayout_13.addWidget(self.label_tune_perfect)

        self.lineEdit_path_tune_perfect = QLineEdit(self.groupBox_tune_perfect)
        self.lineEdit_path_tune_perfect.setObjectName(u"lineEdit_path_tune_perfect")
        self.lineEdit_path_tune_perfect.setReadOnly(True)

        self.horizontalLayout_13.addWidget(self.lineEdit_path_tune_perfect)

        self.pushButton_browse_tune_perfect = QPushButton(self.groupBox_tune_perfect)
        self.pushButton_browse_tune_perfect.setObjectName(u"pushButton_browse_tune_perfect")

        self.horizontalLayout_13.addWidget(self.pushButton_browse_tune_perfect)


        self.verticalLayout_5.addWidget(self.groupBox_tune_perfect)

        self.groupBox_ultrastar_manager = QGroupBox(self.tabPaths)
        self.groupBox_ultrastar_manager.setObjectName(u"groupBox_ultrastar_manager")
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_ultrastar_manager)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(6, 6, 6, 6)
        self.label_ultrastar_manager = QLabel(self.groupBox_ultrastar_manager)
        self.label_ultrastar_manager.setObjectName(u"label_ultrastar_manager")
        sizePolicy4.setHeightForWidth(self.label_ultrastar_manager.sizePolicy().hasHeightForWidth())
        self.label_ultrastar_manager.setSizePolicy(sizePolicy4)
        self.label_ultrastar_manager.setMinimumSize(QSize(32, 32))
        self.label_ultrastar_manager.setMaximumSize(QSize(32, 32))
        self.label_ultrastar_manager.setPixmap(QPixmap(u":/icons/ultrastar-manager.png"))
        self.label_ultrastar_manager.setScaledContents(True)

        self.horizontalLayout_9.addWidget(self.label_ultrastar_manager)

        self.lineEdit_path_ultrastar_manager = QLineEdit(self.groupBox_ultrastar_manager)
        self.lineEdit_path_ultrastar_manager.setObjectName(u"lineEdit_path_ultrastar_manager")
        self.lineEdit_path_ultrastar_manager.setReadOnly(True)

        self.horizontalLayout_9.addWidget(self.lineEdit_path_ultrastar_manager)

        self.pushButton_browse_ultrastar_manager = QPushButton(self.groupBox_ultrastar_manager)
        self.pushButton_browse_ultrastar_manager.setObjectName(u"pushButton_browse_ultrastar_manager")

        self.horizontalLayout_9.addWidget(self.pushButton_browse_ultrastar_manager)


        self.verticalLayout_5.addWidget(self.groupBox_ultrastar_manager)

        self.groupBox_yass_reloaded = QGroupBox(self.tabPaths)
        self.groupBox_yass_reloaded.setObjectName(u"groupBox_yass_reloaded")
        self.horizontalLayout_6 = QHBoxLayout(self.groupBox_yass_reloaded)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(6, 6, 6, 6)
        self.label_yass_reloaded = QLabel(self.groupBox_yass_reloaded)
        self.label_yass_reloaded.setObjectName(u"label_yass_reloaded")
        sizePolicy4.setHeightForWidth(self.label_yass_reloaded.sizePolicy().hasHeightForWidth())
        self.label_yass_reloaded.setSizePolicy(sizePolicy4)
        self.label_yass_reloaded.setMinimumSize(QSize(32, 32))
        self.label_yass_reloaded.setMaximumSize(QSize(32, 32))
        self.label_yass_reloaded.setPixmap(QPixmap(u":/icons/yass-reloaded.png"))
        self.label_yass_reloaded.setScaledContents(True)

        self.horizontalLayout_6.addWidget(self.label_yass_reloaded)

        self.lineEdit_path_yass_reloaded = QLineEdit(self.groupBox_yass_reloaded)
        self.lineEdit_path_yass_reloaded.setObjectName(u"lineEdit_path_yass_reloaded")
        self.lineEdit_path_yass_reloaded.setReadOnly(True)

        self.horizontalLayout_6.addWidget(self.lineEdit_path_yass_reloaded)

        self.pushButton_browse_yass_reloaded = QPushButton(self.groupBox_yass_reloaded)
        self.pushButton_browse_yass_reloaded.setObjectName(u"pushButton_browse_yass_reloaded")

        self.horizontalLayout_6.addWidget(self.pushButton_browse_yass_reloaded)


        self.verticalLayout_5.addWidget(self.groupBox_yass_reloaded)

        self.groupBox_karedi = QGroupBox(self.tabPaths)
        self.groupBox_karedi.setObjectName(u"groupBox_karedi")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox_karedi)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(6, 6, 6, 6)
        self.label_karedi = QLabel(self.groupBox_karedi)
        self.label_karedi.setObjectName(u"label_karedi")
        sizePolicy4.setHeightForWidth(self.label_karedi.sizePolicy().hasHeightForWidth())
        self.label_karedi.setSizePolicy(sizePolicy4)
        self.label_karedi.setMinimumSize(QSize(32, 32))
        self.label_karedi.setMaximumSize(QSize(32, 32))
        self.label_karedi.setPixmap(QPixmap(u":/icons/karedi.png"))
        self.label_karedi.setScaledContents(True)

        self.horizontalLayout_7.addWidget(self.label_karedi)

        self.lineEdit_path_karedi = QLineEdit(self.groupBox_karedi)
        self.lineEdit_path_karedi.setObjectName(u"lineEdit_path_karedi")
        self.lineEdit_path_karedi.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.lineEdit_path_karedi)

        self.pushButton_browse_karedi = QPushButton(self.groupBox_karedi)
        self.pushButton_browse_karedi.setObjectName(u"pushButton_browse_karedi")

        self.horizontalLayout_7.addWidget(self.pushButton_browse_karedi)


        self.verticalLayout_5.addWidget(self.groupBox_karedi)

        self.tabWidget.addTab(self.tabPaths, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 2, 2)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Settings", None))
        self.label_theme.setText(QCoreApplication.translate("Dialog", u"Theme:", None))
        self.label_primary_color.setText(QCoreApplication.translate("Dialog", u"Primary color:", None))
        self.label_3.setText("")
        self.checkBox_colored_background.setText(QCoreApplication.translate("Dialog", u"Colored background", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Dialog", u"View", None))
        self.checkBox_auto_update.setText(QCoreApplication.translate("Dialog", u"Automatically update outdated songs", None))
        self.groupBox_login.setTitle(QCoreApplication.translate("Dialog", u"Login cookies (USDB and Youtube)", None))
#if QT_CONFIG(tooltip)
        self.label_login_cookies.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_login_cookies.setText(QCoreApplication.translate("Dialog", u"Browser:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_browser.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Age-restricted videos require a login. Choose the browser you are logged in with, so that the respective cookie can be retrieved automatically.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_songfile.setTitle(QCoreApplication.translate("Dialog", u"Download song file", None))
#if QT_CONFIG(tooltip)
        self.label_song_file_encoding.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_song_file_encoding.setText(QCoreApplication.translate("Dialog", u"Encoding:", None))
        self.label_song_file_line_endings.setText(QCoreApplication.translate("Dialog", u"Line endings:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_encoding.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Choose UTF-8 for USDX, US Play, US Worldparty and Performous.</p><p>Choose UTF-8 BOM for Vocaluxe (Byte Order Mark may cause trouble in some text editors).</p><p>Choose CP1252 for USDX (pre 1.1) and USDX CMD. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBox_line_endings.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>USDX and variants can handle both line ending types, but if you want to edit the song file manually, your editor of choice may require a certain line ending. UNIX users (MacOS, Linux) should generally use LF (line feed). On Windows, some text editors may require CRLF (carriage return, line feed). USDB currently requires CRLF line endings.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_song_file_format_version.setText(QCoreApplication.translate("Dialog", u"Version:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_format_version.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">V1.0.0</span></p><p>Choose this version for highest compatibility. This uses #MP3 to specifiy the audio file.</p><p><span style=\" font-weight:700;\">V1.1.0</span></p><p>This version switches from #MP3 to #AUDIO to underline that other audio formats than mp3 are supported. For compatibility, the Syncer adds both #MP3 and #AUDIO to the text file, which should cause no issues when loading the song.</p><p><span style=\" font-weight:700;\">V1.2.0</span></p><p>This version introduces new tags #AUDIOURL, #COVERURL, #BACKGROUNDURL and #VIDEOURL to specify URLs for the respective sources. The syncer will fill these tags with the contents of the respective metatags, if available.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_fixes.setTitle(QCoreApplication.translate("Dialog", u"Optional song file fixes", None))
        self.label_song_file_fix_linebreaks.setText(QCoreApplication.translate("Dialog", u"Fix linebreaks:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_fix_linebreaks.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>If this setting is enabled, the linebreak timings will be recalculated, either according to USDX or to YASS rules.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_song_file_fix_first_words_capitalization.setText(QCoreApplication.translate("Dialog", u"Fix capitalization:", None))
        self.checkBox_fix_first_words_capitalization.setText("")
        self.label_song_file_fix_spaces.setText(QCoreApplication.translate("Dialog", u"Fix spaces:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_fix_spaces.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>If this setting is enabled, all inter-word spaces will be shifted to either after or before a word.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_song_file_fix_quotation_marks.setText(QCoreApplication.translate("Dialog", u"Fix quotation marks:", None))
        self.checkBox_fix_quotation_marks.setText("")
        self.groupBox_cover.setTitle(QCoreApplication.translate("Dialog", u"Download cover", None))
        self.label_cover_max_size.setText(QCoreApplication.translate("Dialog", u"Max. size:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_cover_max_size.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Images larger than this will be scaled to the set value.</p><p>Some karaoke software variants may have problems displaying covers larger than 1920x1920 pixels.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_background.setTitle(QCoreApplication.translate("Dialog", u"Download background", None))
#if QT_CONFIG(tooltip)
        self.checkBox_background_always.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>If checked, background images will be downloaded even if there is a video for the song as well.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_background_always.setText("")
        self.label_background_always.setText(QCoreApplication.translate("Dialog", u"Even with video:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"Throttling", None))
        self.label_ytdlp_rate_limit.setText(QCoreApplication.translate("Dialog", u"YouTube rate limit:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_ytdlp_rate_limit.setToolTip(QCoreApplication.translate("Dialog", u"Limit YouTube download bandwidth to avoid getting blocked (per thread)", None))
#endif // QT_CONFIG(tooltip)
        self.label_throttling_threads.setText(QCoreApplication.translate("Dialog", u"Download threads:", None))
#if QT_CONFIG(tooltip)
        self.spinBox_throttling_threads.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>0: use default (number of cores)</p><p>Requires restart to take effect.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_audio.setTitle(QCoreApplication.translate("Dialog", u"Download audio", None))
        self.checkBox_audio_embed_artwork.setText("")
        self.label_audio_embed_artwork.setText(QCoreApplication.translate("Dialog", u"Embed artwork:", None))
        self.label_audio_bitrate.setText(QCoreApplication.translate("Dialog", u"Bitrate:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_audio_bitrate.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>If the audio file is reencoded, the selected bitrate will be used.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_audio_normalize.setText(QCoreApplication.translate("Dialog", u"Normalization:", None))
        self.label_audio_format.setText(QCoreApplication.translate("Dialog", u"Format:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_audio_format.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">M4A:</span> Best quality and speed. Compatible with UltraStar Deluxe, Vocaluxe, Performous and UltraStar World Party.</p><p><span style=\" font-weight:700;\">MP3: </span>Worst quality and speed. Full compatibility.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBox_audio_normalization.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>It is recommended to adjust the volume of your audio files so that they all have the same level of perceived loudness.</p><p>If you use a recent version of USDX (2025.4.0 or newer), then choose <span style=\" font-weight:700;\">ReplayGain</span>, as this does not reencode the file but instead writes the normalization information into the audio header. You have to enable ReplayGain in USDX sound settings for this take effect.</p><p>For karaoke softwares that do not (yet) support replay gain, choose <span style=\" font-weight:700;\">Normalize</span>. This will adjust the loudness by re-encoding the file.</p><p>To skip normalization, choose <span style=\" font-weight:700;\">disabled</span>. This saves time, but resulting audio files will have different loudness levels.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_video.setTitle(QCoreApplication.translate("Dialog", u"Download video", None))
#if QT_CONFIG(tooltip)
        self.groupBox_reencode_video.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.groupBox_reencode_video.setTitle(QCoreApplication.translate("Dialog", u"Reencode video", None))
        self.label_18.setText(QCoreApplication.translate("Dialog", u"New format:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_videoencoder.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.comboBox_fps.setToolTip(QCoreApplication.translate("Dialog", u"Maximum frames per second. Lower values reduce file size.", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_video_embed_artwork.setText("")
        self.label_video_container.setText(QCoreApplication.translate("Dialog", u"Container/codec:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_videocontainer.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>For <span style=\" font-weight:700;\">UltraStar deluxe</span>, <span style=\" font-weight:700;\">Performous</span>, <span style=\" font-weight:700;\">Vocaluxe</span> or other ffmpeg-based karaoke softwares, choose &quot;Best available container/codec&quot; or &quot;mp4 (best available codec)&quot; if you prefer to have an mp4 container.</p><p>For <span style=\" font-weight:700;\">UltraStar CMD</span> (Windows), <span style=\" font-weight:700;\">Melody Mania</span> (Windows) and low-power computers, choose &quot;mp4 (AVC/H.264).</p><p>Otherwise, select a container/codec option that your software supports.</p><p>If the selected container/format option is not available for a given song, the syncer will try to at least get the requested container, and if that is not available either, it will fallback to the best available container/codec.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_video_max_fps.setText(QCoreApplication.translate("Dialog", u"Max. FPS:", None))
        self.label_video_embed_artwork.setText(QCoreApplication.translate("Dialog", u"Embed artwork:", None))
        self.label_video_max_resolution.setText(QCoreApplication.translate("Dialog", u"Max. resolution:", None))
#if QT_CONFIG(tooltip)
        self.comboBox_videoresolution.setToolTip(QCoreApplication.translate("Dialog", u"Maximum video height. Lower values reduce file size.", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_3.setTitle(QCoreApplication.translate("Dialog", u"Discord integration for outdated resources", None))
        self.label_discord.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Allow <span style=\" font-style:italic;\">anonymous</span> notifications:</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.checkBox_discord_allowed.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Enabling this will allow reporting unavailable resource \u2013 <span style=\" font-weight:700;\">entirely anonymously</span> \u2013 to our Karaoke Discord channel so that they can be fixed quickly. Please enable this to contribute to the community.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.checkBox_discord_allowed.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDownload), QCoreApplication.translate("Dialog", u"Download", None))
#if QT_CONFIG(tooltip)
        self.groupBox.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>Determines how song files are stored relative to the song directory. You can use certain placeholder names to reference song attributes.</p><p>The template must contain at least two components, which are separated using slashes. The last component specifies the filename, excluding its extension.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Path template", None))
        self.button_default_path_template.setText(QCoreApplication.translate("Dialog", u"Default", None))
        self.button_insert_placeholder.setText(QCoreApplication.translate("Dialog", u"Insert placeholder", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Result:", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("Dialog", u"File cleanup", None))
        self.checkBox_trash_files.setText(QCoreApplication.translate("Dialog", u"When removing files, send them to the trash folder instead.", None))
        self.checkBox_trash_remotely_deleted_songs.setText(QCoreApplication.translate("Dialog", u"On startup, remove songs that have been deleted on USDB.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabFiles), QCoreApplication.translate("Dialog", u"Files", None))
        self.groupBox_usdx.setTitle(QCoreApplication.translate("Dialog", u"UltraStar deluxe", None))
        self.label_usdx.setText("")
        self.pushButton_browse_usdx.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_vocaluxe.setTitle(QCoreApplication.translate("Dialog", u"Vocaluxe", None))
        self.label_vocaluxe.setText("")
        self.pushButton_browse_vocaluxe.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_performous.setTitle(QCoreApplication.translate("Dialog", u"Performous", None))
        self.label_performous.setText("")
        self.pushButton_browse_performous.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_tune_perfect.setTitle(QCoreApplication.translate("Dialog", u"Tune Perfect", None))
        self.label_tune_perfect.setText("")
        self.pushButton_browse_tune_perfect.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_ultrastar_manager.setTitle(QCoreApplication.translate("Dialog", u"UltraStar Manager", None))
        self.label_ultrastar_manager.setText("")
        self.pushButton_browse_ultrastar_manager.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_yass_reloaded.setTitle(QCoreApplication.translate("Dialog", u"YASS reloaded", None))
        self.label_yass_reloaded.setText("")
        self.pushButton_browse_yass_reloaded.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.groupBox_karedi.setTitle(QCoreApplication.translate("Dialog", u"Karedi", None))
        self.label_karedi.setText("")
        self.pushButton_browse_karedi.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPaths), QCoreApplication.translate("Dialog", u"App Paths", None))
    # retranslateUi

