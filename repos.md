## Repository Configuration (`repos.json`)

The `repos.json` file is used to configure the GitHub repositories that GHPM will manage. It's a JSON formatted file where each entry represents a software package hosted on GitHub.

Each entry in `repos.json` should contain the following fields:

- `owner`: The username or organization name under which the repository is hosted on GitHub.
- `repo`: The repository name.
- `release_asset_filter`: A pattern to identify the correct release assets to download. This usually matches the filename of the assets.
- `package_name`: The name of the software package. This is used for installation and removal of the package.
- 'version_command': an optional command line to give back the version number, 
  could e.g. be something like 'echo VERSION'. Defaults to f'{package_name} --version'
- 'version_result_regular_expression': an optional regular expression to extract the version number from the result of version_command .
  Defaults to the second word from the output of version_command (assuming that the first word is the program name)
- 'package_type': the package type for this resource. usually deb for debian systems, but could also be something different, see package_commands.json

### Example

Here's an example of an entry for the Thorium browser:

```json
[
    {
        "owner": "Alex313031",
        "repo": "Thorium",
        "package_name": "thorium-browser",
        "version_command": "thorium-browser --version",
        "version_result_regular_expression": "\\b(\\d+\\.\\d+\\.\\d+\\.\\d+)\\b",
        "package_type": "deb",
        "release_asset_filter": "*.deb"
    },
]


This entry will direct GHPM to manage the Thorium browser package from the Alex313031/Thorium repository, specifically targeting .deb files for installation and updates.
