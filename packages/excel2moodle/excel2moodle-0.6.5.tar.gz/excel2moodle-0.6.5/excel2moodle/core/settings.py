"""Settings module provides the adjusted subclass of ``PySide6.QtCore.QSettings``."""

import logging
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Literal, overload

logger = logging.getLogger(__name__)


class Tags(StrEnum):
    """Tags and Settings Keys are needed to always acess the correct Value.

    The Tags can be used to acess the settings or the QuestionData respectively.
    As the QSettings settings are accesed via strings, which could easily gotten wrong.
    Further, this Enum defines, which type a setting has to be.
    """

    def __new__(
        cls,
        key: str,
        typ: type,
        default: str | float | Path | bool | None,
        place: str = "project",
    ) -> object:
        """Define new settings class."""
        obj = str.__new__(cls, key)
        obj._value_ = key
        obj._typ_ = typ
        obj._default_ = default
        obj._place_ = place
        return obj

    def __init__(
        self,
        _,
        typ: type,
        default: str | float | Path | None,
        place: str = "project",
    ) -> None:
        self._typ_: type = typ
        self._place_: str = place
        self._default_ = default
        self._full_ = f"{self._place_}/{self._value_}"

    @property
    def default(self) -> str | int | float | Path | bool | None:
        """Get default value for the key."""
        return self._default_

    @property
    def place(self) -> str:
        return self._place_

    @property
    def full(self) -> str:
        return self._full_

    def typ(self) -> type:
        """Get type of the keys data."""
        return self._typ_

    QUESTIONVARIANT = "defaultquestionvariant", int, 1, "testgen"
    INCLUDEINCATS = "includecats", bool, False, "testgen"
    GENEXPORTREPORT = "exportreport", bool, False, "testgen"
    TOLERANCE = "tolerance", float, 0.01, "parser/nf"
    PICTUREFOLDER = "pictureFolder", Path, None, "core"
    PICTURESUBFOLDER = "imgfolder", str, "Abbildungen", "project"
    SPREADSHEETPATH = "spreadsheetFolder", Path, None, "core"
    LOGLEVEL = "loglevel", str, "INFO", "core"
    LOGFILE = "logfile", str, "excel2moodleLogFile.log", "core"
    CATEGORIESSHEET = "categoriessheet", str, "Kategorien", "core"

    IMPORTMODULE = "importmodule", str, None
    TEXT = "text", list, None
    BPOINTS = "bulletpoint", list, None
    TRUE = "true", list, None
    FALSE = "false", list, None
    TYPE = "type", str, None
    NAME = "name", str, None
    RESULT = "result", float, None
    EQUATION = "formula", str, None
    PICTURE = "picture", str, None
    NUMBER = "number", int, None
    ANSTYPE = "answertype", str, None
    QUESTIONPART = "part", list, None
    PARTTYPE = "parttype", str, None
    POINTS = "points", float, 1.0
    PICTUREWIDTH = "imgwidth", int, 500
    ANSPICWIDTH = "answerimgwidth", int, 120
    FIRSTRESULT = "firstresult", float, 0
    WRONGSIGNPERCENT = "wrongsignpercent", int, 50
    WRONGSIGNFB = "wrongsignfeedback", str, "your result has the wrong sign (+-)"
    TRUEFB = "truefeedback", str, "congratulations!!! your answer is right."
    FALSEFB = "falsefeedback", str, "Your answer is sadly wrong, try again!!!"
    PCORRECFB = "partialcorrectfeedback", str, "Your answer is partially right."
    GENERALFB = "feedback", str, "You answered this question."

    MEDIASCRIPTS = "mediascripts", list, None
    MEDIACALL = "parametricmedia", str, None


class Settings:
    values: ClassVar[dict[str, str | float | Path | list]] = {}

    def __contains__(self, tag: Tags) -> bool:
        return bool(tag in type(self).values)

    @classmethod
    def clear(cls) -> None:
        cls.values.clear()

    @classmethod
    def pop(cls, key: str):
        return cls.values.pop(key)

    @overload
    @classmethod
    def get(
        cls,
        key: Literal[Tags.POINTS],
    ) -> float: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[
            Tags.QUESTIONVARIANT,
            Tags.TOLERANCE,
            Tags.PICTUREWIDTH,
            Tags.ANSPICWIDTH,
            Tags.WRONGSIGNPERCENT,
        ],
    ) -> int: ...
    @overload
    @classmethod
    def get(cls, key: Literal[Tags.INCLUDEINCATS, Tags.GENEXPORTREPORT]) -> bool: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[
            Tags.PICTURESUBFOLDER,
            Tags.LOGLEVEL,
            Tags.LOGFILE,
            Tags.CATEGORIESSHEET,
            Tags.IMPORTMODULE,
            Tags.WRONGSIGNFB,
        ],
    ) -> str: ...
    @overload
    @classmethod
    def get(
        cls,
        key: Literal[Tags.PICTUREFOLDER, Tags.SPREADSHEETPATH],
    ) -> Path: ...

    @classmethod
    def get(cls, key: Tags):
        """Get the typesafe settings value.

        If no setting is made, the default value is returned.
        """
        try:
            raw = cls.values[key]
        except KeyError:
            default = key.default
            if default is None:
                return None
            logger.debug("Returning the default value for %s", key)
            return default
        if key.typ() is Path:
            path: Path = Path(raw)
            try:
                path.resolve(strict=True)
            except ValueError:
                logger.warning(
                    f"The settingsvalue {key} couldn't be fetched with correct typ",
                )
                return key.default
            logger.debug("Returning path setting: %s = %s", key, path)
            return path
        try:
            return key.typ()(raw)
        except (ValueError, TypeError):
            logger.warning(
                f"The settingsvalue {key} couldn't be fetched with correct typ",
            )
            return key.default

    @classmethod
    def set(
        cls,
        key: Tags | str,
        value: float | bool | Path | str,
    ) -> None:
        """Set the setting to value."""
        if key in Tags:
            tag = Tags(key) if not isinstance(key, Tags) else key
            try:
                cls.values[tag] = tag.typ()(value)
            except TypeError:
                logger.exception(
                    "trying to save %s = %s %s with wrong type not possible.",
                    tag,
                    value,
                    type(value),
                )
                return
            logger.info("Saved  %s = %s: %s", key, value, tag.typ().__name__)
        else:
            logger.warning("got invalid local Setting %s = %s", key, value)
