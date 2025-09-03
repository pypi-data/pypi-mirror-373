from pathlib import Path

import lxml.etree as ET
import pytest

from excel2moodle.core.dataStructure import QuestionDB
from excel2moodle.core.globals import XMLTags
from excel2moodle.core.settings import Settings, Tags

settings = Settings()

database = QuestionDB(settings)
excelFile = Path("test/TestQuestion.ods")
database.spreadsheet = excelFile
database.readCategoriesMetadata(excelFile)
database.initAllCategories(excelFile)
mcCategory = database.categories["MC1"]
nfmCategory = database.categories["NFM2"]
nfCategory = database.categories["NF3"]
database.parseCategoryQuestions(mcCategory)
database.parseCategoryQuestions(nfmCategory)
database.parseCategoryQuestions(nfCategory)


@pytest.mark.parametrize(
    ("feedbackTag", "feedbackValue"),
    [
        (XMLTags.CORFEEDB, Tags.TRUEFB),
        (XMLTags.INCORFEEDB, Tags.FALSEFB),
        (XMLTags.PCORFEEDB, Tags.PCORRECFB),
    ],
)
def test_mcFeedbacks(feedbackTag: XMLTags, feedbackValue: Tags) -> None:
    for question in mcCategory.questions.values():
        question.getUpdatedElement()
        tree = ET.Element("quiz")
        tree.append(question._element)
        feedback = tree.find("question").find(feedbackTag)
        feedbackTree = ET.fromstring(feedback.find("text").text)
        assert feedbackTree.find("span").text == question.rawData.get(feedbackValue)


def test_nfAnswerFeedbacks() -> None:
    for question in nfCategory.questions.values():
        question.getUpdatedElement()
        tree = ET.Element("quiz")
        tree.append(question._element)
        answers = tree.find("question").findall("answer")
        wrongSignPerc = question.rawData.get(Tags.WRONGSIGNPERCENT)
        for ans in answers:
            trueAns = ans if ans.get("fraction") == "100" else None
        truefeedback = ET.fromstring(trueAns.find("feedback").find("text").text)
        print(truefeedback.find("span").text)
        assert truefeedback.find("span").text == question.rawData.get(Tags.TRUEFB)


def test_nfmAnswerFeedbacks() -> None:
    for question in nfmCategory.questions.values():
        question.getUpdatedElement()
        tree = ET.Element("quiz")
        tree.append(question._element)
        answers = tree.find("question").findall("answer")
        wrongSignPerc = question.rawData.get(Tags.WRONGSIGNPERCENT)
        for ans in answers:
            if ans.get("fraction") == "100":
                trueAns = ans
            elif ans.get("fraction") == str(wrongSignPerc):
                wrongSignAns = ans
        truefeedback = ET.fromstring(trueAns.find("feedback").find("text").text)
        wrongSignEle = ET.fromstring(wrongSignAns.find("feedback").find("text").text)
        print(truefeedback.find("span").text)
        assert wrongSignEle.find("span").text == question.rawData.get(Tags.WRONGSIGNFB)
        assert truefeedback.find("span").text == question.rawData.get(Tags.TRUEFB)
