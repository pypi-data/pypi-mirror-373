"""This Module hosts the various Dialog Classes, that can be shown from main Window."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as ET
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox, QWidget

from excel2moodle import e2mMetadata
from excel2moodle.core.globals import XMLTags
from excel2moodle.core.question import ParametricQuestion, Question
from excel2moodle.core.settings import Tags
from excel2moodle.extra import variableGenerator
from excel2moodle.ui.UI_exportSettingsDialog import Ui_ExportDialog
from excel2moodle.ui.UI_updateDlg import Ui_UpdateDialog
from excel2moodle.ui.UI_variantDialog import Ui_Dialog

if TYPE_CHECKING:
    from excel2moodle.ui.appUi import MainWindow

logger = logging.getLogger(__name__)


class UpdateDialog(QDialog):
    def __init__(
        self, parent: QMainWindow, changelog: str = "", version: str = ""
    ) -> None:
        super().__init__(parent)
        self.ui = Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.ui.changelogBrowser.setMarkdown(changelog)
        self.ui.titleLabel.setText(
            f"<h2>New Version {version} of <i>exel2moodle</i> just dropped!!</h2>"
        )
        self.ui.fundingLabel.setText(
            f'If you find this project useful, please consider supporting its development. <br> <a href="{e2mMetadata["funding"]}">Buy jbosse3 a coffee</a>, so he stays caffeinated during coding.',
        )


class QuestionVariantDialog(QDialog):
    def __init__(self, parent, question: ParametricQuestion) -> None:
        super().__init__(parent)
        self.setWindowTitle("Question Variant Dialog")
        self.maxVal = question.parametrics.variants
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.spinBox.setRange(1, self.maxVal)
        self.ui.catLabel.setText(f"{question.katName}")
        self.ui.qLabel.setText(f"{question.name}")
        self.ui.idLabel.setText(f"{question.id}")

    @property
    def variant(self):
        return self.ui.spinBox.value()

    @property
    def categoryWide(self):
        return self.ui.checkBox.isChecked()


class ExportDialog(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export question Selection")
        self.appUi: MainWindow = parent
        self.ui = Ui_ExportDialog()
        self.ui.setupUi(self)
        self.ui.btnExportFile.clicked.connect(self.getExportFile)
        self.ui.checkBoxExportAll.clicked.connect(self.toggleExportAll)

    @property
    def exportFile(self) -> Path:
        return self._exportFile

    @exportFile.setter
    def exportFile(self, value: Path) -> None:
        self._exportFile = value
        self.ui.btnExportFile.setText(
            f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
        )

    @Slot()
    def toggleExportAll(self) -> None:
        self.ui.spinBoxDefaultQVariant.setEnabled(
            not self.ui.checkBoxExportAll.isChecked()
        )
        self.ui.checkBoxIncludeCategories.setChecked(
            self.ui.checkBoxExportAll.isChecked()
        )

    @Slot()
    def getExportFile(self) -> None:
        path = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            dir=str(self.exportFile),
            filter="xml Files (*.xml)",
        )
        path = Path(path[0])
        if path.is_file():
            self.exportFile = path
            self.ui.btnExportFile.setText(
                f"../{(self.exportFile.parent.name)}/{self.exportFile.name}"
            )
        else:
            logger.warning("No Export File selected")


class QuestionPreview:
    def __init__(self, parent) -> None:
        self.ui = parent.ui
        self.parent = parent

    def _replaceImgPlaceholder(self, elementStr: str) -> str:
        """Replaces '@@PLUGINFILE@@' with the questions Img Folder path."""
        return elementStr.replace(
            "@@PLUGINFILE@@",
            f"{self.pictureFolder}/{self.question.category.NAME}",
        )

    def setupQuestion(self, question: Question) -> None:
        self.pictureFolder = self.parent.settings.get(Tags.PICTUREFOLDER)
        self.ui.previewTextEdit.clear()
        self.question: Question = question
        self.ui.qNameLine.setText(f"{self.question.qtype} - {self.question.name}")
        self.ui.previewTextEdit.append(
            self._replaceImgPlaceholder(
                ET.tostring(self.question.htmlRoot, encoding="unicode")
            )
        )
        self.parent.ui.tableVariables.hide()
        self.setAnswers()

    def setAnswers(self) -> None:
        if isinstance(self.question, ParametricQuestion):
            variableGenerator.populateDataSetTable(
                self.parent.ui.tableVariables, parametrics=self.question.parametrics
            )
            self.parent.ui.tableVariables.show()
        elif self.question.qtype == "NF":
            ans = self.question._element.find(XMLTags.ANSWER)
            self.ui.previewTextEdit.append(f" Result: {ans.find('text').text}")
        elif self.question.qtype == "MC":
            for n, ans in enumerate(self.question._element.findall(XMLTags.ANSWER)):
                self.ui.previewTextEdit.append(
                    f"<b>Answer {n + 1}, Fraction {ans.get('fraction')}:</b>"
                )
                self.ui.previewTextEdit.append(
                    self._replaceImgPlaceholder(ans.find("text").text)
                )


class AboutDialog(QMessageBox):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {e2mMetadata['name']}")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.StandardButton.Close)

        self.aboutMessage: str = f"""
        <h1> About {e2mMetadata["name"]} v{e2mMetadata["version"]}</h1><br>
        <p style="text-align:center">

                <b><a href="{e2mMetadata["homepage"]}">{e2mMetadata["name"]}</a> - {e2mMetadata["description"]}</b>
        </p>
        <p style="text-align:center">
            If you need help you can find some <a href="https://gitlab.com/jbosse3/excel2moodle/-/example/"> examples.</a>
            </br>
            A Documentation can be viewed by clicking "F1",
            or onto the documentation button.
            </br>
        </p>
        <p style="text-align:center">
        To see whats new in version {e2mMetadata["version"]} see the <a href="https://gitlab.com/jbosse3/excel2moodle#changelogs"> changelogs.</a>
        </p>
        <p style="text-align:center">
        This project is maintained by {e2mMetadata["author"]}.
        <br>
        Development takes place at <a href="{e2mMetadata["homepage"]}"> GitLab: {e2mMetadata["homepage"]}</a>
        contributions are very welcome
        </br>
        If you encounter any issues please report them under the <a href="https://gitlab.com/jbosse3/excel2moodle/-/issues/"> repositories issues page </a>.
        </br>
        </p>
        <p style="text-align:center">
        <i>This project is published under {e2mMetadata["license"]}, you are welcome, to share, modify and reuse the code.</i>
        </p>
        """
        self.setText(self.aboutMessage)
