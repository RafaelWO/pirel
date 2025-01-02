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


## CLI Docs
**Usage**:

```console
$ pirel [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--no-cache`: Clear cache before running
* `-v, --verbose`: Enable verbose logging; can be supplied multiple times to increase verbosity. [default: 0]
* `--version`: Dispay the version of pirel
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `check`: Shows release information about your active Python interpreter.
* `guess`: Test your knowledge by answering a question regarding Python releases.
* `list`: Lists all Python releases in a table.

### `pirel check`

Shows release information about your active Python interpreter.

If the active version is end-of-life, the program exits with code 1.
If no active Python interpreter is found, the program exits with code 2.

**Usage**:

```console
$ pirel check [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `pirel guess`

Test your knowledge by answering a question regarding Python releases.

For example, "When was Python 3.9 released?" or "Who was the release manager for
Python 3.6?".

**Usage**:

```console
$ pirel guess [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `pirel list`

Lists all Python releases in a table. Your active Python interpreter is highlighted.

**Usage**:

```console
$ pirel list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

> [!NOTE]
> You can still invoke `pirel` without a subcommand and you will get a table of all Python releases.
> But note that this is **deprecated**, i.e. please use `pirel list`.


## Contributing
PRs are welcome! 🤗

This project uses [uv](https://github.com/astral-sh/uv) to manage packaging.
Please check the [corresponding docs](https://docs.astral.sh/uv/) for installation instructions.

Before you commit any changes, please ensure that you have [pre-commit](https://pre-commit.com)
available on your system. Run `pre-commit install` to install the project's hooks.


## Development
### Generate Video Demo
To generate the video demo on the top, I used [vhs](https://github.com/charmbracelet/vhs).

If you change something in the "tape" file `./assets/cli_demo.tape` run the following
command to update the GIF: `vhs assets/cli_demo.tape`


<!-- Links -->
[cli-example]: https://raw.githubusercontent.com/RafaelWO/pirel/refs/heads/main/assets/images/cli_demo.gif
