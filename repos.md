## Repository Configuration (`repos.json`)

The `repos.json` file is used to configure the GitHub repositories that GHPM will manage. It's a JSON formatted file where each entry represents a software package hosted on GitHub.

Each entry in `repos.json` should contain the following fields:

- `owner`: The username or organization name under which the repository is hosted on GitHub.
- `repo`: The repository name.
- `asset_pattern`: A pattern to identify the correct release assets to download. This usually matches the filename of the assets.
- `package_name`: The name of the software package. This is used for installation and removal of the package.

### Example

Here's an example of an entry for the Thorium browser:

```json
[
    {
        "owner": "Alex313031",
        "repo": "Thorium",
        "asset_pattern": "thorium-browser_*.deb",
        "package_name": "thorium-browser"
    }
]
