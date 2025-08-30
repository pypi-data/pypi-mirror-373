# coding : utf-8

"""
    DB Analytics Tools Data Integration
"""

import time
import datetime

from psycopg2 import OperationalError
import pandas as pd
import streamlit as st

import db_analytics_tools as db


NBCHAR = 70


class ETL:
    """
    SQL Based ETL (Extract, Transform, Load) Class

    This class provides functionality for running SQL-based ETL processes using a database client.

    :param client: An instance of the `Client` class for connecting to the database.
    """

    def __init__(self, client):
        try:
            assert isinstance(client, db.Client)
        except Exception:
            raise Exception("Something went wrong!")

        self.client = client

    @staticmethod
    def generate_date_range(start_date, stop_date=None, freq=None, dates=None, reverse=False, streamlit=False):
        """
        Generate a range of dates.

        :param start_date: The start date for the range.
        :param stop_date: The stop date for the range.
        :param freq: The frequency of the dates ('d' for daily, 'm' for monthly).
        :param dates: A list of dates
        :param reverse: If True, the date range is generated in reverse order (from stop_date to start_date).
        :param streamlit: If True, use Streamlit for progress updates.01
        :return: A list of formatted date strings.
        """
        a = start_date and (start_date or stop_date) and freq and dates is None # Date Range
        b = start_date is None and stop_date is None and freq is None and dates # Specific list of dates
        assert (a and not b) or (not a and b)
        
        if dates:
            dates_ranges = dates
            # Reverse
            if reverse:  # Recent to Old
                dates_ranges.sort(reverse=True)

            print(f'Date Range  : From {dates_ranges[0]} to {dates_ranges[-1]}')
            print(f'Iterations  : {len(dates_ranges)}')

            if streamlit:
                st.markdown(f"<p>Date Range  : From {dates_ranges[0]} to {dates_ranges[-1]}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Iterations  : {len(dates_ranges)}</p>", unsafe_allow_html=True)

            return dates_ranges

        if start_date and stop_date is None:
            print(f'Date        : {start_date}')
            print('Iterations  : 1')

            if streamlit:
                st.markdown(f"<p>Date        : {start_date}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Iterations  : 1</p>", unsafe_allow_html=True)

            return [start_date]

        # Generate continuous dates with formatted strings
        dates_ranges = pd.date_range(start=start_date, end=stop_date, freq='D').strftime('%Y-%m-%d').tolist()

        # Manage Frequency
        if freq.upper() not in ['D', 'M', 'W']:
            raise NotImplementedError("Frequency not supported!")

        if freq.upper() == 'M':
            # Keep only dates that represent the first day of each month
            dates_ranges = [date for date in dates_ranges if date.endswith('-01')]
        elif freq.upper() == 'W':
            # Keep only dates that represent the first day of each week (every 7 days)
            dates_ranges = [date for i, date in enumerate(dates_ranges) if i % 7 == 0]

        # Reverse
        if reverse:  # Recent to Old
            dates_ranges.sort(reverse=True)

        print(f'Date Range  : From {dates_ranges[0]} to {dates_ranges[-1]}')
        print(f'Iterations  : {len(dates_ranges)}')

        if streamlit:
            st.markdown(f"<p>Date Range  : From {dates_ranges[0]} to {dates_ranges[-1]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>Iterations  : {len(dates_ranges)}</p>", unsafe_allow_html=True)

        return dates_ranges

    def run(self, function, start_date=None, stop_date=None, freq=None, dates=None, pause=1, reverse=False, streamlit=False):
        """
        Run a specified SQL function for a range of dates.

        :param function: The SQL function to run for each date.
        :param start_date: The start date for the range.
        :param stop_date: The stop date for the range.
        :param dates: A list of dates
        :param freq: The frequency of the dates ('d' for daily, 'm' for monthly).
        :param pause: The pause time between each function execution.
        :param dates: A list of dates
        :param reverse: If True, the date range is generated in reverse order (from stop_date to start_date).
        :param streamlit: If True, use Streamlit for progress updates.
        """
        # Generate Dates Range
        dates_ranges = self.generate_date_range(start_date, stop_date, freq, dates, reverse, streamlit)

        # Total Iterations
        total_iterations = len(dates_ranges)

        print(f'Function    : {function}')

        # Initialization
        i = 1

        # Send query to the server
        for date in dates_ranges:
            # Pause
            time.sleep(pause)

            print(f"[Running Date: {date}] [Function: {function}] ", end="", flush=True)
            if streamlit:
                st.markdown(f"<span style='font-weight: bold;'>[Running Date: {date}] [Function: {function}] </span>",
                            unsafe_allow_html=True)

            query = f"select {function}('{date}'::date);"
            duration = datetime.datetime.now()

            try:
                self.client.execute(query)
            except Exception as e:
                raise Exception("Something went wrong!")

            duration = datetime.datetime.now() - duration
            progression = i / total_iterations * 100
            progression = f"{progression:.2f}%"
            execuxtion_time = f"Execution time: {duration} [Prog.{progression.rjust(7, '.')}]"
            i += 1
            print(execuxtion_time)
            if streamlit:
                st.markdown(f"<span style='font-weight: bold;'>{execuxtion_time}</span>", unsafe_allow_html=True)

    def run_multiple(self, functions, start_date=None, stop_date=None, freq=None, dates=None, pause=1, reverse=False, streamlit=False):
        """
        Run multiple specified SQL functions for a range of dates.

        :param functions: A list of SQL functions to run for each date.
        :param start_date: The start date for the range.
        :param stop_date: The stop date for the range.
        :param freq: The frequency of the dates ('d' for daily, 'm' for monthly).
        :param pause: The pause time between each function execution.
        :param dates: A list of dates
        :param reverse: If True, the date range is generated in reverse order (from stop_date to start_date).
        :param streamlit: If True, use Streamlit for progress updates.
        """
        # Generate Dates Range
        dates_ranges = self.generate_date_range(start_date, stop_date, freq, dates, reverse, streamlit)

        # Total Iterations
        total_iterations = len(dates_ranges) * len(functions)

        print(f'Functions   : {functions}')

        # Compute MAX Length of functions (Adjust display)
        max_fun = max(len(function) for function in functions)

        # Initialization
        i = 1

        # Send query to the server
        for date in dates_ranges:
            # Show date separator line
            print("*" * (NBCHAR + max_fun + 15))
            for function in functions:
                # Pause
                time.sleep(pause)

                print(f"[Running Date: {date}] [Function: {function.ljust(max_fun, '.')}] ", end="", flush=True)
                if streamlit:
                    st.markdown(
                        f"<span style='font-weight: bold;'>[Running Date: {date}] [Function: {function}] </span>",
                        unsafe_allow_html=True)

                query = f"select {function}('{date}'::date);"
                duration = datetime.datetime.now()

                try:
                    self.client.execute(query)
                except Exception as e:
                    raise Exception("Something went wrong!")

                duration = datetime.datetime.now() - duration
                progression = i / total_iterations * 100
                progression = f"{progression:.2f}%"
                execuxtion_time = f"Execution time: {duration} [Prog.{progression.rjust(7, '.')}]"
                i += 1
                print(execuxtion_time)
                if streamlit:
                    st.markdown(f"<span style='font-weight: bold;'>{execuxtion_time}</span>", unsafe_allow_html=True)


        # Show final date separator line
        print("*" * (NBCHAR + max_fun + 15))


