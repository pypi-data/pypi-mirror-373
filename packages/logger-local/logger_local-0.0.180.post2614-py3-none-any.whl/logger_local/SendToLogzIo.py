import sys
from logging import LogRecord

from logzio.handler import LogzioHandler
from python_sdk_remote.mini_logger import MiniLogger as logger
from python_sdk_remote.utilities import our_get_env

LOGZIO_URL = "https://listener.logz.io:8071"
# "raise_if_not_found=False" as we want to support case when we don't provide the LOGZIO_TOKEN
LOGZIO_TOKEN: str = our_get_env("LOGZIO_TOKEN", raise_if_empty=False,
                                raise_if_not_found=False)

if LOGZIO_TOKEN:
    logzio_handler = LogzioHandler(token=LOGZIO_TOKEN, url=LOGZIO_URL, )
else:
    logzio_handler = None
    print("LOGZIO_TOKEN is not set, logs will not be sent to Logz.io")


# TODO Inherit from a new LoggerWriter pure virtual abstract class
class SendToLogzIo:
    @staticmethod
    def send_to_logzio(data: dict):
        if not logzio_handler:
            return
        try:
            log_record = CustomLogRecord(
                name="log",
                level=data.get('severity_id'),
                pathname=LOGZIO_URL,
                lineno=data.get("line_number"),
                msg=data.get('record'),
                args=data
            )
            if sys.meta_path:  # if sys.meta_path is None, Python is likely shutting down
                logzio_handler.emit(log_record)
        except Exception as exception:
            logger.error("Failed to send log to Logz.io", object={"exception": exception})


class CustomLogRecord(LogRecord):
    def __init__(self,
                 name: str,
                 level: int,
                 pathname: str,
                 lineno: int,
                 msg: str,
                 args,
                 exc_info=None,
                 func: str | None = None,
                 sinfo: str | None = None) -> None:
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)
        for key, value in args.items():
            # Logz.io use this later
            setattr(self, key, value)

    def getMessage(self):
        msg = str(self.msg)
        if self.args:
            try:
                msg = self.msg.format(*self.args)
            except Exception:
                pass
        return msg
