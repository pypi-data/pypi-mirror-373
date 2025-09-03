"""Main Function to make the Package executable."""

import logging.config as logConfig
import signal
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

import excel2moodle
from excel2moodle import __version__, e2mMetadata, mainLogger
from excel2moodle.core import dataStructure
from excel2moodle.core.settings import Settings, Tags
from excel2moodle.extra import updateQuery
from excel2moodle.logger import loggerConfig
from excel2moodle.ui import appUi as ui


def main() -> None:
    app = QApplication(sys.argv)
    excel2moodle.isMain = True
    settings = Settings()
    logfile = Path(settings.get(Tags.LOGFILE)).resolve()
    e2mMetadata["logfile"] = logfile
    if logfile.exists() and logfile.is_file():
        logfile.replace(f"{logfile}.old")
    logConfig.dictConfig(config=loggerConfig)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    database: dataStructure.QuestionDB = dataStructure.QuestionDB(settings)
    window = ui.MainWindow(settings, database)
    database.window = window
    window.show()
    # Update check
    latestTag = updateQuery.get_latest_tag(e2mMetadata.get("API_id"))
    if latestTag is None:
        mainLogger.warning(
            "Couldn't check for Updates, maybe there is  no internet connection"
        )
    if latestTag is not None and latestTag.strip("v") != __version__:
        mainLogger.warning(
            "A new Update is available: %s --> %s ", __version__, latestTag
        )
        changelog = updateQuery.get_changelog(e2mMetadata.get("API_id"))
        # Delay showing the update dialog slightly
        QTimer.singleShot(100, lambda: window.showUpdateDialog(changelog, latestTag))

    for k, v in e2mMetadata.items():
        msg = f"{k:^14s}:  {v}"
        mainLogger.info(msg)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
