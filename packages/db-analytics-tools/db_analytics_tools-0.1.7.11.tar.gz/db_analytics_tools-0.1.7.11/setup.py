# coding : utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="db_analytics_tools",
    version="0.1.7.11",
    url="https://joekakone.github.io/#projects",
    download_url="https://github.com/joekakone/db-analytics-tools",
    project_urls={
        "Bug Tracker": "https://github.com/joekakone/db-analytics-tools/issues",
        "Documentation": "https://joekakone.github.io/db-analytics-tools",
        "Source Code": "https://github.com/joekakone/db-analytics-tools",
    },
    license="MIT",
    author="Joseph Konka",
    author_email="joseph.kakone@gmail.com",
    description="Databases Tools for Data Analytics",
    keywords="databases analytics etl sql orc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "psycopg2-binary>=2.9.9",
        "pyodbc>=5.1.0",
        "pandas>=2.2.1",
        "SQLAlchemy>=2.0.29",
        "streamlit>=1.32.2",
        "matplotlib>=3.4.3"
    ],
    python_requires=">=3.10",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "db_tools=db_analytics_tools.webapp:main"
        ],
    },
)