from datetime import datetime, date, timedelta
from datetime import time as dt_t
import pytz
from dateutil.parser import parse
import calendar
import time


####################
# Common Stuff
####################
def sleep(seconds):
    """
    Pauses the program for the specified number of seconds.

    Parameters:
        seconds (int or float): The duration (in seconds) to pause execution.

    Returns:
        None
    """
    time.sleep(seconds)

def create_timestamp(output_format="%Y%m%d%H%M%S"):
    """
    Generates a timestamp in the specified format.

    Args:
        output_format (str): The desired timestamp format. Defaults to "%Y%m%d%H%M%S".

    Returns:
        str: The current time formatted as per the provided format.

    Example:
        create_time_stamp("%Y-%m-%d %H:%M:%S")
        # Output: "2024-12-21 14:35:42"
    """
    return datetime.now().strftime(output_format)

def create_unix_ts():
    """
    Generates the current Unix timestamp based on the Eastern Time Zone.

    Uses the current time to generate a formatted timestamp, then converts 
    it to a Unix timestamp.

    Returns:
        int: The current Unix timestamp (seconds since epoch in UTC).

    Example:
        >>> create_unix_ts()
        1734863730  # Example output
    """
    ts = create_timestamp(output_format="%Y%m%d%H%M%S")
    unix_ts = convert_to_unix(ts, from_format="%Y%m%d%H%M%S", from_tz="US/Eastern")
    return unix_ts

def get_current_time():
    """
    Returns the current date and time as a `datetime` object.

    Returns:
        datetime: The current date and time.
    
    Example:
        >>> get_current_time()
        datetime.datetime(2024, 12, 22, 14, 35, 42)  # Example output
    """
    return datetime.now()

def get_current_hour(hour_format=24, zero_pad=None):
    """
    Returns the current hour in the specified format (12-hour or 24-hour) with optional zero-padding.

    Parameters:
        hour_format (int, optional): The desired hour format. Accepted values are 12 or 24.
                                     Defaults to 24.
        zero_pad (int, optional): The number of digits for zero-padding in the 24-hour format.
                                  If None, the result is returned as an integer for 24-hour format.
                                  If provided, the result is returned as a string with the specified zero padding.

    Returns:
        int or str: 
            - In 24-hour format: The current hour as an integer or zero-padded string if `zero_pad` is provided.
            - In 12-hour format: The current hour as a string with AM/PM (e.g., "3 PM").

    Raises:
        ValueError: If `hour_format` is not 12 or 24.

    Example:
        >>> get_current_hour(hour_format=24)
        15  # Example output for 3 PM

        >>> get_current_hour(hour_format=24, zero_pad=2)
        '15'

        >>> get_current_hour(hour_format=12)
        '3:15 PM'
    """
    # Get the current hour and minute
    now = datetime.now()
    current_hour_24 = now.hour
    current_minute = now.minute

    # Validate hour_format
    if hour_format not in [12, 24]:
        raise ValueError("hour_format must be 12 or 24.")

    if hour_format == 24:
        # Handle zero-padding for 24-hour format
        if zero_pad is not None:
            return str(current_hour_24).zfill(zero_pad)
        else:
            return current_hour_24
    else:
        # Convert to 12-hour format
        time_string = f"{str(current_hour_24).zfill(2)}{str(current_minute).zfill(2)}00"
        return convert_twenty_four_time_to_twelve_time(time_string, output_format="%I:%M %p")

def get_current_day():
    """
    Returns the current day of the week as a full name (e.g., 'Monday').

    Returns:
        str: The name of the current day (e.g., 'Monday').

    Example:
        >>> get_current_day()
        'Sunday'
    """
    dayInt = datetime.today().weekday()
    if dayInt == 0:
        return 'Monday'
    elif dayInt == 1:
        return 'Tuesday'
    elif dayInt == 2:
        return 'Wednesday'
    elif dayInt == 3:
        return 'Thursday'
    elif dayInt == 4:
        return 'Friday'
    elif dayInt == 5:
        return 'Saturday'
    elif dayInt == 6:
        return 'Sunday'

def get_week_number_for_date(provided_date=None, provided_date_format='%Y%m%d'):
    """
    Gets the ISO week number for a given date. Defaults to the current date if no date is provided.
    ISO weeks start on Mondays.

    Parameters:
        provided_date (str, optional): A date string matching the provided date format.
                                       Defaults to None, which uses the current date.
        provided_date_format (str, optional): The format of the `provided_date` string.
                                              Defaults to '%Y%m%d'.

    Returns:
        int: The ISO week number for the given or current date.

    Raises:
        ValueError: If `provided_date` does not match the `provided_date_format`.

    Example:
        >>> get_week_number_for_current_date()
        51  # Example output for the current week.

        >>> get_week_number_for_current_date("20241222", "%Y%m%d")
        51
    """
    if provided_date is None:
        # Use the current date if no date is provided
        today = date.today()
    else:
        # Parse the provided date string
        date_components = get_date_time_components_given_format(provided_date, provided_date_format)
        today = date(date_components['year'], date_components['month'], date_components['day'])
    
    # Return the ISO week number
    return today.isocalendar()[1]

