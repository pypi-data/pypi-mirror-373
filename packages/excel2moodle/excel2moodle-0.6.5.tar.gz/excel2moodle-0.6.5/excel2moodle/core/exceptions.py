from excel2moodle.core.globals import Tags


class QNotParsedException(Exception):
    def __init__(self, message: str, qID: str | int, *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)
        self.qID = qID


class NanException(QNotParsedException):
    def __init__(self, message, qID, field, *args, **kwargs) -> None:
        super().__init__(message, qID, *args, **kwargs)
        self.field = field


class InvalidFieldException(Exception):
    def __init__(
        self,
        message: str,
        qID: str,
        field: Tags | list[Tags],
        *args: object,
        **kwargs,
    ) -> None:
        super().__init__(message, *args, **kwargs)
        self.field = field
        self.index = qID
