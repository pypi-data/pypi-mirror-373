from random import randint


def sort_list_based_on_reference_list(ref_list, list_to_sort):
    """
    Sorts a list based on the order of values in a reference list.

    Parameters:
        ref_list (list): The reference list that defines the sorting order.
        list_to_sort (list): The list to sort based on the reference list.

    Returns:
        list: A sorted version of `list_to_sort` aligned with `ref_list`.

    Example:
        >>> sort_list_based_on_reference_list([3, 1, 2], ['c', 'a', 'b'])
        ['a', 'b', 'c']
    """
    return [x for (y, x) in sorted(zip(ref_list, list_to_sort), key=lambda pair: pair[0])]

def sort_two_lists_based_on_list_with_values(list_with_values, corresponding_list, reverse=False):
    """
    Sorts two lists simultaneously based on the values of one list.

    Parameters:
        list_with_values (list): The primary list used for sorting.
        corresponding_list (list): The secondary list to be sorted in parallel.
        reverse (bool, optional): If True, sorts in descending order. Defaults to False.

    Returns:
        tuple: Two lists, both sorted based on `list_with_values`.

    Example:
        >>> sort_two_lists_based_on_list_with_values([6, 1, 7], ['cat', 'dog', 'bird'])
        ([1, 6, 7], ['dog', 'cat', 'bird'])
    """
    combined = sorted(zip(list_with_values, corresponding_list), reverse=reverse)
    return [x[0] for x in combined], [x[1] for x in combined]

def sort_a_list_of_dicts_based_on_key(dict_list, key_to_sort, reverse=False):
    """
    Sorts a list of dictionaries based on the values of a specified key.

    Parameters:
        dict_list (list): A list of dictionaries to sort.
        key_to_sort (str): The key whose values will determine the sorting order.
        reverse (bool, optional): If True, sorts in descending order. Defaults to False.

    Returns:
        list: The sorted list of dictionaries.

    Example:
        >>> sort_a_list_of_dicts_based_on_key(
        ...     [{'a': 3}, {'a': 1}, {'a': 2}], key_to_sort='a'
        ... )
        [{'a': 1}, {'a': 2}, {'a': 3}]
    """
    return sorted(dict_list, key=lambda x: x[key_to_sort], reverse=reverse)

def list_term_finder(s_list, matcher, indices=None, first=False, in_string=False, return_index=False):
    """
    Searches a list for items matching a given term, with options for case-insensitive matching.

    Parameters:
        s_list (list): The list to search.
        matcher (str): The term to match.
        indices (list, optional): Specific indices to search in each list element. Defaults to None.
        first (bool, optional): If True, returns the first match only. Defaults to False.
        in_string (bool, optional): If True, uses substring matching. Defaults to False.
        return_index (bool, optional): If True, returns the index of matching items. Defaults to False.

    Returns:
        list or int: A list of matching items or indices, or a single match if `first` is True.

    Example:
        >>> list_term_finder(['apple', 'banana', 'cherry'], 'banana')
        ['banana']
    """
    op_list = []
    op_list_index = []

    for i, item in enumerate(s_list):
        matches = []
        if indices:
            for index in indices:
                target = item[index].lower() if isinstance(item, list) else item.lower()
                if (matcher.lower() in target if in_string else matcher.lower() == target):
                    matches.append(i)
        else:
            target = item[0].lower() if isinstance(item, list) else item.lower()
            if (matcher.lower() in target if in_string else matcher.lower() == target):
                matches.append(i)

        if matches:
            op_list.append(item)
            op_list_index.append(i)

    if return_index:
        return op_list_index
    return op_list[0] if first and op_list else op_list

def clean_list_strings(list_to_clean, list_dimension=1):
    """
    Cleans strings in a list by removing extra whitespace.

    Parameters:
        list_to_clean (list): A list or list of lists containing strings to clean.
        list_dimension (int, optional): Specifies the dimensionality of the list. 
                                         Use 1 for a flat list, 2 for a nested list. Defaults to 1.

    Returns:
        list: The cleaned list.

    Example:
        >>> clean_list_strings(["  hello  world  "])
        ['hello world']
    """
    if list_dimension == 1:
        return [" ".join(item.split()) for item in list_to_clean]
    elif list_dimension == 2:
        return [[" ".join(sub_item.split()) for sub_item in item] for item in list_to_clean]
    return list_to_clean

def return_unique_values(list_all_values):
    """
    Returns a list of unique values from the input list.

    Parameters:
        list_all_values (list): The input list containing values.

    Returns:
        list: A list of unique values.

    Example:
        >>> return_unique_values([1, 2, 2, 3, 3, 3])
        [1, 2, 3]
    """
    return list(set(list_all_values))

def convert_all_list_values(to_type, list_to_convert):
    """
    Converts all values in a list to the specified data type.

    Parameters:
        to_type (str): The target data type ("string", "int", "float").
        list_to_convert (list): The list of values to convert.

    Returns:
        list: The converted list.

    Example:
        >>> convert_all_list_values("float", ["1.23", "4.56"])
        [1.23, 4.56]
    """
    conversion_map = {
        "float": float,
        "int": int,
        "string": str,
    }
    if to_type not in conversion_map:
        raise ValueError(f"Unsupported type: {to_type}")
    return [conversion_map[to_type](i) for i in list_to_convert]

