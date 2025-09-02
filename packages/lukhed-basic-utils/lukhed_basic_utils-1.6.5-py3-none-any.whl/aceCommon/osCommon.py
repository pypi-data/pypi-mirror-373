from pathlib import Path
import os
import platform
import shutil
import sys

def create_file_path_string(list_of_dir=None, base_path_list=None, **kwargs):
    """
    Constructs a file path string by combining a base directory with a list of subdirectories.

    Parameters:
        list_of_dir (list, optional): A list of subdirectory names to append to the base path.
                                      Defaults to an empty list, which returns the base directory as-is.
        base_path_list (list, optional): A list of directory names defining the base path.
                                         If None, the current working directory is used as the base path.
        **kwargs:
            parent (int, optional): Number of parent directories to go up from the current working directory.
            ace_parent (int, optional): Number of parent directories to go up from the location of this script.

    Returns:
        str: The constructed file path as a string.

    Example:
        >>> create_file_path_string(list_of_dir=["subdir", "file.txt"], parent=1)
        '<parent_directory>/subdir/file.txt'
    """
    # Default list of directories
    if list_of_dir is None:
        list_of_dir = ['']

    # Determine the base path
    if base_path_list:
        # Convert the list_for_base_path into an absolute path
        dir_name = Path(*base_path_list)
    elif 'parent' in kwargs:
        parent_level = kwargs['parent']
        dir_name = Path.cwd().parents[parent_level]
    elif 'ace_parent' in kwargs:
        # Get the aceCommon package location
        dir_name = Path(__file__).parents[kwargs['ace_parent']]
    else:
        # Default to current working directory
        dir_name = Path.cwd()

    # Construct the full path
    for item in list_of_dir:
        dir_name = dir_name / item

    return str(dir_name)

def append_to_dir(dir_path_to_add_to, to_append):
    """
    Appends a subdirectory or multiple subdirectories to a given directory path.

    Parameters:
        dir_path_to_add_to (str): The base directory path to which subdirectories will be added.
        to_append (str or list): A single subdirectory (str) or multiple subdirectories (list) to append.

    Returns:
        str: The resulting directory path with appended subdirectories.

    Example:
        >>> append_to_dir("C:/users/test", ["documents", "pictures"])
        'C:/users/test/documents/pictures'
    """
    if type(to_append) == list:
        for dir_name in to_append:
            dir_path_to_add_to = os.path.join(dir_path_to_add_to, dir_name)
        return dir_path_to_add_to
    else:
        return os.path.join(dir_path_to_add_to, to_append)
    
def return_immediate_child_dirs_given_dir(full_dir_path):
    """
    Returns a list of immediate child directories for a given directory path.

    Parameters:
        full_dir_path (str): The directory path to search for child directories.

    Returns:
        list: A list of paths to immediate child directories.

    Example:
        >>> return_immediate_child_dirs_given_dir("/home/user")
        ['/home/user/docs', '/home/user/pictures']
    """
    return [f.path for f in os.scandir(full_dir_path) if f.is_dir()]
    
def return_files_in_dir_as_strings(dir_path):
    """
    Returns a list of file paths in a given directory.

    Parameters:
        dir_path (str): The directory path to retrieve files from.

    Returns:
        list: A sorted list of file paths as strings. Additional sorting is applied only on Linux.

    Example:
        >>> return_files_in_dir_as_strings("/home/user/docs")
        ['/home/user/docs/file1.txt', '/home/user/docs/file2.txt']
    """
    file_list = list()

    for file in os.listdir(dir_path):
        file_list.append(os.fsdecode(file))

    file_list = [append_to_dir(dir_path, x) for x in file_list]

    if "linux" in platform.system().lower():
        file_list.sort()

    return file_list

def check_if_dir_exists(full_path):
    """
    Checks if a directory exists at the specified path.

    Parameters:
        full_path (str): The directory path to check.

    Returns:
        bool: True if the directory exists, False otherwise.

    Example:
        >>> check_if_dir_exists("/home/user/docs")
        True
    """
    if os.path.isdir(full_path):
        return True
    else:
        return False

def create_dir(full_path):
    """
    Creates a directory at the specified path.

    Parameters:
        full_path (str): The full path of the directory to create.

    Returns:
        None

    Raises:
        FileExistsError: If the directory already exists.
        PermissionError: If the directory cannot be created due to insufficient permissions.

    Example:
        >>> create_dir("/home/user/new_folder")
    """
    os.mkdir(full_path)

def check_create_dir_structure(dirPathList, full_path=False, **kwargs):
    """
    Checks if a directory structure exists. Creates missing directories if necessary.

    Parameters:
        dirPathList (list): A list of directory names defining the structure to check or create.
        full_path (bool, optional): If True, treats `dirPathList` as the full path. Defaults to False.
        **kwargs:
            return_path (bool, optional): If True, returns the path of the last directory checked or created.

    Returns:
        int or str: Number of directories created, or the path if `return_path` is True.

    Example:
        >>> check_create_dir_structure(["home", "user", "docs"])
        2  # Number of directories created
    """

    path_flag = 0
    if 'return_path' in kwargs:
        path_flag = 1

    if full_path:
        dirsCreated = 0
        tPath = dirPathList
        if not check_if_dir_exists(dirPathList):
            create_dir(dirPathList)
            dirsCreated = 1
    else:
        pathList = list()
        i = 0
        dirsCreated = 0
        while i < len(dirPathList):
            pathList.append(dirPathList[i])
            tPath = create_file_path_string(pathList)

            if os.path.isdir(tPath):
                pass
            else:
                os.mkdir(tPath)
                dirsCreated = dirsCreated + 1

            i = i + 1

    if path_flag == 1:
        return tPath
    else:
        return dirsCreated
    
