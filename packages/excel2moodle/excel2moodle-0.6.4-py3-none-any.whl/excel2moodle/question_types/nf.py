"""Numerical question implementation."""

from types import UnionType
from typing import ClassVar

import lxml.etree as ET

from excel2moodle.core.globals import (
    Tags,
    XMLTags,
)
from excel2moodle.core.parser import QuestionParser
from excel2moodle.core.question import Question


class NFQuestion(Question):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    nfOpt: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.BPOINTS: str,
    }
    nfMand: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.RESULT: float | int,
    }


class NFQuestionParser(QuestionParser):
    """Subclass for parsing numeric questions."""

    def __init__(self) -> None:
        super().__init__()
        self.feedBackList = {XMLTags.GENFEEDB: Tags.GENERALFB}

    def setup(self, question: NFQuestion) -> None:
        self.question: NFQuestion = question
        super().setup(question)

    def _parseAnswers(self) -> list[ET.Element]:
        result: float = self.rawInput.get(Tags.RESULT)
        ansEle: list[ET.Element] = []
        ansEle.append(self.getNumericAnsElement(result=result))
        return ansEle

    def _finalizeParsing(self) -> None:
        self.tmpEle.append(
            self.getFeedBEle(XMLTags.GENFEEDB, text=self.rawInput.get(Tags.GENERALFB))
        )
        return super()._finalizeParsing()
