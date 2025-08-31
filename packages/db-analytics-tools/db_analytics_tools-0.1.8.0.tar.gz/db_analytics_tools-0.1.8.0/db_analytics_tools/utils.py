# coding : utf-8


"""
    DB Analytics Tools : Utils

    This module provides classes and functions for database interactions and data migration.
"""


import urllib
import datetime
import json

import pandas as pd

# Frequeny
FREQ = {
    "Daily": "d",
    "Weekly": "w",
    "Monthly": "m"
}


class Client:
    """
    SQL Client Class

    This class provides a client for connecting to SQL databases such as PostgreSQL and SQL Server.

    :param host: The hostname or IP address of the database server.
    :param port: The port number to use for the database connection.
    :param database: The name of the database to connect to.
    :param username: The username for authenticating the database connection.
    :param password: The password for authenticating the database connection.
    :param engine: The database engine to use, currently supports 'postgres' and 'sqlserver'.
    :param keep_connection: If True, the connection will be maintained until explicitly closed. If False, the connection
                           will be opened and closed for each database operation (default is False).
    """

    def __init__(self, host, port, database, username, password, engine="postgres", keep_connection=False):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.engine = engine
        self.keep_connection = keep_connection
        # Test Connection #
        self.test_connection()
        # Generate URI #
        self.generate_uri()

    def connect(self, verbose=0):
        """
        Establish a connection to the database.

        :param verbose: If set to 1, print a success message upon connection.
        """
        if self.engine == "postgres":
            import psycopg2
            self.conn = psycopg2.connect(host=self.host,
                                         port=self.port,
                                         database=self.database,
                                         user=self.username,
                                         password=self.password)
        elif self.engine == "sqlserver":
            import pyodbc
            self.conn = pyodbc.connect(f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                                       f"SERVER={self.host};" \
                                       f"DATABASE={self.database};" \
                                       f"UID={self.username};" \
                                       f"PWD={self.password};")
        else:
            raise NotImplementedError("Engine not supported")
        # Create cursor
        self.cursor = self.conn.cursor()
        if verbose == 1:
            print('Connection established successfully !')

    def test_connection(self, verbose=1):
        """
        Test the database connection.

        :param verbose: If set to 1, print a success message upon successful connection.
        :raises Exception: If the connection test fails.
        """
        try:
            self.connect(verbose=1)
            if not self.keep_connection:
                self.close()
        except Exception:
            raise Exception("Something went wrong! Verify database info and credentials.")

    def close(self, verbose=0):
        """
        Close the database connection.

        :param verbose: If set to 1, print a success message upon closing the connection.
        """
        self.cursor.close()
        self.conn.close()
        if verbose == 1:
            print('Connection closed successfully!')

    def generate_uri(self):
        """
        Generate a connection URI based on the provided parameters.
        """
        password = urllib.parse.quote(self.password)
        if self.engine == "postgres":
            self.uri = f"postgresql+psycopg2://{self.username}:{password}@{self.host}:{self.port}/{self.database}"
        elif self.engine == "sqlserver":
            driver = 'ODBC Driver 17 for SQL Server'
            self.uri = f"mssql+pyodbc://{self.username}:{password}@{self.host}:{self.port}/{self.database}?driver={driver}"
        else:
            raise NotImplementedError("Engine not supported")

    def execute(self, query, verbose=0):
        """
        Execute an SQL query.

        :param query: The SQL query to execute.
        :param verbose: If set to 1, print the execution time.
        """
        duration = datetime.datetime.now()
        if not self.keep_connection:
            self.connect()
        self.cursor.execute(query)
        self.conn.commit()
        if not self.keep_connection:
            self.close()
        duration = datetime.datetime.now() - duration
        if verbose == 1:
            print(f'Execution time: {duration}')

    def read_sql(self, query, verbose=0):
        """
        Execute an SQL query and return the result as a Pandas DataFrame.

        :param query: The SQL query to execute.
        :param verbose: If set to 1, print the execution time.
        :return: A Pandas DataFrame containing the query result.
        """
        duration = datetime.datetime.now()
        dataframe = pd.read_sql(query, self.uri)
        duration = datetime.datetime.now() - duration
        if verbose == 1:
            print(f'Execution time: {duration}')

        return dataframe

    def grant(self, table_name, username, level, verbose=0):
        """
        Grant specific privileges on a database table to a user.

        :param table_name: The name of the database table on which to grant privileges.
        :param username: The username of the user to whom privileges will be granted.
        :param level: The level of privileges to grant, which can be one of: 'select', 'update', 'insert', 'delete', 'all'.
        :param verbose: If set to 1, print the execution time.
        """
        assert level in ("select", "update", "insert", "delete", "all")
        mapping = {
            "select": "select",
            "update": "update",
            "insert": "insert",
            "delete": "delete",
            "all": "all privileges"
        }
        query = "grant " + mapping[level] + " on " + table_name + " to " + username + ";"

        duration = datetime.datetime.now()
        if not self.keep_connection:
            self.connect()
        self.cursor.execute(query)
        self.conn.commit()
        if not self.keep_connection:
            self.close()
        duration = datetime.datetime.now() - duration
        if verbose == 1:
            print(f'Execution time: {duration}')

    def revoke(self, table_name, username, level, verbose=0):
        """
        Revoke specific privileges on a database table from a user.

        :param table_name: The name of the database table on which to revoke privileges.
        :param username: The username of the user from whom privileges will be revoked.
        :param level: The level of privileges to revoke, which can be one of: 'select', 'update', 'insert', 'delete', 'all'.
        :param verbose: If set to 1, print the execution time.
        """
        assert level in ("select", "update", "insert", "delete", "all")
        mapping = {
            "select": "select",
            "update": "update",
            "insert": "insert",
            "delete": "delete",
            "all": "all privileges"
        }
        query = "revoke " + mapping[level] + " from " + username + " on " + table_name + ";"

        duration = datetime.datetime.now()
        if not self.keep_connection:
            self.connect()
        self.cursor.execute(query)
        self.conn.commit()
        if not self.keep_connection:
            self.close()
        duration = datetime.datetime.now() - duration
        if verbose == 1:
            print(f'Execution time: {duration}')
            
    def show_sessions(self, include_all=False):
        """
        Retrieves and displays the list of active database sessions for the current user.

        This method queries the database to fetch session details, including session ID, 
        user name, client address, application name, query status, and timestamps.

        - For PostgreSQL, it retrieves detailed session information from `pg_stat_activity`.
        - For SQL Server, it retrieves running requests from `sys.dm_exec_requests`.

        :raises NotImplementedError: If the database engine is not supported.
        :return: A DataFrame containing session details.
        """
        if self.engine == "postgres":
            query = """
                select pid         session_id,
                    rsgid       resource_group_id,
                    sess_id     session_internal_id,
                    usename     username,
                    client_addr client_address,
                    application_name,
                    query,
                    state,
                    waiting,
                    waiting_reason,
                    null        waiting_time_ms,
                    query_start,
                    backend_start,
                    xact_start,
                    state_change,
                    null        cpu_time,
                    null        total_elapsed_time,
                    null        reads_,
                    null        writes_
                from pg_stat_activity
                where usename = current_user
                order by query_start desc;
            """
        elif self.engine == "sqlserver":
            query = """
                SELECT s.session_id                                             AS session_id,
                    NULL                                                     AS resource_group_id,
                    r.request_id                                             AS session_internal_id,
                    s.login_name                                             AS username,
                    s.host_name                                              AS client_address,
                    s.program_name                                           AS application_name,
                    r.command                                                AS query,
                    r.status                                                 AS state,
                    CAST(CASE WHEN r.wait_time = 0 THEN 0 ELSE 1 END AS BIT) AS waiting,
                    r.wait_type                                              AS waiting_reason,
                    r.wait_time                                              AS waiting_time_ms,
                    r.start_time                                             AS query_start,
                    s.login_time                                             AS backend_start,
                    NULL                                                     AS xact_start,
                    NULL                                                     AS state_change,
                    r.cpu_time,
                    r.total_elapsed_time,
                    r.reads                                                  AS reads_,
                    r.writes                                                 AS writes_
                FROM sys.dm_exec_sessions s
                        LEFT JOIN sys.dm_exec_requests r ON s.session_id = r.session_id
                WHERE s.login_name = SUSER_NAME()
                ORDER BY r.start_time DESC;
            """
        else:
            raise NotImplementedError("Engine not supported")
        if include_all:
            return self.read_sql(query)
        
        subset = ["session_id", "resource_group_id","username", "client_address","application_name",
                  "query","state","waiting","waiting_reason","query_start","backend_start"]
        return self.read_sql(query)[subset]
    
    def cancel_query(self, session_id, verbose=0):
        """
        Cancel a running query based on its session ID.

        :param session_id: The session ID of the query to cancel.
        :param verbose: If set to 1, print the execution time.
        """
        if self.engine == "postgres":
            query = f"select pg_cancel_backend({session_id});"
        elif self.engine == "sqlserver":
            query = f"kill {session_id};"
        else:
            raise NotImplementedError("Engine not supported")

        self.execute(query, verbose=verbose)
    
    def cancel_locked_queries(self, verbose=0):
        """
        Cancel a locked queries.

        :param verbose: If set to 1, print the execution time.
        """
        locks = self.show_sessions().query("waiting == True").to_dict(orient="records")
        for lock in locks:
            print(f"Canceling session ID: {lock['session_id']} ... '{lock['query'][:25]}'", end=" ... ")
            self.cancel_query(lock["session_id"], verbose=verbose)
            print("Canceled !")


