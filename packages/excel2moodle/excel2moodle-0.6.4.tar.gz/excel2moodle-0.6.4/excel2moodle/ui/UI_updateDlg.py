# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'UI_updateDlg.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractScrollArea, QApplication, QDialog,
    QDialogButtonBox, QFrame, QLabel, QSizePolicy,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_UpdateDialog(object):
    def setupUi(self, UpdateDialog):
        if not UpdateDialog.objectName():
            UpdateDialog.setObjectName(u"UpdateDialog")
        UpdateDialog.setWindowModality(Qt.WindowModality.NonModal)
        UpdateDialog.resize(540, 512)
        UpdateDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(UpdateDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.titleLabel = QLabel(UpdateDialog)
        self.titleLabel.setObjectName(u"titleLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.titleLabel)

        self.fundingLabel = QLabel(UpdateDialog)
        self.fundingLabel.setObjectName(u"fundingLabel")
        sizePolicy.setHeightForWidth(self.fundingLabel.sizePolicy().hasHeightForWidth())
        self.fundingLabel.setSizePolicy(sizePolicy)
        self.fundingLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fundingLabel.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.fundingLabel)

        self.line = QFrame(UpdateDialog)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.changelogLabel = QLabel(UpdateDialog)
        self.changelogLabel.setObjectName(u"changelogLabel")
        sizePolicy.setHeightForWidth(self.changelogLabel.sizePolicy().hasHeightForWidth())
        self.changelogLabel.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.changelogLabel)

        self.changelogBrowser = QTextBrowser(UpdateDialog)
        self.changelogBrowser.setObjectName(u"changelogBrowser")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.changelogBrowser.sizePolicy().hasHeightForWidth())
        self.changelogBrowser.setSizePolicy(sizePolicy1)
        self.changelogBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.changelogBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.changelogBrowser.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.verticalLayout.addWidget(self.changelogBrowser)

        self.label = QLabel(UpdateDialog)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)

        self.verticalLayout.addWidget(self.label)

        self.buttonBox = QDialogButtonBox(UpdateDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(UpdateDialog)
        self.buttonBox.accepted.connect(UpdateDialog.accept)
        self.buttonBox.rejected.connect(UpdateDialog.reject)

        QMetaObject.connectSlotsByName(UpdateDialog)
    # setupUi

    def retranslateUi(self, UpdateDialog):
        UpdateDialog.setWindowTitle(QCoreApplication.translate("UpdateDialog", u"Dialog", None))
        self.titleLabel.setText(QCoreApplication.translate("UpdateDialog", u"<h2>A new <i>excel2moodle</i> version is available!</h2>", None))
        self.fundingLabel.setText(QCoreApplication.translate("UpdateDialog", u"If you find this project useful, please consider supporting its development.", None))
        self.changelogLabel.setText(QCoreApplication.translate("UpdateDialog", u"<h3>Changelog:</h3>", None))
        self.label.setText(QCoreApplication.translate("UpdateDialog", u"To install the update execute: 'uv tool upgrade excel2moodle'", None))
    # retranslateUi

