# GitHub Package/Program Manager (ghpm)

ghpm is a tool designed to streamline the management of software packages from GitHub repositories. It's inspired by the functionality of traditional package managers like `apt`, tailored for the unique environment of GitHub. GHPM allows users to install, update, and remove software directly from GitHub repositories, handling various types of releases including `.deb`, `.rpm`, and others.

## Features

- **Install, Update, and Remove**: Easily manage software directly from GitHub.
- **Multi-Repository Support**: Handle multiple repositories through a JSON configuration.
- **Flexible and User-Friendly**: Designed with usability in mind, mimicking familiar package manager commands.

## Getting Started

To get started with GHPM, clone this repository to your local machine:

```bash
git clone https://github.com/froeb/ghpm.git
cd ghpm
```

## Prerequisites

    Python 3.x
    Access to GitHub repositories


## Configuration

GHPM uses a JSON configuration file (repos.json) to manage the repositories. Here's an example structure:

```json
[
  {
    "owner": "exampleOwner",
    "repo": "exampleRepo",
    "asset_pattern": "*.deb",
    "package_name": "example-package"
  }
  // Add more repositories as needed
]
```

Edit repos.json to include the repositories you want to manage.

## Usage

The basic commands for GHPM are:

    To install a package: python ghpm.py install
    To update a package: python ghpm.py update
    To remove a package: python ghpm.py remove

## Known limitations

Work in progress, beta status.

The script should now be able to handle the first program/repository that is defined in the repos.json
Tested with the repo for the Thorium browser (see definition in repos.json) only so far
Only works if repos.json is filled correctly, according to the documentation in repos.md
No code for handling more than one program/repository so far, no code for defining, changing or removing repos

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
