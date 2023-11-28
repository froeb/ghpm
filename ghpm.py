## attention, pre ALPHA code!

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
    It checks for the latest version of the program from its GitHub releases, downloads the .deb package, 
    and manages the installation or update using 'nala', a front-end for 'apt'. The script can also remove an 
    existing installation of the program.
    The programs and their github repositories are stored in the repos.json file.

Usage:
    To install programs: python ghpm.py install
    To update programs: python ghpm.py update
    To remove programs: python ghpm.py remove

Dependencies:
    This script uses 'nala' for package management, which is a front-end for 'apt'.
    Ensure 'nala' is installed on your system. To install 'nala', use:
    sudo apt install nala
    
Known limitations:
    Work in progress, beta status.
    The program should now be able to handle the first program/repository that is defined in the repos.json
    Tested with the repo for the Thorium browser only so far
    Only works if repos.json is filled correctly, according to the documentation in repos.md
"""

import requests
import os
import subprocess
import argparse
import tempfile
import json
import re

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
            match = re.search(version_regex, output)
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
           
    parser = argparse.ArgumentParser(description=f'Manage {program} installation.')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    # Add parsers for 'install', 'remove', and 'update' commands
    install_parser = subparsers.add_parser('install')
    remove_parser = subparsers.add_parser('remove')
    update_parser = subparsers.add_parser('update')

    args = parser.parse_args()


    if args.command in ['install', 'update']:
        installed_version = get_installed_version(program, version_command, version_regex)
 
        if args.command == 'update':
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

        if args.command == 'update':
            print(f"Updating {program} from version {installed_version} to {latest_version}...")

        print("Latest .deb release URL:", latest_deb_url)
        # Define a general temporary directory for downloads
        temp_dir = tempfile.gettempdir()
        downloaded_file = download_file(latest_deb_url, temp_dir)
        try:
           install_deb(downloaded_file)
           print(f"download {downloaded_file} and installed it from {temp_dir}")
        except Exception as e:
           print(f"downloading {downloaded_file} and/or installing it from {temp_dir} failed")

    elif args.command == 'remove':
        remove_package(program) 

if __name__ == "__main__":
    main()
