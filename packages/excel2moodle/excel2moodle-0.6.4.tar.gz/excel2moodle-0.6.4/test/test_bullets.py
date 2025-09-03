from pathlib import Path

import pytest

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.settings import Settings, Tags

settings = Settings()

katName = "NFM2"
database = QuestionDB(settings)

settings.set(Tags.QUESTIONVARIANT, 1)
database.spreadsheet = Path("test/TestQuestion.ods")
excelFile = settings.get(Tags.SPREADSHEETPATH)
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)
category = database.categories[katName]


@pytest.mark.parametrize(("qnum", "bnames"), [(1, ["a", "b", "x", "F", "p"])])
def test_bulletVarnames(qnum: int, bnames: list[str]) -> None:
    question = database.setupAndParseQuestion(category, qnum)
    assert question.bulletList.varNames == bnames


@pytest.mark.parametrize(
    ("variant", "bulletName", "bulletStr"),
    [
        (1, "F", r"Kraft \(F = 25,\!0 \mathrm{ kN }\)"),
        (2, "F", r"Kraft \(F = 22,\!0 \mathrm{ kN }\)"),
        (3, "F", r"Kraft \(F = 16,\!0 \mathrm{ kN }\)"),
        (1, "p", r"Streckenlast \(p = 19,\!0 \mathrm{ kN/m }\)"),
        (2, "p", r"Streckenlast \(p = 15,\!0 \mathrm{ kN/m }\)"),
        (3, "p", r"Streckenlast \(p = 13,\!0 \mathrm{ kN/m }\)"),
        (1, "x", r"Strecke \(x = 3,\!0 \mathrm{ m }\)"),
        (2, "x", r"Strecke \(x = 2,\!0 \mathrm{ m }\)"),
        (3, "x", r"Strecke \(x = 1,\!5 \mathrm{ m }\)"),
    ],
)
def test_bulletVariants(variant, bulletName, bulletStr) -> None:
    question = database.setupAndParseQuestion(category, 1)
    question.getUpdatedElement(variant=variant)
    for bullet in question.bulletList.bullets[bulletName].element:
        assert bullet == bulletStr
