"""Main Module which does the heavy lifting.

At the heart is the class ``xmlTest``
"""

import datetime as dt
import logging
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as ET  # noqa: N812
import pandas as pd
import yaml
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog

from excel2moodle import __version__
from excel2moodle.core import stringHelpers
from excel2moodle.core.category import Category
from excel2moodle.core.exceptions import InvalidFieldException, QNotParsedException
from excel2moodle.core.globals import Tags
from excel2moodle.core.question import ParametricQuestion, Question
from excel2moodle.core.settings import Settings
from excel2moodle.core.validator import Validator
from excel2moodle.logger import LogAdapterQuestionID
from excel2moodle.question_types import QuestionTypeMapping
from excel2moodle.question_types.cloze import ClozeQuestion, ClozeQuestionParser
from excel2moodle.question_types.mc import MCQuestion, MCQuestionParser
from excel2moodle.question_types.nf import NFQuestion, NFQuestionParser
from excel2moodle.question_types.nfm import NFMQuestion, NFMQuestionParser
from excel2moodle.ui.dialogs import QuestionVariantDialog
from excel2moodle.ui.treewidget import QuestionItem

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

logger = logging.getLogger(__name__)


class QuestionDBSignals(QObject):
    categoryReady = Signal(Category)
    categoryQuestionsReady = Signal(Category)


def processSheet(sheetPath: str, categoryName: str) -> pd.DataFrame:
    """Parse `categoryName` from the file ``sheetPath`` into the dataframe.

    This Function is meant to be run asynchron for increased speed.
    """
    return pd.read_excel(
        Path(sheetPath),
        sheet_name=str(categoryName),
        index_col=0,
        header=None,
        engine="calamine",
    )


