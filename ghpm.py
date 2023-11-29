"""
ghpm.py
Copyright (C) 2023 by Kai Froeb

This script is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Description:
    This script automates the installation, update, or removal of the applications in the github repository
    on Debian-based Linux distributions, as long as it can be downloaded from there as a deb file. 
    It checks for the latest version of the program from its GitHub releases, downloads the package, 
    and manages the installation or update. The script can also remove an existing installation of the program.
    The programs and their github repositories are stored in the repos.json file.
    Commands how to install, update and remove packaes, depending on the package type are stored in package_commands.json
"""

import subprocess
import json
import sys
import os 
import distro
import requests 
from argparse import ArgumentParser
from tempfile import gettempdir 
from re import search

def get_default_package_type():
    """
    Determine the default package type for the current Linux distribution

    Returns:
        the package type in lowercase, as eg. deb for debian/ubuntu packages
        None when we are on an unsupported distribution
    """
    dist_name = distro.id()
    dist_name = dist_name.lower()
    print(f'your Linux distribution is {dist_name}')
    if 'ubuntu' in dist_name or 'debian' in dist_name or 'linuxmint' in dist_name:
        return 'deb'
    elif 'fedora' in dist_name or 'centos' in dist_name or 'redhat' in dist_name:
        return 'rpm'
    # Add more distributions and package types as needed
    return None

    
