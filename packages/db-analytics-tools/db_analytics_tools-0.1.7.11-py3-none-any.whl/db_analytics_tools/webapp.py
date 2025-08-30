import os
import json
import argparse
import subprocess
import tempfile
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
        self.app_favicon = config.get("app_favicon", "https://cdn-icons-png.flaticon.com/512/4016/4016758.png")
        self.app_logo = config.get("app_logo", "https://cdn-icons-png.flaticon.com/512/4016/4016758.png")
        
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
            page_icon=self.app_favicon, 
            layout="centered", 
            initial_sidebar_state="auto"
        )
        st.title(self.app_name)
        st.write(self.app_description)
        
        # st.logo(
        #     self.app_logo,
        #     link="https://streamlit.io/gallery",
        #     icon_image=self.app_logo,
        # )

        # Sidebar Logo/Image
        # st.sidebar.image(self.app_logo, width=150)
        st.sidebar.markdown(
            f'<div style="text-align: center;"><img src="{self.app_logo}" width="150"></div>',
            unsafe_allow_html=True
        )

        # Sidebar Authentication
        # st.sidebar.title("Authentication")
        st.sidebar.markdown(
            '<h2 style="text-align: center;">Authentication</h2>',
            unsafe_allow_html=True
        )
        engine = st.sidebar.text_input("Engine", value=self.db_info["engine"])
        host = st.sidebar.text_input("Host", value=self.db_info["host"])
        port = st.sidebar.text_input("Port", value=self.db_info["port"])
        database = st.sidebar.text_input("Database", value=self.db_info["database"])
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        self.run_custom_function = st.sidebar.checkbox("Run Custom Function", value=False)

        # Connect Button
        if st.sidebar.button("Connect"):
            if self.authenticate(username, password):
                try:
                    st.session_state.logged_in = True
                    st.session_state.client = db.Client(
                        host=host, port=port, database=database, 
                        username=username, password=password, engine=engine
                    )
                    st.sidebar.success("Authentication successful!")
                    st.session_state.etl = dbi.ETL(st.session_state.client)
                except Exception as e:
                    st.sidebar.error(f"Authentication failed: {e}")

        # Render pipeline selection if logged in
        if st.session_state.logged_in:
            self.render_pipeline_selection()# Add copyright link at the bottom of the sidebar
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            "© 2023 DB Analytics Tools | [About project](https://pypi.org/project/db-analytics-tools/)",
            unsafe_allow_html=True
        )
        
        return self.run_custom_function 

    def render_pipeline_selection(self):
        """
        Renders the main pipeline selection and execution interface.
        Provides dropdowns for selecting the pipeline, start and stop dates,
        and the frequency, along with a "Run" button to initiate processing.
        """
        # Custom Function Input
        if self.run_custom_function:
            selected_pipeline = st.text_input("Custom Pipeline", value="schema.fn_exmpale_function")
            print(selected_pipeline)
        else: # Dropdown for pipeline selection
            selected_pipeline = st.selectbox("Pipeline", list(self.pipelines.keys()))

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
        if self.run_custom_function:
            print("Running custom function")
            pipeline = {
                "pipeline_name": selected_pipeline, 
                "pipeline_type": "single", 
                "pipeline_functions": [selected_pipeline]
            }
            pipeline_type = pipeline["pipeline_type"]
            pipeline_functions = pipeline["pipeline_functions"]
        else:
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



def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="DB Analytics Tools CLI")
    parser.add_argument(
        "command", choices=["start"], help="Command to run the application"
    )
    parser.add_argument(
        "--config", type=str, required=True, help="Path to the configuration file"
    )
    parser.add_argument(
        "--address", type=str, default="127.0.0.1", help="Server address to bind Streamlit (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8050, help="Server port to bind Streamlit (default: 8050)"
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command == "start":
        start_app(args.config, args.address, args.port)

def start_app(config_path, address, port):
    """
    Starts the Streamlit app with the specified configuration file and server settings.

    :param config_path: Path to the configuration file.
    :param address: Server address to bind Streamlit.
    :param port: Server port to bind Streamlit.
    """
    # Load the configuration
    config = db.utils.get_config(config_path)

    # # Setup UI instance
    # ui = dbi.UI(config=config)

    # Streamlit arguments to pass to `subprocess.run`
    streamlit_args = [
        "streamlit", "run", "--server.address", address, "--server.port", str(port),
        "-"]  # Using `-` as the script name to indicate reading from stdin

    # Streamlit script content to initialize the app and run UI.start
    streamlit_script = f"""
import streamlit as st
import db_analytics_tools as db
from db_analytics_tools.webapp import UI

# Load the configuration
config = {json.dumps(config)}

# Initialize UI with config
ui = UI(config=config)

# Start App
ui.start()
"""
    
    # Create a temporary Python file for the Streamlit app
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_file:
        temp_file.write(streamlit_script.encode("utf-8"))
        temp_filename = temp_file.name

    try:
        # Run Streamlit with the temporary file
        subprocess.run([
            "streamlit", "run", temp_filename,
            "--server.address", address,
            "--server.port", str(port)
        ])
    finally:
        # Clean up the temporary file after execution
        os.remove(temp_filename)


if __name__ == "__main__":
    main()
