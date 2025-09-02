from lukhed_basic_utils import osCommon as osC
from lukhed_basic_utils import fileCommon as fC
from lukhed_basic_utils import requestsCommon as rC
from lukhed_basic_utils import timeCommon as tC
from github import Github
from github.Repository import Repository
from github.GithubException import UnknownObjectException
import json
from typing import Optional
import zipfile
import shutil


class GithubHelper:
    def __init__(self, project='your_project_name', repo_name=None, set_config_directory=None, 
                 essential_print_only=False):
        """
        A helper class for interacting with GitHub repositories, handling authentication, 
        and various file operations within a repository.

        Upon instantiation, the class checks for an existing GitHub configuration file
        (`githubConfig.json`) in the lukhed config directory. If a valid configuration
        does not exist, it guides you through creating one, storing the credentials locally.
        Once configurted, the class can then authenticate with GitHub using a personal access token
        associated with a specific project.

        Parameters:
            project (str, optional): Name of the project to activate. Defaults to
                'your_project_name'. Project names are not case sensitive.
            repo_name (str, optional): Name of the repository to activate immediately
                after instantiation. Defaults to None.
            set_config_directory (str, optional): Full path to the directory that contains your GithubHelper config 
                file (token file). Default is None and this class will create a directory in your working directory 
                called 'lukhedConfig' to store the GithubHelper config file.
            essential_print_only (bool, optional): If True, will only print to console essential setup or error 
                messages, defaults to False and full verbosity.

        Attributes:
            _resource_dir (str): Path to the lukhed config directory.
            _github_config_file (str): Full path to the `githubConfig.json` file containing
                user tokens for various projects.
            _github_config (list): Loaded GitHub configuration data (list of dictionaries),
                each containing a "project" and "token" key.
            user (str | None): Authenticated GitHub username, set upon successful authentication.
            project (str | None): Currently active project name (lowercase).
            repo (github.Repository.Repository | None): GitHub repository object for the
                active repository, if any.
            _gh_object (github.Github | None): The authenticated GitHub instance used to
                make API calls.
    """
        
        self.essential_print_only=essential_print_only

        # Check setup upon instantiation
        if set_config_directory is None:
            osC.check_create_dir_structure(['lukhedConfig'])
            self._resource_dir = osC.create_file_path_string(['lukhedConfig'])
        else:
            self._resource_dir = set_config_directory
            if not osC.check_if_dir_exists(self._resource_dir):
                print(f"ERROR: The config directory '{set_config_directory}' does not exist. Exiting...")
                quit()

        self._github_config_file = osC.append_to_dir(self._resource_dir, 'githubConfig.json')
        self._github_config = []
        self.user = None
        self.project = project.lower()
        self.active_project = None
        self.repo = None                                        # type: Optional[Repository]
        self._gh_object = None                                  # type: Optional[Github]
        self._check_setup()

        if repo_name is not None:
            self._set_repo(repo_name)

    
    ###################
    # Setup/Config
    ###################
    def _check_setup(self):
        need_setup = True
        if osC.check_if_file_exists(self._github_config_file):
            # Check for an active github configuration
            self._github_config = fC.load_json_from_file(self._github_config_file)
            if not self._github_config:
                need_setup = True
            else:
                # check if project exists
                self._activate_project()
                need_setup = False
        else:
            # write default config to file
            fC.dump_json_to_file(self._github_config_file, self._github_config)
            need_setup = True

        if need_setup:
            self._prompt_for_setup()

    def _check_print(self, to_print):
        if not self.essential_print_only:
            print(to_print)

    def _activate_project(self):
        
        
        def _search_config_file():
            if self.project in projects:
                # Get the index of the item
                index = projects.index(self.project)
                token = self._github_config[index]['token']
                if self._authenticate(token):
                    self._check_print(f"INFO: {self.project} project was activated")
                    self.active_project = self.project
                    self.user = self._gh_object.get_user().login
                    return True
                else:
                    print("ERROR: Error while trying to authenticate.")
                    return False
            else:
                return False

        # First check projects in local config file
        try:
            projects = [x['project'].lower() for x in self._github_config]
        except Exception as e:
            input((f"ERROR: Error while trying to parse the config file. It may be corrupt."
                   "You can delete the config directory and go through setup again. Press enter to quit."))
            quit()

        
        if _search_config_file():
            # project already in local config file
            return True
        
        # Try updating local config file with github data
        try:
            token = self._github_config[0]['token']
            if self._authenticate(token):
                print(f"INFO: Checking projects associated with github account")
                self.user = self._gh_object.get_user().login
                self._activate_repo(self._gh_repo)
                files = self.get_files_in_repo_path("")
                files = [x.replace(".md", "").replace(".json", "").replace(".txt", "").lower() for x in files]
                if self.project in files:
                    print(f"INFO: Found project '{self.project}' in github account, adding to local config")
                    self._github_config.append({"project": self.project, "token": token})
                    self._update_github_config_file()
                    self.active_project = self.project
                    return True

        except Exception as e:
            try_setup = True

        if try_setup:
            i = input((f'INFO: There is no project "{self.project}" in the config file. Would you like to go thru setup '
                'to add a new Github key for this project name? (y/n): '))
            if i == 'y':
                self._gh_guided_setup()
            else:
                print("Ok, exiting...")
                quit()
    
    def _prompt_for_setup(self):
        i = input("1. You do not have a valid config file to utilize github. Do you want to go thru easy setup? (y/n):")
        if i == 'y':
            self._gh_guided_setup()
        elif i == 'n':
            print("OK, to use github functions, see https://github.com/lukhed/lukhed_basic_utils for more information.")
            quit()
        else:
            print("Did not get an expected result of 'y' or 'n'. Please reinstantiate and try again. Exiting script.")
            quit()

    def _gh_guided_setup(self):
        input(("\n2. Starting setup\n"
               "The github key you provide in this setup will be stored locally only. "
               f"After setup, you can see the config file in your specified destination {self._github_config_file}"
               "\nPress enter to continue"))
        
        token = input("\n3. Login to your Github account and go to https://github.com/settings/tokens. Generate a new "
                      "token and ensure to give it scopes that allow reading and writing to repos. "
                      "Copy the token, paste it below, then press enter:\n")
        token = token.replace(" ", "")
        if self.project == 'your_project_name':
            self.project = input(("\n4. Provide a project name (this is needed for using the class) and press enter. "
                                  "Note: projects are not case sensitive: "))
        account_to_add = {"project": self.project.lower(), "token": token}
        self._github_config.append(account_to_add)
        self._update_github_config_file()
        self._activate_project()

    def _update_github_config_file(self):
        fC.dump_json_to_file(self._github_config_file, self._github_config)

    def _authenticate(self, token):
        self._gh_object = Github(token)
        return True


    ###################
    # Repo Helpers
    ###################
    def _activate_repo(self, repo_name):
        self.repo = self._gh_object.get_repo(self.user + "/" + repo_name)
        self._check_print(f"INFO: {repo_name} repo was activated")
        
    def _parse_repo_dir_list_input(self, repo_dir_list):
        if repo_dir_list is None:
            repo_path = ""
        elif type(repo_dir_list) is str:
            repo_path = repo_dir_list
        else:
            repo_path = "/".join(repo_dir_list)

        return repo_path
    
    def _parse_content_for_upload(self, content):
        if type(content) is dict or type(content) is list:
            content = json.dumps(content)
        else:
            content = str(content)
            
        return content
    
    def _set_repo(self, repo_name):
        try:
            self._activate_repo(repo_name)
            return True
        except Exception as e:
            create_repo = input(f"Your Github account doesn't have repo: '{repo_name}'. Create it? (y/n) ")
            if create_repo == 'y':
                if self.create_repo(repo_name, private=True, create_readme=True):

                    self._activate_repo(repo_name)
            else:
                print(f"OK, no action taken to activate a repo")
                return None
            
    def _get_repo_contents(self, repo_path):
        contents = self.repo.get_contents(repo_path)
        return contents
    
    def create_repo(self, repo_name, description="Repo created by lukhed-basic-utils", private=True, 
                    create_readme=False, readme_content=None):
        """
        Creates a new repository on GitHub.

        Parameters:
            repo_name (str): The name of the repository to create.
            description (str, optional): A brief description of the repository for the commit message.
            private (bool, optional): Determines whether the repository should be private. 
                                      Defaults to True (private repository).
            create_readme (bool, optional): if True, Adds a README.md to the repo with description content.
            readme_content (str, optional): If creating a readme, can control the content to be different than 
                                            description.

        Returns:
            bool: True if the repository was created successfully, False otherwise.

        Example:
            >>> success = obj.create_repo("my-new-repo", description="A test repo", private=True)
        """
        try:
            repo = self._gh_object.get_user().create_repo(
                name=repo_name,
                description=description,
                private=private
            )
            print(f"Repository '{repo.name}' created successfully at {repo.html_url}")

            if create_readme:
                # Define the content for the README.md file
                if readme_content is None:
                    readme_content = "# " + repo_name + f"\n\n{description}"
                else:
                    readme_content = "# " + repo_name + f"\n\n{readme_content}"

                # Create the README.md file in the repository
                repo.create_file(
                    path="README.md",
                    message="Initial commit with README.md",
                    content=readme_content
                )
                print("README.md file created successfully.")

            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    
    def get_list_of_repo_names(self, print_names=False):
        """
        Returns a list of repo names available in the active project. Optionally prints the list to console.

        Parameters:
            print_names (bool, optional): If True, prints the list of available repos to the console. Defaults to False.
        
        Returns:
            list: A list of repo names associated with the active account.
        """
        repos = []
        for repo in self._gh_object.get_user().get_repos():
            repos.append(repo.name)
            if print_names:
                print(repo.name)
    
    def change_repo(self, repo_name):
        """
        Changes the active repository.

        Parameters:
            repo_name (str): Name of the repository to switch to.
        """ 
        self._set_repo(repo_name)
     
    def change_project(self, project, repo_name=None):
        """
        Changes the active project. Optionally switches the repository if repo_name is provided.

        Parameters:
            project (str): Name of the project to activate.
            repo_name (str, optional): Name of the repository to switch to. Defaults to None.
        """
        activated = self._activate_project(project)

        if activated and repo_name is not None:
            self._set_repo(repo_name)

    def get_files_in_repo_path(self, path_as_list_or_str=None):
        """
        Retrieves a list of file paths in the specified repository path.

        Parameters:
            path_as_list_or_str (list | str, optional): Path to a directory in the repository.
            Can be provided as a list of directory segments or a single string. Defaults to None.

        Returns:
            list: A list of file paths (str) found at the specified location in the repository.
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        contents = self._get_repo_contents(repo_path)

        return [x.path for x in contents]

    def retrieve_file_content(self, path_as_list_or_str, decode=True):
        """
        Retrieves the content of a file in the repository. Optionally decodes the content
        and returns either raw text/binary or JSON (if the file is .json).

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository, either
            as a list of directory segments or a single string.

            decode (bool, optional): If True, decodes the file content. If the file is JSON,
                returns a Python dictionary; otherwise returns the raw decoded data. If False,
                returns a ContentFile object. Defaults to True.

        Returns:
            dict | str | None: Decoded JSON object if .json file and decode=True, string content
            for other file types if decode=True, ContentFile object if decode=False, or None
            if the file is not found.

        Example:
            >>> # Retrieve and decode content of a JSON file
            >>> json_data = self.retrieve_file_content(["data", "example.json"], decode=True)
            >>> print(json_data)
            {"key": "value", "numbers": [1, 2, 3]}
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)

        try:
            contents = self._get_repo_contents(repo_path)
        except UnknownObjectException as e:
            # file not found exception
            return None

        if decode:
            if contents.encoding == "base64":
                decoded = contents.decoded_content
            elif contents.download_url:
                # For large files, use the download URL to fetch the file content
                response = rC.make_request(contents.download_url)
                response.raise_for_status()  # Ensure we notice bad responses
                decoded = response.content
            else:
                raise ValueError(f"Unexpected file encoding: {contents.encoding}")
        
            if '.json' in repo_path:
                return json.loads(decoded)
            else:
                return decoded

        else:
            return contents

    def create_file(self, content, path_as_list_or_str, message="no message"):
        """
        Creates a new file in the repository with the specified content.

        Parameters:
            content (str | dict): The content to upload. If dict, it will be converted to JSON.
            path_as_list_or_str (list | str): Path to the file in the repository,
            either as a list of directory segments or a single string.
            message (str, optional): Commit message for the new file. Defaults to "no message".

        Returns:
            dict: A status dictionary returned by the GitHub API after file creation.

        Example:
            >>> # Create a file with some text content
            >>> status = self.create_file("Hello, world!", ["docs", "hello.txt"], "Add hello.txt")
            >>> print(status["commit"].sha)
            6f0e918c...
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        content = self._parse_content_for_upload(content)
        status = self.repo.create_file(path=repo_path, message=message, content=content)
        return status

    def delete_file(self, path_as_list_or_str, message="Delete file"):
        """
        Deletes a file from the repository.

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository,
            either as a list of directory segments or a single string.
            message (str, optional): Commit message for the deletion. Defaults to "Delete file".

        Returns:
            dict | str: A status dictionary returned by the GitHub API after file deletion,
            or an error message if deletion fails.
        """
        repo_path = self._parse_repo_dir_list_input(path_as_list_or_str)
        try:
            # Get the file from the repository
            file = self.repo.get_contents(repo_path)

            # Delete the file
            status = self.repo.delete_file(path=repo_path, message=message, sha=file.sha)
            return status
        except Exception as e:
            return e

    def update_file(self, new_content, path_as_list_or_str, message="Updated content"):
        """
        Updates the content of an existing file in the repository.

        Parameters:
            new_content (str | dict | list): The new content to upload. If dict or list, it will be converted to json.
            path_as_list_or_str (list | str): Path to the existing file in the repository,
            either as a list of directory segments or a single string.
            message (str, optional): Commit message for the update. Defaults to "Updated content".

        Returns:
            dict: A status dictionary returned by the GitHub API after file update.

        Example:
            >>> # Update an existing text file
            >>> update_status = self.update_file("New content goes here",
            ...                                  ["docs", "hello.txt"],
            ...                                  "Update hello.txt")
            >>> print(update_status["commit"].sha)
            83b2fa1c...
        """
        new_content = self._parse_content_for_upload(new_content)
        existing_contents = self.retrieve_file_content(path_as_list_or_str, decode=False)

        status = self.repo.update_file(existing_contents.path, message=message, content=new_content, 
                                       sha=existing_contents.sha)
        return status

    def create_update_file(self, path_as_list_or_str, content, message="create_update_file update"):
        """
        Creates a new file or updates an existing file with the given content.

        Parameters:
            path_as_list_or_str (list | str): Path to the file in the repository, either as a list
            of directory segments or a single string.
            content (str | dict): The content to upload. If dict, it may be converted to JSON
            depending on file type.

        Returns:
            dict: A status dictionary returned by the GitHub API after file creation or update.

        Example:
            >>> # Create or update a file named "config.json"
            >>> status = self.create_update_file(["configs", "config.json"], {"env": "dev", "debug": True})
            >>> print(status["commit"].message)
            Updated content
        """
        if self.file_exists(path_as_list_or_str):
            status = self.update_file(content, path_as_list_or_str, message=message)
        else:
            status = self.create_file(content, path_as_list_or_str, message=message)

        return status

    def file_exists(self, repo_dir_list):
        """
        Checks if a file exists in the repository.

        Parameters:
            repo_dir_list (list | str): Path to the file in the repository,
                either as a list of directory segments or a single string.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        self._parse_repo_dir_list_input(repo_dir_list)
        res = self.retrieve_file_content(repo_dir_list, decode=False)
        if res is None:
            return False
        else:
            return True
        
    def download_repository(self, download_dir, extract=False, rename_internal_folder=True):
        """
        Downloads the repository archive as a ZIP file into the specified download directory.
        If 'extract' is True, the archive will be extracted into a subdirectory of download_dir.

        :param download_dir: The directory where the archive should be saved.
        :param extract: Boolean flag to extract the archive after download.
        :param rename_internal_folder: Bool to rename the internal folder to repo name
        :return: Dl path if download (and extraction, if requested) succeeded, otherwise None.
        """
        
        # Choose archive format and ref (default branch in this example)
        archive_format = "zipball"

        # Get the temporary archive URL for the repo
        dl_url = self.repo.get_archive_link(archive_format)
        
        # Construct a filename for the archive, e.g., "username_reponame_defaultbranch.zip"
        dl_ts = tC.create_timestamp('%Y%m%d')
        safe_repo_name = self.repo.full_name.replace("/", "_")
        archive_filename = f"{safe_repo_name}_{dl_ts}.zip"
        download_path = osC.append_to_dir(download_dir, archive_filename)
        
        # Make the HTTP request using your custom make_request() function
        response = rC.make_request(dl_url)
        
        if response.status_code == 200:
            # Write the binary content to the download file
            with open(download_path, "wb") as file:
                file.write(response.content)
            
            if extract:
                # Define an extraction directory (same name as archive file without the .zip extension)
                extraction_dir = osC.append_to_dir(download_dir, f"{safe_repo_name}_{dl_ts}")
                osC.check_create_dir_structure(extraction_dir, full_path=True)
                try:
                    with zipfile.ZipFile(download_path, "r") as zip_ref:
                        zip_ref.extractall(extraction_dir)
                except zipfile.BadZipFile:
                    print("Error: The downloaded file is not a valid zip archive.")
                    return None
                
                if rename_internal_folder:
                    new_name = osC.append_to_dir(extraction_dir, self.repo.name)
                    gh_dir = osC.return_immediate_child_dirs_given_dir(extraction_dir)[0]
                    shutil.move(gh_dir, new_name)

                return extraction_dir
            
            return download_path
        else:
            print(f"Failed to download repository. HTTP status code: {response.status_code}")
            return None
        
  
