"""Script for verifying the equations written into the ``result`` field of NFM-type Question.

This script does two things.

#. It calculates all the answers obtained from the series of variables.
#. It compares the calculation of the first answer to the ``firstResult`` field.

Usage
=====

From the main UI
----------------

#. Start this tool from the top bar in the main Window under the *Tools* section
#. A new window will open inside you:
#. Enter the Number of the Category
#. Enter the Number of the Question
#. Click on ``Run check now`` and Inspect the results
#. Rinse and repeat

As Script
---------

#. Start this script with ``py -m excel2moodle.extra.equationVerification`` inside the top-level Directory
#. Enter the Number of the Category
#. Enter the Number of the Question
#. Inspect the results
#. Rinse and repeat
"""

from pathlib import Path

import pandas as pd

# Hier Bitte die Frage angeben, die getestet Werden soll:

# ===========================================================


def checkResult(checkerValue: float, calculation: float, tolerance=0.01) -> bool:
    """Checks if the two Arguments are within the tolerance the same value.

    :param checkerValue: the value the calculation is compared against
    :type checkerValue: fleat
    :param calculation: the value to be compared against checker Value
    :type calculation: float
    :param tolerance: the standart tolerance is 0.01 -> 1%
    :type tolerance: float, optional

    :returns:
        True if checkerValue == calculation
        False if checkerValue != calculation
    :rtype: bool
    """
    upper = abs(checkerValue + checkerValue * tolerance)
    lower = abs(checkerValue - checkerValue * tolerance)
    return bool(abs(calculation) > lower and abs(calculation) < upper)


def equationChecker(
    categoryName: str, qNumber: int, spreadsheetFile
) -> tuple[list[str], list[float], float]:
    """This Function calculates all Results an invokes the checkResult function.

    Parameters
    ----------
    categoryName : str
        The category in which the question to be tested is
        This must match a sheet name of the spreadsheet
    qNumber : int
        The number of the question which results are tested
    spreadsheetFile : Path
        The Filepath to the spreadsheet

    Returns
    -------
    bulletPointsString : list[str]
        The string list with the bullet points, with numeric values instead of variables
    results : list[str]
        The list with the calculated results
    checkerValue : float
        The value taken from the ``firstResult`` field

    """
    spreadsheetFile.resolve()
    df = pd.read_excel(spreadsheetFile, sheet_name=categoryName, index_col=0)
    eq = df.loc["result"][qNumber]
    bps = df.loc["bulletPoints"][qNumber]
    try:
        res = float(df.loc["firstResult"][qNumber])
    except Exception:
        res = 0
    bps, calcs = nmq.parseNumericMultiQuestion(df, bps, eq, qNumber)
    return bps, calcs, res


def main(
    spreadsheetFile=Path("../Fragensammlung/Main_question_all.xlsx"),
    catN=None,
    qNumber=None,
) -> None:
    """Takes the Spreadsheet, and asks for a category and a question number."""
    if catN is None:
        catN = input("Geben Sie die Kategorie an: KAT_")
    categoryName = f"KAT_{catN}"
    if qNumber is None:
        qNumber = int(input("Geben Sie die Fragennummer an: "))
    bullets, results, firstResult = equationChecker(
        categoryName, qNumber, spreadsheetFile=spreadsheetFile
    )
    check = False

    for i, calculation in enumerate(results):
        if i == 0 and firstResult != 0:
            check = checkResult(firstResult, calculation)

    if check:
        pass
    else:
        pass


if __name__ == "__main__":
    spreadsheet = input("Geben Sie den Pfad zu dem spreadsheet an:")
    while True:
        main(Path(spreadsheet))