def get_current_year(convert_to_str=True):
    """
    Retrieves the current year.

    Parameters:
        convert_to_str (bool, optional): 
            If True, returns the year as a string. 
            If False, returns the year as an integer. Defaults to True.

    Returns:
        str or int: The current year in string or integer format, depending on the value of `convert_to_str`.

    Example:
        >>> get_current_year()
        '2024'

        >>> get_current_year(convert_to_str=False)
        2024
    """
    current_year = datetime.now().year
    if convert_to_str:
        return str(current_year)
    else:
        return current_year

def get_current_month(format_type="int"):
    """
    Returns the current month in the specified format.
    
    Parameters:
        format_type (str): The format of the month. 
                           "int" for numerical (default), 
                           "str" for full month name.
                           
    Returns:
        int or str: The current month as an integer or string.
    """
    now = datetime.now()
    
    if format_type == "int":
        return now.month
    elif format_type == "str":
        return now.strftime("%B")
    else:
        raise ValueError("Invalid format_type. Use 'int' or 'str'.")

def extract_date_time_components(date_time_string, input_format='%Y%m%dH%M%S'):
    """
    Extracts individual date and time components (year, month, day, hour, minute, second)
    from a date-time string using a specified format.

    Parameters:
        date_time_string (str): The date-time string to parse (e.g., "20241222153045").
        input_format (str, optional): The format of the `date_time_string`. 
                                      Defaults to '%Y%m%dH%M%S'.

    Returns:
        dict: A dictionary containing the extracted components:
              - 'year' (int): The year component.
              - 'month' (int): The month component.
              - 'day' (int): The day component.
              - 'hour' (int): The hour component.
              - 'minute' (int): The minute component.
              - 'second' (int): The second component.

    Raises:
        ValueError: If `date_time_string` does not match `input_format`.

    Example:
        >>> extract_date_time_components("20241222153045")
        {'year': 2024, 'month': 12, 'day': 22, 'hour': 15, 'minute': 30, 'second': 45}
    """
    time_obj = datetime.strptime(date_time_string, input_format)

    return {
        'year': time_obj.year,
        'month': time_obj.month,
        'day': time_obj.day,
        'hour': time_obj.hour,
        'minute': time_obj.minute,
        'second': time_obj.second,
    }

def get_day_of_week_int_given_day(theDay):
    """
    Converts a day name (e.g., 'Monday') to its corresponding integer 
    where Monday is 0 and Sunday is 6.

    Parameters:
        theDay (str): The full name of the day (e.g., 'Monday').

    Returns:
        int: The corresponding integer for the day of the week (Monday=0, Sunday=6).
        str: 'error' if the input day name is invalid.
    """
    try:
        return list(calendar.day_name).index(theDay)
    except ValueError:
        return 'error'

def get_day_name_given_date(date_string, input_format="%Y%m%dH%M%S"):
    """
    Returns the name of the day (e.g., 'Monday') for a given date string.

    Parameters:
        date_string (str): The date string to parse (e.g., '20241222').
        input_format (str, optional): The format of the input date string. 
                                      Defaults to "%Y%m%dH%M%S".

    Returns:
        str: The name of the day corresponding to the given date.

    Example:
        >>> get_day_name_given_date("20241222", input_format="%Y%m%d")
        'Sunday'
    """
    return datetime.strptime(date_string, input_format).strftime("%A")


####################
# Date Stuff
####################
def get_today_date(convert_to_string_format=None):
    """
    Returns today's date as a `datetime.date` object or a formatted string.

    Parameters:
        convert_to_string_format (str, optional): A date format string to convert the date to a string.
                                                  If None, returns a `datetime.date` object.
    
    Returns:
        datetime.date or str: The current date as a `datetime.date` object or a formatted string.

    Example:
        >>> get_today_date()
        datetime.date(2024, 12, 22)

        >>> get_today_date("%Y-%m-%d")
        '2024-12-22'
    """
    d = date.today()
    if convert_to_string_format is None:
        return d
    else:
        return convert_date_to_string(d, string_format=convert_to_string_format)