class KeyManager(GithubHelper):
    def __init__(self, key_name, config_file_preference='local', github_config_dir=None, provide_key_data=None, 
                 force_setup=False, skip_project_setup=False):
        """
        This class manages api key storage and retrieval from new api creation through continued use. 
        There are two options for storage set by the config_file_preference parameter:
        
        'local' - stores/retrieve your api key on your local hard drive (working directory)
        'github' - stores/retrieves your api key in a private repo (helpful to allow access across different hardware)

        To add a new key to be managed, just instantiate the class with the desired parameters and it will walk you 
        through the steps.

        Note: github option requires a github account (free) and a private access token (free). This class will 
        direct you on how to set that up if you are not familiar.

        Once your config file is setup for your key on local or in github, instantiate the class with the same 
        parameters and your key data will be stored in self.key_data or you can use the get_key_data() method.

        Parameters
        ----------
        key_name : str()
            A name for the api key that will be associated with your key in the config file. 
            To use the key in the future, you will use this key name to identify it. It Can be anything 
            but should be representative of the api you are using.
        config_file_preference : str, optional
            'local' to store your api key on your local hardware. 'github' to store 
            your api key in a private github repository. Defaults to 'local'., by default 'local'
        github_config_dir : str(), optional
            Full path to a local directory that contains your GithubHelper config file (token file). Default is 
            None and the GithubHelper class looks in your working directory for 'lukhedConfig' to get/store the 
            GithubHelper config file. If you utilize this option, you will have to provide the location each time 
            you want to use the key (helpful if you have multiple projects pointing to the same github access token).
        provide_key_data : dict() or file path, optional
            When adding a new key to be managed, use this option to provide the key data yourself 
            (instead of going through the guided setup where you paste the key). This is helpful for complex keys 
            that require more than one token or that have additional meta data with them. Two options:
            dict or the full path str to the file that contains the json.
        force_setup : bool, optional
            If True, will force the setup to occur and skip y/n prompts. Defaults to False.
        skip_project_setup : bool, optional
            If True, will skip the project specific setup, allowing you to set a key outside setup prompts (use force 
            update key).
        """

        self._config_dict = {}
        self._config_type = config_file_preference.lower()
        self._provided_key_data = provide_key_data
        self._force_setup = force_setup
        self._skip_project_setup = skip_project_setup

        # Key name and file based on parameters
        self.key_name = key_name
        self.key_file_name = f"{key_name}.json"

        # Set the github access token config location
        self._default_local_config = osC.create_file_path_string(['lukhedConfig'])
        self.github_config_dir = github_config_dir or self._default_local_config

        # Default local key storage if local option chosen
        self._local_key_storage = osC.create_file_path_string(['lukhedConfig', self.key_file_name])

        # Default repo if github option chose
        self._gh_repo = 'lukhedConfig'
        
        self.key_data = None
        if self._config_type == 'github':
            super().__init__(project=key_name, repo_name=self._gh_repo, essential_print_only=True)
            
            if not self._check_load_config_from_github():
                if not self._skip_project_setup:
                    self._guided_api_key_setup()

        else:
            if not self._check_load_config_from_local():
                if not self._skip_project_setup:
                    self._guided_api_key_setup()

        self.get_key_data()

    def _check_load_config_from_github(self):
        if self.file_exists(self.key_file_name):
            if self._provided_key_data:
                # rewrite the data stored on github
                self.create_update_file(self.key_file_name, self._provided_key_data, 
                                        'Updated key data based on provided key data input')
                self._config_dict = self._provided_key_data
            else:
                # get the key data from github
                self._config_dict = self.retrieve_file_content(self.key_file_name)
            return True
        else:
            return False
        
    def _check_load_config_from_local(self):
        config_path = osC.check_create_dir_structure(['lukhedConfig'], return_path=True)
        config_file = osC.append_to_dir(config_path, self.key_file_name)
        if osC.check_if_file_exists(config_file):
            self._config_dict = fC.load_json_from_file(config_file)
            return True
        else:
            return False
        
    def _guided_api_key_setup(self):
        if self._force_setup:
            pass
        else:
            confirm = input((f"You don't have a key stored for '{self.key_name}'. " 
                              "Do you want to go through setup? (y/n)"))
            if confirm != 'y':
                print("OK, Exiting...")
                quit()

        if self._config_type == 'github':
            if self._provided_key_data:
                pass
            else:
                input(("\n1. Starting setup\n"
                    f"The key for '{self.key_name}' you provide in this setup will be stored on your "
                    "private github repo: "
                    f"'{self._gh_repo}/{self.key_file_name}'"
                    "\nPress enter to continue"))
        elif self._config_type == 'local':
            if self._provided_key_data:
                pass
            else:
                input(("\n1. Starting setup\n"
                    f"The key for '{self.key_name}' you provide in this setup will be stored locally at: "
                    f"{self._local_key_storage} "
                    "\nPress enter to continue"))
        else:
            print(f"ERROR: '{self._config_type}' is not a valid config_file_preference")
            quit()
        
        if self._provided_key_data:
            if type(self._provided_key_data) == dict:
                token_dict = self._provided_key_data
            elif type(self._provided_key_data) == str:
                token_dict = fC.load_json_from_file(self._provided_key_data)
            else:
                print(f"ERROR: Your input for 'provide_key_data' is not valid. Must be a dict or file path string.")
                quit()
        else:
            token = input(f"\n2. Copy and paste your '{self.key_name}' key below.\n")
            token = token.replace(" ", "")
            token_dict = {"token": token}

        if self._config_type == 'github':
            r = self.create_update_file(self.key_file_name, token_dict, message=f'created config for {self.key_name}')
            if r['commit']:
                print(f"Config for {self.key_file_name} created successfully and the key is ready for use.")
                self._config_dict = token_dict
                return True
            else:
                print(f"ERROR: Something went wrong in creating your config file on Github. Try again and if the "
                      "problem persists you can check and file bugs at the below link or try the local key storage "
                      "method\n\n https://github.com/lukhed/lukhed_basic_utils")
                return False
        else:
            fC.dump_json_to_file(self._local_key_storage, token_dict)
            print(f"Config for {self.key_name} created successfully and the key is ready for use.")
            self._config_dict = token_dict
            return True
        
    def get_key_data(self):
        """
        Provides your store keyed data (also stored in class variable: key_data)

        Returns
        -------
        dict()
            {'token': 'your token'}
        """

        if self.key_data is None:
            if self._config_type == 'github':
                self.key_data = self.retrieve_file_content([self.key_file_name])
            elif self._config_type == 'local':
                try:
                    self.key_data = fC.load_json_from_file(self._local_key_storage)
                except Exception as e:
                    self.key_data = None
            else:
                print(f"ERROR: '{self._config_type}' is not a valid config_file_preference")
                quit()
            
        return self.key_data
    
    def force_update_key_data(self, new_key_data):
        """
        This function will replace your current key data (json file) with the 'new_key_data' parameter.

        Parameters
        ----------
        new_key_data : dict() or file path
            Two options:
            dict or the full path str to the file that contains the json.
        """

        if type(new_key_data) == dict:
            token_dict = new_key_data
        elif type(new_key_data) == str:
            token_dict = fC.load_json_from_file(new_key_data)
        else:
            print(f"ERROR: Your input for 'new_key_data' is not valid. Must be a dict or file path string.")
            quit()

        if self._config_type == 'github':
            r = self.create_update_file(self.key_file_name, token_dict, message="lukhed_basic_utils updated key data")
            if r['commit']:
                updated = True
        else:
            self.key_data = fC.dump_json_to_file(self._local_key_storage, token_dict)
            updated = True

        if updated:
            print("INFO: Key updated successfully")