def load_package_commands():
    try:
        with open('package_commands.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("package_commands.json was not found in the current directory")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error in package_commands.json: {e}")
        sys.exit(1)

def execute_package_command(command_template, file_or_package_name):
    """
    Executes a package management command.
    Args:
        command_template (str): The command template from package_commands.json.
        file_or_package_name (str): The file path or package name to be used in the command.
    """
    command = command_template.replace("{package}", file_or_package_name)
    try:
        subprocess.run(command.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute package command: {e}")
        

def load_config():
    """
    Loads the configuration data from the repos.json file.

    Returns:
        list: A list of repository configurations as dictionaries.
        
    Raises:
        FileNotFoundError: If repos.json is not found in the current directory.
        json.JSONDecodeError: If repos.json contains invalid JSON.
    """
    with open('repos.json', 'r') as file:
        return json.load(file)

def extract_version_from_filename(filename, version_regex):
    match = search(version_regex, filename)
    if match:
        return match.group(1)
    else:
        print(f"No version found in filename '{filename}' using regex '{version_regex}'")
        return None
        
def get_installed_version(program, version_command, version_regex=None):
    """
    Retrieves the installed version of a program by executing the given version command.

    Args:
        program (str): The name of the program to check the version for.
        version_command (str): The command to execute for getting the version.
        version_regex (str, optional): A regular expression pattern to extract the version from the command output. Defaults to None.

    Returns:
        str: The extracted version number.
        None: If the version could not be determined due to the program not being installed, not found in PATH, or version regex mismatch.

    Raises:
        subprocess.CalledProcessError: If there is an error executing the version command.
    """
    try:
        result = subprocess.run(version_command.split(), capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        # Use regex if provided
        if version_regex:
            match = search(version_regex, output) 
            if match:
                return match.group(1)
            else:
                raise ValueError(f"Version regex '{version_regex}' in repos.json did not match any part of the output of '{version_command}'.")
        else:
            # Fallback simple split logic (modify as needed)
            return output.split()[1]
    except subprocess.CalledProcessError as e:
        print(f"Error while checking version for {program}: {e}")
    except FileNotFoundError:
        print(f"{program} is not installed or not found in PATH.")
    except ValueError as ve:
        print(ve)
    return None
         
def download_file(url, destination_folder):
    """
    Downloads a file from a given URL to a specified destination.
    Args:
        url (str): URL of the file to download.
        destination_folder (str): Folder where the file will be saved.
    Returns:
        str: Path to the downloaded file.
    """
    local_filename = url.split('/')[-1]
    path = os.path.join(destination_folder, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path

def get_latest_release_asset(owner, repo, release_asset_filter):
    """
    Fetches the latest release asset from a GitHub repository based on a specified filter.
    Args:
        owner (str): GitHub username or organization name.
        repo (str): GitHub repository name.
        release_asset_filter (str): A pattern to match the desired release asset.
    Returns:
        str: URL of the latest release asset matching the filter, or None if not found.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Failed to fetch release data from GitHub API for {owner}/{repo}")
        return None
    release_data = response.json()

    # Adjust to handle wildcard and case sensitivity
    filter_extension = release_asset_filter.lstrip('*').lower()
    print(f"Filter extension: {filter_extension}")
    print(f"Assets found in the latest release for {owner}/{repo}:")

    for asset in release_data.get('assets', []):
        print(f" - {asset['name']}")
        if asset['name'].lower().endswith(filter_extension):
            return asset['browser_download_url']
    
    print(f"No matching assets found in the latest release for {owner}/{repo}")
    return None

def main():
    """
    Manages the installation, removal, and updating of Thorium browser.
    Supported commands: install, remove, update.
    """
           
    # Define the current version of the script
    SCRIPT_VERSION = "0.2.0-beta"

    # Setup argparse
    parser = ArgumentParser(description='GHPM: GitHub based Package/Program Manager')
    parser.add_argument('-v', '--version', action='version', version=f'GHPM {SCRIPT_VERSION}',
                        help="show the version number and exit")
    parser.add_argument('-i', '--install', action='store_true', help="install package(s) defined in repos.json")
    parser.add_argument('-u', '--update', action='store_true', help="update package(s) defined in repos.json")
    parser.add_argument('-r', '--remove', action='store_true', help="remove package(s) defined in repos.json")
    
    # If no arguments were provided, print the help message and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    # Determine default package type based on the system's distribution
    default_package_type = get_default_package_type()
    # read in how to install/update/remove packages for the various supported package manager
    package_commands = load_package_commands()

    # Load configuration
    try:
        repo_configs = load_config()  # Load list of repositories
    except FileNotFoundError:
        print("repos.json was not found in the current directory")
        return
    except Exception as e:
        print(f"Error in repos.json: {e}")
        return
        
    for repo_config in repo_configs:
        try:
            # Extracting individual parameters for each repository
            owner = repo_config['owner'].strip()
            if not owner:
                raise ValueError(f"Owner parameter is empty in repos.json for repository '{repo_config['repo']}'")
            repo = repo_config['repo'].strip()
            if not repo:
                raise ValueError(f"Repo parameter is empty in repos.json for repository '{repo}'")
            program = repo_config['package_name'].strip()
            if not program:
                raise ValueError(f"Package_name parameter is empty in repos.json for repository '{repo}'")
            version_command = repo_config.get('version_command', f"{program} --version")
            version_regex = repo_config.get('version_result_regular_expression')
            package_type = repo_config.get('package_type', default_package_type)
            if package_type is None:
                print("Unable to determine the package type for the systems distribution.")
                continue
            if package_type not in package_commands:
                print(f"Unsupported package type '{package_type}' for repository '{repo}'")
                continue            
            release_asset_filter = repo_config.get('release_asset_filter', f"*.{package_type}")
            
        except Exception as e:
            print(f"Error in processing repository '{repo}': {e}")
            continue  # Skip to the next repository configuration

        if args.install or args.update:
            installed_version = get_installed_version(program, version_command, version_regex)
 
            if args.update:
               if installed_version is None:
                   print(f"Could not determine the installed version of {program}.")
                   continue
            
            latest_asset_url = get_latest_release_asset(owner, repo, release_asset_filter)
            if not latest_asset_url:
               print(f"No {version_regex} release found")
               continue

            latest_version = extract_version_from_filename(latest_asset_url.split('/')[-1], version_regex)
            if installed_version == latest_version:
               print(f"Latest version {latest_version} is already installed.")
               continue

            if args.update:
               print(f"Updating {program} from version {installed_version} to {latest_version}...")

            print(f"Latest  {version_regex} release URL:", latest_asset_url)
            # Define a general temporary directory for downloads
            temp_dir = gettempdir()
            try:
                install_command = package_commands[package_type]['install_command']
            except Exception as e:
                print(f"install_command for package type {package_type} not found")
                continue
            # Initialize downloaded_file before try block
            downloaded_file = None  # Initialize downloaded_file
            try:
                downloaded_file = download_file(latest_asset_url, temp_dir)
                if downloaded_file:  # Check if downloaded_file is defined
                    execute_package_command(install_command, downloaded_file)
                    print(f"Downloaded {downloaded_file} and installed it from {temp_dir}")
            except Exception as e:
                print(f"Failed to install {program} via {install_command}: {e}")
                continue

        elif args.remove:
           try:
               remove_command = package_commands[package_type]['remove_command']
               execute_package_command(remove_command, program)
           except Exception as e:
               print(f"failed to remove {program} via the {remove_command}")
               continue

if __name__ == "__main__":
    main()
Attention:
    Work in progress, this is pre alpha stuff!
"""

import subprocess
import json
import sys
import os 
import requests 
from argparse import ArgumentParser
from tempfile import gettempdir 
from re import search

def load_config():
    """
    Loads the configuration data from the repos.json file.

    Returns:
        list: A list of repository configurations as dictionaries.
        
    Raises:
        FileNotFoundError: If repos.json is not found in the current directory.
        json.JSONDecodeError: If repos.json contains invalid JSON.
    """
    with open('repos.json', 'r') as file:
        return json.load(file)

def get_installed_version(program, version_command, version_regex=None):
    """
    Retrieves the installed version of a program by executing the given version command.

    Args:
        program (str): The name of the program to check the version for.
        version_command (str): The command to execute for getting the version.
        version_regex (str, optional): A regular expression pattern to extract the version from the command output. Defaults to None.

    Returns:
        str: The extracted version number.
        None: If the version could not be determined due to the program not being installed, not found in PATH, or version regex mismatch.

    Raises:
        subprocess.CalledProcessError: If there is an error executing the version command.
    """
    try:
        result = subprocess.run(version_command.split(), capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        # Use regex if provided
        if version_regex:
            match = search(version_regex, output) 
            if match:
                return match.group(1)
            else:
                raise ValueError(f"Version regex '{version_regex}' in repos.json did not match any part of the output of '{version_command}'.")
        else:
            # Fallback simple split logic (modify as needed)
            return output.split()[1]
    except subprocess.CalledProcessError as e:
        print(f"Error while checking version for {program}: {e}")
    except FileNotFoundError:
        print(f"{program} is not installed or not found in PATH.")
    except ValueError as ve:
        print(ve)
    return None
         
def install_deb(file_path):
    """
    Installs a .deb file using Nala, with a fallback to dpkg.
    Args:
        file_path (str): Path to the .deb file.
    """
    try:
        subprocess.run(["sudo", "nala", "install", file_path], check=True)
    except subprocess.CalledProcessError:
        print("Nala failed to install the package. Attempting with dpkg...")
        subprocess.run(["sudo", "dpkg", "-i", file_path], check=True)
        subprocess.run(["sudo", "nala", "install", "-f"], check=True)
        
def remove_package(package_name):
    """
    Removes a package using Nala, with a fallback to dpkg.
    Args:
        package_name (str): Name of the package to remove.
    """
    try:
        subprocess.run(["sudo", "nala", "remove", package_name], check=True)
    except subprocess.CalledProcessError:
        print("Nala failed to remove the package. Attempting with dpkg...")
        subprocess.run(["sudo", "dpkg", "-r", package_name], check=True)

def download_file(url, destination_folder):
    """
    Downloads a file from a given URL to a specified destination.
    Args:
        url (str): URL of the file to download.
        destination_folder (str): Folder where the file will be saved.
    Returns:
        str: Path to the downloaded file.
    """
    local_filename = url.split('/')[-1]
    path = os.path.join(destination_folder, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path

def get_latest_deb_release(owner, repo):
    """
    Fetches the latest .deb release from a GitHub repository.
    Args:
        owner (str): GitHub username or organization name.
        repo (str): GitHub repository name.
    Returns:
        str: URL of the latest .deb release, or None if not found.
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(api_url)
    if response.status_code != 200:
        print("Failed to fetch release data from GitHub API")
        return None
    release_data = response.json()
    for asset in release_data.get('assets', []):
        if asset['name'].endswith('.deb'):
            return asset['browser_download_url']
    return None

def main():
    """
    Manages the installation, removal, and updating of Thorium browser.
    Supported commands: install, remove, update.
    """

    try:
        repo_config = load_config()[0]  # Assuming only one repository for now
        # Extracting individual parameters
        owner = repo_config['owner']
        repo = repo_config['repo']
        program = repo_config['package_name']
        version_command = repo_config.get('version_command')
        version_regex = repo_config.get('version_result_regular_expression')
        asset_pattern = repo_config['asset_pattern']
    except FileNotFoundError:
        print("repos.json was not found in the current directory")
        return
    except Exception as e:
        print(f"Error in repos.json: {e}")
        return
           
    # Define the current version of the script
    SCRIPT_VERSION = "0.1.0-beta"

    # Setup argparse
    parser = ArgumentParser(description='GHPM: GitHub based Package/Program Manager')
    parser.add_argument('-v', '--version', action='version', version=f'GHPM {SCRIPT_VERSION}',
                        help="show the version number and exit")
    parser.add_argument('-i', '--install', action='store_true', help="install package(s) defined in repos.json")
    parser.add_argument('-u', '--update', action='store_true', help="update package(s) defined in repos.json")
    parser.add_argument('-r', '--remove', action='store_true', help="remove package(s) defined in repos.json")
    
    # If no arguments were provided, print the help message and exit
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.install or args.update:
        installed_version = get_installed_version(program, version_command, version_regex)
 
        if args.update:
            if installed_version is None:
                print(f"Could not determine the installed version of {program}.")
                return
            
        latest_deb_url = get_latest_deb_release(owner, repo)
        if not latest_deb_url:
            print("No .deb release found")
            return

        latest_version = latest_deb_url.split('/')[-1].split('_')[1]
        if installed_version == latest_version:
            print(f"Latest version {latest_version} is already installed.")
            return

        if args.update:
            print(f"Updating {program} from version {installed_version} to {latest_version}...")

        print("Latest .deb release URL:", latest_deb_url)
        # Define a general temporary directory for downloads
        temp_dir = gettempdir()
        downloaded_file = download_file(latest_deb_url, temp_dir)
        try:
           install_deb(downloaded_file)
           print(f"download {downloaded_file} and installed it from {temp_dir}")
        except Exception as e:
           print(f"downloading {downloaded_file} and/or installing it from {temp_dir} failed")

    elif args.remove:
        remove_package(program) 

if __name__ == "__main__":
    main()
