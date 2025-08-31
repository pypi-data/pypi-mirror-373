import json
import queue
import threading
import time
import traceback

from python_sdk_remote.mini_logger import MiniLogger as logger
from python_sdk_remote.utilities import PRINT_STARS

from .connector_logger import get_connection


# TODO Rename to MySQLWriterViaQueue
# TODO Inherit from a new LoggerWriter pure virtual abstract class
class Writer:
    _instance = None  # Class variable to store the single instance
    _queue: queue.Queue = None

    def __new__(cls, *args, **kwargs):

        if not cls._instance:
            cls._instance = super(Writer, cls).__new__(cls, *args, **kwargs)
            cls._queue = queue.Queue()
            cls._instance._initialize_sending_thread()
        return cls._instance

    def _initialize_sending_thread(self):
        self.sending_thread = threading.Thread(target=self._flush_queue)
        self.sending_thread.daemon = True
        self.sending_thread.name = 'logger-sending-thread'
        self.sending_thread.start()

    def _flush_queue(self):
        while self._queue.empty():
            time.sleep(1)
        connection = get_connection(schema_name="logger", is_treading=True)
        cursor = connection.cursor()
        # TODO use execute many?
        while not self._queue.empty():
            query, values = self._queue.get()
            cursor.execute(query, values)

        cursor.close()
        connection.commit()

    # INSERT to logger_table should be disabled by default and activated using combination of json and Environment variable enabling INSERTing to the logger_table  # noqa: E501
    # This function is called when `self.write_to_sql and self.debug_mode.is_logger_output(component_id=
    #                               self.component_id, logger_output=LoggerOutputEnum.MySQLDatabase, message_severity.value)`
    def add_message_and_payload(self, message_str: str, params_to_insert_dict: dict) -> int:
        print(f"{PRINT_STARS}Writer.py Writer.add_message_and_payload() message={message_str} params_to_insert={params_to_insert_dict}")  # noqa E501
        # TODO Will it solve the error?
        if 'locals_before_exception' in params_to_insert_dict:
            params_to_insert_dict['locals_before_exception_text'] = str(params_to_insert_dict['locals_before_exception'])
            print(f"{PRINT_STARS}Stringified params_to_insert_dict['locals_before_exception']")

            try:
                xxx = json.dumps(params_to_insert_dict['locals_before_exception'])
                print(f"{PRINT_STARS}locals_before_exception is valid JSON json.dumps()={xxx}")
            except (TypeError, ValueError):
                print(f"{PRINT_STARS}Warning: locals_before_exception is not valid JSON")

            # TODO Due to error message we deleted it.
            del params_to_insert_dict['locals_before_exception']

        else:
            print(f"{PRINT_STARS}params_to_insert_dict['locals_before_exception'] not found")

        try:
            try:
                # location_id = 0
                if params_to_insert_dict.get('latitude') and params_to_insert_dict.get('longitude'):
                    location_query = (f"INSERT INTO location.location_table (coordinate) "
                                      f"VALUES (POINT({params_to_insert_dict.get('latitude')},"
                                      f"              {params_to_insert_dict.get('longitude')}));")
                    # TODO: location_id = cursor.lastrowid
                    self._queue.put((location_query, []))

                    params_to_insert_dict.pop('latitude', None)
                    params_to_insert_dict.pop('longitude', None)

                # params_to_insert['location_id'] = location_id

            except Exception as exception:
                logger.exception("Exception logger Writer.py add_message_and_payload after adding location ", exception)

            listed_values = [str(k) for k in params_to_insert_dict.values()]
            joined_keys = ','.join(list(params_to_insert_dict.keys()))
            if 'message' not in params_to_insert_dict:
                listed_values.append(message_str)
                joined_keys += (',' if params_to_insert_dict else '') + 'message'

            placeholders = ','.join(['%s'] * len(listed_values))
            insert_logger_sql = f"INSERT INTO logger.logger_table ({joined_keys}) VALUES ({placeholders})"
            print(f"***insert_logger_sql={insert_logger_sql}")

            # async = use queue
            # TODO Support for sync and async
            is_async = False
            if is_async:
                logger_id = 0
                self._queue.put((insert_logger_sql, listed_values))
                if not self.sending_thread.is_alive():
                    self._initialize_sending_thread()
                # TODO How to get the logger_id from the queue?
                # logger_id: int = self._queue.get_nowait().lastrowid if self._queue.get_nowait().lastrowid else None

            else:
                connection = get_connection(schema_name="logger", is_treading=True)
                cursor = connection.cursor()
                print(f"{PRINT_STARS}Writer.py add_message_and_payload() listed_values={listed_values}")
                cursor.execute(insert_logger_sql, listed_values)
                logger_id = cursor.lastrowid
                print(f"{PRINT_STARS}Writer.py add_message_and_payload() logger_id={logger_id}")
                connection.commit()

            print(f"Writer.py add_message_and_payload() logger_id={logger_id}")
            return logger_id

        except Exception as exception:
            logger.exception(f"{PRINT_STARS}Exception logger Writer.py add_message_and_payload after insert to logger table",
                             exception)

            # TODO Can we make it generic?
            tb = traceback.extract_tb(exception.__traceback__)
            line_number = tb[-1].lineno
            print(f"Exception occurred on line {line_number}")

            # TODO What is the reason?
            if " denied " not in str(exception).lower():
                raise exception
            else:
                print("Please ask your Team-Lead to grant you INSERT permissions to the logger database.")  # noqa: E501
                raise exception
