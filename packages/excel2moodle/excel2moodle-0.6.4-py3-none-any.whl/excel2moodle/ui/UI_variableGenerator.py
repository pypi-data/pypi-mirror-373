# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_variableGenerator.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QDialog,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_VariableGeneratorDialog(object):
    def setupUi(self, VariableGeneratorDialog):
        if not VariableGeneratorDialog.objectName():
            VariableGeneratorDialog.setObjectName(u"VariableGeneratorDialog")
        VariableGeneratorDialog.resize(604, 634)
        self.verticalLayout = QVBoxLayout(VariableGeneratorDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_existing_variables = QGroupBox(VariableGeneratorDialog)
        self.groupBox_existing_variables.setObjectName(u"groupBox_existing_variables")
        self.groupBox_existing_variables.setCheckable(True)
        self.groupBox_existing_variables.setChecked(False)
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_existing_variables)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tableWidget_existing_variables = QTableWidget(self.groupBox_existing_variables)
        if (self.tableWidget_existing_variables.columnCount() < 1):
            self.tableWidget_existing_variables.setColumnCount(1)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_existing_variables.setHorizontalHeaderItem(0, __qtablewidgetitem)
        self.tableWidget_existing_variables.setObjectName(u"tableWidget_existing_variables")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget_existing_variables.sizePolicy().hasHeightForWidth())
        self.tableWidget_existing_variables.setSizePolicy(sizePolicy)
        self.tableWidget_existing_variables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableWidget_existing_variables.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.verticalLayout_4.addWidget(self.tableWidget_existing_variables)


        self.verticalLayout.addWidget(self.groupBox_existing_variables)

        self.groupBox_variables = QGroupBox(VariableGeneratorDialog)
        self.groupBox_variables.setObjectName(u"groupBox_variables")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_variables)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tableWidget_variables = QTableWidget(self.groupBox_variables)
        if (self.tableWidget_variables.columnCount() < 4):
            self.tableWidget_variables.setColumnCount(4)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_variables.setHorizontalHeaderItem(0, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_variables.setHorizontalHeaderItem(1, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_variables.setHorizontalHeaderItem(2, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_variables.setHorizontalHeaderItem(3, __qtablewidgetitem4)
        self.tableWidget_variables.setObjectName(u"tableWidget_variables")
        sizePolicy.setHeightForWidth(self.tableWidget_variables.sizePolicy().hasHeightForWidth())
        self.tableWidget_variables.setSizePolicy(sizePolicy)
        self.tableWidget_variables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout_2.addWidget(self.tableWidget_variables)


        self.verticalLayout.addWidget(self.groupBox_variables)

        self.groupBox_rules = QGroupBox(VariableGeneratorDialog)
        self.groupBox_rules.setObjectName(u"groupBox_rules")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_rules)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidget_rules = QListWidget(self.groupBox_rules)
        self.listWidget_rules.setObjectName(u"listWidget_rules")
        self.listWidget_rules.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout_3.addWidget(self.listWidget_rules)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_newRule = QLineEdit(self.groupBox_rules)
        self.lineEdit_newRule.setObjectName(u"lineEdit_newRule")

        self.horizontalLayout.addWidget(self.lineEdit_newRule)

        self.pushButton_addRule = QPushButton(self.groupBox_rules)
        self.pushButton_addRule.setObjectName(u"pushButton_addRule")

        self.horizontalLayout.addWidget(self.pushButton_addRule)

        self.pushButton_removeRule = QPushButton(self.groupBox_rules)
        self.pushButton_removeRule.setObjectName(u"pushButton_removeRule")

        self.horizontalLayout.addWidget(self.pushButton_removeRule)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBox_rules)

        self.groupBox_generated_variables = QGroupBox(VariableGeneratorDialog)
        self.groupBox_generated_variables.setObjectName(u"groupBox_generated_variables")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_generated_variables)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.tableWidget_generated_variables = QTableWidget(self.groupBox_generated_variables)
        self.tableWidget_generated_variables.setObjectName(u"tableWidget_generated_variables")
        sizePolicy.setHeightForWidth(self.tableWidget_generated_variables.sizePolicy().hasHeightForWidth())
        self.tableWidget_generated_variables.setSizePolicy(sizePolicy)
        self.tableWidget_generated_variables.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.tableWidget_generated_variables.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.verticalLayout_5.addWidget(self.tableWidget_generated_variables)


        self.verticalLayout.addWidget(self.groupBox_generated_variables)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_numSets = QLabel(VariableGeneratorDialog)
        self.label_numSets.setObjectName(u"label_numSets")

        self.horizontalLayout_2.addWidget(self.label_numSets)

        self.spinBox_numSets = QSpinBox(VariableGeneratorDialog)
        self.spinBox_numSets.setObjectName(u"spinBox_numSets")
        self.spinBox_numSets.setMinimum(1)
        self.spinBox_numSets.setMaximum(1000)
        self.spinBox_numSets.setValue(10)

        self.horizontalLayout_2.addWidget(self.spinBox_numSets)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton_generate = QPushButton(VariableGeneratorDialog)
        self.pushButton_generate.setObjectName(u"pushButton_generate")

        self.horizontalLayout_2.addWidget(self.pushButton_generate)

        self.pushButton_save = QPushButton(VariableGeneratorDialog)
        self.pushButton_save.setObjectName(u"pushButton_save")

        self.horizontalLayout_2.addWidget(self.pushButton_save)

        self.pushButton_cancel = QPushButton(VariableGeneratorDialog)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")

        self.horizontalLayout_2.addWidget(self.pushButton_cancel)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(VariableGeneratorDialog)

        QMetaObject.connectSlotsByName(VariableGeneratorDialog)
    # setupUi

    def retranslateUi(self, VariableGeneratorDialog):
        VariableGeneratorDialog.setWindowTitle(QCoreApplication.translate("VariableGeneratorDialog", u"Variable Set Generator", None))
        self.groupBox_existing_variables.setTitle(QCoreApplication.translate("VariableGeneratorDialog", u"Existing Variable Sets", None))
        ___qtablewidgetitem = self.tableWidget_existing_variables.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Variable", None));
        self.groupBox_variables.setTitle(QCoreApplication.translate("VariableGeneratorDialog", u"Variable Constraints (Min/Max)", None))
        ___qtablewidgetitem1 = self.tableWidget_variables.horizontalHeaderItem(0)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Variable", None));
        ___qtablewidgetitem2 = self.tableWidget_variables.horizontalHeaderItem(1)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Min", None));
        ___qtablewidgetitem3 = self.tableWidget_variables.horizontalHeaderItem(2)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Max", None));
        ___qtablewidgetitem4 = self.tableWidget_variables.horizontalHeaderItem(3)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Decimal Places", None));
        self.groupBox_rules.setTitle(QCoreApplication.translate("VariableGeneratorDialog", u"Inter-Variable Rules", None))
        self.lineEdit_newRule.setPlaceholderText(QCoreApplication.translate("VariableGeneratorDialog", u"e.g., a < b * 2 or c >= a + b", None))
        self.pushButton_addRule.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Add Rule", None))
        self.pushButton_removeRule.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Remove Selected", None))
        self.groupBox_generated_variables.setTitle(QCoreApplication.translate("VariableGeneratorDialog", u"Generated Variable Sets (Preview)", None))
        self.label_numSets.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Number of Sets to Generate:", None))
        self.pushButton_generate.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Preview", None))
        self.pushButton_save.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Save Variables", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("VariableGeneratorDialog", u"Cancel", None))
    # retranslateUi

