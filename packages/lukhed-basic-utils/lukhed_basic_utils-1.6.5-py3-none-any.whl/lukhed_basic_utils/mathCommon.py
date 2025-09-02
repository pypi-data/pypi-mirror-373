import random
import statistics
import numpy as np
import pandas as pd
from lukhed_basic_utils import matplotlibBasics
from scipy.stats import linregress, percentileofscore


def generate_psuedo_random_number(start, end):
    """
    Generates a pseudo-random integer between the specified start and end values (inclusive).

    Parameters:
        start (int): The lower bound of the random number range.
        end (int): The upper bound of the random number range.

    Returns:
        int: A random integer between start and end (inclusive).

    Example:
        >>> generate_psuedo_random_number(1, 10)
        7
    """
    randNumber = random.randint(start, end)
    return randNumber

def calculate_percent_change(start_num, end_num, round_spot=2):
    """
    Calculates the percentage change between two numbers, rounded to the specified number of decimal places.

    Parameters:
        start_num (float): The starting number.
        end_num (float): The ending number.
        round_spot (int, optional): The number of decimal places to round the result. Defaults to 2.

    Returns:
        float: The percentage change as a decimal (e.g., 0.25 for 25%).
        None: If the starting number is 0, since division by zero is undefined.

    Example:
        >>> calculate_percent_change(100, 125, round_spot=2)
        0.25
    """
    if start_num == 0:
        return None  # Division by zero is undefined
    raw_change = (end_num - start_num) / start_num
    return pretty_round_function(raw_change, round_spot)

def convert_percentage_string_to_float(to_convert, is_list=False, round_spot=2):
    """
    Converts a percentage string (e.g., '75.56%') to a float (e.g., 0.7556). 
    Can also handle lists of percentage strings.

    Parameters:
        to_convert (str or list): The percentage string(s) to convert.
        is_list (bool, optional): If True, expects a list of percentage strings.

    Returns:
        float or list: The converted float(s), rounded to 2 decimal places.
        str: "error" if conversion fails.

    Example:
        >>> convert_percentage_string_to_float('75.56%')
        0.76

        >>> convert_percentage_string_to_float(['75.56%', '50.00%'], is_list=True)
        [0.76, 0.5]
    """
    if is_list:
        try:
            return [pretty_round_function(float(p.strip('%')) / 100, round_spot) for p in to_convert]
        except ValueError:
            raise ValueError("Invalid percentage string in list.")
    else:
        try:
            return pretty_round_function(float(to_convert.strip('%')) / 100, round_spot)
        except ValueError:
            raise ValueError("Invalid percentage string.")

def convert_float_to_string_percent(to_convert, round_spot=2):
    """
    Converts a float to a percentage string rounded to two decimal places.

    Parameters:
        to_convert (float): The float value to convert.

    Returns:
        str: The percentage string (e.g., "75.56%").

    Example:
        >>> convert_float_to_string_percent(0.7556)
        '75.56%'
    """
    return f"{pretty_round_function(to_convert * 100, round_spot)}%"

def convert_int_string_to_int(to_convert):
    """
    Converts a string representation of an integer (e.g., '1,234') to an integer.
    Supports lists of strings as input.

    Parameters:
        to_convert (str or list): The string(s) to convert.

    Returns:
        int or list: The converted integer(s).
        str: "error" if conversion fails.

    Example:
        >>> convert_int_string_to_int("1,234")
        1234

        >>> convert_int_string_to_int(["1,234", "2,345"])
        [1234, 2345]
    """
    try:
        if isinstance(to_convert, list):
            return [int(x.replace(',', '').replace('+', '')) for x in to_convert]
        else:
            return int(to_convert.replace(',', '').replace('+', ''))
    except ValueError as e:
        raise ValueError(f"Invalid integer string: {e}")

def convert_float_to_string_percent(to_convert, round_spot=2):
    """
    Converts a float to a percentage string rounded to two decimal places.

    Parameters:
        to_convert (float): The float value to convert.

    Returns:
        str: The percentage string (e.g., "75.56%").

    Example:
        >>> convert_float_to_string_percent(0.7556)
        '75.56%'
    """
    return f"{pretty_round_function(to_convert * 100, round_spot)}%"
        
def pretty_round_function(float_num, round_num=2):
    """
    Rounds a float to the specified number of decimal places and ensures
    the result always has exactly that many decimal places in string representation.

    Parameters:
        float_num (float): The number to round.
        round_num (int, optional): The number of decimal places to round to. Defaults to 2.

    Returns:
        float: The rounded number with consistent decimal places in its string representation.

    Example:
        >>> pretty_round_function(1.5, 2)
        1.50

        >>> pretty_round_function(1.234, 2)
        1.23
    """
    return float(f"{float_num:.{round_num}f}")

