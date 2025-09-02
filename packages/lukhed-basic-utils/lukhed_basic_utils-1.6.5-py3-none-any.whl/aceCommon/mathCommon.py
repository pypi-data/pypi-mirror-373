import random
import statistics


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
