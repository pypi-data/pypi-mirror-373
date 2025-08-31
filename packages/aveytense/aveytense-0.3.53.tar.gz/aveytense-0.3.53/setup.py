# py -m build
# twine upload dist/* --config-file ./config.pypirc

from setuptools import setup
import aveytense, os

try:
    with open(os.path.dirname(aveytense.__file__) + "\\readme.md", "r") as f:
        long_description = f.read()
        
except FileNotFoundError:
    long_description = \
"""
# AveyTense

**AveyTense** is a library written by Aveyzan using Python, which provides especially extensions to inbuilt Python solutions.

## Features

Features are included in [this page](https://aveyzan.xyz/aveytense).
For code changes see [this Google document](https://docs.google.com/document/d/1GC_KAOXML65jNfBZA8GhVViqPnrMoFtbLv_jHvUhBlg/edit?usp=sharing).

## Getting started

To install AveyTense, run the following command:

```
pip install aveytense
```

Ensure you have [`typing_extensions`](https://pypi.org/project/typing_extensions) PyPi project with version 4.10.0 or above, and Python 3.8 or above.

If you think you are out of date, consider checking out [releases section](https://pypi.org/project/aveytense/#history) and running following command:

```py
pip install --upgrade aveytense
```

After installation process, you can import module `aveytense`, which imports AveyTense components into your project.

> **Note**: It is highly recommended to install latest final version of AveyTense. Do not rely on alpha, beta releases, and
> release candidates before their final counterparts are published.

> **Warning**: Some definitions will be still prone for errors due to the backward-compatibility. For code changes to completely
> support Python versions before Python 3.12 there will be still need to inspect every definition included in the project.

## Support

You can support my project via donation on my [Ko-Fi](https://ko-fi.com/aveyzan). This isn't necessary but will be much appreciated.

If you found anomalies in code or/and want to suggest changes, consider sending mail to [my email](mailto:aveyzan@gmail.com) or
creating an issue in [the GitHub repository](https://github.com/Aveyzan/AveyTense/issues). Bug fixes will be issued in future versions
of AveyTense. The project isn't intended to be a malware.

- Aveyzan (30th May 2025), AveyTense Project Owner

AveyTense project maintained on PyPi since 7th August 2024.

© 2024-Present Aveyzan // License: MIT
"""

setup(
    name = 'aveytense',
    version = aveytense.__version__, # check this before uploading!!
    description = "Library written in Python, includes several extensions for inbuilt Python solutions",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    author_email = "aveyzan@gmail.com",
    author = 'Aveyzan',
    license = "MIT",
    packages = [
        "aveytense",
        "aveytense._ᴧv_collection"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Software Development"
    ],
    package_data = {
        "aveytense": ["py.typed"],
    },
    include_package_data = True,
    install_requires = [
        "typing_extensions >= 4.10.0"
    ],
    python_requires = ">=3.8",
    project_urls = {
        "Documentation": "https://aveyzan.xyz/aveytense/",
        "Changes": "https://docs.google.com/document/d/1GC_KAOXML65jNfBZA8GhVViqPnrMoFtbLv_jHvUhBlg/edit?usp=sharing",
        "Repository": "https://github.com/Aveyzan/aveytense",
        "Ko-Fi Donations": "https://ko-fi.com/aveyzan",
        "Issues": "https://github.com/Aveyzan/aveytense/issues/"
    },
)