"""The `treewidget` Module provides the `QuestionItem` and the `CategoryItem` item.

Those two are subclasses of `QTreeWidgetItem`, to provide an easy interface
of accessing the corresponding questions from the items.
"""

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem

from excel2moodle.core.dataStructure import Category
from excel2moodle.core.question import ParametricQuestion, Question

logger = logging.getLogger(__name__)


class QuestionItem(QTreeWidgetItem):
    def __init__(self, parent, question: Question | ParametricQuestion) -> None:
        super().__init__(parent)
        self.setData(2, Qt.UserRole, question)
        self.refresh()

    def refresh(self) -> None:
        question = self.question
        self.setText(0, question.id)
        self.setText(1, question.name)
        self.setText(2, str(question.points))
        if isinstance(question, ParametricQuestion):
            self.setText(3, str(question.parametrics.variants))

    @property
    def question(self) -> Question | ParametricQuestion:
        """Return the question Object the QTreeWidgetItem represents."""
        return self.data(2, Qt.UserRole)


class CategoryItem(QTreeWidgetItem):
    def __init__(self, parent, category: Category) -> None:
        super().__init__(parent)
        self.setData(2, Qt.UserRole, category)
        self.refresh()

    def updateVariantCount(self) -> None:
        var = self.getMaxVariants()
        if var != 0:
            self.setText(3, str(var))

    def iterateChildren(self):
        for child in range(self.childCount()):
            yield self.child(child)

    def getMaxVariants(self) -> int:
        count: int = 0
        for child in self.iterateChildren():
            q = child.question
            if isinstance(q, ParametricQuestion):
                count = max(q.parametrics.variants, count)
        return count

    @property
    def category(self) -> Category:
        return self.data(2, Qt.UserRole)

    def refresh(self) -> None:
        for child in self.iterateChildren():
            child.refresh()
        # Update category data, as it might have changed
        cat = self.category
        self.setText(0, cat.NAME)
        self.setText(1, cat.desc)
        self.setText(2, str(cat.points))
        self.updateVariantCount()
