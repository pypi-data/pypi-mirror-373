# LocalSiteMap
![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
[![Code Size](https://img.shields.io/github/languages/code-size/infinitode/localsitemap)](https://github.com/infinitode/localsitemap)
![Downloads](https://pepy.tech/badge/localsitemap)
![License Compliance](https://img.shields.io/badge/license-compliance-brightgreen.svg)
![PyPI Version](https://img.shields.io/pypi/v/localsitemap)

LocalSiteMap is an open-source Python package designed for generating sitemaps from local files. It tracks `HTML` and `HTM` files, and generates complete sitemaps for the root website, including directories.

### Changes in version 1.0.1:
- Added `show_progress` boolean to print out mapping progress, pages mapped, and files found.

### Changes in version 1.0.0:
- Added initial package code, with automatic directory crawling to generate the `sitemap.xml` file.

> [!IMPORTANT]
> `LocalSiteMap` crawls any directory found in the root folder, be sure to add exclusions for important directories, or hidden/resource/file directories.

## Installation

You can install LocalSiteMap using pip:

```bash
pip install localsitemap
```

## Supported Python Versions

LocalSiteMap supports the following Python versions:

- Python 3.6
- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11/Later (Preferred)

Please ensure that you have one of these Python versions installed before using LocalSiteMap. LocalSiteMap may not work as expected on lower versions of Python than the supported.

## Features

- **Directory Crawling**: `LocalSiteMap` automatically crawls all subdirectories and files under the root directory, recursively adding them to your sitemap.
- **Automatic Last Modified Checks**: The package also automatically checks when the file has last been modified when adding it to the sitemap.
- - **Customizable**: You can customize the sitemap generation process by excluding specific directories or files.
- **Easy to Use**: With just a few lines of code, you can generate a complete sitemap for your local website.
- **Open Source**: LocalSiteMap is open source, allowing you to inspect, modify, and contribute to the code.

## Usage

### Generating a sitemap

```python
from localsitemap import generate_sitemap

# Root site directory
root_directory = r"path/to/your/website/directory"

# Domain of your website (where it is hosted)
base_url_of_your_website = "https://example.com"

# List of file paths or directories to exclude from the sitemap
excluded = ["auth", "forms", "template.html", "media", ".git", ".vscode", "node_modules"]  # Example exclusions

# Generate the sitemap
generate_sitemap(root_directory, base_url_of_your_website, "sitemap.xml", excluded, show_progress=True)
print("Sitemap generated in sitemap.xml")
```

## Contributing

Contributions are welcome! If you encounter any issues, have suggestions, or want to contribute to LocalSiteMap, please open an issue or submit a pull request on [GitHub](https://github.com/infinitode/localsitemap).

## License

LocalSiteMap is released under the terms of the **MIT License (Modified)**. Please see the [LICENSE](https://github.com/infinitode/localsitemap/blob/main/LICENSE) file for the full text.

**Modified License Clause**

The modified license clause grants users the permission to make derivative works based on the LocalSiteMap software. However, it requires any substantial changes to the software to be clearly distinguished from the original work and distributed under a different name.
