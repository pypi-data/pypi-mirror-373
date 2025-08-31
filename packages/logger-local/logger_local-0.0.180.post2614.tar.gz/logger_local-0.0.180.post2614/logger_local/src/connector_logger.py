# TODO Maybe we should call it MiniDatabase like we have MiniLogger (MiniDatabase is not using database-mysql-local)
from functools import lru_cache

import mysql.connector
# TODO How can we use it to analyse the error?
# from mysql.connector import errorcode
# from mysql.connector import MySQLConnection
from python_sdk_remote.utilities import get_sql_hostname, get_sql_username, get_sql_password, our_get_env
from python_sdk_remote.mini_logger import MiniLogger

# We are using the database directly to avoid cyclic dependency (so ConnectorLogger is similar to Connector class)


# TODO Shall we add this functionality also to database-mysql-local?
# TODO Shall we delete the function as we have method in ConnectorLogger
@lru_cache
def get_connection(schema_name: str, is_treading: bool = False) -> mysql.connector:
    # is_treading is used to get a dedicated connection from cache.
    if schema_name == "logger":
        host: str = our_get_env(key="LOGGER_MYSQL_HOSTNAME", default=get_sql_hostname())
        user: str = our_get_env(key="LOGGER_MYSQL_USERNAME", default=get_sql_username())
        password: str = our_get_env(key="LOGGER_MYSQL_PASSWORD", default=get_sql_password())
    else:
        host: str = get_sql_hostname()
        user: str = get_sql_username()
        password: str = get_sql_password()

    try:
        # : mysql.connector.MySQLConnection
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=schema_name,
            autocommit=True,
            buffered=True
        )
        print(f"get_connection() connection.is_connected()={connection.is_connected()}")
        print("get_connection() connection.__class__="+(str)(connection.__class__))
    except Exception as e:
        raise Exception(f"Error connecting to MySQL: {e}. {host=}, {password=}, {user=}, {schema_name=}")
    return connection


# TODO Shall we support multiple cursors? Shall we take execute() and fetchone() from ConnectorLogger to CursorLogger?
class ConnectorLogger:

    connection: mysql.connector.MySQLConnection = None
    cursor = None  # : mysql.connector.MySQLCursor = None

    @lru_cache
    def get_connection(self, schema_name: str, is_treading: bool = False):  # -> mysql.connector:
        # is_treading is used to get a dedicated connection from cache.
        if schema_name == "logger":
            host: str = our_get_env(key="LOGGER_MYSQL_HOSTNAME", default=get_sql_hostname())
            user = our_get_env(key="LOGGER_MYSQL_USERNAME", default=get_sql_username())
            password = our_get_env(key="LOGGER_MYSQL_PASSWORD", default=get_sql_password())
        else:
            host = get_sql_hostname()
            user = get_sql_username()
            password = get_sql_password()

        try:
            # : mysql.connector.MySQLConnection
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=schema_name,
                autocommit=True,
                buffered=True
            )
            print(f"get_connection() connection.is_connected()={self.connection.is_connected()}")
            print("get_connection() connection.__class__="+(str)(self.connection.__class__))
        except Exception as e:
            raise Exception(f"Error connecting to MySQL: {e}. {host=}, {password=}, {user=}, {schema_name=}")
        self.cursor = self.connection.cursor()
        # return self.connection

    def clean_buffer(self) -> None:
        """Cleans any remaining result sets from previous execute() calls"""
        try:
            while self.cursor and self.cursor.nextset():
                # Consume any remaining result sets
                pass
        except Exception as exception:
            MiniLogger.error(object={"Error cleaning cursor buffer": exception})

    def execute(self, sql: str, parameters: dict = None):  # -> None:
        # Allow running execute twice
        self.clean_buffer()
        print(f"ConnectionLogger.execute() type of self={type(self)}")
        print(f"ConnectionLogger.execute()self.__class__={self.__class__}")
        if self.cursor is None:
            raise Exception("Cursor is None. Please call get_connection() first.")
        # TODO Do we need this?
        if parameters is None:
            parameters = ()
            execute_result = self.cursor.execute(sql)
        else:
            execute_result = self.cursor.execute(sql, parameters)
        print(f"execute_result={execute_result}")
        return execute_result

    def fetchone(self) -> dict:
        return self.cursor.fetchone()

    # We have equivalent method in logger-local-python and in database-mysql-local-python  # noqa E501
    def commit(self) -> None:
        is_try_fetchall_to_resolve_commit_command_out_of_sync_exception = False
        # 1st try to commit
        try:
            self.connection.commit()
        except Exception as exception:
            MiniLogger.error(object={"1st try to commit exception": exception})
        # MySQLInterfaceError("Commands out of sync; you can't run this command now")}
        except mysql.connector.errors.InterfaceError as exception:
            print("Got mysql.connector.errors.InterfaceError exception err.errno=", exception.errno)
            # if err.errno == errorcode.CR_CONN_HOST_ERROR: # Example: Connection refused
            #    print("Connection to MySQL server failed.")
            MiniLogger.error(object={"1st try to commit got MySQLInterfaceError exception": exception})
            # Trying to resolve "Commands out of sync; you can't run this command now" error, when doing commit()
            # TODO check if we got the relevant exception and fetch
            # mini_logger("May be we didn't finish all the data from the previous query")
            is_try_fetchall_to_resolve_commit_command_out_of_sync_exception = True  # noqa E501

        if is_try_fetchall_to_resolve_commit_command_out_of_sync_exception:
            try:
                _ = self.cursor.fetchall()
            except Exception as exception:
                MiniLogger.error(object={"Try to fetchall() after exception when committing exception=": exception})

        # 2nd try to commit
        try:
            self.connection.commit()
        except Exception as exception:
            MiniLogger.error(object={"exception": exception})
