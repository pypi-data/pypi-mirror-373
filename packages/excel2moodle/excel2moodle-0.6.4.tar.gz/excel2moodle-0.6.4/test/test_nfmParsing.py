import re
from pathlib import Path

import lxml.etree as ET
import pytest

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

settings = Settings()

katName = "NFM2"
database = QuestionDB(settings)
excelFile = Path("test/TestQuestion.ods")
database.spreadsheet = excelFile
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)
nfmCategory = database.categories[katName]
database.parseCategoryQuestions(nfmCategory)


@pytest.mark.parametrize(
    ("variant", "result"),
    [
        (1, 127.0),
        (2, 153.571),
        (3, 74.375),
    ],
)
def test_resultValueOfNFMQuestion(variant, result) -> None:
    question = database.setupAndParseQuestion(nfmCategory, 1)
    question.getUpdatedElement(variant=variant)
    givenTolerance = question.rawData.get(Tags.TOLERANCE)
    tree = ET.Element("quiz")
    tree.append(question._element)
    answers = tree.find("question").findall("answer")
    tolerance = answers[0].find("tolerance")
    ansval = answers[0].find("text")
    ansvalInverted = answers[1].find("text")
    assert ansval.text == str(result)
    assert ansvalInverted.text == str(result * (-1))
    assert tolerance.text == str(round(result * givenTolerance, 3))


@pytest.mark.parametrize(
    ("variant", "result"),
    [
        (1, 127.0),
        (2, 153.571),
        (3, 74.375),
    ],
)
def test_invertedResult(variant, result) -> None:
    for qNum, question in nfmCategory.questions.items():
        question.getUpdatedElement(variant=variant)
        givenTolerance = question.rawData.get(Tags.TOLERANCE)
        givenWrongSignPercent = question.rawData.get(Tags.WRONGSIGNPERCENT)
        tree = ET.Element("quiz")
        tree.append(question._element)
        answers = tree.find("question").findall("answer")
        ansvalInverted = answers[1].find("text")
        wrongSignPercent = answers[1].get("fraction")
        print(f"Testing Question {qNum}")
        print("Wrong Answer is:")
        ET.dump(answers[1])
        assert wrongSignPercent == str(givenWrongSignPercent)
        assert ansvalInverted.text == str(result * (-1))


@pytest.mark.parametrize(
    ("variant", "bullets"),
    [
        (1, [5, 7, 3, 25, 19]),
        (2, [7, 5, 2, 22, 15]),
        (3, [4, 5, 1.5, 16, 13]),
        pytest.param(3, [2, 5, 1.6, 16, 13], marks=pytest.mark.xfail),
        pytest.param(2, [5, 7, 3, 25, 19], marks=pytest.mark.xfail),
    ],
)
def test_bulletValueAccordingToResult(variant, bullets) -> None:
    question = database.setupAndParseQuestion(nfmCategory, 1)
    qEle = question.getUpdatedElement(variant=variant)
    qtext = qEle.find("questiontext").find("text")
    textStr = f"<root>{qtext.text}</root>"
    textTree = ET.XML(textStr, ET.XMLParser(remove_blank_text=True))
    ulist = textTree.find("div").find("ul")
    items = ulist.findall("li")
    for it, bullet in zip(items, bullets, strict=False):
        val = re.findall(r"=\s(\d+,\\!\d+)\s\\mathrm", it.text)
        val = val[0].replace(r",\!", ".")
        assert float(val) == bullet


@pytest.mark.parametrize(
    ("variant", "result"),
    [
        (1, "127.0"),
        (2, "153.571"),
        (3, "74.375"),
    ],
)
def test_calculatWithImportModule(variant, result) -> None:
    question = database.setupAndParseQuestion(nfmCategory, 3)
    question.getUpdatedElement(variant=variant)
    tree = ET.Element("quiz")
    tree.append(question._element)
    answer = tree.find("question").find("answer")
    tolerance = answer.find("tolerance")
    ansval = answer.find("text")
    tol = question.rawData.get(Tags.TOLERANCE)
    assert ansval.text == result
    assert tolerance.text == str(round(float(result) * tol, 3))
