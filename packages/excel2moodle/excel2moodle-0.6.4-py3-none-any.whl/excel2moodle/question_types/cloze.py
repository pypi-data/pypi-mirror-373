"""Implementation of tde cloze question type.

This question type is like the NFM but supports multiple fields of answers.
All Answers are calculated off an equation using the same variables.
"""

import logging
import math
import re
from typing import Literal, overload

import lxml.etree as ET

from excel2moodle.core.exceptions import QNotParsedException
from excel2moodle.core.globals import (
    Tags,
    TextElements,
)
from excel2moodle.core.question import (
    ParametricQuestion,
    Parametrics,
    QuestionData,
)
from excel2moodle.core.settings import Tags
from excel2moodle.logger import LogAdapterQuestionID
from excel2moodle.question_types.nfm import NFMQuestionParser

logger = logging.getLogger(__name__)


class ClozePart:
    def __init__(
        self,
        question: ParametricQuestion,
        text: list[str],
        number: int,
    ) -> None:
        self.question = question
        self.text: ET.Element = self._setupText(text)
        self.num: int = number
        if not self.text:
            msg = f"Answer part for cloze question {self.question.id} is invalid without partText"
            raise ValueError(msg)
        self.logger = LogAdapterQuestionID(
            logger, {"qID": f"{self.question.id}-{self.num}"}
        )
        self._typ: Literal["NFM", "MC", "UNSET"]
        self._element: ET.Element
        self.result: Parametrics

    @property
    def clozeElement(self) -> ET.Element:
        if not hasattr(self, "_clozeElement"):
            msg = "Cloze Part has no _clozeElement"
            raise QNotParsedException(msg, f"{self.question.id}-{self.num}")
        return self._element

    @clozeElement.setter
    def clozeElement(self, element: ET.Element) -> None:
        self._element = element

    def updateCloze(self, variant: int = 1) -> None:
        self.logger.info("Updating cloze to variant %s", variant)
        if not hasattr(self, "_element"):
            msg = "Cloze Part has no _clozeElement"
            raise QNotParsedException(msg, f"{self.question.id}-{self.num}")
        if self.typ == "MC":
            self.logger.debug("MC Answer Part already up to date.")
            return
        if self.typ == "NFM":
            result = self.result.getResult(variant)
            self._element.text = self.getNumericAnsStr(
                self.question.rawData,
                result,
                self.question.rawData.get(Tags.TOLERANCE),
                wrongSignCount=self.question.rawData.get(Tags.WRONGSIGNPERCENT),
                points=self.points,
            )
            self.logger.debug("Updated NFM cloze: %s", self._element.text)
        return

    @property
    def typ(self) -> Literal["NFM", "MC", "UNSET"]:
        if not hasattr(self, "_typ"):
            self.logger.warning("Type not set")
            return "UNSET"
        return self._typ

    @typ.setter
    def typ(self, partType: Literal["NFM", "MC", "UNSET"]) -> None:
        if not hasattr(self, "_typ"):
            self._typ = partType
            self.logger.info("Set type to: %s", self._typ)
            if self._typ == "NFM":
                self.result: Parametrics
            elif self._typ == "MC":
                self.falseAnswers: list[str] = []
                self.trueAnswers: list[str] = []

    @property
    def id(self) -> str:
        return f"{self.question.id}-{self.num}"

    @property
    def points(self) -> int:
        """Points of clozes can be only integers.

        Otherwise the moodle import fails.
        """
        if hasattr(self, "_points"):
            return self._points
        return 0
        self.question.logger.error("Invalid call to points of unparsed cloze part")
        return 0

    @points.setter
    def points(self, points: int) -> None:
        self._points = max(0, points)

    @property
    def mcAnswerString(self) -> str:
        if hasattr(self, "_mcAnswer"):
            return self._mcAnswer
        msg = "No MC Answer was set"
        raise ValueError(msg)

    @mcAnswerString.setter
    def mcAnswerString(self, answerString: str) -> None:
        self._mcAnswer: str = answerString

    def _setupText(self, text: list[str]) -> ET.Element:
        textItem: ET.Element = TextElements.LISTITEM.create()
        for t in text:
            textItem.append(TextElements.PLEFT.create())
            textItem[-1].text = t
        return textItem

    def __repr__(self) -> str:
        return f"Cloze Part {self.id}-{self.typ}"

    @staticmethod
    def getNumericAnsStr(
        questionData: QuestionData,
        result: float,
        tolerance: float = 0.0,
        points: int = 1,
        wrongSignCount: int = 0,
        wrongSignFeedback: str | None = None,
    ) -> str:
        """Generate the answer string from `result`.

        Parameters.
        ----------
        wrongSignCount:
            If the wrong sign `+` or `-` is given, how much of the points should be given.
            Interpreted as percent.
        tolerance:
            The relative tolerance, as fraction

        """
        if wrongSignFeedback is None:
            wrongSignFeedback = questionData.get(Tags.WRONGSIGNFB)
        if wrongSignCount == 0:
            wrongSignCount = questionData.get(Tags.WRONGSIGNPERCENT)
        if tolerance == 0.0:
            tolerance = questionData.get(Tags.TOLERANCE)
        absTol = f":{round(result * tolerance, 3)}"
        answerParts: list[str | float] = [
            "{",
            points,
            ":NUMERICAL:=",
            round(result, 3),
            absTol,
            "~%",
            wrongSignCount,
            "%",
            round(result * (-1), 3),
            absTol,
            f"#{wrongSignFeedback}",
            "}",
        ]
        answerPStrings = [str(part) for part in answerParts]
        return "".join(answerPStrings)

    @staticmethod
    def getMCAnsStr(
        true: list[str],
        false: list[str],
        points: int = 1,
    ) -> str:
        """Generate the answer string for the MC answers."""
        truePercent: float = round(100 / len(true), 1)
        falsePercent: float = round(100 / len(false), 1)
        falseList: list[str] = [f"~%-{falsePercent}%{ans}" for ans in false]
        trueList: list[str] = [f"~%{truePercent}%{ans}" for ans in true]
        answerParts: list[str | float] = [
            "{",
            points,
            ":MULTIRESPONSE:",
        ]
        answerParts.extend(trueList)
        answerParts.extend(falseList)
        answerParts.append("}")

        answerPStrings = [str(part) for part in answerParts]
        return "".join(answerPStrings)


