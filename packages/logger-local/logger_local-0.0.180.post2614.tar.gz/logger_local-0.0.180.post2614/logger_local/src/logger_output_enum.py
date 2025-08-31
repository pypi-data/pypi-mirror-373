from enum import Enum


class LoggerOutputEnum(Enum):
    """
    LoggerOutputEnum

    Attributes:
        Console
        MySQLDatabase
        Logz.io
    """
    Console = "Console"
    MySQLDatabase = "MySQLDatabase"
    Logzio = "Logz.io"
