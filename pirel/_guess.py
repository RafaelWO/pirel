from __future__ import annotations

import abc
import csv
import datetime
import inspect
import random
from typing import Callable, Iterable, Optional, TextIO

import platformdirs
from rich.console import Console
from rich.prompt import DefaultType, Prompt
from rich.text import Text

import pirel

from .releases import PythonRelease

STATS_DIR = platformdirs.user_data_path("pirel")
STATS_FILENAME = "guess_stats.csv"
STATS_FIELDNAMES = ["time", "question_cls", "target_release", "score"]


class PirelPrompt(Prompt):
    """A customized `rich.prompt.Prompt` that needs choices and returns a str.

    The choices are rendered as possible answers for a question prefixed by a), b), etc.

    Example:
        >>> prompt = PirelPrompt("What year do we have?", choices=["2020", "2024", "2022"])
        >>> answer = prompt()
        What year do we have?
         a) 2020
         b) 2024
         c) 2022
        >
    """

    prompt_suffix = "\n> "
    illegal_choice_message = "[prompt.invalid.choice]Please select one of the available options or indices (a, b, etc.)"
    choices: list[str]
    stream: Optional[TextIO] = None  # To be mocked during tests

    def __init__(
        self,
        prompt: str,
        *,
        choices: list[str],
        console: Optional[Console] = None,
        password: bool = False,
        case_sensitive: bool = True,
        show_default: bool = True,
    ):
        super().__init__(
            prompt,
            choices=choices,
            show_choices=True,
            console=console,
            password=password,
            case_sensitive=case_sensitive,
            show_default=show_default,
        )
        self.choice_enum = "abcdefgh"[: len(self.choices)]

    def make_prompt(self, default: DefaultType) -> Text:
        """Make prompt text.

        Args:
            default (DefaultType): Default value.

        Returns:
            Text: Text to display in prompt.
        """
        prompt = self.prompt.copy()
        prompt.end = ""

        if self.show_choices and self.choices:
            # We want to list the choices as lines
            choices = "\n".join(
                f" {i}) {c}" for i, c in zip(self.choice_enum, self.choices)
            )

            prompt.append("\n")
            prompt.append(choices, "prompt.choices")

        if (
            default != ...
            and self.show_default
            and isinstance(default, (str, self.response_type))
        ):
            prompt.append(" ")
            _default = self.render_default(default)
            prompt.append(_default)

        prompt.append(self.prompt_suffix)

        return prompt

    def check_choice(self, value: str) -> bool:
        """Check value is in the list of valid choices.

        Args:
            value (str): Value entered by user.

        Returns:
            bool: True if choice was valid, otherwise False.
        """
        return value in self.choice_enum or super().check_choice(value)

    def process_response(self, value: str) -> str:
        """Process response from user, convert to prompt type.

        Args:
            value (str): String typed by user.

        Raises:
            InvalidResponse: If ``value`` is invalid.

        Returns:
            str: The value to be returned from ask method.
        """
        if value in self.choice_enum:
            return self.choices[self.choice_enum.index(value)]
        else:
            return super().process_response(value)