def create_client(host, port, database, username, password, engine, keep_connection):
    """
    Creates a SQL Client instance for database operations.

    This function establishes a connection to the specified database server with the provided
    credentials and engine type. It returns a `Client` instance which can be used to interact with
    the database, allowing data extraction, transformation, and loading (ETL) operations.

    :param host: str - The hostname or IP address of the database server.
    :param port: int - The port number to use for the database connection.
    :param database: str - The name of the database to connect to.
    :param username: str - The username for authenticating the database connection.
    :param password: str - The password for authenticating the database connection.
    :param engine: str - The database engine to use; supported values are 'postgres' and 'sqlserver'.
    :param keep_connection: bool - If True, the connection will be maintained until explicitly closed.
                            If False, the connection will be opened and closed for each operation.
    :return: Client - A `Client` instance configured for interacting with the specified database.
    """
    client = Client(host=host,
                    port=port,
                    database=database,
                    username=username,
                    password=password,
                    engine=engine,
                    keep_connection=keep_connection)
    return client


def create_client_from_config(config):
    """
    Creates a SQL Client instance from a configuration dictionary.

    This function takes a configuration dictionary containing the necessary connection details
    and creates a `Client` instance for performing data operations. The configuration dictionary
    should contain the following keys: 'host', 'port', 'database', 'username', 'password',
    'engine', and 'keep_connection'.

    :param config: dict - A dictionary containing the database connection parameters:
                   - host: str - The hostname or IP address of the database server.
                   - port: int - The port number to use for the database connection.
                   - database: str - The name of the database to connect to.
                   - username: str - The username for authenticating the database connection.
                   - password: str - The password for authenticating the database connection.
                   - engine: str - The database engine to use; supported values are 'postgres' and 'sqlserver'.
                   - keep_connection: bool - If True, the connection will be maintained until explicitly closed.
                                              If False, the connection will be opened and closed for each operation.
    :return: Client - A `Client` instance configured for interacting with the specified database.
    """
    client = Client(host=config.get("host"),
                    port=config.get("port"),
                    database=config.get("database"),
                    username=config.get("username"),
                    password=config.get("password"),
                    engine=config.get("engine"),
                    keep_connection=config.get("keep_connection", False))
    return client


