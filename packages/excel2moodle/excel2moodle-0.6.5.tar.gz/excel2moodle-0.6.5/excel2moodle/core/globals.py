from enum import Enum, StrEnum

import lxml.etree as ET

from excel2moodle.core.settings import Tags

QUESTION_TYPES = {
    "NF": "numerical",
    "NFM": "numerical",
    "MC": "multichoice",
    "CLOZE": "cloze",
}


class TextElements(Enum):
    PLEFT = "p", "text-align: left;"
    SPANRED = "span", "color: rgb(239, 69, 64)"
    SPANGREEN = "span", "color: rgb(152, 202, 62)"
    SPANORANGE = "span", "color: rgb(152, 100, 100)"
    ULIST = "ul", ""
    LISTITEM = "li", "text-align: left;"
    DIV = "div", ""

    def create(self, tag: str | None = None):
        if tag is None:
            tag, style = self.value
        else:
            style = self.value[1]
        return ET.Element(tag, dir="ltr", style=style)

    @property
    def style(
        self,
    ) -> str:
        return self.value[1]


class XMLTags(StrEnum):
    def __new__(cls, value: str, dfkey: Tags | None = None):
        obj = str.__new__(cls, value)
        obj._value_ = value
        if dfkey is not None:
            obj._dfkey_ = dfkey
        return obj

    def __init__(self, _: str, dfkey: Tags | None = None, getEle=None) -> None:
        if isinstance(dfkey, Tags):
            self._dfkey_: str = dfkey
        if getEle:
            self._getEle_: object = getEle

    @property
    def dfkey(self) -> str:
        return self._dfkey_

    def set(self, getEle) -> None:
        self._getEle_ = getEle

    def __repr__(self) -> str:
        msg = []
        msg.append(f"XML Tag {self.value=}")
        if hasattr(self, "_dfkey_"):
            msg.append(f"Df Key {self.dfkey=}")
        return "\n".join(msg)

    NAME = "name", Tags.NAME
    QTEXT = "questiontext", Tags.TEXT
    QUESTION = "question"
    TEXT = "text"
    PICTURE = "file", Tags.PICTURE
    GENFEEDB = "generalfeedback"
    CORFEEDB = "correctfeedback"
    PCORFEEDB = "partialcorrectfeedback"
    INCORFEEDB = "incorrectfeedback"
    ANSFEEDBACK = "feedback"
    POINTS = "defaultgrade"
    PENALTY = "penalty"
    HIDE = "hidden"
    ID = "idnumber"
    TYPE = "type"
    ANSWER = "answer"
    TOLERANCE = "tolerance"


feedBElements = {
    XMLTags.CORFEEDB: TextElements.SPANGREEN.create(),
    XMLTags.PCORFEEDB: TextElements.SPANORANGE.create(),
    XMLTags.INCORFEEDB: TextElements.SPANRED.create(),
    XMLTags.ANSFEEDBACK: TextElements.SPANGREEN.create(),
    XMLTags.GENFEEDB: TextElements.SPANGREEN.create(),
}