class QuestionDB:
    """The QuestionDB is the main class for processing the Spreadsheet.

    It provides the functionality, for setting up the categories and Questions.
    Any interaction with the questions are done by its methods.
    """

    signals = QuestionDBSignals()
    validator: Validator = Validator()
    nfParser: NFQuestionParser = NFQuestionParser()
    nfmParser: NFMQuestionParser = NFMQuestionParser()
    mcParser: MCQuestionParser = MCQuestionParser()
    clozeParser: ClozeQuestionParser = ClozeQuestionParser()

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.window: QMainWindow | None = None
        self.categoriesMetaData: pd.DataFrame
        self.categories: dict[str, Category]
        self._exportedQuestions: list[Question] = []
        self._exportedAll: bool = False

    @property
    def spreadsheet(self) -> Path:
        return self._spreadsheet

    @spreadsheet.setter
    def spreadsheet(self, sheet) -> None:
        self.settings.clear()
        self._spreadsheet = sheet
        self.settings.set(Tags.SPREADSHEETPATH, sheet)
        logger.info("saved new spreadsheet %s", sheet)

    def readCategoriesMetadata(self, sheetPath: Path | None = None) -> pd.DataFrame:
        """Read the metadata and questions from the spreadsheet.

        Get the category data from the spreadsheet and stores it in the
        ``categoriesMetaData`` dataframe
        Setup the categories and store them  in ``self.categories = {}``
        Pass the question data to the categories.

        Raises
        ------
        ValueError
            When there is no 'seetings' worksheet in the file.
        InvalidFieldException
            When the settings are invalid
            Or When the categories Sheet doesn't provide the necessary keys.

        Before raising it logges the exceptions with a meaningful message.

        """
        sheetPath = sheetPath if sheetPath else self.spreadsheet
        logger.info("Start Parsing the Excel Metadata Sheet\n")
        with Path(sheetPath).open("rb") as f:
            settingDf = pd.read_excel(
                f,
                sheet_name="settings",
                index_col=0,
                header=None,
                engine="calamine",
            )
        logger.debug("Found the settings: \n\t%s", settingDf)
        settingDf = self.harmonizeDFIndex(settingDf)
        settingsDict = Validator.dfToDict(settingDf[1])
        Validator.listify(settingsDict)
        for tag, value in settingsDict.items():
            self.settings.set(tag, value)

        self._validateProjectSettings(sheetPath=sheetPath)
        with Path(sheetPath).open("rb") as f:
            self.categoriesMetaData = pd.read_excel(
                f,
                sheet_name=self.settings.get(Tags.CATEGORIESSHEET),
                index_col=0,
                engine="calamine",
            )
        if "description" not in self.categoriesMetaData.columns:
            msg = f"You need to specify the 'description' tag for each category in the sheet '{self.settings.get(Tags.CATEGORIESSHEET)}'."
            raise InvalidFieldException(msg, "0000", "description")
        logger.info("Sucessfully read categoriesMetaData")
        return self.categoriesMetaData

    def _validateProjectSettings(self, sheetPath: Path) -> None:
        if Tags.LOGLEVEL in self.settings:
            level: str = self.settings.get(Tags.LOGLEVEL)
            if level.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR"):
                self.settings.pop(Tags.LOGLEVEL)
                logger.warning("You specified an unsupported Loglevel: %s", level)
        if self.window is not None:
            self.window.logHandler.setLevel(self.settings.get(Tags.LOGLEVEL).upper())
        if Tags.IMPORTMODULE in self.settings:
            logger.warning(
                "Appending: %s to sys.path. All names defined by it will be usable",
                sheetPath.parent,
            )
            sys.path.append(str(sheetPath.parent))
        if Tags.PICTURESUBFOLDER not in self.settings:
            logger.warning("You didn't specify an image Folder. This may cause errors.")
        imgFolder = self.settings.get(Tags.SPREADSHEETPATH).parent / self.settings.get(
            Tags.PICTURESUBFOLDER
        )
        catSheet = self.settings.get(Tags.CATEGORIESSHEET)
        if catSheet not in pd.ExcelFile(sheetPath, engine="calamine").sheet_names:
            msg = f"The specified categories sheet: '{catSheet}' doesn't exist."
            raise InvalidFieldException(msg, "00000", Tags.CATEGORIESSHEET)
        try:
            imgFolder.resolve(strict=True)
        except FileNotFoundError:
            msg = f"Img Path: {imgFolder} could not be found"
            raise InvalidFieldException(msg, "00000", Tags.PICTURESUBFOLDER)
        else:
            self.settings.set(Tags.PICTUREFOLDER, imgFolder.resolve())
            logger.info("Set up the project settings")

    def initAllCategories(self, sheetPath: Path | None = None) -> None:
        """Read all category sheets and initialize all Categories."""
        sheetPath = sheetPath if sheetPath else self.spreadsheet
        if not hasattr(self, "categoriesMetaData"):
            logger.error("Can't process the Categories without Metadata")
            return
        if hasattr(self, "categories"):
            self.categories.clear()
        else:
            self.categories: dict[str, Category] = {}
        with pd.ExcelFile(sheetPath, engine="calamine") as excelFile:
            for categoryName in excelFile.sheet_names:
                logger.debug("Starting to read category %s", categoryName)
                if categoryName in self.categoriesMetaData.index:
                    self.initCategory(categoryName, sheetPath=sheetPath)

    def asyncInitAllCategories(self, sheetPath: Path | None = None) -> None:
        """Read all category sheets asynchron and initialize all Categories.

        It does the same as `initAllCategories` but the parsing of the excelfile
        is done asynchron via `concurrent.futures.ProcessPoolExecutor`
        """
        sheetPath = sheetPath if sheetPath else self.spreadsheet
        if not hasattr(self, "categoriesMetaData"):
            logger.error("Can't process the Categories without Metadata")
            return
        if hasattr(self, "categories"):
            self.categories.clear()
        else:
            self.categories: dict[str, Category] = {}
        sheetNames = []
        with pd.ExcelFile(sheetPath, engine="calamine") as excelFile:
            sheetNames = [
                name
                for name in excelFile.sheet_names
                if name in self.categoriesMetaData.index
            ]
        logger.debug("found those category sheets: \n %s ", sheetNames)
        with ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(processSheet, str(sheetPath), sheet): sheet
                for sheet in sheetNames
            }
            for future in as_completed(futures):
                categoryName = futures[future]
                try:
                    categoryDataF = future.result()
                    self._setupCategory(categoryDataF, categoryName)
                    logger.debug("Finished processing %s", categoryName)
                except Exception as e:
                    logger.exception("Error processing sheet %s: %s", categoryName, e)
                    logger.debug("Future exception: %s", future.exception())

    def initCategory(
        self, categoryName: str, sheetPath: Path | None = None
    ) -> bool | Category:
        """Read `categoryName` from the ``sheetPath`` and initialize the category.
        Returns the Category and appends it to `self.categories`.
        """
        sheetPath = sheetPath if sheetPath else self.spreadsheet
        katDf = pd.read_excel(
            sheetPath,
            sheet_name=str(categoryName),
            index_col=0,
            header=None,
            engine="calamine",
        )
        if not katDf.empty:
            logger.debug("Sucessfully read the Dataframe for cat %s", categoryName)
            return self._setupCategory(katDf, categoryName)
        return False

    @staticmethod
    def harmonizeDFIndex(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Convert the index strings to lowercase without whitespace."""
        index = dataframe.index.str.lower()
        harmonizedIdx = ["".join(i.split()) if pd.notna(i) else i for i in index]
        dataframe.index = pd.Index(harmonizedIdx)
        return dataframe

    def _setupCategory(self, categoryDf: pd.DataFrame, categoryName: str) -> Category:
        """Setup the category from the ``dataframe``.

        :emits: categoryReady(self) Signal.
        """
        categoryDf: pd.DataFrame = self.harmonizeDFIndex(categoryDf)
        categorySettings: dict[str, float | int | str] = self.harmonizeDFIndex(
            self.categoriesMetaData.loc[categoryName]
        ).to_dict()
        nanSettings: list[str] = [
            k for k, v in categorySettings.items() if pd.isna(v) or k not in Tags
        ]
        for na in nanSettings:
            categorySettings.pop(na)
        category = Category(
            categoryName,
            self.categoriesMetaData["description"].loc[categoryName],
            dataframe=categoryDf,
            settings=categorySettings,
        )
        if hasattr(self, "categories"):
            self.categories[categoryName] = category
            self.signals.categoryReady.emit(category)
        else:
            logger.warning("Can't append initialized category to the database")
        logger.debug("Category %s is initialized", categoryName)
        return category

    def parseAllQuestions(self) -> None:
        """Parse all question from all categories.

        The categories need to be initialized first.
        """
        for category in self.categories.values():
            self.parseCategoryQuestions(category)

    def parseCategoryQuestions(self, category: Category) -> None:
        """Parse all questions inside ``category``.

        The category has to be initialized first.
        """
        for qNum in category.dataframe.columns:
            try:
                self.setupAndParseQuestion(category, qNum)
            except (InvalidFieldException, QNotParsedException, AttributeError):
                logger.exception(
                    "Question %s%02d couldn't be parsed. The Question Data: \n %s",
                    category.id,
                    qNum,
                    category.dataframe[qNum],
                )
        self.signals.categoryQuestionsReady.emit(category)

    @classmethod
    def setupAndParseQuestion(cls, category: Category, qNumber: int) -> Question:
        """Check if the Question Data is valid. Then parse it.

        The Question data is accessed from  `category.dataframe` via its number
        First it is checked if all mandatory fields for the given question type
        are provided.
        Then in checks, weather the data has the correct type.
        If the data is valid, the corresponding parser is fed with the data and run.

        Raises
        ------
        QNotParsedException
            If the parsing of the question is not possible this is raised
        InvalidFieldException
            If the data of the question is invalid.
            This gives more information wheather a missing field, or the invalid type
            caused the Exception.

        """
        locallogger = LogAdapterQuestionID(
            logger, {"qID": f"{category.id}{qNumber:02d}"}
        )
        locallogger.debug("Starting to check Validity")
        qdat = category.dataframe[qNumber]
        if not isinstance(qdat, pd.Series):
            locallogger.error("cannot validate data that isn't a pd.Series")
            msg = "cannot validate data that isn't a pd.Series"
            raise QNotParsedException(msg, f"{category.id}{qNumber}")
        cls.validator.setup(qdat, qNumber)
        cls.validator.validate()
        validData = cls.validator.getQuestionData()
        qtype: str = validData.get(Tags.TYPE)
        logger.debug("Question type is: %s", qtype)
        question = QuestionTypeMapping[qtype].create(category, validData)
        if question.isParsed:
            locallogger.info("Question already parsed")
            return question
        if isinstance(question, NFQuestion):
            cls.nfParser.setup(question)
            locallogger.debug("setup a new NF parser ")
            cls.nfParser.parse()
        elif isinstance(question, MCQuestion):
            cls.mcParser.setup(question)
            locallogger.debug("setup a new MC parser ")
            cls.mcParser.parse()
        elif isinstance(question, NFMQuestion):
            cls.nfmParser.setup(question)
            locallogger.debug("setup a new NFM parser ")
            cls.nfmParser.parse()
        elif isinstance(question, ClozeQuestion):
            cls.clozeParser.setup(question)
            locallogger.debug("setup a new CLOZE parser")
            cls.clozeParser.parse()
        else:
            msg = "couldn't setup Parser"
            raise QNotParsedException(msg, question.id)
        category.appendQuestion(qNumber, question)
        return question

    def appendQuestions(
        self,
        questions: list[QuestionItem],
        file: Path | None = None,
        pCount: int = 0,
        qCount: int = 0,
    ) -> None:
        """Append selected question Elements to the tree."""
        self._exportedQuestions.clear()
        tree = ET.Element("quiz")
        catdict: dict[Category, list[Question]] = {}
        for q in questions:
            logger.debug(f"got a question to append {q=}")
            cat = q.parent().category
            if cat not in catdict:
                catdict[cat] = []
            catdict[cat].append(q.question)
        for cat, qlist in catdict.items():
            self._appendQElements(
                cat,
                qlist,
                tree=tree,
                includeHeader=self.settings.get(Tags.INCLUDEINCATS),
            )
        stringHelpers.printDom(tree, file=file)
        if self.settings.get(Tags.GENEXPORTREPORT):
            self.generateExportReport(file, pCount=pCount, qCount=qCount)

    def _appendQElements(
        self,
        cat: Category,
        qList: list[Question],
        tree: ET.Element,
        includeHeader: bool = True,
    ) -> None:
        variant: int = self.settings.get(Tags.QUESTIONVARIANT)
        if includeHeader or variant == -1:
            tree.append(cat.getCategoryHeader())
            logger.debug(f"Appended a new category item {cat=}")
            self._exportedAll: bool = True
        for q in qList:
            if not isinstance(q, ParametricQuestion):
                tree.append(q.getUpdatedElement())
                self._exportedQuestions.append(q)
                continue
            if variant == -1:
                tree.append(cat.getCategoryHeader(subCategory=q.id))
                for var in range(q.parametrics.variants):
                    tree.append(q.getUpdatedElement(variant=var))
            elif variant == 0 or variant > q.parametrics.variants:
                dialog = QuestionVariantDialog(self.window, q)
                if dialog.exec() == QDialog.Accepted:
                    variant = dialog.variant
                    logger.debug("Die Fragen-Variante %s wurde gewählt", variant)
                else:
                    logger.warning("Keine Fragenvariante wurde gewählt.")
                tree.append(q.getUpdatedElement(variant=variant))
            else:
                tree.append(q.getUpdatedElement(variant=variant))
            self._exportedQuestions.append(q)

    def generateExportReport(
        self, file: Path | None = None, pCount: int = 0, qCount: int = 0
    ) -> None:
        """Generate a YAML report of the exported questions."""
        if not self._exportedQuestions:
            return
        if file:
            base_path = file.with_name(f"{file.stem}_export_report.yaml")
        else:
            base_path = self.spreadsheet.parent / "export_report.yaml"

        for i in range(99):
            report_path = base_path.with_name(f"{base_path.stem}-{i:02d}.yaml")
            if not report_path.resolve().exists():
                break

        report_data = {
            "export_metadata": {
                "export_time": dt.datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S"),
                "excel2moodle_version": __version__,
            },
            "categories": {},
        }
        if qCount != 0:
            report_data["export_metadata"]["question_count"] = qCount
        if pCount != 0:
            report_data["export_metadata"]["total_point_count"] = pCount

        sorted_questions = sorted(
            self._exportedQuestions, key=lambda q: (q.category.name, q.id)
        )

        for question in sorted_questions:
            category_name = question.category.name
            if category_name not in report_data["categories"]:
                report_data["categories"][category_name] = {
                    "description": question.category.desc,
                    "questions": [],
                }

            question_data = {"id": question.id, "name": question.name}
            if isinstance(question, ParametricQuestion) and question.currentVariant > 0:
                if self._exportedAll:
                    question_data["exported_variant"] = "all"
                else:
                    question_data["exported_variant"] = question.currentVariant + 1

            report_data["categories"][category_name]["questions"].append(question_data)

        with report_path.open("w") as f:
            yaml.dump(report_data, f, sort_keys=False)
