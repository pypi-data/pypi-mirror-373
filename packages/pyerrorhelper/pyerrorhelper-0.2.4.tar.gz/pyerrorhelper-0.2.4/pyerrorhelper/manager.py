import sys
from pyerrorhelper.ollamembedder import OllamaEmbedder
import traceback
from pyerrorhelper.base import BaseErrorHandler
from types import TracebackType


class ErrorManager(BaseErrorHandler):
    def __init__(self) -> None:
        self.slm = OllamaEmbedder()
        self.old_hook = sys.excepthook

    def process_exception(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        tb_list = traceback.format_tb(exc_traceback)
        tb_output = "".join(tb_list)
        summary = self.slm.summarize(tb_output)
        print(summary)

    def install(self) -> None:
        sys.excepthook = self.process_exception

    def uninstall(self) -> None:
        sys.excepthook = self.old_hook
