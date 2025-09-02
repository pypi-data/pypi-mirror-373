import sys
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from lukhed_basic_utils.osCommon import create_file_path_string, append_to_dir, create_root_path_starting_from_drive

def test_create_file_path_string():
    print("Test 1: Base path provided as a list:")
    path1 = create_file_path_string(
        list_of_dir=['subdir', 'file.txt'],
        base_path_list=['C:', 'Users', 'dad', 'Documents']
    )
    expected_path1 = Path('C:', 'Users', 'dad', 'Documents', 'subdir', 'file.txt')
    print(path1)
    assert Path(path1) == expected_path1, "Base path list test failed"

    print("\nTest 2: Default to current working directory:")
    path2 = create_file_path_string(list_of_dir=['subdir', 'file.txt'])
    expected_path2 = Path.cwd() / 'subdir' / 'file.txt'
    print(path2)
    assert Path(path2) == expected_path2, "Default working directory test failed"

    print("\nTest 3: Custom base path using ace_parent:")
    path3 = create_file_path_string(list_of_dir=['config'], ace_parent=1)
    # Adjust this test based on your project structure
    print(path3)
    assert 'config' in path3, "Relative ace_parent test failed"

    print("\nTest 4: Current working directory fallback:")
    path4 = create_file_path_string(list_of_dir=['mydir'])
    expected_path4 = Path.cwd() / 'mydir'
    print(path4)
    assert Path(path4) == expected_path4, "Current working directory fallback test failed"

def test_append_to_dir():
    print("Test 1: Single subdirectory append:")
    base_dir = "C:/Users/dad/Documents"
    to_append = "subdir"
    result = append_to_dir(base_dir, to_append)
    expected = os.path.join(base_dir, to_append)
    print(result)
    assert Path(result) == Path(expected), "Single subdirectory append test failed"

    print("\nTest 2: Multiple subdirectories append as list:")
    base_dir = "C:/Users/dad/Documents"
    to_append = ["subdir1", "subdir2", "file.txt"]
    result = append_to_dir(base_dir, to_append)
    expected = os.path.join(base_dir, "subdir1", "subdir2", "file.txt")
    print(result)
    assert Path(result) == Path(expected), "Multiple subdirectories append test failed"

    print("\nTest 3: Append with an empty base path:")
    base_dir = ""
    to_append = ["root", "subdir"]
    result = append_to_dir(base_dir, to_append)
    expected = os.path.join(base_dir, "root", "subdir")
    print(result)
    assert Path(result) == Path(expected), "Empty base path append test failed"

    print("\nTest 4: Append single directory to a relative base path:")
    base_dir = "mydir"
    to_append = "subdir"
    result = append_to_dir(base_dir, to_append)
    expected = os.path.join(base_dir, to_append)
    print(result)
    assert Path(result) == Path(expected), "Relative base path append test failed"

    print("\nTest 5: Append to root directory:")
    base_dir = "/"
    to_append = "etc"
    result = append_to_dir(base_dir, to_append)
    expected = os.path.join(base_dir, to_append)
    print(result)
    assert Path(result) == Path(expected), "Root directory append test failed"

def test_create_root_path_starting_from_drive():
    print(create_root_path_starting_from_drive('C:'))

if __name__ == '__main__':
    test_create_root_path_starting_from_drive()
