from types import TracebackType


class BaseErrorHandler:
    def process_exception(
        self,
        type: type[BaseException],
        value: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        pass