class Question(abc.ABC):
    """Base class for a question regarding Python releases."""

    question: str
    target_release: PythonRelease
    get_target_field: Callable[[PythonRelease], str]

    def __init__(self, releases: list[PythonRelease]):
        if not hasattr(self, "target_release"):
            self.target_release = random.choice(releases)
        self.releases = releases
        self.choices = self.build_choices()

    @property
    def correct_answer(self) -> str:
        """Returns the correct answer as a string by calling `get_target_field` on the
        target release object.

        Returns:
            str: The answer for the question.
        """
        return self.get_target_field(self.target_release)

    def generate_incorrect_choices(
        self,
        *predicates: Callable[[PythonRelease], bool],
        k: int = 3,
        remove_duplicates: bool = False,
    ) -> list[PythonRelease]:
        """Generates random choices of `PythonRelease` objects excluding the target
        release (i.e. the answer).

        Args:
            *predicates (Callable[[PythonRelease], bool]): A set of predicates to apply
                as filters for the releases.
            k (int, optional): The number of choices to return. Defaults to 3.

        Returns:
            list[PythonRelease]: A list of releases to serve as incorrect answers.
        """
        # Shuffle releases to have a random set of choices
        random.shuffle(self.releases)

        candidates: Iterable[PythonRelease] = filter(
            lambda x: x != self.target_release, self.releases
        )
        for pred in predicates:
            candidates = filter(pred, candidates)

        if remove_duplicates:
            candidates = {
                self.get_target_field(rel): rel for rel in candidates
            }.values()
        return list(candidates)[:k]

    def format_question(self) -> str:
        """Hook to format the question."""
        return self.question

    def incorrect_choices(self) -> list[PythonRelease]:
        """Hook to create a set of incorrect choices."""
        return self.generate_incorrect_choices()

    def build_choices(self) -> list[str]:
        """Builds all choices for a question by combining the target release/answer and
        the incorrect ones.

        Returns:
            list[str]: A list of choices.
        """

        choices = list(
            map(self.get_target_field, [self.target_release, *self.incorrect_choices()])
        )
        # Shuffle so that correct choice is not first item
        random.shuffle(choices)
        return choices

    def ask(self) -> bool:
        """Construct the prompt for the question, prompt the user, and return the
        result.

        Returns:
            bool: `True` if the answer was correct, else `False`.
        """
        prompt = PirelPrompt(
            self.format_question(),
            choices=self.choices,
            console=pirel.CONTEXT.rich_console,
        )
        answer = prompt(stream=PirelPrompt.stream)
        if answer == self.correct_answer:
            pirel.CONTEXT.rich_console.print(
                f"[prompt.choices]{answer}[/] is [green]correct![/]"
            )
            return True
        else:
            pirel.CONTEXT.rich_console.print(
                f"[prompt.choices]{answer}[/] is [red]wrong![/]"
                f" (Correct answer: [prompt.choices]{self.correct_answer}[/])"
            )
            return False


class LatestVersionQuestion(Question):
    question: str = "What is the latest stable version of Python?"
    __doc__ = question

    def __init__(self, releases: list[PythonRelease]):
        self.target_release = max(filter(lambda x: x._status == "bugfix", releases))
        self.get_target_field = lambda x: x.version
        super().__init__(releases)

    def incorrect_choices(self) -> list[PythonRelease]:
        return self.generate_incorrect_choices(lambda x: x.version.startswith("3"))


class VersionDateQuestion(Question):
    question: str = "When was Python {version} released?"
    __doc__ = question

    def __init__(self, releases: list[PythonRelease]):
        self.target_release = random.choice(releases)
        self.get_target_field = lambda x: x._released.isoformat()
        super().__init__(releases)

    def format_question(self) -> str:
        return self.question.format(version=self.target_release.version)


class DateVersionQuestion(Question):
    question: str = "Which version of Python was released on {release_date}?"
    __doc__ = question

    def __init__(self, releases: list[PythonRelease]):
        self.target_release = random.choice(releases)
        self.get_target_field = lambda x: x.version
        super().__init__(releases)

    def format_question(self) -> str:
        return self.question.format(release_date=self.target_release._released)


class ReleaseManagerVersionQuestion(Question):
    question: str = "Who was the release manager for Python {version}?"
    __doc__ = question

    def __init__(self, releases: list[PythonRelease]):
        self.get_target_field = lambda x: x._release_manager
        super().__init__(releases)

    def format_question(self) -> str:
        return self.question.format(version=self.target_release._version)

    def incorrect_choices(self) -> list[PythonRelease]:
        return self.generate_incorrect_choices(remove_duplicates=True)


def store_question_score(question: Question, score: int) -> None:
    """Save question score to user data."""
    if not STATS_DIR.exists():
        STATS_DIR.mkdir(parents=True)

    stats_file = STATS_DIR / STATS_FILENAME
    with stats_file.open("a", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=STATS_FIELDNAMES, quoting=csv.QUOTE_NONNUMERIC
        )
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(
            {
                "time": datetime.datetime.now().isoformat(),
                "question_cls": question.__class__.__name__,
                "target_release": question.target_release.version,
                "score": score,
            }
        )


def get_random_question() -> Question:
    """Randomly picks one of the available questions.

    Returns:
        type[Question]: A class of type `Question`.
    """
    question_cls = random.choice(
        [
            var
            for var in globals().values()
            if inspect.isclass(var) and issubclass(var, Question) and var != Question
        ]
    )
    return question_cls(pirel.CONTEXT.releases.to_list())
