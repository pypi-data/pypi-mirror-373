"""This Python program helps to create Moodle questions in less time.

The aim is to put alle the information for the questions into a spreadsheet
file, and then parse it, to generate Moodle compliant XML-Files.
Furthermore this program lets you create a single ``.xml``-File with a selection
of questions, that then can be imported to a Moodle-Test.

Concept
=========
The concept is, to store the different questions into categories of similar
types and difficulties of questions, for each of which, a separated sheet in
the Spreadsheet document should be created.

There Should be a sheet called *"Kategorien"*, where an overview over the
different categories is stored.
This sheet stores The names and descriptions, for all categories.
The name have to be the same as the actual sheet names with the questions.
Furthermore the points used for grading, are set in the "Kategorien" sheet

Functionality
===============
* Parse multiple Choice Questions, each into one XML file
* Parse Numeric Questions, each into one XML file
* create single XML File from a selection of questions
"""

import logging
from importlib import metadata
from importlib.metadata import version

try:
    __version__ = version("excel2moodle")
except Exception:
    __version__ = "unknown"

e2mMetadata: dict = {}
if __package__ is not None:
    meta = metadata.metadata(__package__)
    e2mMetadata = {
        "version": __version__,
        "name": meta["name"],
        "description": meta["summary"],
        "author": meta["author"],
        "license": meta["license-expression"],
        "documentation": "https://jbosse3.gitlab.io/excel2moodle",
        "homepage": meta["project-url"].split()[1],
        "issues": "https://gitlab.com/jbosse3/excel2moodle/issues",
        "funding": "https://ko-fi.com/jbosse3",
        "API_id": "jbosse3%2Fexcel2moodle",
    }


mainLogger = logging.getLogger(__name__)