def get_date_offset_from_today(x, convert_to_string_format=None):
    """
    Returns the date `x` days from today as a `datetime.date` object or a formatted string.

    Parameters:
        x (int): The number of days from today. Positive for future dates, negative for past dates.
        convert_to_string_format (str, optional): A date format string to convert the date to a string.
                                                  If None, returns a `datetime.date` object.
    
    Returns:
        datetime.date or str: The date `x` days from today as a `datetime.date` object or a formatted string.

    Example:
        >>> get_date_offset_from_today(5)
        datetime.date(2024, 12, 27)

        >>> get_date_offset_from_today(-3, "%Y-%m-%d")
        '2024-12-19'
    """
    d = date.today() + timedelta(days=x)
    if convert_to_string_format is None:
        return d
    else:
        return convert_date_to_string(d, string_format=convert_to_string_format)

def get_yesterday_date(convert_to_string_format=None):
    """
    Returns yesterday's date as a `datetime.date` object or a formatted string.

    Parameters:
        convert_to_string_format (str, optional): A date format string to convert the date to a string.
                                                  If None, returns a `datetime.date` object.
    
    Returns:
        datetime.date or str: Yesterday's date as a `datetime.date` object or a formatted string.

    Example:
        >>> get_yesterday_date()
        datetime.date(2024, 12, 21)

        >>> get_yesterday_date("%Y-%m-%d")
        '2024-12-21'
    """
    d = get_date_offset_from_today(-1)
    if convert_to_string_format is None:
        return d
    else:
        return convert_date_to_string(d, string_format=convert_to_string_format)

def get_tomorrow_date(convert_to_string_format=None):
    """
    Returns tomorrow's date as a `datetime.date` object or a formatted string.

    Parameters:
        convert_to_string_format (str, optional): A date format string to convert the date to a string.
                                                  If None, returns a `datetime.date` object.
    
    Returns:
        datetime.date or str: Tomorrow's date as a `datetime.date` object or a formatted string.

    Example:
        >>> get_tomorrow_date()
        datetime.date(2024, 12, 23)

        >>> get_tomorrow_date("%Y-%m-%d")
        '2024-12-23'
    """
    d = get_date_offset_from_today(1)
    if convert_to_string_format is None:
        return d
    else:
        return convert_date_to_string(d, string_format=convert_to_string_format)
    

####################
# Conversion Stuff
####################
def convert_non_python_format(date_string, time_zone="US/Eastern", single_output_format=None):
    """
    Parses a non-standard or human-readable date/time string (e.g., ISO 8601, epoch) and converts it to 
    the specified timezone. Optionally, returns the result in a single specified format.

    Parameters:
        date_string (str): The date/time string to parse.
        time_zone (str): The desired timezone for the output (default is "US/Eastern").
        single_output_format (str, optional): A format string for `strftime` to return a single formatted 
                                              output. If None, returns a dictionary with various components 
                                              and common formats.

    Returns:
        dict or str: A dictionary with standardized components and common date/time formats if 
                     `single_output_format` is None. Otherwise, returns a single formatted string.

    Raises:
        ValueError: If the date string cannot be parsed or converted.
    """
    try:
        # Parse the input date string
        parsed_time = parse(date_string)
        
        # Convert to the target timezone
        target_tz = pytz.timezone(time_zone)
        localized_time = parsed_time.astimezone(target_tz)

        if single_output_format is None:
            # Generate common formats and components
            output = {
                'datetime_object': localized_time,
                'iso_8601': localized_time.isoformat(),
                'human_readable': localized_time.strftime("%Y-%m-%d %I:%M %p"),
                'year': localized_time.year,
                'month': localized_time.month,
                'day': localized_time.day,
                'hour': localized_time.hour,
                'minute': localized_time.minute,
                'second': localized_time.second,
                '%Y-%m-%d': localized_time.strftime("%Y-%m-%d"),
                '%I:%M %p': localized_time.strftime("%I:%M %p"),
                '%Y%m%d%H%M%S': localized_time.strftime("%Y%m%d%H%M%S")
            }
        else:
            output = localized_time.strftime(single_output_format)
            
    except Exception as e:
        raise ValueError(f"Failed to parse date string '{date_string}': {e}")
        
    return output

def convert_date_to_string(date_to_convert, string_format="%Y%m%d%H%M%S"):
    """
    Converts a `datetime.date` or `datetime.datetime` object to a formatted string.

    Parameters:
        date_to_convert (datetime.date or datetime.datetime): The date object to be converted.
        string_format (str, optional): The desired format of the output string. Defaults to "%Y%m%d%H%M%S".
                                       Refer to Python's `strftime` format codes for valid formats.

    Returns:
        str: The date formatted as a string according to the specified format.

    Raises:
        AttributeError: If the `date_to_convert` object does not support the `strftime` method.

    Example:
        >>> from datetime import datetime
        >>> today = datetime(2024, 12, 22)
        >>> convert_date_to_string(today, string_format="%Y-%m-%d")
        '2024-12-22'

        >>> convert_date_to_string(today)
        '20241222000000'
    """
    return date_to_convert.strftime(string_format)

