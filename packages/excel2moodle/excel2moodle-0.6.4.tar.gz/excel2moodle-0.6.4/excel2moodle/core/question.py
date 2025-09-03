import base64
import logging
import math
import re
from copy import deepcopy
from pathlib import Path
from types import UnionType
from typing import TYPE_CHECKING, ClassVar, Literal, overload

import lxml.etree as ET
from asteval import Interpreter

from excel2moodle.core.category import Category
from excel2moodle.core.exceptions import QNotParsedException
from excel2moodle.core.globals import (
    QUESTION_TYPES,
    Tags,
)
from excel2moodle.core.settings import Settings, Tags
from excel2moodle.logger import LogAdapterQuestionID

if TYPE_CHECKING:
    from excel2moodle.core.bullets import BulletList

loggerObj = logging.getLogger(__name__)
settings = Settings()


class QuestionData(dict):
    @property
    def categoryFallbacks(self) -> dict[str, float | str]:
        return self._categoryFallbacks

    @categoryFallbacks.setter
    def categoryFallbacks(self, fallbacks: dict) -> None:
        self._categoryFallbacks: dict[str, float | str] = fallbacks

    @overload
    def get(
        self,
        key: Literal[
            Tags.NAME,
            Tags.ANSTYPE,
            Tags.PICTURE,
            Tags.EQUATION,
            Tags.TRUEFB,
            Tags.FALSEFB,
            Tags.GENERALFB,
            Tags.WRONGSIGNFB,
        ],
        default: object = None,
    ) -> str: ...
    @overload
    def get(
        self,
        key: Literal[
            Tags.BPOINTS,
            Tags.TRUE,
            Tags.FALSE,
            Tags.QUESTIONPART,
            Tags.TEXT,
            Tags.MEDIASCRIPTS,
        ],
        default: object = None,
    ) -> list: ...
    @overload
    def get(
        self,
        key: Literal[
            Tags.NUMBER,
            Tags.PICTUREWIDTH,
            Tags.ANSPICWIDTH,
            Tags.WRONGSIGNPERCENT,
        ],
        default: object = None,
    ) -> int: ...
    @overload
    def get(
        self, key: Literal[Tags.PARTTYPE, Tags.TYPE], default: object = None
    ) -> Literal["MC", "NFM", "CLOZE"]: ...
    @overload
    def get(
        self,
        key: Literal[Tags.TOLERANCE, Tags.POINTS, Tags.FIRSTRESULT],
        default: object = None,
    ) -> float: ...
    @overload
    def get(self, key: Literal[Tags.RESULT], default: object = None) -> float | str: ...

    def get(self, key, default=None):
        """Get the value for `key` with correct type.

        If `key == Tags.TOLERANCE` the tolerance is checked to be a perc. fraction
        """
        if key in self:
            val = self[key]
        elif key in self.categoryFallbacks:
            val = self.categoryFallbacks.get(key)
        else:
            val = settings.get(key)
        try:
            typed = key.typ()(val)
        except (TypeError, ValueError):
            return None
        if key == Tags.TOLERANCE:
            loggerObj.debug("Verifying Tolerance")
            if typed <= 0 or typed >= 100:
                typed = settings.get(Tags.TOLERANCE)
            return typed if typed < 1 else typed / 100
        return typed


