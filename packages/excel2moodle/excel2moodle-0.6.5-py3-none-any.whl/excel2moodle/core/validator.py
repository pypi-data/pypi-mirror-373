"""This Module checks if the data inside the Spreadsheet is valid.

Those things are considered:

#. The mandatory entries must not be ``Nan``
#. All fields must have the right data-type

If Those checks pass, a question is created,
which can be accessed via ``Validator.question``
"""

import logging

import pandas as pd

from excel2moodle.core import stringHelpers
from excel2moodle.core.exceptions import InvalidFieldException
from excel2moodle.core.globals import QUESTION_TYPES, Tags
from excel2moodle.core.question import QuestionData
from excel2moodle.core.settings import Settings
from excel2moodle.question_types import QuestionTypeMapping

logger = logging.getLogger(__name__)

settings = Settings()


class Validator:
    """Validate the question data from the spreadsheet.

    Creates a dictionary with the data, for easier access later.
    """

    def setup(self, df: pd.Series, index: int) -> None:
        self.df = df
        self.index = index
        typ = self.df.loc[Tags.TYPE]
        if typ not in QUESTION_TYPES:
            msg = f"No valid question type provided. {typ} is not a known type"
            raise InvalidFieldException(msg, "index:02d", Tags.TYPE)
        self.mandatory = QuestionTypeMapping[typ].value.mandatoryTags
        self.optional = QuestionTypeMapping[typ].value.optionalTags

    def validate(self) -> None:
        qid = f"{self.index:02d}"
        checker, missing = self._mandatory()
        if not checker:
            msg = f"Question {qid} misses the key {missing}"
            if missing is not None:
                raise InvalidFieldException(msg, qid, missing)
        checker, missing = self._typeCheck()
        if not checker:
            msg = f"Question {qid} has wrong typed data {missing}"
            if missing is not None:
                raise InvalidFieldException(msg, qid, missing)

    @staticmethod
    def dfToDict(df: pd.Series) -> dict[str, int | float | list[str] | str]:
        """Convert a dataframe to dictionary, preserving lists."""
        dic: dict[str, int | float | list[str] | str] = {}
        for var, val in df.items():
            if not isinstance(var, str):
                continue
            if pd.isna(val):
                continue
            if var in dic:
                if isinstance(dic[var], list):
                    dic[var].append(val)
                else:
                    existing = dic[var]
                    dic[var] = [existing, val]
            else:
                dic[var] = val
        return dic

    def getQuestionData(self) -> QuestionData:
        """Get the data from the spreadsheet as a dictionary."""
        self.qdata = self.dfToDict(self.df)
        self.listify(self.qdata)
        tol = float(self.qdata.get(Tags.TOLERANCE, 0))
        if tol < 0 or tol > 99:
            tol = settings.get(Tags.TOLERANCE)
        elif tol != 0:
            self.qdata[Tags.TOLERANCE] = tol if tol < 1 else tol / 100

        if self.qdata[Tags.TYPE] == "NFM":
            self.qdata[Tags.EQUATION] = str(self.qdata[Tags.RESULT])
        return QuestionData(self.qdata)

    @staticmethod
    def listify(dictionary: dict) -> None:
        """Converts to list all tag values, which are supposed to be a list."""
        for key in dictionary:
            k: str = key.split(":")[0]
            if k in Tags:
                tag = Tags(k)
                logger.info("Got the Tag %s from key: %s", tag, key)
                if tag.typ() is list and not isinstance(dictionary[key], list):
                    dictionary[key] = stringHelpers.getListFromStr(dictionary[key])
                    logger.info("Converted Input to list for %s", key)

    def _mandatory(self) -> tuple[bool, Tags | None]:
        """Detects if all keys of mandatory are filled with values."""
        checker = pd.Series.notna(self.df)
        for k in self.mandatory:
            try:
                c = checker[k]
            except KeyError:
                return False, k
            if isinstance(c, pd.Series):
                if not c.any():
                    return False, k
            elif not c:
                return False, k
        return True, None

    def _typeCheck(self) -> tuple[bool, list[Tags] | None]:
        invalid: list[Tags] = []
        for field, typ in self.mandatory.items():
            if field in self.df and isinstance(self.df[field], pd.Series):
                for f in self.df[field]:
                    if pd.notna(f) and not isinstance(f, typ):
                        invalid.append(field)
            elif not isinstance(self.df[field], typ):
                invalid.append(field)
        for field, typ in self.optional.items():
            if field in self.df and isinstance(self.df[field], pd.Series):
                for f in self.df[field]:
                    if pd.notna(f) and not isinstance(f, typ):
                        invalid.append(field)
        if len(invalid) == 0:
            return True, None
        return False, invalid
