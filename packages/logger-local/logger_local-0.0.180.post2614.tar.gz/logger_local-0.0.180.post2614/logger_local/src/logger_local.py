# TODO One class in each file

# TODO Update the __version__ automatically
__version__ = "0.0.179-2614"  # Package version

import inspect
import json
import logging
import os
import random
import re
import string
import sys
import threading
import traceback
from datetime import date
from functools import lru_cache

# import haggis.logs
from python_sdk_remote.mini_logger import MiniLogger
from python_sdk_remote.utilities import our_get_env, get_environment_name, deprecation_warning_function
from user_context_remote.user_context import UserContext

from .component import Component
from .logger_fields import LoggerFields
from .logger_output_enum import LoggerOutputEnum
from .message_severity import MessageSeverity
from .send_to_logzIo import SendToLogzIo
from .writer import Writer
from .debug_mode import DebugMode

# TODO We prefer to change it to True
global_write_to_logzio = False

logzio_token = our_get_env("LOGZIO_TOKEN", raise_if_not_found=False)
if logzio_token is None:
    global_write_to_logzio = False

logzio_url = "https://listener.logz.io:8071"
# TODO Replace all strings with constants/enum used across the product
COMPUTER_LANGUAGE = "Python"
loggers = {}
mandatory_fields_by_class = {}  # used by the MetaLogger

# TODO: ipv4 ipv6
# TODO: another severity for custom end
# TODO: save records on buffer before sending to sql to improve performance


# TODO Add optional parameter to logger.start()
#  which called api_call, so logger.start will call api_management
#  to insert into api_call_table all fields including session_id.

session_length = 30
# TODO: verify the session is unique?
session = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(session_length))
# We must display the session when created, so we can debug. do not delete the bellow line
print('LoggerLocal.py session=' + session)

# TODO Convert MYSQL to enum
MYSQL = 'MySQL'


