"""Implementations of all different question types.

For each question type supported by excel2moodle here are the implementations.
Two classes need to be defined for each type:

* The Question class subclassing core.Question()
* The Parser class subclassing core.Parser()

Both go into a module named ``excel2moodle.question_types.type.py``
"""

from enum import Enum

from excel2moodle.core.category import Category
from excel2moodle.question_types.cloze import ClozeQuestion
from excel2moodle.question_types.mc import MCQuestion
from excel2moodle.question_types.nf import NFQuestion
from excel2moodle.question_types.nfm import NFMQuestion


class QuestionTypeMapping(Enum):
    """The Mapping between question-types name and the classes."""

    MC = MCQuestion
    NF = NFQuestion
    NFM = NFMQuestion
    CLOZE = ClozeQuestion

    def create(
        self,
        category: Category,
        questionData: dict[str, str | int | float | list[str]],
        **kwargs,
    ):
        return self.value(category, questionData, **kwargs)
