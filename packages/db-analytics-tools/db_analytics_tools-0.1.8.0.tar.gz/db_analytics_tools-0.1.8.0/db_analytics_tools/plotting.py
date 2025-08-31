# coding : utf-8

"""
    DB Analytics Tools Data Visualization
"""

import matplotlib.pyplot as plt


def pie_chart(label, size, data):
    """
    Create a pie chart.

    :param label: A column from the dataset to be used as labels for each slice of the pie chart.
    :param size: A column from the dataset to be used as the size of each slice.
    :param data: The dataset containing the data for the pie chart.
    """
    plt.pie(x=data[size], labels=data[label], autopct='%.2f')


def donut_chart(label, size, data):
    """
    Create a donut chart.

    :param label: A column from the dataset to be used as labels for each slice of the donut chart.
    :param size: A column from the dataset to be used as the size of each slice.
    :param data: The dataset containing the data for the donut chart.
    """
    plt.pie(x=data[size], labels=data[label], autopct='%.2f')


def bar_plot(label, height, data):
    """
    Create a bar plot.

    :param label: A column from the dataset to be used as labels for the bars.
    :param height: A column from the dataset to be used as the height of the bars.
    :param data: The dataset containing the data for the bar plot.
    """
    plt.bar(x=data[label], height=data[height])


def line_plot(x, y, data):
    """
    Create a line plot.

    :param x: A column from the dataset to be used as the x-axis values.
    :param y: A column from the dataset to be used as the y-axis values.
    :param data: The dataset containing the data for the line plot.
    """
    plt.plot(data[x], data[y])
