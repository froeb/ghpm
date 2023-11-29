# GHPM (GitHub Package/Program Manager)

GHPM is a script that automates the installation, update, or removal of applications hosted on GitHub repositories for Debian-based Linux distributions. It checks for the latest version of the program from its GitHub releases, downloads the package, and manages the installation or update using Debian's package management tools. The script also provides functionality for removing an existing installation of the program.

## Features

- Supports installation, update, and removal of software packages from specified GitHub repositories.
- Automatically fetches the latest release assets based on provided filters.
- Handles Debian (`*.deb`) packages with dependency resolution.
- Utilizes `apt-get` for installations to manage dependencies effectively.
- Configurable through `repos.json` for specifying repositories and `package_commands.json` for package management commands.

## Configuration

### Repositories Configuration (`repos.json`)

Define the repositories and packages to manage in `repos.json`. Each entry should specify the following:

- `owner`: GitHub username or organization name.
- `repo`: Repository name.
- `package_name`: Name of the package.
- `version_command`: Command to check the installed version of the package.
- `version_result_regular_expression`: Regex to extract the version number from the command output.
- `package_type`: Type of package (e.g., `deb` for Debian packages).
- `release_asset_filter`: Filter to identify the correct asset from the GitHub release.

#### Example entry:

```json
{
    "owner": "example",
    "repo": "example-repo",
    "package_name": "example-package",
    "version_command": "example-package --version",
    "version_result_regular_expression": "(\\d+\\.\\d+\\.\\d+)",
    "package_type": "deb",
    "release_asset_filter": "example-package_*.deb"
}
```

### Package Commands Configuration (package_commands.json)

Define the package management commands for different package types in package_commands.json. Specify the installation, update, and removal commands.

#### Example:

```json

{
    "deb": {
        "install_command": "sudo apt-get install -f {package}",
        "update_command": "sudo apt-get update && sudo apt-get install -f {package}",
        "remove_command": "sudo apt-get remove {package}"
    }
}
```

## Usage

```bash
Run ghpm.py with the following options:

    -i, --install: Install packages defined in repos.json.
    -u, --update: Update packages defined in repos.json.
    -r, --remove: Remove packages defined in repos.json.
    -v, --version: Show the script version and exit.
```

### Example:

```bash

python ghpm.py -i  # Install packages
```

## Dependencies

    Python 3
    requests library
    Access to apt-get for Debian-based distributions.

## Limitations

    Currently supports only Debian package types (*.deb).
    Requires properly formatted repos.json and package_commands.json for operation.
    Requires a lot of testing and possible bugfixing

## License

GHPM is released under the GNU General Public License v3.0.

  
## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

## Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request


## License

Distributed under the GPL-3.0 License. See LICENSE for more information.

## Contact

Kai Froeb - github@froeb.net
Home page: https://kai.froeb.net
Project Link: https://github.com/froeb/ghpm

## Final Note

This README is subject to change as GHPM continues to evolve and improve.
