import logging
import re

import lxml.etree as ET

from excel2moodle.core.question import Parametrics

loggerObj = logging.getLogger(__name__)


class MediaCall:
    def __init__(self, callString: str, divId: str) -> None:
        self.call: str = re.sub(r"\(", f'("{divId}", ', callString)
        self._scriptElem = ET.Element("script")
        self._scriptElem.text = callString
        self.divId = divId

    @property
    def element(self) -> ET.Element:
        return self._scriptElem

    def update(self, parametrics: Parametrics, variant: int = 0) -> None:
        updatedCall = self.call
        for var, val in parametrics.variables.items():
            updatedCall = re.sub(rf",\s+{var}\s*", f", {val[variant]}", updatedCall)
        self._scriptElem.text = updatedCall
        loggerObj.info("Inserted function call: %s", updatedCall)
