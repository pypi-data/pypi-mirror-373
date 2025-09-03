"""AppUi holds the extended  class mainWindow() and any other main Windows.

It needs to be seperated from ``windowMain.py`` because that file will be changed by the
``pyside6-uic`` command, which generates the python code from the ``.ui`` file
"""

import logging
from pathlib import Path

from PySide6.QtCore import QRunnable, QSettings, Qt, QThreadPool, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHeaderView,
    QMainWindow,
    QMessageBox,
)

from excel2moodle import e2mMetadata, mainLogger
from excel2moodle.core.category import Category
from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.exceptions import InvalidFieldException
from excel2moodle.core.question import ParametricQuestion
from excel2moodle.core.settings import Settings, Tags
from excel2moodle.extra.variableGenerator import VariableGeneratorDialog
from excel2moodle.logger import LogWindowHandler
from excel2moodle.question_types.mc import MCQuestion
from excel2moodle.question_types.nf import NFQuestion
from excel2moodle.ui import dialogs
from excel2moodle.ui.equationChecker import EqCheckerWindow
from excel2moodle.ui.treewidget import CategoryItem, QuestionItem
from excel2moodle.ui.UI_mainWindow import Ui_MoodleTestGenerator

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, testDB: QuestionDB) -> None:
        super().__init__()
        self.settings = settings
        self.qSettings = QSettings("jbosse3", "excel2moodle")
        self.logHandler = LogWindowHandler()
        mainLogger.addHandler(self.logHandler)
        logger.info("Settings are stored under: %s", self.qSettings.fileName())

        self.excelPath: Path | None = None
        self.mainPath = self.excelPath.parent if self.excelPath is not None else None
        self.exportFile = Path()
        self.testDB = testDB
        self.ui = Ui_MoodleTestGenerator()
        self.ui.setupUi(self)
        self.exportDialog = dialogs.ExportDialog(self)
        self.questionPreview = dialogs.QuestionPreview(self)
        self.eqChecker = EqCheckerWindow()
        self.connectEvents()
        logger.info("Settings are stored under: %s", self.qSettings.fileName())
        self.ui.treeWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.treeWidget.header().setSectionResizeMode(
            QHeaderView.ResizeToContents,
        )
        self.ui.pointCounter.setReadOnly(True)
        self.ui.questionCounter.setReadOnly(True)
        self.setStatus(
            "Wählen Sie eine Excel Tabelle mit den Fragen aus",
        )
        self.threadPool = QThreadPool()
        self._restoreSettings()

    def _restoreSettings(self) -> None:
        """Restore the settings from the last session, if they exist."""
        self.exportDialog.ui.checkBoxIncludeCategories.setChecked(
            self.qSettings.value(Tags.INCLUDEINCATS, defaultValue=True, type=bool)
        )
        variant = self.qSettings.value(Tags.QUESTIONVARIANT, defaultValue=1, type=int)
        if variant == -1:
            self.exportDialog.ui.checkBoxExportAll.setChecked(True)
            self.exportDialog.ui.spinBoxDefaultQVariant.setEnabled(False)
        else:
            self.exportDialog.ui.spinBoxDefaultQVariant.setValue(variant)
        try:
            self.resize(self.qSettings.value("windowSize"))
            self.move(self.qSettings.value("windowPosition"))
        except Exception:
            pass
        if self.qSettings.contains(Tags.SPREADSHEETPATH.full):
            sheet = self.qSettings.value(Tags.SPREADSHEETPATH.full)
            self.setSheetPath(sheet)

    def connectEvents(self) -> None:
        self.ui.treeWidget.itemSelectionChanged.connect(self.onSelectionChanged)
        self.ui.checkBoxQuestionListSelectAll.checkStateChanged.connect(
            self.toggleQuestionSelectionState,
        )
        self.logHandler.emitter.signal.connect(self.updateLog)
        self.ui.actionEquationChecker.triggered.connect(self.openEqCheckerDlg)
        self.ui.actionParseAll.triggered.connect(self.parseSpreadsheetAll)
        self.testDB.signals.categoryQuestionsReady.connect(self.treeRefreshCategory)
        self.ui.actionSpreadsheet.triggered.connect(self.actionSpreadsheet)
        self.ui.actionExport.triggered.connect(self.onButGenTest)
        self.ui.buttonSpreadsheet.clicked.connect(self.actionSpreadsheet)
        self.ui.buttonExport.clicked.connect(self.onButGenTest)
        self.ui.treeWidget.itemClicked.connect(self.updateQuestionPreview)
        self.ui.actionAbout.triggered.connect(self.openAboutDlg)
        self.ui.actionDocumentation.triggered.connect(self.openDocumentation)
        self.ui.actionGenerateVariables.triggered.connect(self.openVariableGeneratorDlg)
        self.ui.actionCopyVariables.triggered.connect(self.copyVariablesToClipboard)
        self.ui.actionOpenSpreadsheetExternal.triggered.connect(
            self.openSpreadsheetExternally
        )

    def showUpdateDialog(self, changelog, version) -> None:
        dialog = dialogs.UpdateDialog(self, changelog=changelog, version=version)
        dialog.exec()

    @Slot()
    def parseSpreadsheetAll(self) -> None:
        """Event triggered by the *Tools/Parse all Questions* Event.

        It parses all the Questions found in the spreadsheet
        and then refreshes the list of questions.
        If successful it prints out a list of all exported Questions
        """
        self.ui.treeWidget.clear()
        process = ParseAllThread(self.testDB, self)
        self.threadPool.start(process)

    def setSheetPath(self, sheet: Path) -> None:
        logger.debug("Received new spreadsheet.")
        if not sheet.is_file():
            logger.warning("Sheet is not a file")
            self.setStatus("[ERROR] keine Tabelle angegeben")
            return
        self.excelPath = sheet
        self.mainPath = sheet.parent
        self.ui.buttonSpreadsheet.setText(f"../{sheet.name}")
        self.testDB.spreadsheet = sheet
        self.qSettings.setValue(Tags.SPREADSHEETPATH.full, sheet)
        self.parseSpreadsheetAll()
        self.setStatus("[OK] Excel Tabelle wurde eingelesen")

    def updateLog(self, log) -> None:
        self.ui.loggerWindow.append(log)

    def closeEvent(self, event) -> None:
        logger.info("Closing. Saving window stats.")
        self.qSettings.setValue("windowSize", self.size())
        self.qSettings.setValue("windowPosition", self.pos())
        self.qSettings.setValue(
            Tags.INCLUDEINCATS, self.settings.get(Tags.INCLUDEINCATS)
        )
        self.qSettings.setValue(
            Tags.QUESTIONVARIANT,
            self.settings.get(Tags.QUESTIONVARIANT),
        )

    @Slot()
    def onSelectionChanged(self, **args) -> None:
        """Whenever the selection changes the total of selected points needs to be recalculated."""
        count: int = 0
        questions: int = 0
        selection = self.ui.treeWidget.selectedItems()
        for q in selection:
            questions += 1
            count += q.question.points
        self.ui.pointCounter.setValue(count)
        self.ui.questionCounter.setValue(questions)
        if self.eqChecker.isVisible():
            self.openEqCheckerDlg()

    @Slot()
    def toggleQuestionSelectionState(self, state) -> None:
        setter = state == Qt.Checked
        root = self.ui.treeWidget.invisibleRootItem()
        childN = root.childCount()
        for i in range(childN):
            qs = root.child(i).childCount()
            for q in range(qs):
                root.child(i).child(q).setSelected(setter)

    @Slot()
    def onButGenTest(self) -> None:
        """Open a file Dialog so the export file may be choosen."""
        selection: list[QuestionItem] = self.ui.treeWidget.selectedItems()
        self.exportDialog.exportFile = Path(self.mainPath / "TestFile.xml")
        qCount = self.ui.questionCounter.value()
        pCount = self.ui.pointCounter.value()
        self.exportDialog.ui.questionCount.setValue(qCount)
        self.exportDialog.ui.pointCount.setValue(pCount)
        if self.exportDialog.exec():
            self.exportFile = self.exportDialog.exportFile
            self.settings.set(
                Tags.INCLUDEINCATS,
                self.exportDialog.ui.checkBoxIncludeCategories.isChecked(),
            )
            self.settings.set(
                Tags.QUESTIONVARIANT,
                -1
                if self.exportDialog.ui.checkBoxExportAll.isChecked()
                else self.exportDialog.ui.spinBoxDefaultQVariant.value(),
            )
            self.settings.set(
                Tags.GENEXPORTREPORT,
                self.exportDialog.ui.checkBoxGenerateReport.isChecked(),
            )
            logger.info("New Export File is set %s", self.exportFile)
            self.testDB.appendQuestions(
                selection, self.exportFile, pCount=pCount, qCount=qCount
            )
        else:
            logger.info("Aborting Export")

    @Slot()
    def actionSpreadsheet(self) -> None:
        file = QFileDialog.getOpenFileName(
            self,
            self.tr("Open Spreadsheet"),
            dir=str(self.mainPath),
            filter=self.tr("Spreadsheet(*.xlsx *.ods)"),
            selectedFilter=("*.ods"),
        )
        path = Path(file[0]).resolve(strict=True)
        self.setSheetPath(path)

    @Slot(Category)
    def treeRefreshCategory(self, cat: Category) -> None:
        """Append Category with its Questions to the treewidget.

        If the category already has an item, refresh it.
        """
        # Find existing item
        for i in range(self.ui.treeWidget.topLevelItemCount()):
            item = self.ui.treeWidget.topLevelItem(i)
            # The top level items are categories
            if isinstance(item, CategoryItem) and item.category.NAME == cat.NAME:
                item.refresh()
                return

        catItem = CategoryItem(self.ui.treeWidget, cat)
        catItem.setFlags(catItem.flags() & ~Qt.ItemIsSelectable)
        try:
            for q in cat.questions.values():
                QuestionItem(catItem, q)
        except ValueError:
            logger.exception("No Questions to update.")
        catItem.updateVariantCount()
        self.ui.treeWidget.sortItems(0, Qt.SortOrder.AscendingOrder)

    @Slot()
    def updateQuestionPreview(self) -> None:
        item = self.ui.treeWidget.currentItem()
        if isinstance(item, QuestionItem):
            self.questionPreview.setupQuestion(item.question)
        else:
            logger.info("current Item is not a Question, can't preview")

    def setStatus(self, status) -> None:
        self.ui.statusbar.clearMessage()
        self.ui.statusbar.showMessage(self.tr(status))

    @Slot()
    def openEqCheckerDlg(self) -> None:
        item = self.ui.treeWidget.currentItem()
        if isinstance(item, QuestionItem):
            question = item.question
            if isinstance(question, (NFQuestion, MCQuestion)):
                logger.debug("Can't check an MC or NF Question")
            else:
                logger.debug("opening wEquationChecker \n")
                self.eqChecker.setup(item.question)
                self.eqChecker.show()
        else:
            logger.debug("No Question Item selected: %s", type(item))

    @Slot()
    def openAboutDlg(self) -> None:
        about = dialogs.AboutDialog(self)
        about.exec()

    @Slot()
    def openDocumentation(self) -> None:
        url = QUrl(e2mMetadata["documentation"])
        logger.info("Opening documentation in your Webbrowser...%s", url)
        QDesktopServices.openUrl(url)

    @Slot()
    def openVariableGeneratorDlg(self) -> None:
        item = self.ui.treeWidget.currentItem()
        if isinstance(item, QuestionItem):
            question = item.question
            if isinstance(question, ParametricQuestion):
                dialog = VariableGeneratorDialog(self, parametrics=question.parametrics)
                if dialog.exec():
                    self.questionPreview.setupQuestion(question)
                    self.treeRefreshCategory(question.category)
                    logger.info("Updated QuestionItem display for %s", question.id)
                    self.copyVariablesToClipboard(
                        variables=question.parametrics.variables
                    )
                else:
                    logger.warning("No variable sets were generated.")
            else:
                logger.info("Selected item is not a ParametricQuestion.")
        else:
            logger.info("No Question Item selected.")

    @Slot()
    def copyVariablesToClipboard(
        self, variables: dict[str, list[float | int]] | None = None
    ) -> None:
        if variables is None:
            variables = {}
        if not variables:
            item = self.ui.treeWidget.currentItem()
            if isinstance(item, QuestionItem):
                question = item.question
                if isinstance(question, ParametricQuestion):
                    variables = question.parametrics.variables
        varsList = [
            f"{name}\t{';    '.join(map(str, vals))}"
            for name, vals in variables.items()
        ]
        clipb = QApplication.clipboard()
        variablesStr = "\n".join(varsList)
        clipb.setText(variablesStr)
        logger.info("Copied all variables to the clipboard")
        QMessageBox.information(
            self,
            "Variables Copied.",
            """All variables from the parametric Question are saved to the system clipboard.\n
            You can paste them into the spreadsheet.
            Make sure to import them with 'Tab' as the seperator.""",
        )

    @Slot()
    def openSpreadsheetExternally(self) -> None:
        if self.excelPath is None:
            return
        spreadsheetPath = QUrl(f"file://{self.excelPath.resolve()}")
        logger.info("Opening: %s", spreadsheetPath)
        QDesktopServices.openUrl(spreadsheetPath)


class ParseAllThread(QRunnable):
    """Parse the whole Spreadsheet.
    Start by reading the spreadsheet asynchron.
    When finished parse all Categories subsequently.
    """

    def __init__(self, questionDB: QuestionDB, mainApp: MainWindow) -> None:
        super().__init__()
        self.testDB = questionDB
        self.mainApp = mainApp

    @Slot()
    def run(self) -> None:
        try:
            self.testDB.readCategoriesMetadata()
        except InvalidFieldException:
            logger.exception("Youre spreadsheet questionbank isn't correctly setup.")
        except ValueError:
            logger.exception(
                "Did you forget to specify a 'settings' sheet in the file?"
            )
        else:
            self.testDB.asyncInitAllCategories(self.mainApp.excelPath)
            self.mainApp.setStatus("[OK] Tabellen wurde eingelesen")
            self.testDB.parseAllQuestions()