def convert_twelve_hour_string_to_twenty_four_hour_string(hour_string, minute_string, hour_type="pm"):
    """
    Converts a 12-hour time format (with hour, minute, and AM/PM) to a 24-hour time format.

    Parameters:
        hour_string (str): The hour in 12-hour format (e.g., "1", "12").
                           Should be a string representing an integer.
        minute_string (str): The minutes (e.g., "5", "09").
                             Should be a string representing an integer.
        hour_type (str, optional): Either "am" or "pm" to indicate the time period.
                                   Defaults to "pm".

    Returns:
        str: The time in 24-hour format as a string (e.g., "13:05").
    
    Raises:
        ValueError: If `hour_type` is not "am" or "pm".

    Example:
        >>> convert_twelve_hour_string_to_twenty_four_hour_string("1", "05", "pm")
        '13:05'

        >>> convert_twelve_hour_string_to_twenty_four_hour_string("12", "00", "am")
        '00:00'
    """
    # Normalize input strings
    hour_string = hour_string.zfill(2)
    minute_string = minute_string.zfill(2)
    hour_type = hour_type.lower()

    # Validate hour_type
    if hour_type not in ["am", "pm"]:
        raise ValueError("hour_type must be 'am' or 'pm'.")

    # Convert hour_string based on hour_type
    if hour_string == "12":
        hour_converted = "00" if hour_type == "am" else "12"
    else:
        hour_converted = hour_string if hour_type == "am" else str(int(hour_string) + 12).zfill(2)

    return f"{hour_converted}:{minute_string}"

def convert_twenty_four_time_to_twelve_time(time_string, input_format="%H%M%S", output_format="%I:%M %p",
                                            strip_padded_zero_on_hour=False):
    """
    Converts a time in 24-hour format to 12-hour format with optional customization.

    Parameters:
        time_string (str): The time string in 24-hour format (e.g., "133000" for 1:30 PM).
        input_format (str, optional): The format of the input `time_string`. 
                                      Defaults to "%H%M%S" (24-hour time without separators).
        output_format (str, optional): The desired format for the output time string.
                                       Defaults to "%I:%M %p" (e.g., "01:30 PM").
        strip_padded_zero_on_hour (bool, optional): If True, removes the leading zero from the hour 
                                                    in the 12-hour format (e.g., "01:30 PM" becomes "1:30 PM").
                                                    Defaults to False.

    Returns:
        str: The time converted to the specified 12-hour format.

    Raises:
        ValueError: If the `time_string` does not match the `input_format`.

    Example:
        >>> convert_twenty_four_time_to_twelve_time("133000")
        '01:30 PM'

        >>> convert_twenty_four_time_to_twelve_time("090500", strip_padded_zero_on_hour=True)
        '9:05 AM'

        >>> convert_twenty_four_time_to_twelve_time("154530", input_format="%H%M%S", output_format="%I:%M:%S %p")
        '03:45:30 PM'
    """
    # Parse the input time string into a datetime object
    t = datetime.strptime(time_string, input_format)

    # Format the time into the desired 12-hour format
    answer = t.strftime(output_format)

    # Optionally strip the leading zero from the hour
    if strip_padded_zero_on_hour and answer[0] == "0":
        answer = answer[1:]

    return answer

def convert_string_to_datetime(date_time_string, string_format='%Y%m%dH%M%S'):
    """
    Converts a formatted date-time string to a `datetime.datetime` object.

    Parameters:
        date_time_string (str): The date-time string to convert (e.g., "20241222153045").
        string_format (str, optional): The format of the input string. Defaults to '%Y%m%dH%M%S'.
                                       Refer to Python's `strptime` format codes for valid formats.

    Returns:
        datetime.datetime: The `datetime` object corresponding to the input string.

    Raises:
        ValueError: If the `date_time_string` does not match the provided `string_format`.

    Example:
        >>> convert_string_to_datetime("20241222153045", string_format="%Y%m%dH%M%S")
        datetime.datetime(2024, 12, 22, 15, 30, 45)

        >>> convert_string_to_datetime("2024-12-22 15:30:45", string_format="%Y-%m-%d %H:%M:%S")
        datetime.datetime(2024, 12, 22, 15, 30, 45)
    """
    return datetime.strptime(date_time_string, string_format)