# TODO Rename Logger to LoggerLocal and create Logger for backward compatibility (As we should have two classes with different names LoggerLocal and LoggerRemote)  # noqa
class Logger(logging.Logger):
    @staticmethod
    def __get_base_logger(mandatory_fields, **kwargs) -> None:
        # This method is called by the metaclass to get the mandatory fields from the base classes in inheritance
        # This is needed because the metaclass is called before the __init__ method
        # Alternatively, we can return a logging.getLogger(), as those are not used in such cases,
        # but we might miss cases where the user forget to provide the mandatory fields
        mandatory_fields_to_cache = {k: v for k, v in kwargs['object'].items() if k in mandatory_fields}
        if mandatory_fields_to_cache and 'class' in kwargs.get('object', {}):
            mandatory_fields_by_class[kwargs['object']['class']] = mandatory_fields_to_cache
        if 'bases' in kwargs.get('object', {}):
            for base in kwargs['object']['bases']:
                cached_mandatory_fields = mandatory_fields_by_class.get(base.__name__, {})
                if cached_mandatory_fields:
                    kwargs['object'].update(cached_mandatory_fields)
                    break

            if not all(k in kwargs.get('object', {}) for k in mandatory_fields):
                # (I am not so sure if it is needed)
                for base in kwargs['object']['bases']:
                    if hasattr(base, 'logger'):  # if some base has logger attribute, use its mandatory fields
                        kwargs['object'].update({k: v for k, v in base.logger.additional_fields.items()})

    @staticmethod
    def create_logger(**kwargs):

        # Add deprecation warning message if we have developer_email and not developer_email_address  # noqa E501

        # Backward compatibility
        OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME = 'developer_email'
        DEVELOPER_EMAIL_ADDRESS_FIELD_NAME = 'developer_email_address'
        if kwargs.get('object', {}).get(OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME):  # noqa E501
            CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX: str = f"logger-local-python logger_local.py create_logger() TODO Please change {OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME} to {DEVELOPER_EMAIL_ADDRESS_FIELD_NAME} in the logger object of component_id="  # noqa E501
            if 'object' in kwargs and 'component_id' in kwargs['object']:
                CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX += " component_id=" + str(kwargs['object']['component_id'])  # noqa E501
            if 'object' in kwargs and 'componentId' in kwargs['object']:
                CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX += " componentId=" + str(kwargs['object']['componentId'])  # noqa E501
            if 'object' in kwargs and 'component_name' in kwargs['object']:
                CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX += " component_name=" + kwargs['object']['component_name']  # noqa E501
            if 'object' in kwargs and 'componentName' in kwargs['object']:
                CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX += " componentName=" + kwargs['object']['componentName']  # noqa E501
            # TODO Please change print() to a new logger.todo_change_json_field()
            print("LoggerLocal.py create_logger() " + CREATE_LOGGER_OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME_MESSAGE_PREFIX)
            deprecation_warning_function(OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME,
                                         DEVELOPER_EMAIL_ADDRESS_FIELD_NAME)  # noqa E501
            # Selfheal
            kwargs['object'][DEVELOPER_EMAIL_ADDRESS_FIELD_NAME] = \
                kwargs['object'].pop(OLD_DEVELOPER_EMAIL_ADDRESS_FIELD_NAME)

        # TODO Shall we support also camelCase?
        mandatory_fields = ('component_id', 'component_name',
                            'component_category',
                            DEVELOPER_EMAIL_ADDRESS_FIELD_NAME)
        Logger.__get_base_logger(mandatory_fields, **kwargs)

        # TODO Enable this feature flag when we support for example: both component_id and componentId
        IS_ENABLE_CHECKING_THE_MANDATORY_FIELDS: bool = False
        if (not IS_ENABLE_CHECKING_THE_MANDATORY_FIELDS):
            # TODO Check if we don't have both componentId and component_id and have a dedicated warning message
            if not all(k in kwargs.get('object', {}) for k in mandatory_fields):
                # TODO When running in debug_mode, a more specific error message, which field is missing  # noqa E501
                # TODO Make the message dynamic based on mandatory_fields
                raise Exception("Logger PACKAGE_VERSION=" + __version__ + " create_logger() Please insert component_id, component_name, component_category and developer_email_address "  # noqa E501
                                f"in the object sent to the logger (not {kwargs.get('object', {})})")

        # get cached logger if exists or create a new one
        component_id = int(kwargs['object']['component_id'])
        component_category = kwargs['object']['component_category']
        unique_logger_key = (component_id, component_category)

        if unique_logger_key in loggers and not kwargs.get('ignore_cached_logger', False):
            return loggers.get(unique_logger_key)
        else:
            logger = Logger(**kwargs)
            loggers[unique_logger_key] = logger
            return logger

    def __init__(self, *,
                 handler: logging.Handler = logging.StreamHandler(stream=sys.stdout),
                 formatter: logging.Formatter = None,
                 level: int | str = None,
                 **kwargs) -> None:
        self._is_write_to_sql = False  # Override LOGGER_IS_WRITE_TO_SQL manually

        self.debug_mode = DebugMode(logger_minimum_severity=level)
        self.component_id = int(kwargs['object']['component_id'])
        self.logger_table_fields = {}
        self.update_logger_table_fields()
        self.user_context = None
        self.additional_fields = kwargs['object'].copy()
        self.additional_fields["session"] = session

        self.logger = self.initiate_logger(handler=handler, formatter=formatter,
                                           level=self.debug_mode.logger_minimum_severity)
        self.logger.name = kwargs['object']['component_name']

        super().__init__(name=self.logger.name)

    @staticmethod
    def initiate_logger(*, handler: logging.Handler = logging.StreamHandler(stream=sys.stdout),  # noqa E501
                        formatter: logging.Formatter = None,
                        level: int = None) -> logging.Logger:

        # logging levels: INFO = 20, DEBUG = 10
        # Python 3.13.3 doesn't support haggis due to _acquireLock changes
        # Implement custom logging level addition compatible with Python 3.13.3
        # try:
        #     # Try using haggis first (for backward compatibility with older Python versions)
        #     haggis.logs.add_logging_level(level_name="VERBOSE", level_num=logging.DEBUG + 1, method_name="verbose")
        #     haggis.logs.add_logging_level(level_name="INIT", level_num=logging.DEBUG + 2, method_name="init")
        #     haggis.logs.add_logging_level(level_name="START", level_num=logging.DEBUG + 3, method_name="start")
        #     haggis.logs.add_logging_level(level_name="END", level_num=logging.DEBUG + 4, method_name="end")
        # except Exception:
        #     # Fall back to direct implementation for Python 3.13.3+
        def add_custom_level(level_name, level_num, method_name):
            # Add the custom level to the logging module
            if not hasattr(logging, level_name):
                setattr(logging, level_name, level_num)
                logging.addLevelName(level_num, level_name)

            # Add the method to the Logger class
            def log_for_level(self, message, *args, **kwargs):
                if self.isEnabledFor(level_num):
                    self._log(level_num, message, args, **kwargs)

            def log_to_root(message, *args, **kwargs):
                logging.log(level_num, message, *args, **kwargs)

            setattr(logging.Logger, method_name, log_for_level)
            setattr(logging, method_name, log_to_root)

        # Add our custom logging levels
        add_custom_level("VERBOSE", logging.DEBUG + 1, "verbose")
        add_custom_level("INIT", logging.DEBUG + 2, "init")
        add_custom_level("START", logging.DEBUG + 3, "start")
        add_custom_level("END", logging.DEBUG + 4, "end")

        if not formatter:
            if isinstance(handler, logging.StreamHandler) and stream_supports_colour(handler.stream):
                formatter = _ColourFormatter()
            else:
                dt_fmt = '%H:%M:%S'  # '%Y-%m-%d %H:%M:%S'
                formatter = logging.Formatter('[{asctime}] [{levelname:<8}]: {message}', dt_fmt, style='{')
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.propagate = False  # Prevents the log messages from being displayed multiple times.

        our_levels_to_logging = {
            MessageSeverity.Debug: logging.DEBUG,
            MessageSeverity.Verbose: logging.VERBOSE,  # noqa
            MessageSeverity.Init: logging.INIT,  # noqa
            MessageSeverity.Start: logging.START,  # noqa
            MessageSeverity.End: logging.END,  # noqa
            MessageSeverity.Information: logging.INFO,
            MessageSeverity.Warning: logging.WARNING,
            MessageSeverity.Error: logging.ERROR,
            MessageSeverity.Exception: logging.ERROR,
            MessageSeverity.Critical: logging.CRITICAL,
        }
        # Debug = 100, Verbose = 200. If level = 101 we want the one that is bigger than 101, i.e. Verbose
        level = min(our_levels_to_logging.keys(),
                    key=lambda x: x.value if x.value >= level else MessageSeverity.Debug.value)

        logger.setLevel(our_levels_to_logging[MessageSeverity(level)])
        logger.addHandler(handler)
        return logger

    def __log(self, *, function, message_severity: MessageSeverity, log_message, **kwargs) -> dict:
        logger_ids_dict = {}
        # This method is called A LOT of times, so we have to make sure it's very efficient
        write_to_console = self.debug_mode.is_logger_output(
            component_id=self.component_id, logger_output=LoggerOutputEnum.Console,
            severity_level=message_severity.value)
        write_to_sql = self._is_write_to_sql or self.debug_mode.is_logger_output(
            component_id=self.component_id, logger_output=LoggerOutputEnum.MySQLDatabase,
            severity_level=message_severity.value)
        write_to_logzio = global_write_to_logzio & self.debug_mode.is_logger_output(
            component_id=self.component_id, logger_output=LoggerOutputEnum.Logzio,
            severity_level=message_severity.value)
        if not any((write_to_console, write_to_sql, write_to_logzio)):
            return

        if kwargs:
            kwargs = obfuscate_log_dict(kwargs)

        if 'extra_kwargs' in kwargs.get('object', {}):  # from meta logger
            extra_kwargs = kwargs['object']['extra_kwargs']
            kwargs['object'].pop('extra_kwargs', None)
        else:
            extra_kwargs = {}

        depth = 3 if "is_meta_logger" not in kwargs else 4  # 1 for the meta wrapper
        function_name = kwargs.get('object', {}).get('function_name', extra_kwargs.get(
            'path', self.get_current_function_name(depth=depth)))
        if write_to_console and (log_message or kwargs):
            # filter empty logger.start() and logger.end()
            log_string = function_name
            if log_message:
                log_string += " " + log_message
            if kwargs:
                log_string += " | " + "kwargs=" + str(kwargs.get('object', kwargs))
            function(log_string)

        if not write_to_sql and not write_to_logzio:
            return

        log_object = {
            'severity_id': message_severity.value,
            'severity_name': message_severity.name
        }
        if log_message:
            log_object['log_message'] = log_message

        if isinstance(kwargs.get('object', {}).get('exception'), Exception):
            exception = kwargs['object']['exception']
            stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)
            del kwargs['object']['exception']
            kwargs['object']['error_stack'] = str(stack_trace)
            kwargs['object']['severity_id'] = MessageSeverity.Exception.value
            kwargs['object']["is_assertion_error"] = isinstance(exception, AssertionError)

        if 'object' not in kwargs:
            kwargs['object'] = {}
        kwargs['object'].update(log_object)
        if extra_kwargs:
            kwargs['object'].update(extra_kwargs)
        kwargs = self.insert_to_payload_extra_vars(**kwargs)
        self.insert_to_object(**kwargs)

        kwargs['object']['function_name'] = function_name
        kwargs['object'] = {k: str(v) for k, v in kwargs['object'].items()}  # json serializable

        print("Logger.__log kwargs['object']", kwargs['object'])
        if write_to_sql:
            logger_ids_dict[MYSQL] = Writer().add_message_and_payload(str(log_message), kwargs['object'])
        if write_to_logzio:
            logger_ids_dict['lozzio'] = SendToLogzIo.send_to_logzio(kwargs['object'])

        return logger_ids_dict

    def init(self, log_message: str = None, **kwargs):
        # TODO: Why do we need it?
        self.__log(function=self.logger.init,  # noqa
                   message_severity=MessageSeverity.Init,
                   log_message=log_message, **kwargs)

    def start(self, log_message: str = None, **kwargs) -> dict:

        start_logger_ids_dict: dict = \
            self.__log(function=self.logger.start,  # noqa
                       message_severity=MessageSeverity.Start,
                       log_message=log_message,
                       **kwargs)
        return start_logger_ids_dict

    def end(self, log_message: str = None, **kwargs) -> dict:
        end_logger_ids_dict: dict = \
            self.__log(function=self.logger.end,  # noqa
                       message_severity=MessageSeverity.End,
                       log_message=log_message,
                       **kwargs)
        return end_logger_ids_dict

    def info(self, log_message: str = None, **kwargs) -> dict:
        info_logger_ids_dict: dict = \
            self.__log(function=self.logger.info, message_severity=MessageSeverity.Information,
                       log_message=log_message, **kwargs)
        return info_logger_ids_dict

    def warning(self, log_message: str = None, **kwargs) -> dict:
        warning_logger_ids_dict: dict = \
            self.__log(function=self.logger.warning, message_severity=MessageSeverity.Warning, log_message=log_message,
                       **kwargs)
        return warning_logger_ids_dict

    def debug(self, log_message: str = None, **kwargs) -> dict:
        debug_logger_ids_dict: dict = \
            self.__log(function=self.logger.debug, message_severity=MessageSeverity.Debug, log_message=log_message,
                       **kwargs)
        return debug_logger_ids_dict

    def critical(self, log_message: str = None, **kwargs) -> dict:
        critical_logger_ids_dict: dict = \
            self.__log(function=self.logger.critical, message_severity=MessageSeverity.Critical, log_message=log_message,
                       **kwargs)
        return critical_logger_ids_dict

    def verbose(self, log_message: str = None, **kwargs) -> dict:
        verbose_logger_ids_dict: dict = \
            self.__log(function=self.logger.verbose,  # noqa
                       message_severity=MessageSeverity.Verbose, log_message=log_message, **kwargs)
        return verbose_logger_ids_dict

    def error(self, log_message: str = None, **kwargs) -> dict:
        if isinstance(kwargs.get('object'), Exception):
            kwargs['object'] = {"exception": kwargs['object']}
        error_logger_ids_dict: dict = \
            self.__log(function=self.logger.error, message_severity=MessageSeverity.Error, log_message=log_message,
                       **kwargs)
        return error_logger_ids_dict

    def exception(self, log_message: str = None, **kwargs) -> None:
        """This method should be called only in tests / top level functions / api calls.
        (not when invoking `raise` after catching an exception,
            otherwise the traceback will be wrong and logged multiple times)
        """
        exception_object = None
        if 'object' in kwargs:
            if isinstance(kwargs['object'], Exception):
                exception_object = kwargs['object']
                kwargs['object'] = {"exception": kwargs['object']}
            elif 'exception' in kwargs['object']:
                exception_object = kwargs['object']['exception']

        # We use logger.error because we don't want to print the traceback multiple times.  # noqa E501
        exception_logger_ids_dict: dict = \
            self.__log(function=self.logger.error,
                       message_severity=MessageSeverity.Exception,
                       log_message=log_message,
                       **kwargs)
        # TODO Add the exception_logger_ids_dict
        if exception_object:
            # Add logger IDs to exception object
            if hasattr(exception_object, 'logger_ids'):
                exception_object.logger_ids = exception_logger_ids_dict
            else:
                setattr(exception_object, 'logger_ids', exception_logger_ids_dict)
            raise exception_object
        else:
            raise Exception(log_message + str(exception_logger_ids_dict))

    # deprecate
    @lru_cache(maxsize=64)  # don't print the same warning multiple times
    def deprecation_warning(self, old_name: str, new_name: str,
                            start_date: date = None,
                            message: str = None) -> None:
        if start_date and start_date < date.today():
            return
        warnings_message = f"Please use {new_name} instead of {old_name} message={message}."  # noqa E501
        try:
            warnings_message += " Called from: " + inspect.stack()[2].filename
        except Exception:
            pass
        self.warning(warnings_message)

    def _insert_variables(self, **kwargs):
        object_data = kwargs.get("object", {})
        self.logger_table_fields.update(object_data)
        self.additional_fields.update(object_data)

    def insert_to_object(self, **kwargs):
        object_data = kwargs.get("object", {})
        object_data.update({field: field_value for field, field_value in self.logger_table_fields.items()
                            if field_value is not None})

    def update_logger_table_fields(self) -> None:
        # LOGGER_IS_WRITE_TO_SQL can be True, False or None.
        logger_table_fields = LoggerFields.get_logger_table_fields()
        if logger_table_fields:
            for field in logger_table_fields:
                self.logger_table_fields[field] = None

    def clean_variables(self):
        for field in self.logger_table_fields:
            self.logger_table_fields[field] = None
        self.additional_fields.clear()

    def insert_to_payload_extra_vars(self, **kwargs):
        try:
            # TODO I think we can't get the effective user/profile this way
            self.user_context = UserContext()
        except Exception as exception:
            MiniLogger.exception("Error while trying to login using user identification and password", exception)  # noqa
            # exception("Error while trying to login using user identification and password", exception)  # noqa
        message: str = kwargs['object'].pop('message', None)
        depth = 4 if "is_meta_logger" not in kwargs else 5  # 1 for the meta wrapper
        kwargs['object']['filename'] = kwargs['object'].get('filename', self.get_filename(depth=depth))
        kwargs['object']['path'] = kwargs['object'].get('path', self.get_path(depth=depth))
        kwargs['object']['class_name'] = kwargs['object'].get('class_name', self.get_calling_class(depth=depth))
        kwargs['object']['line_number'] = self.get_calling_line_number(depth=depth)
        kwargs['object']['environment'] = get_environment_name()
        kwargs['object']['computer_language'] = COMPUTER_LANGUAGE
        kwargs['object']['thread_id'] = threading.get_native_id()
        kwargs['object']['process_id'] = os.getpid()

        if self.user_context is not None:
            kwargs['object']['real_name'] = self.user_context.get_real_name()
            kwargs['object']['user_identifier'] = our_get_env("PRODUCT_USER_IDENTIFIER")
            kwargs['object']['created_effective_profile_id'] = self.user_context.get_effective_profile_id()
            kwargs['object']['created_effective_user_id'] = self.user_context.get_effective_user_id()
            kwargs['object']['created_real_user_id'] = self.user_context.get_real_user_id()
            kwargs['object']['created_user_id'] = self.user_context.get_real_user_id()
            kwargs['object']['updated_effective_profile_id'] = self.user_context.get_effective_profile_id()
            kwargs['object']['updated_effective_user_id'] = self.user_context.get_effective_user_id()
            kwargs['object']['updated_real_user_id'] = self.user_context.get_real_user_id()
            kwargs['object']['updated_user_id'] = self.user_context.get_real_user_id()

        kwargs['object'].update({field: field_value for field, field_value in self.logger_table_fields.items()
                                 if field_value is not None})
        kwargs['object'].update(self.additional_fields)
        component_json = self.get_component_json(self.component_id)
        if component_json:
            for field in component_json.keys():
                if field not in kwargs['object']:
                    field_value = component_json[field]
                    if field_value is not None:
                        kwargs['object'][field] = field_value
        if message is not None:
            kwargs['object']['message'] = message
        object_data = kwargs.get("object", {})
        object_data["record"] = json.dumps({key: str(value) for key, value in object_data.items()
                                            if key not in self.logger_table_fields})
        object_data = {key: value for key, value in object_data.items() if key in self.logger_table_fields}
        kwargs["object"] = object_data
        return kwargs

    @staticmethod
    def get_filename(depth: int) -> str:
        return os.path.basename(Logger.get_path(depth))

    @staticmethod
    def get_path(depth: int) -> str:
        return inspect.stack()[depth].filename

    @staticmethod
    def get_current_function_name(depth: int):
        stack = inspect.stack()
        # 0 = 'get_current_function_name', 1 = '__log', 2 = start/end/info...
        caller_frame = stack[depth]
        function_name = caller_frame.function
        return function_name

    @staticmethod
    def get_calling_class(depth: int) -> str:
        stack = inspect.stack()
        calling_module = inspect.getmodule(stack[depth].frame)
        return calling_module.__name__ if calling_module else None

    @staticmethod
    def get_calling_line_number(depth: int) -> int:
        stack = inspect.stack()
        calling_frame = stack[depth]
        return calling_frame.lineno

    def get_component_json(self, component_id: int) -> dict:
        component_json = Component.get_details_by_component_id(component_id)
        # TODO component_json != None and
        if component_json != {}:
            self.logger_table_fields.update(component_json)
        return component_json

    def is_component_complete(self):
        is_component_complete_result = (getattr(self, 'component_name') is None or
                                        getattr(self, 'component_type') is None or
                                        getattr(self, 'component_category') is None or
                                        getattr(self, 'testing_framework') is None or
                                        getattr(self, 'api_type') is None
                                        )
        return is_component_complete_result

    # TODO Shall we use set_...() or ...(is_write_to_sql: bool)
    def set_is_write_to_sql(self, is_write_to_sql: bool) -> None:
        # TODO We have self._is_write_to_sql and DebugMode.is_write_to_sql maybe both should use DebugMode.is_write_to_sql  # noqa E501
        # TODO How it is using LOGGER_IS_WRITE_TO_SQL?
        self._is_write_to_sql = is_write_to_sql
        # I think we prefer not to call MiniLogger to avoid circular calls
        MiniLogger.info(f"_is_write_to_sql={self._is_write_to_sql}")

    def get_is_write_to_sql(self) -> bool:
        return self._is_write_to_sql