class Question:
    standardTags: ClassVar[dict[str, str | float]] = {
        "hidden": 0,
        "penalty": 0.33333,
    }
    mandatoryTags: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.TEXT: str,
        Tags.NAME: str,
        Tags.TYPE: str,
    }
    optionalTags: ClassVar[dict[Tags, type | UnionType]] = {
        Tags.PICTURE: int | str,
        Tags.MEDIACALL: list,
    }

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        dictionaries = ("standardTags", "mandatoryTags", "optionalTags")
        for dic in dictionaries:
            cls._mergeDicts(dic)

    @classmethod
    def _mergeDicts(cls, dictName) -> None:
        superDict = getattr(super(cls, cls), dictName)
        subDict = getattr(cls, dictName, {})
        mergedDict = superDict.copy()
        mergedDict.update(subDict)
        setattr(cls, dictName, mergedDict)

    @classmethod
    def addStandardTag(cls, key, value) -> None:
        cls.standardTags[key] = value

    def __init__(
        self,
        category: Category,
        rawData: QuestionData,
        parent=None,
    ) -> None:
        self.rawData: QuestionData = rawData
        self.rawData.categoryFallbacks = category.settings
        self.category = category
        self.katName = self.category.name
        self.moodleType = QUESTION_TYPES[self.qtype]
        self._element: ET.Element = None
        self.isParsed: bool = False
        self.picture: Picture
        self.id: str
        self.htmlRoot: ET.Element
        self.bulletList: BulletList
        self.textElement: ET.Element
        self._setID()
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": self.id})
        self.logger.debug("Sucess initializing")

    @property
    def points(self) -> float:
        return self.rawData.get(Tags.POINTS)

    @property
    def name(self) -> str:
        return self.rawData.get(Tags.NAME)

    @property
    def qtype(self) -> str:
        return self.rawData.get(Tags.TYPE)

    def __repr__(self) -> str:
        li: list[str] = []
        li.append(f"Question v{self.id}")
        li.append(f"{self.qtype}")
        return "\t".join(li)

    def getUpdatedElement(self, variant: int = 0) -> ET.Element:
        """Update and get the Question Elements to reflect the version.

        Each Subclass needs to implement its specific logic.
        Things needed to be considered:
            Question Text
            Bullet Points
            Answers
        """
        self.textElement.text = ET.CDATA(
            ET.tostring(self.htmlRoot, encoding="unicode", pretty_print=True)
        )
        return deepcopy(self._element)

    def _setID(self, id=0) -> None:
        if id == 0:
            self.id: str = f"{self.category.id}{self.rawData.get(Tags.NUMBER):02d}"
        else:
            self.id: str = str(id)


class ParametricQuestion(Question):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rules: list[str] = []
        self.parametrics: Parametrics
        self._variant: int
        self.updateQue: list

    @property
    def currentVariant(self) -> int:
        return self._variant

    def getUpdatedElement(self, variant: int = 0) -> ET.Element:
        """Update the bulletItem.text With the values for variant.

        `ParametricQuestion` updates the bullet points.
        `Question` returns the Element.

        """
        if not hasattr(self, "updateQue"):
            msg = "Can't assemble a parametric question, without the updateQue"
            raise QNotParsedException(msg, self.id)

        for obj in self.updateQue:
            obj.update(parametrics=self.parametrics, variant=variant)
        self._variant = variant
        return super().getUpdatedElement(variant)


class Parametrics:
    """Object for parametrizing the numeric Questions.

    Equation storing the variables, equation, and results.
    """

    astEval = Interpreter(with_import=True)

    def __init__(
        self,
        equation: str | dict[int, str],
        firstResult: float | dict[int, float] = 0.0,
        identifier: str = "0000",
    ) -> None:
        self.equations: dict[int, str] = (
            equation if isinstance(equation, dict) else {1: equation}
        )
        self._resultChecker: dict[int, float] = (
            firstResult if isinstance(firstResult, dict) else {1: firstResult}
        )
        self.id = identifier
        self._variables: dict[str, list[float | int]] = {}
        self.results: dict[int, list[float]] = {}
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": self.id})

    @property
    def variants(self) -> int:
        number = 1000
        for li in self._variables.values():
            number = min(number, len(li))
        return number

    @property
    def variableRules(self) -> list[str]:
        if hasattr(self, "_rules"):
            return self._rules
        return []

    @variableRules.setter
    def variableRules(self, rules: list[str]) -> None:
        self._rules = rules

    def getResult(self, number: int = 1, equation: int = 1) -> float:
        """Get the result for the variant `number` from the `equation` number."""
        self.logger.debug(
            "Returning result %s, variant: %s",
            self.results[equation][number - 1],
            number,
        )
        return self.results[equation][number - 1]

    @property
    def variables(self) -> dict[str, list[float | int]]:
        return self._variables

    @variables.setter
    def variables(self, variables: dict[str, list[float | int]]) -> None:
        self._variables: dict[str, list[float | int]] = variables
        self._calculateResults()
        self.logger.info("Updated parameters and results")

    def _calculateResults(self) -> dict[int, list[float]]:
        self.logger.info("Updating Results for new variables")
        for num in self.equations:
            # reset the old results, and set a list for each equation
            self.results[num] = []
        for variant in range(self.variants):
            type(self).setupAstIntprt(self._variables, variant)
            self.logger.debug("Setup The interpreter for variant: %s", variant + 1)
            for num, eq in self.equations.items():
                result = type(self).astEval(eq)
                if not isinstance(result, float | int):
                    msg = f"The expression: '{eq}'  = {result} could not be evaluated."
                    raise QNotParsedException(msg, self.id)
                self.logger.info(
                    "Calculated expr. %s (variant %s): %s = %.3f ",
                    num,
                    variant + 1,
                    eq,
                    result,
                )
                if variant == 0 and not math.isclose(
                    result, self._resultChecker[num], rel_tol=0.01
                ):
                    self.logger.warning(
                        "The calculated result %s differs from given firstResult: %s",
                        result,
                        self._resultChecker,
                    )
                self.logger.debug(
                    "Calculated result %s for variant %s", result, variant
                )
                self.results[num].append(round(result, 3))
        return self.results

    def resetVariables(self) -> None:
        self._variables = {}
        self.logger.info("Reset the variables")

    @classmethod
    def setupAstIntprt(cls, var: dict[str, list[float | int]], index: int) -> None:
        """Setup the asteval Interpreter with the variables."""
        for name, value in var.items():
            cls.astEval.symtable[name] = value[index]