def initialize_list_of_list(list_len, initialize_value=None):
    """
    Initializes a list of lists with a specified length and optional default value.

    Parameters:
        list_len (int): The number of sublists.
        initialize_value (optional): The value to initialize each sublist with. Defaults to None.

    Returns:
        list: A list of initialized sublists.

    Example:
        >>> initialize_list_of_list(3, 0)
        [[0], [0], [0]]
    """
    return [[initialize_value] for _ in range(list_len)]

def get_most_frequently_occurring_list_item(list_data):
    """
    Finds the most frequently occurring item in a list.

    Parameters:
        list_data (list): The input list.

    Returns:
        Any: The item with the highest frequency in the list.

    Example:
        >>> get_most_frequently_occurring_list_item([1, 2, 2, 3, 3, 3])
        3
    """
    return max(set(list_data), key=list_data.count)

def check_if_list_has_duplicates(list_to_check):
    """
    Checks if a list contains duplicate values.

    Parameters:
        list_to_check (list): The input list to check for duplicates.

    Returns:
        bool: True if duplicates exist, False otherwise.

    Example:
        >>> check_if_list_has_duplicates([1, 2, 3, 4])
        False
        >>> check_if_list_has_duplicates([1, 2, 3, 1])
        True
    """
    return len(list_to_check) != len(set(list_to_check))

def create_list_of_colors(n):
    """
    Generates a list of random hex color codes.

    Parameters:
        n (int): The number of random colors to generate.

    Returns:
        list: A list of hex color codes.

    Example:
        >>> create_list_of_colors(3)
        ['#A1B2C3', '#F4E5D6', '#123ABC']
    """
    return [f'#{randint(0, 0xFFFFFF):06X}' for _ in range(n)]

def check_for_value_in_list_of_dicts_given_key(list_of_dicts, key, value):
    """
    Checks if a value exists for a specified key in a list of dictionaries.

    Parameters:
        list_of_dicts (list): The list of dictionaries to search.
        key (str): The key to check in each dictionary.
        value (Any): The value to search for.

    Returns:
        dict or None: The first dictionary where the key-value pair matches, or None if no match is found.

    Example:
        >>> check_for_value_in_list_of_dicts_given_key(
        ...     [{'name': 'Alice'}, {'name': 'Bob'}], 'name', 'Alice'
        ... )
        {'name': 'Alice'}
    """
    for dictionary in list_of_dicts:
        if dictionary.get(key) == value:
            return dictionary
    return None

def check_for_key_in_list_of_dicts_given_key(list_of_dicts, key):
    """
    Checks if a key exists in any dictionary within a list of dictionaries.

    Parameters:
        list_of_dicts (list): The list of dictionaries to search.
        key (str): The key to check.

    Returns:
        dict or None: The first dictionary where the key exists, or None if the key is not found.

    Example:
        >>> check_for_key_in_list_of_dicts_given_key(
        ...     [{'name': 'Alice'}, {'age': 25}], 'age'
        ... )
        {'age': 25}
    """
    for dictionary in list_of_dicts:
        if key in dictionary:
            return dictionary
    return None

def rank_list_of_numbers(numbers):
    """
    Ranks a list of numbers, assigning tied ranks for duplicate values.

    Parameters:
        numbers (list): The list of numbers to rank.

    Returns:
        list: A list of rank strings corresponding to the input numbers.

    Example:
        >>> rank_list_of_numbers([4, 2, 4, 5, 1])
        ['T-2', 'T-1', 'T-2', '4', '1']
    """
    sorted_numbers = sorted(set(numbers), reverse=True)
    ranks = {num: f'T-{rank+1}' if numbers.count(num) > 1 else str(rank+1)
             for rank, num in enumerate(sorted_numbers)}
    return [ranks[number] for number in numbers]

def split_list_into_chunks(original_list, chunk_size):
    """
    Splits a list into smaller chunks of a specified size.

    Parameters:
        original_list (list): The list to split.
        chunk_size (int): The maximum size of each chunk.

    Returns:
        list: A list of chunks (sublists).

    Example:
        >>> split_list_into_chunks([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """

    chunked_lists = [original_list[i:i + chunk_size] for i in range(0, len(original_list), chunk_size)]

    return chunked_lists

def remove_dict_duplicates_in_list(key, list_of_dicts):
    """
    Removes duplicate dictionaries from a list based on a specified key.

    Parameters:
        key (str): The key to check for uniqueness.
        list_of_dicts (list): The list of dictionaries to process.

    Returns:
        list: A list of unique dictionaries based on the specified key.

    Example:
        >>> remove_dict_duplicates_in_list(
        ...     'id', [{'id': 1, 'name': 'Alice'}, {'id': 1, 'name': 'Bob'}, {'id': 2, 'name': 'Carol'}]
        ... )
        [{'id': 1, 'name': 'Bob'}, {'id': 2, 'name': 'Carol'}]
    """

    # Create a dictionary with the unique key values and their corresponding dictionary
    unique_dict = {d[key]: d for d in list_of_dicts}

    # Return the list of values from the unique dictionary
    return list(unique_dict.values())
