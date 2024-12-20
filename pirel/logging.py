import logging

from rich.logging import RichHandler


def setup_logging(verbosity: int = 0) -> None:
    """Sets up the basic logging configuration.

    Args:
        verbosity (int): Configures the log level which defaults to WARNING.
            A `verbosity` of `0` maps to WARNING, `1` -> INFO, and `2` (or more)
            -> DEBUG. Defaults to `0`.
    """
    base_loglevel = logging.WARNING  # 30
    # Calculate the log level based on verbosity, i.e. subtract intervals of 10
    # from level WARNING (30).
    loglevel = max(base_loglevel - (verbosity * 10), logging.DEBUG)
    logging.basicConfig(
        level=loglevel,
        format="%(message)s",
        handlers=[RichHandler(show_path=False, show_time=False)],
    )