def convert_string_to_timezone(pytz_timezone):
    """
    Converts a given timezone string to a `pytz.timezone` object.

    This function accepts any valid timezone string supported by `pytz` 
    and returns the corresponding timezone object. Below are examples of valid timezones:
        - US/Alaska
        - US/Aleutian
        - US/Arizona
        - US/Central
        - US/East-Indiana
        - US/Eastern
        - US/Hawaii
        - US/Indiana-Starke
        - US/Michigan
        - US/Mountain
        - US/Pacific
        - US/Pacific-New
        - US/Samoa

    Parameters:
        pytz_timezone (str): The name of the timezone (e.g., "US/Eastern").
                             Must be a valid timezone string recognized by `pytz`.

    Returns:
        pytz.timezone: The `pytz.timezone` object corresponding to the given timezone string.

    Raises:
        pytz.UnknownTimeZoneError: If the provided timezone string is not recognized.

    Example:
        >>> tz = convert_timezone("US/Eastern")
        >>> print(tz)
        US/Eastern
    """

    return pytz.timezone(pytz_timezone)

def convert_to_unix(from_ts, from_format="%Y%m%d%H%M%S", from_tz="US/Eastern"):
    """
    Converts a timestamp string from a specified format and timezone into a Unix timestamp.

    Parameters:
        from_ts (str): The input timestamp string to be converted (e.g., "20241222101530").
        from_format (str, optional): The format of the input timestamp string.
                                     Defaults to "%Y%m%d%H%M%S".
        from_tz (str, optional): The timezone of the input timestamp string.
                                 Must be a valid timezone name recognized by `pytz`.
                                 Defaults to "US/Eastern".

    Returns:
        int: The Unix timestamp (seconds since epoch, UTC) corresponding to the input timestamp.

    Raises:
        ValueError: If `from_ts` does not match the specified `from_format`.
        pytz.UnknownTimeZoneError: If `from_tz` is not a valid timezone.

    Example:
        >>> convert_to_unix("20241222101530", from_format="%Y%m%d%H%M%S", from_tz="US/Eastern")
        1734863730

        >>> convert_to_unix("2024-12-22 10:15:30", from_format="%Y-%m-%d %H:%M:%S", from_tz="US/Eastern")
        1734863730
    """

    # Set the time zone for the input timestamp
    from_zone = pytz.timezone(from_tz)

    # Parse the input timestamp string to a datetime object
    local_time = datetime.strptime(from_ts, from_format)

    # Localize the datetime object to the provided time zone
    local_time = from_zone.localize(local_time)

    # Convert the localized time to UTC
    utc_time = local_time.astimezone(pytz.utc)

    # Convert UTC datetime to Unix timestamp
    unix_timestamp = int(utc_time.timestamp())

    return unix_timestamp

def convert_to_iso(from_ts, from_format="%Y%m%d%H%M%S", from_tz="US/Eastern"):
    """
    Converts a timestamp string in a given format to an ISO 8601 formatted string.

    Parameters:
        from_ts (str): The input timestamp string to be converted (e.g., "20241222101530").
        from_format (str, optional): The format of the input timestamp. Defaults to "%Y%m%d%H%M%S".
        from_tz (str, optional): The time zone of the input timestamp. Defaults to "US/Eastern".

    Returns:
        str: The ISO 8601 formatted timestamp in UTC.

    Raises:
        ValueError: If the input timestamp cannot be parsed.

    Example:
        >>> convert_to_iso("20241222101530", from_format="%Y%m%d%H%M%S", from_tz="US/Eastern")
        '2024-12-22T15:15:30+00:00'
    """
    # Set the time zone for the input timestamp
    from_zone = pytz.timezone(from_tz)

    # Parse the input timestamp string to a datetime object
    local_time = datetime.strptime(from_ts, from_format)

    # Localize the datetime object to the provided time zone
    local_time = from_zone.localize(local_time)

    # Convert the localized time to UTC
    utc_time = local_time.astimezone(pytz.utc)

    # Return the ISO 8601 formatted string
    return utc_time.isoformat()

def convert_date_format(date_string, from_format="%Y%m%d%H%M%S", to_format="%m-%d-%Y"):
    """
    Converts a date string from one format to another.

    Parameters:
        date_string (str): The date string to convert (e.g., "20241222153045").
        from_format (str): The format of the input date string.
                           Defaults to "%Y%m%d%H%M%S".
        to_format (str): The desired output format for the date string.
                         Defaults to "%m-%d-%Y".

    Returns:
        str: The converted date string in the specified output format.

    Example:
        >>> convert_date_format("20241222153045", from_format="%Y%m%d%H%M%S", to_format="%m-%d-%Y")
        '12-22-2024'

        >>> convert_date_format("2024-12-22", from_format="%Y-%m-%d", to_format="%d/%m/%Y")
        '22/12/2024'
    """
    return datetime.strptime(date_string, from_format).strftime(to_format)

