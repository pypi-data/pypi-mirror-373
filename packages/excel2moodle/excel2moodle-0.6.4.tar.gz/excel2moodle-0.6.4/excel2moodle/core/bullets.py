import logging
import re

import lxml.etree as ET

from excel2moodle.core import stringHelpers
from excel2moodle.core.globals import TextElements
from excel2moodle.core.question import ParametricQuestion, Parametrics
from excel2moodle.logger import LogAdapterQuestionID

loggerObj = logging.getLogger(__name__)


class BulletList:
    def __init__(self, rawBullets: list[str], qID: str) -> None:
        self.rawBullets: list[str] = rawBullets
        self.element: ET.Element = ET.Element("ul")
        self.bullets: dict[str | int, BulletP] = {}
        self.id = qID
        self.logger = LogAdapterQuestionID(loggerObj, {"qID": self.id})
        self._setupBullets(rawBullets)

    def update(self, parametrics: Parametrics, variant: int = 1) -> None:
        variables: dict[str, list[float]] = parametrics.variables
        for var, bullet in self.bullets.items():
            bullet.update(value=variables[var][variant - 1])

    def getVariablesDict(self, question: ParametricQuestion) -> dict[str, list[float]]:
        """Read variabel values for vars in `question.rawData`.

        Returns
        -------
        A dictionary containing a list of values for each variable name

        """
        keyList = self.varNames
        dic: dict = {}
        for k in keyList:
            val = question.rawData[k.lower()]
            if isinstance(val, str):
                li = stringHelpers.getListFromStr(val)
                variables: list[float] = [float(i.replace(",", ".")) for i in li]
                dic[str(k)] = variables
            else:
                dic[str(k)] = [str(val)]
        loggerObj.debug("The following variables were provided: %s", dic)
        return dic

    @property
    def varNames(self) -> list[str]:
        names = [i for i in self.bullets if isinstance(i, str)]
        if len(names) > 0:
            self.logger.debug("returning Var names: %s", names)
            return names
        msg = "Bullet variable names not given."
        raise ValueError(msg)

    def _setupBullets(self, bps: list[str]) -> ET.Element:
        self.logger.debug("Formatting the bulletpoint list")
        varFinder = re.compile(r"=\s*\{(\w+)\}")
        for i, item in enumerate(bps):
            sc_split = item.split()
            name = sc_split[0]
            var = sc_split[1]
            quant = sc_split[3]
            unit = sc_split[4]

            match = re.search(varFinder, item)
            if match is None:
                self.logger.debug("Got a normal bulletItem")
                num: float = float(quant.replace(",", "."))
                bulletName = i + 1
            else:
                bulletName = match.group(1)
                num: float = 0.0
                self.logger.debug("Got an variable bulletItem, match: %s", match)

            self.bullets[bulletName] = BulletP(name=name, var=var, unit=unit, value=num)
            self.element.append(self.bullets[bulletName].element)
        return self.element


class BulletP:
    def __init__(self, name: str, var: str, unit: str, value: float = 0.0) -> None:
        self.name: str = name
        self.var: str = var
        self.unit: str = unit
        self.element: ET.Element
        self.update(value=value)

    def update(self, value: float = 1) -> None:
        if not hasattr(self, "element"):
            self.element = TextElements.LISTITEM.create()
        valuestr = str(value).replace(".", r",\!")
        self.element.text = (
            f"{self.name} \\( {self.var} = {valuestr} \\mathrm{{ {self.unit} }} \\)"
        )
