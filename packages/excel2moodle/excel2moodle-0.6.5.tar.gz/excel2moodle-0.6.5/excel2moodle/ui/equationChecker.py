import logging
import math
from pathlib import Path

from PySide6.QtWidgets import QWidget

from excel2moodle import mainLogger
from excel2moodle.core.question import ParametricQuestion
from excel2moodle.core.settings import Tags
from excel2moodle.logger import LogWindowHandler
from excel2moodle.question_types.nfm import NFMQuestionParser

from .UI_equationChecker import Ui_EquationChecker

logger = logging.getLogger(__name__)

loggerSignal = LogWindowHandler()
mainLogger.addHandler(loggerSignal)


class EqCheckerWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.excelFile = Path()
        self.ui = Ui_EquationChecker()
        self.ui.setupUi(self)
        self.ui.buttonRunCheck.clicked.connect(
            lambda: self.updateCalculation(),
        )
        self.question: ParametricQuestion

    def updateCalculation(self) -> None:
        equation = self.ui.equationText.toPlainText()
        results: list[float] = []
        firstResult = self.question.rawData.get(Tags.FIRSTRESULT)
        for i in range(self.question.variants):
            NFMQuestionParser.setupAstIntprt(self.question.variables, i)
            results.append(float(NFMQuestionParser.astEval(equation)))
        check: bool = False
        self.ui.textResultsOutput.insertHtml(f"<hr><br><h2>{equation:^30}</h2><br>")
        for i, calculation in enumerate(results):
            if i == 0 and firstResult != 0:
                check = bool(math.isclose(calculation, firstResult, rel_tol=0.01))
                self.ui.lineCalculatedRes.setText(f"{calculation}")
                self.ui.textResultsOutput.append(f"<h3>Result {check = }</h3><br>")
            self.ui.textResultsOutput.append(
                f"Ergebnis {i + 1}: \t{calculation}",
            )
        if check:
            self.ui.lineCheckResult.setText("[OK]")
            logger.info(
                " [OK] The first calculated result matches 'firstResult'",
            )
        else:
            self.ui.lineCheckResult.setText("[ERROR]")
            logger.warning(
                "The first calculated result does not match 'firstResult'",
            )

    def setup(self, question: ParametricQuestion) -> None:
        self.question = question
        self.ui.textResultsOutput.clear()
        self.ui.equationText.clear()
        bullets = question.rawData.get(Tags.BPOINTS)
        firstResult = question.rawData.get(Tags.FIRSTRESULT)
        self.ui.lineFirstResult.setText(str(firstResult))
        self.ui.equationText.appendPlainText(question.rawData.get(Tags.EQUATION))
        for bullet in bullets:
            self.ui.textResultsOutput.append(bullet)
        self.updateCalculation()
