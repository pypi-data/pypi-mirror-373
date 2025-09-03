import logging

import lxml.etree as ET

import excel2moodle.core.etHelpers as eth
from excel2moodle.core.bullets import BulletList
from excel2moodle.core.exceptions import QNotParsedException
from excel2moodle.core.globals import (
    Tags,
    TextElements,
    XMLTags,
    feedBElements,
)
from excel2moodle.core.question import ParametricQuestion, Picture, Question
from excel2moodle.core.settings import Settings, Tags
from excel2moodle.extra.scriptCaller import MediaCall
from excel2moodle.logger import LogAdapterQuestionID

loggerObj = logging.getLogger(__name__)


class QuestionParser:
    """Setup the Parser Object.

    This is the superclass which implements the general Behaviour of he Parser.
    Important to implement the answers methods.
    """

    settings = Settings()

    def __init__(self) -> None:
        """Initialize the general Question parser."""
        self.logger: logging.LoggerAdapter

    def setup(self, question: Question) -> None:
        self.question: Question = question
        self.rawInput = question.rawData
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": self.question.id})
        self.logger.debug(
            "The following Data was provided: %s",
            self.rawInput,
        )

    def hasPicture(self) -> bool:
        """Create a ``Picture`` object ``question``if the question needs a pic."""
        if hasattr(self, "picture") and self.question.picture.ready:
            return True
        picKey = self.rawInput.get(Tags.PICTURE)
        f = self.settings.get(Tags.PICTUREFOLDER)
        svgFolder = (f / self.question.katName).resolve()
        if not hasattr(self.question, "picture"):
            self.question.picture = Picture(
                picKey,
                svgFolder,
                self.question.id,
                width=self.rawInput.get(Tags.PICTUREWIDTH),
            )
        return bool(self.question.picture.ready)

    def getMainTextElement(self) -> ET.Element:
        """Get the root question Text with the question paragraphs."""
        textHTMLroot: ET._Element = ET.Element("div")
        ET.SubElement(
            ET.SubElement(textHTMLroot, "p"), "b"
        ).text = f"ID {self.question.id}"
        text = self.rawInput[Tags.TEXT]
        for t in text:
            par = TextElements.PLEFT.create()
            par.text = t
            textHTMLroot.append(par)
        self.logger.debug("Created main Text with: %s paragraphs", len(text))
        return textHTMLroot

    def appendToTmpEle(
        self,
        eleName: str,
        text: str | Tags,
        txtEle=False,
        **attribs,
    ) -> None:
        """Append ``text`` to the temporary Element.

        It uses the data from ``self.rawInput`` if ``text`` is type``DFIndex``
        Otherwise the value of ``text`` will be inserted.
        """
        t = self.rawInput.get(text) if isinstance(text, Tags) else text
        if txtEle is False:
            self.tmpEle.append(eth.getElement(eleName, t, **attribs))
        elif txtEle is True:
            self.tmpEle.append(eth.getTextElement(eleName, t, **attribs))

    def _appendStandardTags(self) -> None:
        """Append the elements defined in the ``cls.standardTags``."""
        self.logger.debug(
            "Appending the Standard Tags %s", type(self.question).standardTags.items()
        )
        for k, v in type(self.question).standardTags.items():
            self.appendToTmpEle(k, text=v)

    def parse(self) -> None:
        """Parse the Question.

        Generates an new Question Element stored as ``self.tmpEle:ET.Element``
        if no Exceptions are raised, ``self.tmpEle`` is passed to ``question.element``
        """
        self.logger.info("Starting to parse")
        self.tmpEle: ET.Elemnt = ET.Element(
            XMLTags.QUESTION, type=self.question.moodleType
        )
        self.appendToTmpEle(XMLTags.NAME, text=Tags.NAME, txtEle=True)
        self.appendToTmpEle(XMLTags.ID, text=self.question.id)
        textRootElem = ET.Element(XMLTags.QTEXT, format="html")
        self.mainTextEle = ET.SubElement(textRootElem, "text")
        self.tmpEle.append(textRootElem)
        if self.question.qtype != "CLOZE":
            self.appendToTmpEle(XMLTags.POINTS, text=str(self.question.points))
        self._appendStandardTags()

        self.htmlRoot = ET.Element("div")
        self.htmlRoot.append(self.getMainTextElement())
        if Tags.BPOINTS in self.rawInput:
            bps: list[str] = self.rawInput[Tags.BPOINTS]
            try:
                bullets: BulletList = BulletList(bps, self.question.id)
            except IndexError:
                msg = f"konnt Bullet Liste {self.question.id} nicht generieren"
                raise QNotParsedException(
                    msg,
                    self.question.id,
                )
            self.htmlRoot.append(bullets.element)
            self.question.bulletList = bullets
            if isinstance(self.question, ParametricQuestion):
                self.question.updateQue = [bullets]
        if self.hasPicture():
            self.htmlRoot.append(self.question.picture.htmlTag)
            textRootElem.append(self.question.picture.element)
        if Tags.MEDIACALL in self.rawInput:
            self.insertScriptedMedia()
        ansList = self._parseAnswers()
        if ansList is not None:
            for ele in ansList:
                self.tmpEle.append(ele)
        self._finalizeParsing()

    def _finalizeParsing(self) -> None:
        """Pass the parsed element trees to the question.

        Intended for the subclasses to do extra stuff.
        """
        self.question._element = self.tmpEle
        self.question.htmlRoot = self.htmlRoot
        self.question.isParsed = True
        self.question.textElement = self.mainTextEle
        self.logger.info("Sucessfully parsed")

    def getFeedBEle(
        self,
        feedback: XMLTags,
        text: str | None = None,
        style: TextElements | None = None,
    ) -> ET.Element:
        span = feedBElements[feedback] if style is None else style.create()
        if text is None:
            self.logger.error("Giving a feedback without providing text is nonsens")
            text = self.rawInput.get(Tags.GENERALFB)
        ele = ET.Element(feedback, format="html")
        par = TextElements.PLEFT.create()
        span.text = text
        par.append(span)
        ele.append(eth.getCdatTxtElement(par))
        return ele

    def insertScriptedMedia(self) -> None:
        """Load the scripts, insert the div and call a Function."""
        for script in self.rawInput.get(Tags.MEDIASCRIPTS):
            ET.SubElement(
                self.htmlRoot, "script", type="text/javascript", src=script
            ).text = ""
        divId = f"scriptedMedia-{self.question.id}"
        ET.SubElement(self.htmlRoot, "div", id=divId).text = ""
        scriptCall = MediaCall(self.rawInput.get(Tags.MEDIACALL), divId=divId)
        self.htmlRoot.append(scriptCall.element)
        if isinstance(self.question, ParametricQuestion):
            self.question.updateQue.append(scriptCall)

    def _parseAnswers(self) -> list[ET.Element] | None:
        """Needs to be implemented in the type-specific subclasses."""
        return None

    def getNumericAnsElement(
        self,
        result: float = 0.0,
        fraction: float = 100,
        feedback: str | None = None,
        format: str = "moodle_auto_format",
    ) -> ET.Element:
        """Get ``<answer/>`` Element specific for the numerical Question.

        The element contains those children:
            ``<text/>`` which holds the value of the answer
            ``<tolerance/>`` with the *relative* tolerance for the result in percent
            ``<feedback/>`` with general feedback for a true answer.
        """
        ansEle: ET.Element = eth.getTextElement(
            XMLTags.ANSWER,
            text=str(result),
            fraction=str(fraction),
            format=format,
        )
        if feedback is None:
            feedback = self.rawInput.get(Tags.TRUEFB)
        ansEle.append(
            self.getFeedBEle(
                feedback=XMLTags.ANSFEEDBACK,
                text=feedback,
                style=TextElements.SPANGREEN,
            ),
        )
        absTolerance = round(result * self.rawInput.get(Tags.TOLERANCE), 4)
        ansEle.append(eth.getElement(XMLTags.TOLERANCE, text=str(absTolerance)))
        return ansEle