####################
# Calculation Stuff
####################
def subtract_time_stamps(t1, t2, time_format=None, detailed=False):
    """
    Subtracts two timestamps and returns the difference.
    
    Parameters:
        t1 (str): The first timestamp.
        t2 (str): The second timestamp.
        time_format (str, optional): The format of the timestamps. If None, assumes ISO 8601.
        detailed (bool, optional): If True, returns a breakdown of the difference in 
                                   days, hours, minutes, and seconds. If False, returns
                                   the difference in seconds. Default is False.
    
    Returns:
        int or dict: The difference in seconds (if `detailed` is False) or 
                     a dictionary with a breakdown of the time difference (if `detailed` is True).
    """
    # Parse the timestamps
    if time_format is None:  # Assume ISO 8601
        dt1 = datetime.fromisoformat(t1)
        dt2 = datetime.fromisoformat(t2)
    else:  # Use the provided time format
        dt1 = datetime.strptime(t1, time_format)
        dt2 = datetime.strptime(t2, time_format)
    
    # Calculate the difference
    difference = dt1 - dt2
    total_seconds = int(difference.total_seconds())

    if not detailed:
        return total_seconds
    else:
        # Adjust for days in hours, minutes, and seconds
        days = difference.days
        hours = difference.seconds // 3600
        minutes = (difference.seconds % 3600) // 60
        seconds = difference.seconds % 60

        hours += days * 24
        minutes += days * 1440
        seconds += days * 86400

        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }

def add_days_to_date(start_date, day_increment, input_format="%Y%m%d%H%M%S", ouput_format="%Y%m%d%H%M%S", 
                     force_return_date_object=False):
    """
    Adds a specified number of days to a given start date and returns the resulting date.

    Parameters:
        start_date (str or datetime): The starting date. If a string, it should match the `input_format`. 
                                      If it's a `datetime` object, set `input_format="date"`.
        day_increment (int): The number of days to add to the start date. Can be negative for subtraction.
        input_format (str, optional): The format of the `start_date` if it is a string. 
                                      Default is "%Y%m%d%H%M%S".
        output_format (str, optional): The format of the resulting date if returned as a string.
                                       Default is "%Y%m%d%H%M%S".
        force_return_date_object (bool, optional): If True, returns the resulting date as a `datetime` object. 
                                                   If False, returns a formatted string. Default is False.

    Returns:
        datetime or str: The resulting date as a `datetime` object if `force_return_date_object` is True.
                         Otherwise, returns a string formatted according to `output_format`.

    Raises:
        ValueError: If the `start_date` string does not match the `input_format`.
    
    Example:
        >>> add_days_to_date("20241222000000", 5)
        '20241227000000'
        
        >>> add_days_to_date(datetime(2024, 12, 22, 0, 0), 5, input_format="date", force_return_date_object=True)
        datetime.datetime(2024, 12, 27, 0, 0)
    """
    if input_format != "date":
        date_1 = datetime.strptime(start_date, input_format)
    else:
        date_1 = start_date

    end_date = date_1 + timedelta(days=day_increment)

    if force_return_date_object:
        return end_date
    else:
        return convert_date_to_string(end_date, time_format=ouput_format)
    
def add_seconds_to_time_stamp(base_date_time, seconds_to_add, date_format='%Y%m%d%H%M%S', 
                              force_return_time_object=False):
    """
    Adds a specified number of seconds to a given timestamp and returns the resulting timestamp.

    Parameters:
        base_date_time (str or datetime): The starting date and time. If a string, it should match the `date_format`.
        seconds_to_add (int): The number of seconds to add to the base timestamp. Can be negative for subtraction.
        date_format (str, optional): The format of the `base_date_time` if it is a string.
                                     Default is '%Y%m%d%H%M%S'.
        force_return_time_object (bool, optional): If True, returns the resulting time as a `datetime` object.
                                                   If False, returns a string formatted according to `date_format`.
                                                   Default is False.

    Returns:
        datetime or str: The resulting date and time as a `datetime` object if `force_return_time_object` is True.
                         Otherwise, returns a string formatted according to `date_format`.

    Raises:
        ValueError: If `base_date_time` is a string and does not match the provided `date_format`.

    Example:
        >>> add_seconds_to_time_stamp("20241222000000", 3600)
        '20241222010000'
        
        >>> add_seconds_to_time_stamp(datetime(2024, 12, 22, 0, 0, 0), 3600, force_return_time_object=True)
        datetime.datetime(2024, 12, 22, 1, 0, 0)
    """
    time_object = convert_string_to_datetime(base_date_time, string_format=date_format)
    new_time_object = time_object + timedelta(seconds=seconds_to_add)
    if force_return_time_object:
        return new_time_object
    else:
        return new_time_object.strftime(date_format)
    
