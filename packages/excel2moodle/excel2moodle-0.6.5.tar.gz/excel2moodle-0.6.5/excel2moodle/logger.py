"""Logging Setup for Excel2moodle.

Mainly this sets up the general configuration.
This includes emitting the signals for the main Window, to fast forward all logs.
"""

import logging

from PySide6.QtCore import QObject, QSettings, Signal

from excel2moodle.core.settings import Settings, Tags

qSettings = QSettings("jbosse3", "excel2moodle")
settings = Settings()

loggerConfig = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[{levelname:^8s}] {module:.^14s}:  {message}",
            "style": "{",
        },
        "file": {
            "format": "%(asctime)s [%(levelname)-5s] %(name)12s: %(message)s",
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",  # Default is stderr
        },
        "file": {
            "level": "DEBUG",
            "formatter": "file",
            "class": "logging.FileHandler",
            # "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": qSettings.value(
                Tags.LOGFILE, defaultValue=Tags.LOGFILE.default
            ),
            # "when": "M",
            # "interval": 1,
            # "backupCount": "3",
            "delay": "true",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "excel2moodle.questionParser": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "__main__": {  # if __name__ == '__main__'
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


class QSignaler(QObject):
    signal = Signal(str)


class LogWindowHandler(logging.Handler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.emitter = QSignaler()
        # Define a formatter with log level and module
        log_format = "[%(levelname)s] %(module)s: %(message)s"
        self.formatter = logging.Formatter(log_format)
        self.setFormatter(self.formatter)
        loglevel = settings.get(Tags.LOGLEVEL)
        self.setLevel(loglevel)
        self.logLevelColors = {
            "DEBUG": "gray",
            "INFO": "green",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "pink",
        }

    def handle(self, record) -> bool:
        info = record.exc_info
        if record.exc_info:
            excType, excVal, excTraceB = record.exc_info
            exc_info_msg = f"[{excType.__name__}]: <b>{excVal}</b>"
            record.exc_text = exc_info_msg
            record.exc_info = None
        try:
            super().handle(record)
        finally:
            record.exc_info = info
            record.exc_text = None
        return True

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the signal, with a new logging message."""
        log_message = self.format(record)
        msg = log_message.replace("\n", "<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        color = self.logLevelColors.get(record.levelname, "black")
        prettyMessage = f'<span style="color:{color};">{msg}</span>'
        self.emitter.signal.emit(prettyMessage)


class LogAdapterQuestionID(logging.LoggerAdapter):
    """Prepend the Question ID to the logging messages."""

    def process(self, msg, kwargs):
        """Append the Question ID to the log Message."""
        return "[{}]: {}".format(self.extra["qID"], msg), kwargs
