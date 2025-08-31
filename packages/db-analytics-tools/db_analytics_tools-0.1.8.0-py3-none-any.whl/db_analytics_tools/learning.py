# coding : utf-8

"""
    DB Analytics Tools Machine Learning
"""


import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt


class ForecastKPI:
    """
    A class to forecast Key Performance Indicators (KPIs) using historical data.
    """

    def __init__(self, historical_data, date_column):
        """
        Initializes the ForecastKPI class with historical data.

        :param historical_data: A Pandas DataFrame containing historical KPI data.
        :param date_column: The name of the column containing date information.
        """
        self.historical_data = historical_data
        self.date_column = date_column
        self.kpi_columns = historical_data.columns.difference([date_column])

    def describe(self):
        """
        Provides a summary of the historical KPI data.
        """
        data = []
        for col in self.kpi_columns:
            data.append({
                "KPI": col,
                "Mean": self.historical_data[col].mean(),
                "Median": self.historical_data[col].median(),
                "Min": self.historical_data[col].min(),
                "Max": self.historical_data[col].max(),
                "Std Dev": self.historical_data[col].std(),
                "Missing Values": self.historical_data[col].isnull().sum()
            })
            
        return pd.DataFrame(data)

    def decompose_time_series(self, kpi_name, model='additive', period=None, plot=True):
        """
        Decomposes a specific KPI into trend, seasonal, and residual components.

        :param kpi_name: The name of the KPI column to decompose.
        :param model: The type of decomposition model ('additive' or 'multiplicative').
                      Additive: Use when seasonal variations are constant over time.
                      Multiplicative: Use when seasonal variations are proportional to the trend.
        :param period: The number of observations in a cycle (e.g., 12 for monthly data).
                       If not provided, statsmodels will try to infer it.
        :param plot: If True, plots the decomposed components.
        :return: A DecomposeResult object containing the components.
        """
        if kpi_name not in self.kpi_columns:
            raise ValueError(f"KPI '{kpi_name}' not found in the data.")
        
        series = self.historical_data[kpi_name].dropna()
        
        # Check if there's enough data for decomposition
        if len(series) < 2 * period if period else len(series) < 2:
            raise ValueError("Not enough data to perform decomposition.")

        result = seasonal_decompose(series, model=model, period=period)

        if plot:
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True, figsize=(12, 10))
            ax1.set_title(f'Décomposition de la série temporelle pour {kpi_name}', fontsize=16)
            
            result.observed.plot(ax=ax1, title='Original')
            ax1.grid(True)
            
            result.trend.plot(ax=ax2, title='Tendance')
            ax2.grid(True)
            
            result.seasonal.plot(ax=ax3, title='Saisonnalité')
            ax3.grid(True)
            
            result.resid.plot(ax=ax4, title='Résidus (Bruit)')
            ax4.grid(True)
            
            plt.tight_layout()
            plt.show()

        return result

    def train_model(self):
        """
        Trains a machine learning model on the historical data.
        """
        pass

    def predict(self, future_dates):
        """
        Predicts KPI values for the given future dates.

        :param future_dates: A list of future dates to predict KPI values for.
        :return: A Pandas DataFrame containing the predicted KPI values.
        """
        pass