class ClozeQuestion(ParametricQuestion):
    """Cloze Question Type."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.questionParts: dict[int, ClozePart] = {}
        self.questionTexts: list[ET.Element] = []
        self.parametrics: Parametrics

    @property
    def partsNum(self) -> int:
        return len(self.questionParts)

    @property
    def points(self) -> int:
        """Points for the cloze question. The sum of all its parts points.

        Returns only integer values.
        """
        pts: int = 0
        if not self.isParsed:
            msg = "The Cloze question has no points because it is not yet parsed"
            self.logger.warning(msg)
            return pts
        for p in self.questionParts.values():
            pts = pts + p.points
        return pts

    def getUpdatedElement(self, variant: int = 0) -> ET.Element:
        """Update and get the Question Elements to reflect the version.

        `ClozeQuestion` Updates the text.
        `ParametricQuestion` updates the bullet points.
        `Question` returns the element.
        """
        for part in self.questionParts.values():
            part.updateCloze(variant=variant)
        return super().getUpdatedElement(variant=variant)


class ClozeQuestionParser(NFMQuestionParser):
    """Parser for the cloze question type."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.question: ClozeQuestion

    def setup(self, question: ClozeQuestion) -> None:
        self.question: ClozeQuestion = question
        super().setup(question)

    def _parseAnswers(self) -> None:
        self._setupParts()
        self._parseAnswerParts()

    def _setupParts(self) -> None:
        parts: dict[int, ClozePart] = {}
        for key in self.rawInput:
            if key.startswith(Tags.QUESTIONPART):
                partNumber = self.getPartNumber(key)
                parts[partNumber] = ClozePart(
                    self.question, self.rawInput[key], partNumber
                )
        partsNum = len(parts)
        equations: dict[int, str] = self._getPartValues(Tags.RESULT)
        trueAnsws: dict[int, list[str]] = self._getPartValues(Tags.TRUE)
        falseAnsws: dict[int, list[str]] = self._getPartValues(Tags.FALSE)
        points: dict[int, float] = self._getPartValues(Tags.POINTS)
        firstResult: dict[int, float] = self._getPartValues(Tags.FIRSTRESULT)
        for num, part in parts.items():
            loclogger = LogAdapterQuestionID(
                logger, {"qID": f"{self.question.id}-{num}"}
            )
            eq = equations.get(num)
            trueAns = trueAnsws.get(num)
            falseAns = falseAnsws.get(num)
            if falseAns is not None and trueAns is not None and eq is None:
                loclogger.info("Setting up MC answer part...")
                part.typ = "MC"
                part.falseAnswers = falseAns
                part.trueAnswers = trueAns
            elif eq is not None and falseAns is None and trueAns is None:
                loclogger.info("Seting up NFM part..")
                if not hasattr(self.question, "parametrics"):
                    loclogger.info("Adding new Parametrics Object to cloze question")
                    self.question.parametrics = Parametrics(
                        equation=eq,
                        firstResult=firstResult.get(num, 0.0),
                        identifier=f"{self.question.id}-{num}",
                    )
                else:
                    loclogger.info("Adding new equation to parametrics")
                    self.question.parametrics.equations[num] = eq
                    self.question.parametrics._resultChecker[num] = firstResult.get(
                        num, 0.0
                    )
                if not hasattr(part, "result"):
                    part.result = self.question.parametrics
                part.typ = "NFM"
                loclogger.info("Set up NFM answer part.")
            else:
                msg = f"Unclear Parts are defined. Either define `true:{num}` and `false:{num}` or `result:{num}` "
                raise QNotParsedException(msg, self.question.id)
        if len(points) == 0:
            pts = round(self.rawInput.get(Tags.POINTS) / partsNum, 3)
            point = self._roundClozePartPoints(pts)
            for part in parts.values():
                part.points = point
        else:
            loclogger.warning(
                "Some Answer parts are missing the points, they will get the standard points"
            )
            for num, part in parts.items():
                part.points = self._roundClozePartPoints(points=points.get(num))
        self.question.questionParts = parts

    def _roundClozePartPoints(self, points: float | None = None) -> int:
        """Get the integer points for the cloze part."""
        if points is None:
            points = self.rawInput.get(Tags.POINTS)
        corrPoints: int = round(points)
        if not math.isclose(corrPoints, points):
            self.logger.warning(
                "Type cloze supports only integers as points. %s was round to %s",
                points,
                corrPoints,
            )
        return corrPoints

    @overload
    def _getPartValues(self, Tag: Literal[Tags.RESULT]) -> dict[int, str]: ...
    @overload
    def _getPartValues(
        self, Tag: Literal[Tags.POINTS, Tags.FIRSTRESULT]
    ) -> dict[int, float]: ...
    @overload
    def _getPartValues(
        self, Tag: Literal[Tags.TRUE, Tags.FALSE]
    ) -> dict[int, list[str]]: ...
    def _getPartValues(self, Tag):
        tagValues: dict = {
            self.getPartNumber(key): self.rawInput[key]
            for key in self.rawInput
            if key.startswith(Tag)
        }
        return tagValues

    def _parseAnswerParts(self) -> None:
        """Parse the numeric or MC result items."""
        answersList = ET.Element("ol")
        self.question.parametrics.variables = self.question.bulletList.getVariablesDict(
            self.question
        )
        for partNum, part in self.question.questionParts.items():
            if part.typ == "NFM":
                result = self.question.parametrics.getResult(1, partNum)
                ansStr = ClozePart.getNumericAnsStr(
                    self.rawInput,
                    result=result,
                    points=part.points,
                )
                self.logger.debug("Generated %s answer part: %s ", partNum, ansStr)
            elif part.typ == "MC":
                ansStr = ClozePart.getMCAnsStr(
                    part.trueAnswers,
                    part.falseAnswers,
                    points=part.points,
                )
                part.mcAnswerString = ansStr
                self.logger.debug("Appended MC part %s: %s", partNum, ansStr)
            else:
                msg = "Type of the answer part is invalid"
                raise QNotParsedException(msg, self.id)
            unorderedList = TextElements.ULIST.create()
            answerItem = TextElements.LISTITEM.create()
            answerItem.text = ansStr
            part.clozeElement = answerItem
            unorderedList.append(answerItem)
            part.text.append(unorderedList)
            self.logger.debug("Appended part %s %s to main text", partNum, part)
            answersList.append(part.text)
        self.htmlRoot.append(answersList)

    def getPartNumber(self, indexKey: str) -> int:
        """Return the number of the question Part.

        The number should be given after the `:` colon.
        This is number is used, to reference the question Text
        and the expected answer fields together.
        """
        try:
            num = re.findall(r":(\d+)$", indexKey)[0]
        except IndexError:
            msg = f"No :i question Part value given for {indexKey}"
            raise QNotParsedException(msg, self.question.id)
        else:
            return int(num)