def create_etl(host, port, database, username, password, engine, keep_connection):
    """
    Create an ETL (Extract, Transform, Load) instance with the specified database connection parameters.

    :param host: The hostname or IP address of the database server.
    :param port: The port number to use for the database connection.
    :param database: The name of the database to connect to.
    :param username: The username for authenticating the database connection.
    :param password: The password for authenticating the database connection.
    :param engine: The database engine to use, currently supports 'postgres' and 'sqlserver'.
    :param keep_connection: If True, the connection will be maintained until explicitly closed. If False, the connection
                           will be opened and closed for each database operation (default is False).
    :return: An ETL instance for performing data extraction, transformation, and loading.
    """
    client = db.Client(host=host,
                       port=port,
                       database=database,
                       username=username,
                       password=password,
                       engine=engine,
                       keep_connection=keep_connection)
    etl = ETL(client)
    return etl


import json
import streamlit as st
from psycopg2 import OperationalError
import db_analytics_tools as db
import db_analytics_tools.integration as dbi

class UI:
    def __init__(self, config):
        """
        Initializes the UI with database configuration and pipelines.

        :param config: A dictionary containing configuration details for the database,
                       allowed users, and pipeline configurations.
        """
        self.db_info = config["db_info"]
        self.allowed_users = config["allowed_users"]
        self.pipelines = self.get_pipelines(config["pipelines"])
        self.app_name = config["app_name"]
        self.app_description = config["app_description"]
        self.functions = {pipeline["pipeline_name"]: pipeline for pipeline in config["pipelines"]}
        
        # Initialize session state variables if they don't exist
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "client" not in st.session_state:
            st.session_state.client = None
        if "etl" not in st.session_state:
            st.session_state.etl = None

    @staticmethod
    def get_pipelines(pipelines):
        """
        Processes and organizes pipeline configurations into a dictionary format
        with pipeline names as keys and pipeline details as values. Additionally,
        it adds single function options for multiple pipelines.

        :param pipelines: A list of pipeline configuration dictionaries.
        :return: A dictionary where each key is a unique pipeline name and each value is the pipeline configuration.
        """
        pipelines_ = {
            f"{elt['pipeline_name']} ({elt['pipeline_type']})": elt
            for elt in pipelines
        }
        
        # Add individual functions as single pipelines for multi-function pipelines
        pipelines_.update({
            f"{fun} ({elt['pipeline_name']})": {
                "pipeline_name": fun,
                "pipeline_type": "single",
                "pipeline_functions": [fun]
            } 
            for elt in pipelines if elt["pipeline_type"] == "multiple" for fun in elt["pipeline_functions"]
        })
        
        return pipelines_

    def authenticate(self, username, password):
        """
        Authenticates a user by verifying the username and password against allowed users.

        :param username: The username entered by the user.
        :param password: The password entered by the user.
        :return: True if authentication is successful, False otherwise.
        """
        if username == "" or password == "":
            st.sidebar.error("Missing credentials!")
            return False
        elif username not in self.allowed_users:
            st.sidebar.error("You are not allowed! Please contact the administrator.")
            return False
        return True

    def start(self):
        """
        Launches the Streamlit application with authentication and UI functionality.
        Displays the application title, description, and handles authentication.
        """
        # App Layout and Sidebar Configuration
        st.set_page_config(
            page_title=f"Job Executor - {self.app_name}", 
            page_icon="https://cdn-icons-png.flaticon.com/512/4016/4016758.png", 
            layout="centered", 
            initial_sidebar_state="auto"
        )
        st.title(self.app_name)
        st.write(self.app_description)

        # Sidebar Authentication
        st.sidebar.title("Authentication")
        engine = st.sidebar.text_input("Engine", value=self.db_info["engine"])
        host = st.sidebar.text_input("Host", value=self.db_info["host"])
        port = st.sidebar.text_input("Port", value=self.db_info["port"])
        database = st.sidebar.text_input("Database", value=self.db_info["database"])
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        # Connect Button
        if st.sidebar.button("Connect"):
            if self.authenticate(username, password):
                try:
                    st.session_state.logged_in = True
                    st.sidebar.success("Authentication successful!")
                    st.session_state.client = db.Client(
                        host=host, port=port, database=database, 
                        username=username, password=password, engine=engine
                    )
                    st.session_state.etl = dbi.ETL(st.session_state.client)
                except Exception as e:
                    st.sidebar.error(f"Authentication failed: {e}")

        # Render pipeline selection if logged in
        if st.session_state.logged_in:
            self.render_pipeline_selection()

    def render_pipeline_selection(self):
        """
        Renders the main pipeline selection and execution interface.
        Provides dropdowns for selecting the pipeline, start and stop dates,
        and the frequency, along with a "Run" button to initiate processing.
        """
        # Dropdown for pipeline selection
        selected_pipeline = st.selectbox("Function", list(self.pipelines.keys()))

        # Date selection
        start_date = st.date_input("Start Date")
        stop_date = st.date_input("Stop Date")

        # Frequency selection
        selected_freq = db.utils.FREQ[st.selectbox("Frequency", db.utils.FREQ.keys())]

        # Run Button
        if st.button("Run"):
            try:
                result = self.process_function(selected_pipeline, start_date, stop_date, selected_freq)
                st.write("Result:")
                st.write(result)
            except OperationalError:
                st.error("Operational Error!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

    def process_function(self, selected_pipeline, start_date, stop_date, freq):
        """
        Executes the selected pipeline with the provided parameters.

        :param selected_pipeline: The name of the pipeline to execute.
        :param start_date: The start date for the pipeline execution.
        :param stop_date: The end date for the pipeline execution.
        :param freq: The frequency of execution (e.g., daily, weekly, monthly).
        :return: A result message detailing the selected pipeline and execution parameters.
        """
        pipeline = self.pipelines[selected_pipeline]
        pipeline_type = pipeline["pipeline_type"]
        pipeline_functions = pipeline["pipeline_functions"]

        result = f"You selected: {selected_pipeline}\nStart Date: {start_date}\nStop Date: {stop_date}"

        if pipeline_type == "single":
            st.session_state.etl.run(
                function=pipeline_functions[0], start_date=start_date, 
                stop_date=stop_date, freq=freq, reverse=False, streamlit=True
            )
        elif pipeline_type == "multiple":
            st.session_state.etl.run_multiple(
                functions=pipeline_functions, start_date=start_date, 
                stop_date=stop_date, freq=freq, reverse=False, streamlit=True
            )
        else:
            raise NotImplementedError("Pipeline type not supported.")

        return result