class Picture:
    def __init__(
        self, picKey: str, imgFolder: Path, questionId: str, width: int = 0
    ) -> None:
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": questionId})
        self.picID: str
        w: int = width if width > 0 else settings.get(Tags.PICTUREWIDTH)
        self.size: dict[str, str] = {"width": str(w)}
        self.ready: bool = False
        self.imgFolder = imgFolder
        self.htmlTag: ET.Element
        self.path: Path
        self.questionId: str = questionId
        self.logger.debug("Instantiating a new picture in %s", picKey)
        if self.getImgId(picKey):
            self.ready = self._getImg()
        else:
            self.ready = False

    def getImgId(self, imgKey: str) -> bool:
        """Get the image ID and width based on the given key.

        The key should either be the full ID (as the question) or only the question Num.
        If only the number is given, the category.id is prepended.
        The width should be specified by `ID:width:XX`. where xx is the px value.
        """
        width = re.findall(r"\:width\:(\d+)", str(imgKey))
        height = re.findall(r"\:height\:(\d+)", str(imgKey))
        if len(width) > 0 and width[0]:
            self.size["width"] = width[0]
        elif len(height) > 0 and height[0]:
            self.size["height"] = height[0]
            self.size.pop("width")
        self.logger.debug("Size of picture is %s", self.size)
        if imgKey in ("true", "True", "yes"):
            self.picID = self.questionId
            return True
        num: list[int | str] = re.findall(r"^\d+", str(imgKey))
        app: list[int | str] = re.findall(r"^\d+([A-Za-z_\-]+)", str(imgKey))
        if imgKey in ("false", "nan", False) or len(num) == 0:
            return False
        imgID: int = int(num[0])
        if imgID < 100:
            picID = f"{self.questionId[:2]}{imgID:02d}"
        elif imgID < 10000:
            picID = f"{imgID:04d}"
        else:
            msg = f"The imgKey {imgKey} is invalid, it should be a 4 digit question ID with an optional suffix"
            raise QNotParsedException(msg, self.questionId)
        if len(app) > 0 and app[0]:
            self.picID = f"{picID}{app[0]}"
        else:
            self.picID = str(picID)
        self.logger.debug("Evaluated the imgID %s from %s", self.picID, imgKey)
        return True

    def _getBase64Img(self, imgPath: Path):
        with imgPath.open("rb") as img:
            return base64.b64encode(img.read()).decode("utf-8")

    def _getImg(self) -> bool:
        suffixes = ["png", "svg", "jpeg", "jpg", "JPG", "jxl"]
        paths = [
            path
            for suf in suffixes
            for path in self.imgFolder.glob(f"{self.picID}.{suf}")
        ]
        self.logger.debug("Found the following paths %s", paths)
        try:
            self.path = paths[0]
        except IndexError:
            msg = f"The Picture {self.imgFolder}/{self.picID} is not found"
            self.logger.warning(msg=msg)
            self.element = None
            return False
            # raise FileNotFoundError(msg)
        base64Img = self._getBase64Img(self.path)
        self.element: ET.Element = ET.Element(
            "file",
            name=f"{self.path.name}",
            path="/",
            encoding="base64",
        )
        self.element.text = base64Img
        self.htmlTag = ET.Element(
            "img",
            src=f"@@PLUGINFILE@@/{self.path.name}",
            alt=f"Bild {self.path.name}",
            **self.size,
        )
        return True
