# Pirel

<div align="center" markdown="1">

**The Python release cycle in your terminal!**

[![Package Version](https://img.shields.io/pypi/v/pirel.svg)](https://pypi.org/project/pirel/)
[![Python Version](https://img.shields.io/pypi/pyversions/pirel.svg)](https://pypi.org/project/pirel/)
[![License](https://img.shields.io/github/license/RafaelWO/unparallel)](https://github.com/RafaelWO/unparallel/blob/main/LICENSE)

</div>


![cli-example][cli-example]


## Installation
It is recommended to install Pirel as a globally available CLI tool via `pipx` (or `uv tool`, etc.).
This way you Pirel will show you the status of your active Python interpreter.

```
pipx install pirel
```

You can also install Pirel into a specific virtual environment.

```
pip install pirel
```


## Usage
Simply type `pirel` in your terminal and you will get a table of all Python releases. Your active Python interpreter is marked with an asterisk.


<!-- Links -->
[cli-example]: https://raw.githubusercontent.com/RafaelWO/pirel/refs/heads/main/assets/images/cli_demo.gif

## Contributing
PRs are welcome! 🤗

This project uses [uv](https://github.com/astral-sh/uv) to manage packaging.
Please check the [corresponding docs](https://docs.astral.sh/uv/) for installation instructions.

Before you commit any changes, please ensure that you have [pre-commit](https://pre-commit.com)
available on your system. Run `pre-commit install` to install the project's hooks.