def get_most_recently_modified_file_in_path_list(file_list):
    """
    Finds the most recently modified file in a given list of file paths.

    Parameters:
        file_list (list): A list of file paths to check.

    Returns:
        str: The file path of the most recently modified file.

    Raises:
        ValueError: If `file_list` is empty.

    Example:
        >>> get_most_recently_modified_file_in_path_list(["file1.txt", "file2.txt"])
        "file2.txt"
    """
    modified_list = list()
    for f in file_list:
        modified_list.append(os.path.getmtime(f))

    max_index = modified_list.index(max(modified_list))
    return file_list[max_index]

def check_if_file_exists(full_path):
    """
    Checks if a file exists at the specified path.

    Parameters:
        full_path (str): The file path to check.

    Returns:
        bool: True if the file exists, False otherwise.

    Example:
        >>> check_if_file_exists("/home/user/docs/file.txt")
        True
    """
    if os.path.isfile(full_path):
        return True
    else:
        return False

def delete_file(file_path):
    """
    Deletes a file at the specified path.

    Parameters:
        file_path (str): The path of the file to delete.

    Returns:
        bool: True if the file was deleted, False if the file does not exist.

    Example:
        >>> delete_file("/home/user/docs/file.txt")
        True
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def delete_directory_with_contents(filePath):
    """
    Deletes a directory and all its contents.

    Parameters:
        filePath (str): The path of the directory to delete.

    Returns:
        str: 'success' if the directory was deleted, 
             'failed: file DNE' if the directory does not exist.

    Example:
        >>> delete_directory_with_contents("/home/user/temp_dir")
        'success'
    """
    if os.path.exists(filePath):
        shutil.rmtree(filePath)
        return 'success'
    return 'failed: file DNE'

def copy_directory_with_contents(source_full_path, destination_full_path):
    """
    Copies an entire directory, including all its contents, to a new location.

    Parameters:
        source_full_path (str): The path of the directory to copy.
        destination_full_path (str): The destination path for the copied directory.

    Returns:
        str: The path to the copied directory.

    Example:
        >>> copy_directory_with_contents("/home/user/source_dir", "/home/user/destination_dir")
        '/home/user/destination_dir'
    """
    return shutil.copytree(source_full_path, destination_full_path)

def block_print():
    """
    Redirects `sys.stdout` to suppress console output.

    Returns:
        None

    Example:
        >>> block_print()
        # Console output will be suppressed
    """
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    """
    Restores `sys.stdout` to enable console output.

    Returns:
        None

    Example:
        >>> enable_print()
        # Console output will be restored
    """
    sys.stdout = sys.__stdout__

def copy_file(source_file, dest_file):
    """
    Copies a file from the source path to the destination path.

    Parameters:
        source_file (str): The path of the source file.
        dest_file (str): The path where the file should be copied.

    Returns:
        str: 'success' if the file was copied successfully, 
             'failed' if an error occurred.

    Example:
        >>> copy_file("/home/user/source.txt", "/home/user/destination.txt")
        'success'
    """
    try:
        shutil.copyfile(source_file, dest_file)
        return 'success'
    except:
        return 'failed'

def create_root_path_starting_from_drive(root_drive_str):
    """
    Creates a root directory path starting from the specified drive.

    Parameters:
        root_drive_str (str): The drive letter (e.g., "C:").

    Returns:
        str: The root directory path (e.g., "C:/").

    Example:
        >>> create_root_path_starting_from_drive("C:")
        'C:/'
    """
    root_drive = os.path.join(root_drive_str, os.sep)
    return root_drive

def extract_file_name_given_full_path(full_path):
    """
    Extracts the file name from a full file path.

    Parameters:
        full_path (str): The full path of the file.

    Returns:
        str: The file name.

    Example:
        >>> extract_file_name_given_full_path("/home/user/docs/file.txt")
        'file.txt'
    """
    return os.path.basename(full_path)

def get_last_folder_from_path(full_path):
    """
    Extracts the name of the last folder in a given path.

    Parameters:
        full_path (str): The full directory path.

    Returns:
        str: The name of the last folder in the path.

    Example:
        >>> get_last_folder_from_path("/home/user/docs")
        'docs'
    """
    without_extra_slash = os.path.normpath(full_path)
    last_part = os.path.basename(without_extra_slash)
    return last_part

def get_parent_dir_given_full_dir(full_dir_path):
    """
    Returns the parent directory of a given directory path.

    Parameters:
        full_dir_path (str): The full directory path.

    Returns:
        str: The path to the parent directory.

    Example:
        >>> get_parent_dir_given_full_dir("/home/user/docs")
        '/home/user'
    """
    return os.path.dirname(full_dir_path)

def get_working_dir():
    """
    Returns the current working directory.

    Returns:
        str: The current working directory path.

    Example:
        >>> get_working_dir()
        '/home/user'
    """
    return os.getcwd()

def is_platform_windows():
    """
    Checks if the current platform is Windows.

    Returns:
        bool: True if the platform is Windows, False otherwise.

    Example:
        >>> is_platform_windows()
        True  # On a Windows system
    """

    if os.name == "nt":
        return True
    else:
        return False