def truncate_table(db_client, table_name, if_exists):
    """
    Truncate a database table.

    This function removes all rows from the specified table in the database, effectively resetting it.

    :param db_client: An instance of the `Client` class for connecting to the database.
    :param table_name: The name of the table to truncate, in the format 'schema_name.table_name'.
    """
    
    if if_exists == "truncate":
        if db_client.engine == "postgres":
            sql = f"TRUNCATE TABLE {table_name};"
        elif db_client.engine == "sqlserver":
            sql = f"TRUNCATE TABLE {table_name};"
        else:
            raise NotImplementedError("Engine not supported for truncate operation")
        db_client.execute(query=sql)


def dataframe_to_csv(dataframe, output_file, sep=";", encoding='latin_1'):
    """
    Save a Pandas DataFrame to a CSV file.

    :param dataframe: The Pandas DataFrame to be saved.
    :param output_file: The path to the output CSV file.
    :param sep: The delimiter to use between fields in the CSV file.
    :param encoding: The character encoding for the CSV file (default is 'latin_1').
    """
    dataframe.to_csv(output_file,
                     sep=sep,
                     encoding=encoding,
                     index=False)


def db_to_csv(query, db_client, output_file, sep=";", encoding='latin_1'):
    """
    Execute a SQL query and save the result to a CSV file.

    :param query: The SQL query to be executed.
    :param db_client: An instance of the `Client` class for connecting to the database.
    :param output_file: The path to the output CSV file.
    :param sep: The delimiter to use between fields in the CSV file.
    :param encoding: The character encoding for the CSV file (default is 'latin_1').
    """
    dataframe = db_client.read_sql(query)
    dataframe_to_csv(dataframe=dataframe,
                     output_file=output_file,
                     sep=sep,
                     encoding=encoding)


