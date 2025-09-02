from difflib import SequenceMatcher
from re import sub
import json
import re


def remove_all_white_space_characters(string_to_alter):
    """
    Removes all extra whitespace characters from a string, leaving only single spaces between words.

    Parameters:
        string_to_alter (str): The input string to modify.

    Returns:
        str: A string with all extra whitespace removed.

    Example:
        >>> remove_all_white_space_characters("This   is  a   test")
        'This is a test'
    """
    new_string = " ".join(string_to_alter.split())
    return new_string

def remove_numbers_from_string(string_to_alter):
    """
    Removes all numeric characters from a given string.

    Parameters:
        string_to_alter (str): The input string to modify.

    Returns:
        str: A string with all numbers removed.

    Example:
        >>> remove_numbers_from_string("abc123def456")
        'abcdef'
    """
    return re.sub(r'\d', '', string_to_alter)

def extract_numbers_from_string(string_with_number):
    """
    Extracts all numeric substrings from a given string.

    Parameters:
        string_with_number (str): The input string containing numbers.

    Returns:
        list: A list of numeric substrings found in the input string.

    Example:
        >>> extract_numbers_from_string("abc123def456")
        ['123', '456']
    """
    number_pattern = r'\d+'  # Matches one or more digits
    matches = re.findall(number_pattern, string_with_number)
    return matches

def add_substring_at_specified_index(string_to_alter, string_to_add, position_to_add):
    """
    Inserts a substring into a string at the specified index.

    Parameters:
        string_to_alter (str): The original string.
        string_to_add (str): The substring to insert.
        position_to_add (int): The index at which to insert the substring.

    Returns:
        str: The modified string with the substring inserted.

    Example:
        >>> add_substring_at_specified_index("HelloWorld", " ", 5)
        'Hello World'
    """
    new_string = string_to_alter[: position_to_add] + string_to_add + string_to_alter[position_to_add:]
    return new_string

def get_special_str(special_str):
    """
    Converts a keyword or phrase into a corresponding special character.

    Parameters:
        special_str (str): The input keyword or phrase (e.g., "alert", "checkmark").

    Returns:
        str: The corresponding special character, or None if no match is found.

    Example:
        >>> get_special_str("checkmark")
        '✅'

        >>> get_special_str("unknown")
        None
    """
    special_str = special_str.lower()
    mapping = {
        "alert": "🚨",
        "siren": "🚨",
        "police car light": "🚨",
        "checkmark": "✅",
        "check mark": "✅",
        "check": "✅",
        "cross": "✖",
        "cross mark": "✖",
        "x": "✖",
        "crossmark": "✖",
        "push": "⏺",
        "robot": "🤖",
        "note": "📝",
        "notepad": "📝",
        "black x": "✖️",
        "black cross": "✖️",
        "?": "❔",
        "question mark": "❔",
        "question": "❔"
    }
    return mapping.get(special_str)

def return_similar_metric(string1, string2):
    """
    Calculates the similarity ratio between two strings using SequenceMatcher.

    Parameters:
        string1 (str): The first string.
        string2 (str): The second string.

    Returns:
        float: A similarity ratio between 0 and 1, where 1 indicates identical strings.

    Example:
        >>> return_similar_metric("hello", "helo")
        0.8
    """
    return SequenceMatcher(None, string1, string2).ratio()

def convert_float_to_currency(float_to_convert):
    """
    Converts a float to a currency-formatted string.

    Parameters:
        float_to_convert (float): The float value to format.

    Returns:
        str: The currency-formatted string (e.g., "$1,234.56").

    Example:
        >>> convert_float_to_currency(1234.56)
        '$1,234.56'
    """
    return "${:,.2f}".format(float_to_convert)

def convert_currency_string_to_float(money_string):
    """
    Converts a currency-formatted string to a float.

    Parameters:
        money_string (str): The currency string to convert (e.g., "$1,234.56").

    Returns:
        float: The numeric value of the currency string.

    Example:
        >>> convert_currency_string_to_float("$1,234.56")
        1234.56
    """
    return float(sub(r'[^\d.]', '', money_string))

def convert_string_to_json(str_to_convert):
    """
    Converts a JSON-formatted string into a Python dictionary or list.

    Parameters:
        str_to_convert (str): The JSON-formatted string to parse.

    Returns:
        dict or list: The parsed Python object (e.g., a dictionary or list).

    Raises:
        json.JSONDecodeError: If the string is not valid JSON.

    Example:
        >>> convert_string_to_json('{"key": "value"}')
        {'key': 'value'}
    """
    return json.loads(str_to_convert)