def get_average_given_list(list_to_average, round_spot=2):
    """
    Calculates the average of a list of numbers, rounded to the specified number of decimal places.

    Parameters:
        list_to_average (list): The list of numbers to average.
        round_spot (int, optional): The number of decimal places to round to. Defaults to 2.

    Returns:
        float: The average of the list, rounded to the specified decimal places.

    Example:
        >>> get_average_given_list([1, 2, 3, 4, 5], round_spot=1)
        3.0
    """
    s = sum(list_to_average)
    values = len(list_to_average)
    return pretty_round_function(s / values, round_spot)

def scale_list_by_factor(list_to_scale, factor, round_spot=2):
    """
    Scales each value in a list by a specified factor, rounding the results to a defined number of decimal places.

    Parameters:
        list_to_scale (list): A list of numerical values to scale.
        factor (float): The factor by which to scale each value in the list.
        round_spot (int, optional): The number of decimal places to round each scaled value. Defaults to 2.

    Returns:
        list: A list of scaled and rounded values.

    Example:
        >>> scale_list_by_factor([1.5, 2.3, 3.0], 1.1)
        [1.65, 2.53, 3.3]

        >>> scale_list_by_factor([10, 20, 30], 0.5, round_spot=1)
        [5.0, 10.0, 15.0]
    """
    return [pretty_round_function(x * factor, round_spot) for x in list_to_scale]

def make_list_relative_to_max(list_of_values, sort=False, round_spot=2):
    """
    Scales a list of values to be relative to the maximum value in the list.

    Parameters:
        list_of_values (list): The list of numbers to scale.
        sort (bool, optional): If True, sorts the result in descending order. Defaults to False.

    Returns:
        list: A list of values scaled relative to the maximum value.

    Example:
        >>> make_list_relative_to_max([10, 20, 30], sort=True)
        [1.0, 0.67, 0.33]
    """

    list_max = max(list_of_values)
    relative_list = [pretty_round_function(x / list_max, round_spot) for x in list_of_values]
    if sort:
        relative_list.sort(reverse=True)
    return relative_list

def get_median_given_list(list_data, round_spot=2):
    """
    Calculates the median of a list of numerical values, rounding the result to a specified number of decimal places.

    Parameters:
        list_data (list): A list of numerical values.
        round_spot (int, optional): The number of decimal places to round the median. Defaults to 2.

    Returns:
        float: The median value of the list, rounded to the specified number of decimal places.

    Example:
        >>> get_median_given_list([1, 2, 3, 4, 5])
        3.0

        >>> get_median_given_list([10, 20, 30, 40], round_spot=1)
        25.0
    """
    median_value = statistics.median(list_data)
    return pretty_round_function(median_value, round_spot)

def get_np():
    """
    Returns the numpy module.
    :return:
    """
    return np

def get_pd():
    """
    Returns the pandas module.
    :return:
    """
    return pd

def calculate_number_set_data(num_list):
    d = np.array(num_list)
    total_values = len(num_list)
    mean = np.mean(d)
    sigma = np.std(d)
    median = np.median(d)
    ninety_percentile = np.percentile(d, 90)
    ten_percentile = np.percentile(d, 10)

    op_dict = {
        "length": total_values,  # The values of the histogram bins.
        "mean": mean,  # The edges of the bins.
        "median": median,
        "standardDeviation": sigma,
        "90Percentile": ninety_percentile,
        "10Percentile": ten_percentile,
        "min": min(num_list),
        "max": max(num_list)
    }

    return op_dict

