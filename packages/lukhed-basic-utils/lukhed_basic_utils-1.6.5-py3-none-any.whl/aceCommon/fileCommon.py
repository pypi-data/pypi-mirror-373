import csv
import json
from zipfile import ZipFile


def return_lines_in_file(filePath, delimiter=",", skip_header=False, single_column=False):
    """
    Reads a CSV file and returns its contents as a list of lists or a list of strings (optional).

    Parameters:
        filePath (str): Path to the file to read.
        delimiter (str, optional): Delimiter used in the CSV file. Defaults to ",".
        skip_header (bool, optional): If True, skips the first line of the file. Defaults to False.
        single_column (bool, optional): If True, returns only the first column of each row. Defaults to False.

    Returns:
        list: A list of lists (each line as a list of columns) or a list of strings (first column only).

    Example:
        >>> return_lines_in_file("example.csv", delimiter=",", skip_header=True, single_column=True)
        ['header1', 'header2', ...]
    """
    return_list = []

    with open(filePath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)

        if skip_header:
            next(reader)

        if single_column:
            for row in reader:
                return_list.append(row[0])
        else:
            for row in reader:
                return_list.append(row)

    return return_list


def write_zip_to_csv(zipObject, filePath, headerList):
    """
    Writes a zipped object to a CSV file with a header.

    Parameters:
        zipObject (iterable): The zipped object containing rows of data.
        filePath (str): Path to the CSV file to create.
        headerList (list): List of column headers.

    Returns:
        None

    Example:
        >>> write_zip_to_csv(zip([1, 2], [3, 4]), "output.csv", ["Column1", "Column2"])
    """
    with open(filePath, 'w', encoding='utf-8', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(headerList)
        wr.writerows(zipObject)


def write_list_of_list_to_csv(filePath, ll):
    """
    Writes a list of lists to a CSV file.

    Parameters:
        filePath (str): Path to the CSV file to create.
        ll (list of lists): The data to write, where each inner list represents a row.

    Returns:
        None

    Example:
        >>> write_list_of_list_to_csv("output.csv", [[1, 2], [3, 4]])
    """
    with open(filePath, 'w', encoding='utf-8', newline='') as f:
        csv_out = csv.writer(f)
        csv_out.writerows(ll)


def add_line_to_csv(filePath, listToAdd, location=None, create=False):
    """
    Adds a line to a CSV file. Optionally inserts the line at a specific location and creates the file if it doesn't 
    exist.

    Parameters:
        filePath (str): Path to the CSV file to update.
        listToAdd (list): The line to add, represented as a list of values.
        location (int, optional): The line index to insert the new line. If None, appends the line to the end. 
        Defaults to None. create (bool, optional): If True, creates the file if it doesn't exist. Defaults to False.

    Returns:
        None

    Example:
        >>> add_line_to_csv("example.csv", ["value1", "value2"], location=0, create=True)
    """
    lines = []

    # Check if the file should be created if it doesn't exist
    if create:
        try:
            with open(filePath, 'r', encoding='utf-8') as test_file:
                pass
        except FileNotFoundError:
            create_blank_file(filePath)

    # Read existing content from the file
    with open(filePath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            lines.append(row)

    # Add the new line to the specified location or append to the end
    if location is None:
        lines.append(listToAdd)
    else:
        lines.insert(location, listToAdd)

    # Write the updated content back to the file
    with open(filePath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(lines)


def update_csv_file_given_line_and_column(fPath, update_line_list, update_column_list, update_entry_list):
    """
    Updates specific entries in a CSV file based on line and column indices.

    Parameters:
        fPath (str): Path to the CSV file to update.
        update_line_list (list): List of line indices to update.
        update_column_list (list): List of column indices corresponding to each line.
        update_entry_list (list): List of new values to insert at the specified line and column indices.

    Returns:
        None

    Example:
        >>> update_csv_file_given_line_and_column("example.csv", [0, 1], [1, 2], ["new1", "new2"])
    """
    lines = list()

    previous_version = return_lines_in_file(fPath)

    counter = 0
    for rIndex in update_line_list:
        cIndex = update_column_list[counter]
        entry = update_entry_list[counter]
        if isinstance(cIndex, int):
            previous_version[rIndex][cIndex] = entry
        else:
            previous_version[rIndex].append(entry)
        counter = counter + 1

    write_list_of_list_to_csv(fPath, previous_version)


def append_column_to_file(fpath, column_as_list):
    """
    Appends a new column to a CSV file.

    Parameters:
        fpath (str): Path to the CSV file to update.
        column_as_list (list): List of values to append as a new column. 
                               The length must match the number of rows in the file.

    Returns:
        None

    Example:
        >>> append_column_to_file("example.csv", ["new1", "new2"])
    """
    previous_version = return_lines_in_file(fpath)

    counter = 0
    for line in previous_version:
        line.append(column_as_list[counter])
        counter = counter + 1
    write_list_of_list_to_csv(fpath, previous_version)


def write_list_to_file(fpath, list_to_write, **kwargs):
    """
    Writes a list of strings to a file, each as a separate line.

    Parameters:
        fpath (str): Path to the file to create or overwrite.
        list_to_write (list): The list of strings to write.
        **kwargs:
            - endline (str, optional): 'yes' to add a newline after each item. Defaults to 'yes'.

    Returns:
        None

    Example:
        >>> write_list_to_file("example.txt", ["line1", "line2"], endline="no")
    """
    chartTitle = ''
    endFlag = 'yes'
    if 'endline' in kwargs:
        endFlag = kwargs.get('endline')
    if endFlag == 'yes':
        with open(fpath, 'w') as f:
            for item in list_to_write:
                f.write(item + '\n')
    else:
        with open(fpath, 'w') as f:
            for item in list_to_write:
                f.write(item)


def write_json_string_to_file(fpath, jayson):
    """
    Writes a JSON string to a file.

    Parameters:
        fpath (str): The path to the file where the JSON string will be written.
        jayson (str): The JSON string to write to the file.

    Returns:
        None

    Example:
        >>> json_data = '{"name": "John", "age": 30}'
        >>> write_json_string_to_file("data.json", json_data)
    """
    with open(fpath, 'w') as f:
        f.writelines(jayson)


def load_json_from_file(fpath):
    """
    Loads JSON data from a file and returns it as a Python object.

    Parameters:
        fpath (str): The path to the JSON file to load.

    Returns:
        dict: A dictionary or list parsed from the JSON file. If the file is empty or contains invalid JSON, returns an empty dictionary.

    Example:
        >>> data = load_json_from_file("data.json")
        >>> print(data)
        {"name": "John", "age": 30}
    """
    with open(fpath, 'r') as f:
        try:
            op_json = json.load(f)
        except json.decoder.JSONDecodeError:
            op_json = dict()

    return op_json


def dump_json_to_file(fpath, jayson_dict_or_list_of_dicts):
    """
    Writes a Python dictionary or list of dictionaries to a file in JSON format.

    Parameters:
        fpath (str): The path to the file where the JSON data will be written.
        jayson_dict_or_list_of_dicts (dict or list): The data to write to the file in JSON format.

    Returns:
        None

    Example:
        >>> data = {"name": "John", "age": 30}
        >>> dump_json_to_file("data.json", data)
    """
    with open(fpath, 'w') as f:
        json.dump(jayson_dict_or_list_of_dicts, f)


def clear_file(fpath):
    """
    Clears the contents of a file by overwriting it with an empty string.

    Parameters:
        fpath (str): The path to the file to clear.

    Returns:
        None

    Example:
        >>> clear_file("data.txt")
    """
    with open(fpath, 'w') as f:
        test = 1


def write_line_to_file(fpath, string_to_write):
    """
    Writes a single line to a file, overwriting its contents.

    Parameters:
        fpath (str): The path to the file to write to.
        string_to_write (str): The string to write as a single line in the file.

    Returns:
        None

    Example:
        >>> write_line_to_file("data.txt", "This is a test line.")
    """
    with open(fpath, 'w') as the_file:
        the_file.write(string_to_write)


def read_single_line_from_file(fpath):
    """
    Reads the first line from a file.

    Parameters:
        fpath (str): The path to the file to read.

    Returns:
        str: The first line of the file as a string.

    Example:
        >>> line = read_single_line_from_file("data.txt")
        >>> print(line)
        "This is a test line."
    """
    with open(fpath) as f:
        config = f.readline()

    return config


def return_column_in_csv_as_list(f_path, col_index, header='no'):
    """
    Extracts a specific column from a CSV file and returns it as a list.

    Parameters:
        f_path (str): The path to the CSV file.
        col_index (int): The index of the column to extract (starting from 0).
        header (str, optional): If 'yes', skips the first line (header) of the file. Defaults to 'no'.

    Returns:
        list: A list of values from the specified column.

    Example:
        >>> return_column_in_csv_as_list("data.csv", 1, header="yes")
        ['value1', 'value2', 'value3']
    """

    return_list = list()

    with open(f_path, 'r', encoding='utf-8') as f:
        temp = csv.reader(f, delimiter=',')
        if header == 'yes':
            next(temp)
        counter = 0
        for row in temp:
            return_list.append(row[col_index])
            counter = counter + 1

    return return_list


def write_content_to_file(f_name, content):
    """
    Writes binary content to a file.

    Parameters:
        f_name (str): The path to the file to write to.
        content (bytes): The binary content to write.

    Returns:
        None

    Example:
        >>> content = b"Binary data here"
        >>> write_content_to_file("output.bin", content)
    """
    with open(f_name, 'wb') as f:
        f.write(content)


def unzip_file(path_to_zip_file):
    """
    Extracts all files from a ZIP archive.

    Parameters:
        path_to_zip_file (str): Path to the ZIP file to extract.

    Returns:
        None

    Raises:
        FileNotFoundError: If the ZIP file does not exist.
        BadZipFile: If the file is not a valid ZIP file.

    Example:
        >>> unzip_file("example.zip")
    """
    with ZipFile(path_to_zip_file, 'r') as zip_file:
        zip_file.extractall()


def create_blank_file(f_path):
    """
    Creates an empty file at the specified path. If the file already exists, it will be cleared.

    Parameters:
        f_path (str): The path to the file to create or clear.

    Returns:
        None

    Example:
        >>> create_blank_file("new_file.txt")
    """
    with open(f_path, 'w') as fp:
        pass