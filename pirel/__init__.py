import functools

from rich.console import Console

from pirel.releases import PythonReleases, load_releases

__version__ = "0.4.0"


class PirelContext:
    """Contains objects that should be shared within the CLI application.

    The intuition behind this context class is to make some objects, like the rich
    console or the release cycle data object globally available.

    Since we don't have to load the releases data if a user runs e.g. `pirel --version`,
    the `releases` property it is implemented as a cached property to allow "lazy"
    evaluation.
    """

    def __init__(self) -> None:
        self.rich_console = Console(highlight=False)

    @functools.cached_property
    def releases(self) -> PythonReleases:
        """Returns the Python release cycle data.

        This property is
        """
        return load_releases()


CONTEXT = PirelContext()