def check_if_date_time_string_is_in_given_range(time_to_check, start_range, end_range, input_format="%Y%m%d%H%M%S"):
    """
    Checks if a given date-time string falls within a specified range.

    Parameters:
        time_to_check (str): The date-time string to check.
        start_range (str): The start of the date-time range.
        end_range (str): The end of the date-time range.
        input_format (str, optional): The format of the date-time strings. 
                                      Defaults to "%Y%m%d%H%M%S".

    Returns:
        bool: True if `time_to_check` falls within the range (inclusive), False otherwise.

    Raises:
        ValueError: If any of the input strings do not match the `input_format`.

    Example:
        >>> check_if_date_time_string_is_in_given_range("20241222050000", "20241222000000", "20241223000000")
        True

        >>> check_if_date_time_string_is_in_given_range("20241224050000", "20241222000000", "20241223000000")
        False

        >>> check_if_date_time_string_is_in_given_range("2024-12-22 05:00:00", "2024-12-22 00:00:00", 
        "2024-12-23 00:00:00", input_format="%Y-%m-%d %H:%M:%S")
        True
    """

    time_to_check = datetime.strptime(time_to_check, input_format)
    start_range = datetime.strptime(start_range, input_format)
    end_range = datetime.strptime(end_range, input_format)

    return start_range <= time_to_check <= end_range

def get_week_bounds_given_week_number(week_int, provided_year=None, output_format="%Y%m%d"):
    """
    Retrieves the start (Monday) and end (Sunday) dates of a given ISO week number for a specified year.
    
    Parameters:
        week_int (int or str): The ISO week number (e.g., 1 for the first week of the year).
        provided_year (int or str, optional): The year for which the week bounds are needed.
                                              If None, the current year is used. Defaults to None.
        output_format (str, optional): The format of the returned dates. Defaults to "%Y%m%d".
                                       Refer to Python's `strftime` format codes for valid formats.

    Returns:
        dict: A dictionary containing:
              - 'monday' (str): The date of the Monday of the specified week in the specified format.
              - 'sunday' (str): The date of the Sunday of the specified week in the specified format.

    Raises:
        ValueError: If the provided `week_int` or `provided_year` results in an invalid ISO week or year.

    Notes:
        - Assumes ISO 8601 week numbering, where weeks start on Monday.
        - ISO weeks: Week 1 is the first week with at least four days in the new year.

    References:
        - https://stackoverflow.com/questions/17087314/get-date-from-week-number

    Example:
        >>> get_week_bounds_given_week_number(1, 2024, output_format="%Y-%m-%d")
        {'monday': '2024-01-01', 'sunday': '2024-01-07'}

        >>> get_week_bounds_given_week_number(52, 2023)
        {'monday': '20231225', 'sunday': '20231231'}
    """

    if provided_year is None:
        year = get_current_year()
    else:
        year = str(provided_year)

    to_convert = year + "-" + str(week_int)
    monday = datetime.strptime(to_convert + '-1', "%G-%V-%u")
    sunday = datetime.strptime(to_convert + '-7', "%G-%V-%u")

    monday = convert_date_to_string(monday, string_format=output_format)
    sunday = convert_date_to_string(sunday, string_format=output_format)

    return {"monday": monday, "sunday": sunday}

def get_week_start_and_week_end_dates_for_date(date_input, input_format="%Y%m%d", output_format="%Y%m%d"):
    """
    Calculates the start (Monday) and end (Sunday) dates of the week for a given date.

    Parameters:
        date_input (str): A date string corresponding to the `input_format`.
                          Represents the target date for which the week's start and end dates are calculated.
        input_format (str, optional): The format of the input `date_input`. Defaults to "%Y%m%d".
                                      Refer to Python's `strptime` format codes for valid formats.
        output_format (str, optional): The format of the output dates. Defaults to "%Y%m%d".

    Returns:
        dict: A dictionary containing:
              - "weekStart" (str): The start date (Monday) of the week in the specified `output_format`.
              - "weekEnd" (str): The end date (Sunday) of the week in the specified `output_format`.

    Raises:
        ValueError: If the `date_input` does not match the `input_format`.

    Example:
        >>> get_week_start_and_week_end_dates_for_date("20241222", input_format="%Y%m%d", output_format="%Y-%m-%d")
        {'weekStart': '2024-12-16', 'weekEnd': '2024-12-22'}

        >>> get_week_start_and_week_end_dates_for_date("2024-12-22", input_format="%Y-%m-%d")
        {'weekStart': '20241216', 'weekEnd': '20241222'}
    """

    date_input = convert_string_to_datetime(date_input, string_format=input_format)
    start = date_input - timedelta(days=date_input.weekday())
    end = start + timedelta(days=6)

    return {
        "weekStart": convert_date_to_string(start, string_format=output_format),
        "weekEnd": convert_date_to_string(end, string_format=input_format)
    }

