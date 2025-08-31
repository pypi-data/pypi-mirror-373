# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ReportDialog.ui'
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
    QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QRadioButton,
    QSizePolicy, QSpacerItem, QSpinBox, QSplitter,
    QTabWidget, QVBoxLayout, QWidget)
from usdb_syncer.gui.resources.qt import resources as resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(663, 498)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QSize(0, 0))
        self.verticalLayout_5 = QVBoxLayout(Dialog)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_source = QGroupBox(Dialog)
        self.groupBox_source.setObjectName(u"groupBox_source")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_source)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radioButton_locally_available_songs = QRadioButton(self.groupBox_source)
        self.radioButton_locally_available_songs.setObjectName(u"radioButton_locally_available_songs")
        self.radioButton_locally_available_songs.setChecked(True)

        self.verticalLayout_3.addWidget(self.radioButton_locally_available_songs)

        self.radioButton_selected_songs = QRadioButton(self.groupBox_source)
        self.radioButton_selected_songs.setObjectName(u"radioButton_selected_songs")

        self.verticalLayout_3.addWidget(self.radioButton_selected_songs)

        self.radioButton_all_songs = QRadioButton(self.groupBox_source)
        self.radioButton_all_songs.setObjectName(u"radioButton_all_songs")

        self.verticalLayout_3.addWidget(self.radioButton_all_songs)


        self.verticalLayout_5.addWidget(self.groupBox_source)

        self.tabWidget_report_type = QTabWidget(Dialog)
        self.tabWidget_report_type.setObjectName(u"tabWidget_report_type")
        self.tabWidget_report_type.setMinimumSize(QSize(0, 200))
        self.tab_pdf = QWidget()
        self.tab_pdf.setObjectName(u"tab_pdf")
        self.verticalLayout_2 = QVBoxLayout(self.tab_pdf)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(self.tab_pdf)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_columns = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_columns.setObjectName(u"verticalLayout_columns")
        self.verticalLayout_columns.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_columns.addWidget(self.label_7)

        self.optional_columns = QListWidget(self.layoutWidget)
        self.optional_columns.setObjectName(u"optional_columns")

        self.verticalLayout_columns.addWidget(self.optional_columns)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayout_settings = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_settings.setObjectName(u"verticalLayout_settings")
        self.verticalLayout_settings.setContentsMargins(0, 0, 0, 0)
        self.groupBox_page_layout = QGroupBox(self.layoutWidget1)
        self.groupBox_page_layout.setObjectName(u"groupBox_page_layout")
        self.gridLayout = QGridLayout(self.groupBox_page_layout)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_columns = QLabel(self.groupBox_page_layout)
        self.label_columns.setObjectName(u"label_columns")

        self.gridLayout.addWidget(self.label_columns, 3, 0, 1, 1)

        self.label_font_size = QLabel(self.groupBox_page_layout)
        self.label_font_size.setObjectName(u"label_font_size")

        self.gridLayout.addWidget(self.label_font_size, 4, 0, 1, 1)

        self.label_pagesize = QLabel(self.groupBox_page_layout)
        self.label_pagesize.setObjectName(u"label_pagesize")

        self.gridLayout.addWidget(self.label_pagesize, 0, 0, 1, 1)

        self.comboBox_pdf_orientation = QComboBox(self.groupBox_page_layout)
        self.comboBox_pdf_orientation.setObjectName(u"comboBox_pdf_orientation")

        self.gridLayout.addWidget(self.comboBox_pdf_orientation, 1, 1, 1, 1)

        self.spinBox_pdf_font_size = QSpinBox(self.groupBox_page_layout)
        self.spinBox_pdf_font_size.setObjectName(u"spinBox_pdf_font_size")
        self.spinBox_pdf_font_size.setMinimum(7)
        self.spinBox_pdf_font_size.setMaximum(20)
        self.spinBox_pdf_font_size.setValue(10)

        self.gridLayout.addWidget(self.spinBox_pdf_font_size, 4, 1, 1, 1)

        self.spinBox_pdf_columns = QSpinBox(self.groupBox_page_layout)
        self.spinBox_pdf_columns.setObjectName(u"spinBox_pdf_columns")
        self.spinBox_pdf_columns.setMinimum(1)
        self.spinBox_pdf_columns.setMaximum(4)

        self.gridLayout.addWidget(self.spinBox_pdf_columns, 3, 1, 1, 1)

        self.label_orientation = QLabel(self.groupBox_page_layout)
        self.label_orientation.setObjectName(u"label_orientation")

        self.gridLayout.addWidget(self.label_orientation, 1, 0, 1, 1)

        self.comboBox_pdf_pagesize = QComboBox(self.groupBox_page_layout)
        self.comboBox_pdf_pagesize.setObjectName(u"comboBox_pdf_pagesize")

        self.gridLayout.addWidget(self.comboBox_pdf_pagesize, 0, 1, 1, 1)

        self.spinBox_pdf_margin = QSpinBox(self.groupBox_page_layout)
        self.spinBox_pdf_margin.setObjectName(u"spinBox_pdf_margin")
        self.spinBox_pdf_margin.setMinimum(10)
        self.spinBox_pdf_margin.setMaximum(30)
        self.spinBox_pdf_margin.setSingleStep(5)
        self.spinBox_pdf_margin.setValue(20)

        self.gridLayout.addWidget(self.spinBox_pdf_margin, 2, 1, 1, 1)

        self.label_margin = QLabel(self.groupBox_page_layout)
        self.label_margin.setObjectName(u"label_margin")

        self.gridLayout.addWidget(self.label_margin, 2, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 5, 1, 1, 1)


        self.verticalLayout_settings.addWidget(self.groupBox_page_layout)

        self.splitter.addWidget(self.layoutWidget1)

        self.verticalLayout_2.addWidget(self.splitter)

        self.tabWidget_report_type.addTab(self.tab_pdf, "")
        self.tab_json = QWidget()
        self.tab_json.setObjectName(u"tab_json")
        self.verticalLayout_4 = QVBoxLayout(self.tab_json)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_json_indent = QLabel(self.tab_json)
        self.label_json_indent.setObjectName(u"label_json_indent")

        self.horizontalLayout.addWidget(self.label_json_indent)

        self.spinBox_json_indent = QSpinBox(self.tab_json)
        self.spinBox_json_indent.setObjectName(u"spinBox_json_indent")
        self.spinBox_json_indent.setMinimum(2)
        self.spinBox_json_indent.setMaximum(4)
        self.spinBox_json_indent.setSingleStep(2)
        self.spinBox_json_indent.setValue(4)

        self.horizontalLayout.addWidget(self.spinBox_json_indent)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget_report_type.addTab(self.tab_json, "")

        self.verticalLayout_5.addWidget(self.tabWidget_report_type)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_5.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        self.tabWidget_report_type.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"New Report", None))
        self.groupBox_source.setTitle(QCoreApplication.translate("Dialog", u"Source", None))
        self.radioButton_locally_available_songs.setText(QCoreApplication.translate("Dialog", u"Locally available songs", None))
        self.radioButton_selected_songs.setText(QCoreApplication.translate("Dialog", u"Selected songs", None))
        self.radioButton_all_songs.setText(QCoreApplication.translate("Dialog", u"All songs", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"Optional data to include:", None))
        self.groupBox_page_layout.setTitle(QCoreApplication.translate("Dialog", u"PDF Page layout", None))
        self.label_columns.setText(QCoreApplication.translate("Dialog", u"Columns:", None))
        self.label_font_size.setText(QCoreApplication.translate("Dialog", u"Font size:", None))
        self.label_pagesize.setText(QCoreApplication.translate("Dialog", u"Page size:", None))
        self.label_orientation.setText(QCoreApplication.translate("Dialog", u"Orientation:", None))
        self.label_margin.setText(QCoreApplication.translate("Dialog", u"Margins:", None))
        self.tabWidget_report_type.setTabText(self.tabWidget_report_type.indexOf(self.tab_pdf), QCoreApplication.translate("Dialog", u"PDF Report", None))
        self.label_json_indent.setText(QCoreApplication.translate("Dialog", u"Indent:", None))
        self.tabWidget_report_type.setTabText(self.tabWidget_report_type.indexOf(self.tab_json), QCoreApplication.translate("Dialog", u"JSON Report", None))
    # retranslateUi