def create_histogram(value_list, bins='auto', color='auto', x_axis_title=None, title=None, show_plot=True, save_location=None):
    """
    Plots a histogram of the values provided, returns the relevant information about the plot.
    :param value_list: list(), list of values you want to create a histogram on
    :param bins: can be "auto" to be auto generated, an int() to specify the number of equal bins to be created for
                 the histogram, or a list, which must follow document here:
                 https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.hist.html
    :param color: str(), hex color, example: #0504aa
    :param show_plot: bool(), True=will show plot, False=will not
    :param x_axis_title: str(), title to display on the histogram x axis
    :param title: str(), title to display for the histogram title
    :param save_location: str(), path where you want to save the image
    :return: dict(), information about the histogram
    """
    op_dict = dict()
    plt = matplotlibBasics.get_plt()

    d = np.array(value_list)
    mean = np.mean(d)
    sigma = np.std(d)
    ninety_percentile = np.percentile(d, 90)
    ten_percentile = np.percentile(d, 10)
    if color == 'auto':
        color = '#0504aa'

    if x_axis_title is None:
        x_axis_title = ""
    if title is None:
        title = ""

    n, bins, patches = plt.hist(x=d, bins=bins, color=color, rwidth=.85)

    plt.grid(axis='y')
    plt.xlabel(x_axis_title)
    plt.ylabel('Frequency')
    plt.title(title)
    max_freq = n.max()

    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(max_freq / 10) * 10 if max_freq % 10 else max_freq + 10)
    plt.axvline(mean, color='r', linewidth=1, label="Mean = " + str(pretty_round_function(mean)))
    plt.axvline(ninety_percentile, color='g', linewidth=1, label="90th % = " + str(pretty_round_function(ninety_percentile)))
    plt.legend()
    plt.figtext(0.1, 0, "std = " + str(pretty_round_function(sigma)))

    if show_plot:
        plt.show()

    op_dict = {
        "n": n,                         # The values of the histogram bins.
        "bins": bins,                   # The edges of the bins.
        "patches": patches,             # Container of individual artists used to create the histogram
        "mean": mean,
        "standardDeviation": sigma,
        "90Percentile": ninety_percentile
    }

    if save_location is None:
        return op_dict
    else:
        plt.savefig(save_location)
        return op_dict
    
def return_outlier_in_list(data_1):
    # data_1 is a list of numbers that is examined. List of outliers is returned.
    outliers = []

    threshold = 3
    mean_1 = np.mean(data_1)
    std_1 = np.std(data_1)

    for y in data_1:
        z_score = (y - mean_1) / std_1
        if np.abs(z_score) > threshold:
            outliers.append(y)

    return outliers

def simple_moving_average_given_list(list_of_period_values, period_average):
    # takes in a list of values and period average desired
    # returns a moving average list
    # if x_labels is added, the x_lables that apply to the average desired will be returned
    x = np.array(list_of_period_values)
    w = period_average
    return list(_numpy_functions_supporting_moving_average(x, w))

def _numpy_functions_supporting_moving_average(x, w):
    # This function will be taking the convolution of the sequence x and a sequence of ones of length w.
    # Note that the chosen mode is valid so that the convolution product is only given
    # for points where the sequences overlap completely.
    # https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-numpy-scipy
    return np.convolve(x, np.ones(w), 'valid') / w

def simple_moving_average_given_dict(data_series_dict, period, **kwargs):
    # Takes in a dictionary of the data series you want a moving average you want. Will be applied to y (second item)
    # Example:
    # input_dict = {
    #                   'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11, 12],
    #                   'y': [290, 260, 288, 300, 310, 303, 329, 340, 316, 330, 308, 310]
    #           }
    # output_dict = {
    #                   'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    #                   'y': [290, 260, 288, 300, 310, 303, 329, 340, 316, 330, 308, 310]
    #                   'ma': [nan, nan, nan, nan, nan, 291.., 298.., 311.., 316.., 321.., 321.0.., 322..]
    # kwargs: round=#, series='key to apply average to' (by default the second key is chosen)

    target_series = ''
    if 'series' in kwargs:
        target_series = kwargs['series']
    else:
        i = 0
        for key in data_series_dict:
            if i == 1:
                target_series = key
            i = i + 1

    df = pd.DataFrame(data_series_dict)
    df['ma'] = df.rolling(window=period)[target_series].mean()
    op_dict = df.to_dict(orient='list')

    if 'round' in kwargs:
        round_digit = kwargs['round']
        i = 0
        while i < len(op_dict['ma']):
            op_dict['ma'][i] = round(op_dict['ma'][i], round_digit)
            i = i + 1

    return op_dict

def trend_detector(list_of_x, list_of_y, order=1):
    result = np.polyfit(list_of_x, list_of_y, order)
    slope = result[-2]
    return float(slope)

def best_fit_line_calculations(list_of_x, list_of_y):
    line_info = linregress(list_of_x, list_of_y)
    return line_info

def data_frame_to_x_y_list(df):
    x_list = df.index.tolist()
    y_list = df.values.tolist()
    return x_list, y_list

def translate_list_to_percentile(list_to_translate):
    return [percentileofscore(list_to_translate, x, 'rank') for x in list_to_translate]

def convert_list_to_np_array(list_to_convert):
    return np.array(list_to_convert)