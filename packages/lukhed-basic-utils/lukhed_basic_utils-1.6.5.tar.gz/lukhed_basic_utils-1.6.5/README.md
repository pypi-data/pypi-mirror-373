# lukhed_basic_utils

A collection of basic utility functions for Python projects.

## Installation and Usage

```bash
pip install lukhed-basic-utils
```

## osCommon

A set utility functions for interacting with the operating system's file and directory structures.  

### Example Usage

```python
from lukhed_basic_utils import osCommon as osC
```


#### Creating Operating System Agnostic FIle Path Strings
```python
example_path = osC.create_file_path_string(list_of_dir=['subdir', 'file.txt'])
print(example_path)
```

```python
#output
/home/user/current_working_dir/subdir/file.txt
```

#### Retrieving File Names in Directory

```python
return_files_in_dir_as_strings("/home/user/docs", return_file_names_only=True)
```

```python
# output
['file1.txt', 'file2.txt']
```

## fileCommon

A set utility functions for working with local files.  

```python
from lukhed_basic_utils import fileCommon as fC
```

## githubCommon

A class for working with the Github API, geared toward utilizing github repo's as storage or shared config.

```python
from lukhed_basic_utils.githubCommon import GithubHelper
```

### Retrieve JSON Content Stored In a Github Repo
```python
gC = GithubHelper(project='lukhed', repo_name='exampleRepo')
example_dict = gC.retrieve_file_content('someConfig.json')
```

## Other Utility Files
### classCommon
### listWorkCommon
### mathCommon
### stringCommon
### timeCommon

For more documentation, check pypi page:
https://pypi.org/project/lukhed-basic-utils/