def get_days_in_month(month_int, year_int="current"):
    """
    Returns the number of days in the specified month and year.

    Parameters:
        month_int (int): The month as an integer (1 for January, 12 for December).
        year_int (int or str, optional): The year as an integer (e.g., 2024) or "current" 
                                         to use the current year. Defaults to "current".

    Returns:
        int: The number of days in the specified month.

    Raises:
        ValueError: If `month_int` is not in the range 1 to 12, or if `year_int` is invalid.

    Example:
        >>> get_days_in_month(2, 2024)
        29  # February in a leap year

        >>> get_days_in_month(11)
        30  # Assuming the current year is 2024
    """
    if year_int == "current":
        year = time.localtime().tm_year
    else:
        year = year_int

    days_in_month = calendar.monthrange(year, month_int)[1]

    return days_in_month

def check_if_current_time_is_after_set_target_time(target_hour, target_minute, ref_time=None):
    """
    Checks whether the current time (or a specified reference time) is after or equal 
    to the given target time.

    Parameters:
        target_hour (int): The target hour in 24-hour format (0-23).
        target_minute (int): The target minute (0-59).
        ref_time (datetime.datetime, optional): A reference datetime object to compare against. 
                                                If None, the current time is used. Defaults to None.

    Returns:
        bool: True if the current or reference time is greater than or equal to the target time, 
              False otherwise.

    Raises:
        ValueError: If `target_hour` or `target_minute` is out of range.

    Example:
        >>> check_if_current_time_is_after_set_target_time(15, 30)
        True  # If the current time is 3:35 PM

        >>> ref_time = datetime(2024, 12, 22, 14, 0)
        >>> check_if_current_time_is_after_set_target_time(15, 30, ref_time=ref_time)
        False
    """
    if ref_time is None:
        current_datetime = get_current_time()
    else:
        current_datetime = ref_time

    target_time = dt_t(target_hour, target_minute)

    return current_datetime.time() >= target_time
    
def find_date_in_string(input_string):
    """
    Finds and returns the first matching date in the input string based on predefined patterns.

    Parameters:
        input_string (str): The string to search for dates.

    Returns:
        str or None: The first matched date as a string, or None if no dates are found.

    Patterns:
        - YYYY-MM-DD (e.g., "2024-12-22")
        - MM/DD/YYYY (e.g., "12/22/2024")
        - MM-DD-YYYY (e.g., "12-22-2024")
        - DD Month YYYY (e.g., "22 December 2024")
        - Month DD, YYYY (e.g., "December 22, 2024")
        - YYYYMMDD (e.g., "20241222")
        - YYYYMMDDHHMMSS (e.g., "20241222153045")
        - YY-MM-DD (e.g., "24-12-22")
        - MM/DD/YY (e.g., "12/22/24")
        - MM-DD-YY (e.g., "12-22-24")
        - YYMMDD (e.g., "241222")
        - YYMMDDHHMMSS (e.g., "241222153045")

    Example:
        >>> find_date_in_string("The meeting is scheduled for 2024-12-22.")
        '2024-12-22'

        >>> find_date_in_string("No dates here!")
        None
    """
    import re

    # Define possible date patterns
    date_patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
        r'\b\d{2}/\d{2}/\d{4}\b',  # MM/DD/YYYY
        r'\b\d{2}-\d{2}-\d{4}\b',  # MM-DD-YYYY
        r'\b\d{2} \b\w+ \d{4}\b',  # DD Month YYYY
        r'\b\w+ \d{2}, \d{4}\b',   # Month DD, YYYY
        r'\d{8}',                  # YYYYMMDD
        r'\d{14}',                 # YYYYMMDDHHMMSS
        r'\b\d{2}-\d{2}-\d{2}\b',  # YY-MM-DD
        r'\b\d{2}/\d{2}/\d{2}\b',  # MM/DD/YY
        r'\b\d{2}-\d{2}-\d{2}\b',  # MM-DD-YY
        r'\d{6}',                  # YYMMDD
        r'\d{12}'                  # YYMMDDHHMMSS
    ]

    # Check each pattern in the input string
    for pattern in date_patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group()

    return None