def get_github_json(owner, repo, path, provide_full_url=None):
    """
    Fetches a JSON file from a GitHub repository.

    Parameters
    ----------
    owner : str
        The owner of the repository.
    repo : str
        The name of the repository.
    path : str
        The path to the JSON file in the repository.
    provide_full_url : str, optional
        If provided, will use this URL instead of constructing one from the owner, repo, and path. 
        Defaults to None.

    Returns
    -------
    dict
        The JSON data from the specified
    """
    if provide_full_url:
        url = provide_full_url
    else:
        # Construct raw content URL
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
    
    # Send GET request
    response = rC.request_json(url)
    
    return response

def get_github_image(owner, repo, path, provide_full_url=None, save_path=None):
    """
    Fetches an image file from a GitHub repository.

    Parameters
    ----------
    owner : str
        The owner of the repository.
    repo : str
        The name of the repository.
    path : str
        The path to the image file in the repository.
    provide_full_url : str, optional
        If provided, will use this URL instead of constructing one from the owner, repo, and path.
        Defaults to None.
    save_path : str, optional
        If provided, saves the image to the specified path.
        Defaults to None, which returns the binary content.

    Returns
    -------
    bytes or bool
        The binary image data if save_path is None, otherwise True if successful or False if failed.
    """
    if provide_full_url:
        url = provide_full_url
    else:
        # Construct raw content URL
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
    
    # Send GET request
    response = rC.make_request(url)
    
    if response.status_code == 200:
        if save_path:
            try:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            except Exception as e:
                print(f"Error saving image: {e}")
                return False
        else:
            return response.content
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")
        return False