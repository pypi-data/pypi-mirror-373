from enum import Enum


# TODO Can we use the enum from python-sdk-remote-python-package/python_sdk_remote/src/constants_src_mini_logger.py and delete it from here.  # noqa E501
class MessageSeverity(Enum):
    Debug = 100
    Verbose = 200
    Init = 300
    Start = 400
    End = 402
    Information = 500
    Warning = 600
    Error = 700
    Critical = 800
    Exception = 900
