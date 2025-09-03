from pathlib import Path

import pytest

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

settings = Settings()
excelFile = Path("test/TestQuestion.ods").resolve()
katName = "NFM2"
database = QuestionDB(settings)

settings.set(Tags.QUESTIONVARIANT, 1)
database.spreadsheet = excelFile
database.readCategoriesMetadata(excelFile)
category = database.initCategory(katName, sheetPath=excelFile)
question = database.setupAndParseQuestion(category=category, qNumber=1)
questionData = question.rawData

CATTOLERANCE = 0.05


@pytest.mark.parametrize(
    ("tag", "expectedType"),
    [
        (Tags.BPOINTS, list),
        (Tags.TEXT, list),
        (Tags.ANSPICWIDTH, int),
        (Tags.POINTS, float),
        (Tags.MEDIASCRIPTS, list),
    ],
)
def test_validatorQuestionDataGeneration(tag, expectedType) -> None:
    assert type(questionData.get(tag)) == expectedType


def test_readOneLenghtListFromSettings() -> None:
    assert len(settings.values[Tags.MEDIASCRIPTS]) == 1
    assert type(settings.values[Tags.MEDIASCRIPTS]) is list


@pytest.mark.parametrize(
    ("tag", "expectedLiteral"),
    [
        (Tags.TYPE, ("MC", "NFM", "CLOZE")),
    ],
)
def test_literalReturs(tag, expectedLiteral) -> None:
    assert questionData.get(tag) in expectedLiteral


def test_ReturnTypeWhileIterating() -> None:
    for tag in Tags:
        if tag.place == "project":
            val = questionData.get(tag)
            if val:
                assert type(val) == tag.typ()


@pytest.mark.parametrize(
    ("tag", "value"),
    [
        (Tags.POINTS, 5.0),
        (Tags.PICTUREWIDTH, 650),
        (Tags.WRONGSIGNPERCENT, 30),
        (Tags.TOLERANCE, CATTOLERANCE),
    ],
)
def test_usageOfCategorySettings(tag, value) -> None:
    assert questionData.get(tag) == value


@pytest.mark.parametrize(
    ("val", "expectation"),
    [
        (-1, CATTOLERANCE),
        (0, CATTOLERANCE),
        (23, 0.23),
        (100, CATTOLERANCE),
    ],
)
def test_manipulateInvaldTolerance(val, expectation) -> None:
    questionData.categoryFallbacks[Tags.TOLERANCE] = val
    assert questionData.get(Tags.TOLERANCE) == expectation
