# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'regeltest_save.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect,
                            Qt)
from PySide6.QtWidgets import (QDialogButtonBox,
                               QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
                               QSpinBox, QWidget)


class Ui_RegeltestSave(object):
    def setupUi(self, RegeltestSave):
        if not RegeltestSave.objectName():
            RegeltestSave.setObjectName(u"RegeltestSave")
        RegeltestSave.resize(760, 542)
        RegeltestSave.setFocusPolicy(Qt.NoFocus)
        self.gridLayout = QGridLayout(RegeltestSave)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_3 = QWidget(RegeltestSave)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setFocusPolicy(Qt.StrongFocus)
        self.horizontalLayout_3 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.title_edit = QLineEdit(self.widget_3)
        self.title_edit.setObjectName(u"title_edit")

        self.horizontalLayout_3.addWidget(self.title_edit)

        self.gridLayout.addWidget(self.widget_3, 0, 2, 1, 1)

        self.label = QLabel(RegeltestSave)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.widget_2 = QWidget(RegeltestSave)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.output_edit = QLineEdit(self.widget_2)
        self.output_edit.setObjectName(u"output_edit")

        self.horizontalLayout_2.addWidget(self.output_edit)

        self.output_edit_button = QPushButton(self.widget_2)
        self.output_edit_button.setObjectName(u"output_edit_button")

        self.horizontalLayout_2.addWidget(self.output_edit_button)

        self.gridLayout.addWidget(self.widget_2, 3, 2, 1, 1)

        self.buttonBox = QDialogButtonBox(RegeltestSave)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 3)

        self.label_3 = QLabel(RegeltestSave)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.scrollArea = QScrollArea(RegeltestSave)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.question_scrollable = QWidget()
        self.question_scrollable.setObjectName(u"question_scrollable")
        self.question_scrollable.setGeometry(QRect(0, 0, 740, 142))
        self.scrollArea.setWidget(self.question_scrollable)

        self.gridLayout.addWidget(self.scrollArea, 8, 0, 1, 3)

        self.label_2 = QLabel(RegeltestSave)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.activate_mc_button = QPushButton(RegeltestSave)
        self.activate_mc_button.setObjectName(u"activate_mc_button")

        self.horizontalLayout_4.addWidget(self.activate_mc_button)

        self.deactivate_mc_button = QPushButton(RegeltestSave)
        self.deactivate_mc_button.setObjectName(u"deactivate_mc_button")

        self.horizontalLayout_4.addWidget(self.deactivate_mc_button)

        self.gridLayout.addLayout(self.horizontalLayout_4, 6, 0, 1, 3)

        self.fontsize_spinBox = QSpinBox(RegeltestSave)
        self.fontsize_spinBox.setObjectName(u"fontsize_spinBox")
        self.fontsize_spinBox.setMinimum(9)
        self.fontsize_spinBox.setMaximum(15)
        self.fontsize_spinBox.setValue(11)

        self.gridLayout.addWidget(self.fontsize_spinBox, 4, 2, 1, 1)

        self.widget = QWidget(RegeltestSave)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.icon_path_edit = QLineEdit(self.widget)
        self.icon_path_edit.setObjectName(u"icon_path_edit")

        self.horizontalLayout.addWidget(self.icon_path_edit)

        self.icon_edit_button = QPushButton(self.widget)
        self.icon_edit_button.setObjectName(u"icon_edit_button")

        self.horizontalLayout.addWidget(self.icon_edit_button)

        self.gridLayout.addWidget(self.widget, 1, 2, 1, 1)

        self.label_4 = QLabel(RegeltestSave)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 0, 1, 1)

        QWidget.setTabOrder(self.title_edit, self.icon_path_edit)
        QWidget.setTabOrder(self.icon_path_edit, self.icon_edit_button)
        QWidget.setTabOrder(self.icon_edit_button, self.output_edit)
        QWidget.setTabOrder(self.output_edit, self.output_edit_button)
        QWidget.setTabOrder(self.output_edit_button, self.widget_3)

        self.retranslateUi(RegeltestSave)
        self.buttonBox.accepted.connect(RegeltestSave.accept)
        self.buttonBox.rejected.connect(RegeltestSave.reject)
        RegeltestSave.windowTitleChanged.connect(self.title_edit.setFocus)

        QMetaObject.connectSlotsByName(RegeltestSave)
    # setupUi

    def retranslateUi(self, RegeltestSave):
        RegeltestSave.setWindowTitle(QCoreApplication.translate("RegeltestSave", u"Save Regeltest", None))
        self.label.setText(QCoreApplication.translate("RegeltestSave", u"Titel", None))
        self.output_edit_button.setText(QCoreApplication.translate("RegeltestSave", u"Ausw\u00e4hlen", None))
        self.label_3.setText(QCoreApplication.translate("RegeltestSave", u"Speicherort", None))
        self.label_2.setText(QCoreApplication.translate("RegeltestSave", u"Iconpfad", None))
        self.activate_mc_button.setText(
            QCoreApplication.translate("RegeltestSave", u"Alle Multiple-Choice aktivieren", None))
        self.deactivate_mc_button.setText(
            QCoreApplication.translate("RegeltestSave", u"Alle Multiple-Choice deaktivieren", None))
        self.fontsize_spinBox.setSuffix(QCoreApplication.translate("RegeltestSave", u" pt", None))
        self.icon_edit_button.setText(QCoreApplication.translate("RegeltestSave", u"Ausw\u00e4hlen", None))
        self.label_4.setText(QCoreApplication.translate("RegeltestSave", u"Schriftgr\u00f6\u00dfe", None))
    # retranslateUi

