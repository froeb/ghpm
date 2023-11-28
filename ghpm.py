## attention, pre ALPHA code!

import json
import requests
import os
import subprocess

def load_config():
    with open('repos.json', 'r') as file:
        return json.load(file)

def get_latest_release(repo_config):
    api_url = f"https://api.github.com/repos/{repo_config['owner']}/{repo_config['repo']}/releases/latest"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Failed to fetch release data for {repo_config['repo']}")
        return None
    return response.json()

def download_asset(asset_url, destination_folder):
    local_filename = asset_url.split('/')[-1]
    path = os.path.join(destination_folder, local_filename)
    with requests.get(asset_url, stream=True) as r:
        r.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path

def install_deb(file_path):
    subprocess.run(["sudo", "dpkg", "-i", file_path], check=True)

def main():
    repo_config = load_config()[0]  # Assuming only one repository for now

    release_data = get_latest_release(repo_config)
    if not release_data:
        return

    asset_pattern = repo_config['asset_pattern']
    for asset in release_data['assets']:
        if asset['name'].endswith('.deb') and asset_pattern in asset['name']:
            print(f"Downloading and installing {asset['name']}")
            asset_url = asset['browser_download_url']
            destination_folder = "/tmp"  # Generalized download folder
            downloaded_file = download_asset(asset_url, destination_folder)
            install_deb(downloaded_file)
            break

if __name__ == "__main__":
    main()