# Copyright: https://github.com/Rapptz/discord.py/blob/master/discord/utils.py#L1241
def is_docker() -> bool:
    path = '/proc/self/cgroup'
    is_docker_result = os.path.exists('/.dockerenv') or (os.path.isfile(path) and any('docker' in line for line in open(path)))
    return is_docker_result


def stream_supports_colour(stream) -> bool:
    # Pycharm and Vscode support colour in their inbuilt editors
    colors_in_logs = our_get_env("LOGGER_COLORS_IN_LOGS", "")
    if colors_in_logs.lower() == "true":
        return True
    elif colors_in_logs.lower() == "false":
        return False

    if 'PYCHARM_HOSTED' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode':
        return True

    is_a_tty = hasattr(stream, 'isatty') and stream.isatty()  # TTY = terminal
    if sys.platform != 'win32':
        # Docker does not consistently have a tty attached to it
        stream_supports_colour_result = is_a_tty or is_docker()
        return stream_supports_colour_result

    # ANSICON checks for things like ConEmu
    # WT_SESSION checks if this is Windows Terminal
    stream_supports_colour_result = is_a_tty or ('ANSICON' in os.environ or 'WT_SESSION' in os.environ)
    return stream_supports_colour_result


class _ColourFormatter(logging.Formatter):
    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # '1' means bold, '2' means dim, '0' means reset, and '4' means underline.

    def format(self, record):
        level_colours = [
            (logging.DEBUG, '\x1b[40;1m'),  # Debug level in bold black background
            (logging.VERBOSE, '\x1b[36;1m'),  # Verbose level in bold cyan foreground   # noqa
            (logging.INIT, '\x1b[46;1m'),  # Init level in bold cyan background         # noqa
            (logging.START, '\x1b[42;1m'),  # Start level in bold green background      # noqa
            (logging.END, '\x1b[41;1m'),  # End level in bold red background            # noqa
            (logging.INFO, '\x1b[34;1m'),  # Info level in bold blue foreground
            (logging.WARNING, '\x1b[33;1m'),  # Warning level in bold yellow foreground
            (logging.ERROR, '\x1b[31m'),  # Error level in red foreground
            (logging.CRITICAL, '\x1b[41m'),  # Critical level with red background
        ]

        formats = {
            level: logging.Formatter(
                f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[0m %(message)s',
                '%H:%M:%S',  # '%Y-%m-%d %H:%M:%S'
            )
            for level, colour in level_colours
        }

        formatter = formats.get(record.levelno, formats[logging.DEBUG])

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


# obfuscation
# TODO obfuscate_dict(...) - As we want to use it also from other places
# TODO Move this method to python-sdk
# TODO Every time we change this function please change also the function in typescript-sdk  # noqa: E501
def obfuscate_log_dict(log_dict: dict) -> dict:
    """
    Obfuscate keys:
    - %password%
    - %secret%
    - %token%
    - %jwt%
    - %e%mail%
    - %phone%
    - %name% (first / last / nick / user etc.)
    - %address%
    - %ssn%
    """
    environment_name: str = get_environment_name()
    # TODO || self.user_context.in_role(ADMIN_ROLE)
    # TODO Change "play1" everywhere to PLAY1_ENVIRONMENT from python-sdk
    if environment_name == "play1":
        return log_dict
    obfuscated_log_dict = {}
    # TODO the value can contain str like password='...'
    for key, value in log_dict.items():
        if isinstance(value, dict):
            obfuscated_log_dict[key] = obfuscate_log_dict(value)
        # TODO in case of email_address or email or main obfuscate to something like this S*****@*****P.Com
        elif re.search(r'password|secret|token|jwt|e[\-_]?mail|phone|name|address|ssn', str(key), re.IGNORECASE):
            # TODO Maybe we can reveal a small part
            obfuscated_log_dict[key] = "***"
        else:
            obfuscated_log_dict[key] = value
    return obfuscated_log_dict
