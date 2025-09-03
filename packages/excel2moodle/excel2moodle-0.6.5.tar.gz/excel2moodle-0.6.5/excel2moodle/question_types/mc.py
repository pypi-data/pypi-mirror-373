"""Multiple choice Question implementation."""

from types import UnionType
from typing import ClassVar

import lxml.etree as ET

import excel2moodle.core.etHelpers as eth
from excel2moodle.core import stringHelpers
from excel2moodle.core.exceptions import InvalidFieldException, QNotParsedException
from excel2moodle.core.globals import (
    Tags,
    TextElements,
    XMLTags,
)
from excel2moodle.core.parser import QuestionParser
from excel2moodle.core.question import Picture, Question
from excel2moodle.core.settings import Tags


class MCQuestion(Question):
    """Multiple-choice Question Implementation."""

    standardTags: ClassVar[dict[str, str | float]] = {
        "single": "false",
        "shuffleanswers": "true",
        "answernumbering": "abc",
        "showstandardinstruction": "0",
        "shownumcorrect": "",
    }
    mcOpt: ClassVar[dict[Tags, type | UnionType]] = {}
    mcMand: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.TRUE: str,
        Tags.FALSE: str,
        Tags.ANSTYPE: str,
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.AnsStyles = ["math", "unit", "text", "picture"]


class MCQuestionParser(QuestionParser):
    """Parser for the multiple choice Question."""

    def __init__(self) -> None:
        super().__init__()

    def setup(self, question: MCQuestion) -> None:
        self.question: MCQuestion = question
        super().setup(question)

    def getAnsElementsList(
        self,
        answerList: list,
        fraction: float = 50,
        format="html",
    ) -> list[ET.Element]:
        elementList: list[ET.Element] = []
        for i, ans in enumerate(answerList):
            p = TextElements.PLEFT.create()
            if self.answerType == "picture":
                p.append(ans)
            else:
                p.text = str(ans)
            text = eth.getCdatTxtElement(p)
            elementList.append(
                ET.Element(XMLTags.ANSWER, fraction=str(fraction), format=format),
            )
            elementList[-1].append(text)
            if fraction < 0:
                elementList[-1].append(
                    self.getFeedBEle(
                        XMLTags.ANSFEEDBACK,
                        text=self.rawInput.get(Tags.FALSEFB),
                        style=TextElements.SPANRED,
                    ),
                )
                if self.answerType == "picture":
                    elementList[-1].append(self.falseImgs[i].element)
            elif fraction > 0:
                elementList[-1].append(
                    self.getFeedBEle(
                        XMLTags.ANSFEEDBACK,
                        text=self.rawInput.get(Tags.TRUEFB),
                        style=TextElements.SPANGREEN,
                    ),
                )
                if self.answerType == "picture":
                    elementList[-1].append(self.trueImgs[i].element)
        return elementList

    def _parseAnswers(self) -> list[ET.Element]:
        self.answerType = self.rawInput.get(Tags.ANSTYPE)
        if self.answerType not in self.question.AnsStyles:
            msg = f"The Answer style: {self.answerType} is not supported"
            raise InvalidFieldException(msg, self.question.id, Tags.ANSTYPE)
        if self.answerType == "picture":
            f = self.settings.get(Tags.PICTUREFOLDER)
            imgFolder = (f / self.question.katName).resolve()
            width = self.rawInput.get(Tags.ANSPICWIDTH)
            self.trueImgs: list[Picture] = [
                Picture(t, imgFolder, self.question.id, width=width)
                for t in self.rawInput.get(Tags.TRUE)
            ]
            self.falseImgs: list[Picture] = [
                Picture(t, imgFolder, self.question.id, width=width)
                for t in self.rawInput.get(Tags.FALSE)
            ]
            trueAnsList: list[str] = [pic.htmlTag for pic in self.trueImgs if pic.ready]
            falseAList: list[str] = [pic.htmlTag for pic in self.falseImgs if pic.ready]
            if len(trueAnsList) == 0 or len(falseAList) == 0:
                msg = "No Answer Pictures could be found"
                raise QNotParsedException(msg, self.question.id)
        else:
            trueAnsList: list[str] = stringHelpers.texWrapper(
                self.rawInput.get(Tags.TRUE), style=self.answerType
            )
            self.logger.debug(f"got the following true answers \n {trueAnsList=}")
            falseAList: list[str] = stringHelpers.texWrapper(
                self.rawInput.get(Tags.FALSE), style=self.answerType
            )
            self.logger.debug(f"got the following false answers \n {falseAList=}")
        truefrac = 1 / len(trueAnsList) * 100
        falsefrac = 1 / len(falseAList) * (-100)
        self.tmpEle.find(XMLTags.PENALTY).text = str(round(truefrac / 100, 4))
        ansList = self.getAnsElementsList(trueAnsList, fraction=round(truefrac, 4))
        ansList.extend(
            self.getAnsElementsList(falseAList, fraction=round(falsefrac, 4)),
        )
        return ansList

    def parse(self) -> None:
        super().parse()
        feedBacks = {
            XMLTags.CORFEEDB: Tags.TRUEFB,
            XMLTags.PCORFEEDB: Tags.PCORRECFB,
            XMLTags.INCORFEEDB: Tags.FALSEFB,
        }
        for feedb, tag in feedBacks.items():
            self.tmpEle.append(self.getFeedBEle(feedb, text=self.rawInput.get(tag)))
        self._finalizeParsing()
