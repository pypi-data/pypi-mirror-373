from pathlib import Path
from typing import TYPE_CHECKING

import lxml.etree as ET

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

if TYPE_CHECKING:
    from excel2moodle.core.question import Question

settings = Settings()

database = QuestionDB(settings)

settings.set(Tags.QUESTIONVARIANT, 1)
database.spreadsheet = Path("test/TestQuestion.ods")
excelFile = settings.get(Tags.SPREADSHEETPATH)
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)


def test_nameOfMCQwithUmlaut() -> None:
    category = database.categories["MC1"]
    database.setupAndParseQuestion(category, 1)
    tree = ET.Element("quiz")
    qlist: list[Question] = [category.questions[1]]
    database._appendQElements(category, qlist, tree, includeHeader=False)
    qEle = tree.find("question")
    name = qEle.find("name").find("text")
    singleAns = qEle.find("single")
    assert singleAns.text == "false"
    assert name.text == "Aufgabe 1ü"


def test_resultValueOfNFMQuestion() -> None:
    category = database.categories["NFM2"]
    database.setupAndParseQuestion(category, 1)
    tree = ET.Element("quiz")
    qlist: list[Question] = []
    qlist.append(category.questions[1])
    print(qlist)
    settings.set(Tags.QUESTIONVARIANT, 1)
    database._appendQElements(category, qlist, tree, includeHeader=False)
    result = tree.find("question").find("answer").find("text")
    assert result.text == "127.0"


def test_settingSpreadsheet() -> None:
    assert isinstance(excelFile, Path)
    assert excelFile.stem == "TestQuestion"