def dataframe_to_db(dataframe, db_client, destination_table, if_exists="append", chunksize=10000):
    """
    Load data from a Pandas DataFrame to a database table.

    :param dataframe: Pandas DataFrame containing the data to be loaded.
    :param db_client: Database client.
    :param destination_table: Destination table in the format 'schema_name.table_name'.
    :param if_exists: Action to take if the table already exists ('fail', 'replace', or 'append').
    :param chunksize: Number of rows to insert in each batch (default is 10000).
    """
    schema_name, table_name = destination_table.split(".")
    
    # if_exists == "truncate"
    truncate_table(db_client, destination_table, if_exists)

    dataframe.to_sql(name=table_name,
                     schema=schema_name,
                     con=db_client.uri,
                     index=False,
                     chunksize=chunksize,
                     method="multi",
                     if_exists=if_exists)


def csv_to_db(input_file, db_client, destination_table, sep=";", if_exists="append", chunksize=10000):
    """
    Load data from a CSV file to a database table.

    :param input_file: Path to the input CSV file.
    :param db_client: Database client.
    :param destination_table: Destination table in the format 'schema_name.table_name'.
    :param sep: Separator character for the CSV file (default is ';').
    :param if_exists: Action to take if the table already exists ('fail', 'replace', or 'append').
    :param chunksize: Number of rows to insert in each batch (default is 10000).
    """
    dataframe = pd.read_csv(input_file, sep=sep)
    
    # if_exists == "truncate"
    truncate_table(db_client, destination_table, if_exists)

    dataframe_to_db(dataframe=dataframe,
                    db_client=db_client,
                    destination_table=destination_table,
                    sep=sep,
                    if_exists=if_exists,
                    chunksize=chunksize)


def db_to_db(query, source_client, destination_client, destination_table, if_exists="append", chunksize=10000):
    """
    Transfer data from one database to another using an SQL query.

    :param query: SQL query to retrieve data from the source database.
    :param source_client: Source database client.
    :param destination_client: Destination database client.
    :param destination_table: Destination table in the format 'schema_name.table_name'.
    :param if_exists: Action to take if the destination table already exists ('fail', 'replace', or 'append').
    :param chunksize: Number of rows to insert in each batch (default is 10000).
    """
    dataframe = source_client.read_sql(query)
    
    # if_exists == "truncate"
    truncate_table(destination_client, destination_table, if_exists)

    dataframe_to_db(dataframe=dataframe,
                    db_client=destination_client,
                    destination_table=destination_table,
                    if_exists=if_exists,
                    chunksize=chunksize)


def get_config(path):
    with open(path, "r") as f:
        config = json.load(f)

    return config
