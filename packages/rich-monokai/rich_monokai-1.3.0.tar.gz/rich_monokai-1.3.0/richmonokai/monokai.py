#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# MIT License

# Copyright (c) 2021 Matt Doyle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import types

from contextlib import contextmanager
from rich.color import Color
from rich.console import Console as DefaultConsole
from rich.table import Table
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    ProgressColumn,
    TaskID,
    TextColumn,
    track,
)
from rich.style import Style
from rich.text import Text
from rich.theme import Theme
from typing import Tuple, Type, Iterator, List, Iterable


COLOR = types.SimpleNamespace(
    BLACK=Color.from_ansi(235),
    BLUE=Color.from_ansi(81),
    BROWN=Color.from_ansi(95),
    DARK_GRAY_1=Color.from_ansi(237),
    DARK_GRAY_2=Color.from_ansi(238),
    GREEN=Color.from_ansi(148),
    LIGHT_GRAY_1=Color.from_ansi(241),
    LIGHT_GRAY_2=Color.from_ansi(244),
    ORANGE=Color.from_ansi(208),
    PURPLE=Color.from_ansi(141),
    RED=Color.from_ansi(197),
    WHITE=Color.from_ansi(231),
    YELLOW=Color.from_ansi(222),
)


BACKGROUND = types.SimpleNamespace(
    BLACK=Style(bgcolor=COLOR.BLACK),
    BLUE=Style(bgcolor=COLOR.BLUE),
    BROWN=Style(bgcolor=COLOR.BROWN),
    DARK_GRAY_1=Style(bgcolor=COLOR.DARK_GRAY_1),
    DARK_GRAY_2=Style(bgcolor=COLOR.DARK_GRAY_2),
    GREEN=Style(bgcolor=COLOR.GREEN),
    LIGHT_GRAY_1=Style(bgcolor=COLOR.LIGHT_GRAY_1),
    LIGHT_GRAY_2=Style(bgcolor=COLOR.LIGHT_GRAY_2),
    ORANGE=Style(bgcolor=COLOR.ORANGE),
    PURPLE=Style(bgcolor=COLOR.PURPLE),
    RED=Style(bgcolor=COLOR.RED),
    WHITE=Style(bgcolor=COLOR.WHITE),
    YELLOW=Style(bgcolor=COLOR.YELLOW),
)


FOREGROUND = types.SimpleNamespace(
    BLACK=Style(color=COLOR.BLACK),
    BLUE=Style(color=COLOR.BLUE),
    BROWN=Style(color=COLOR.BROWN),
    DARK_GRAY_1=Style(color=COLOR.DARK_GRAY_1),
    DARK_GRAY_2=Style(color=COLOR.DARK_GRAY_2),
    GREEN=Style(color=COLOR.GREEN),
    LIGHT_GRAY_1=Style(color=COLOR.LIGHT_GRAY_1),
    LIGHT_GRAY_2=Style(color=COLOR.LIGHT_GRAY_2),
    ORANGE=Style(color=COLOR.ORANGE),
    PURPLE=Style(color=COLOR.PURPLE),
    RED=Style(color=COLOR.RED),
    WHITE=Style(color=COLOR.WHITE),
    YELLOW=Style(color=COLOR.YELLOW),
)


ATTRIBUTE = types.SimpleNamespace(
    BLINK=Style(blink=True),
    BLINK2=Style(blink2=True),
    BOLD=Style(bold=True),
    CONCEAL=Style(conceal=True),
    DIM=Style(dim=True),
    ENCIRCLE=Style(encircle=True),
    FRAME=Style(frame=True),
    ITALIC=Style(italic=True),
    NOT_BOLD=Style(bold=False),
    NOT_DIM=Style(dim=False),
    NOT_ITALIC=Style(italic=False),
    OVERLINE=Style(overline=True),
    REVERSE=Style(reverse=True),
    STRIKE=Style(strike=True),
    UNDERLINE=Style(underline=True),
    UNDERLINE2=Style(underline2=True),
    RESET=Style(
        bold=False,
        dim=False,
        italic=False,
        underline=False,
        blink=False,
        blink2=False,
        reverse=False,
        conceal=False,
        strike=False,
        underline2=False,
        frame=False,
        encircle=False,
        overline=False,
    ),
)

STYLES = {
    "bar.back": FOREGROUND.BLACK,
    "bar.complete": FOREGROUND.WHITE,
    "bar.finished": FOREGROUND.GREEN,
    "bar.pulse": FOREGROUND.ORANGE,
    "black": FOREGROUND.BLACK,
    "blink": ATTRIBUTE.BLINK,
    "blink2": ATTRIBUTE.BLINK2,
    "bold": ATTRIBUTE.BOLD,
    "bright": ATTRIBUTE.NOT_DIM,
    "code": ATTRIBUTE.BOLD + ATTRIBUTE.REVERSE,
    "cyan": FOREGROUND.BLUE,
    "dim": ATTRIBUTE.DIM,
    "emphasize": ATTRIBUTE.ITALIC,
    "green": FOREGROUND.GREEN,
    "inspect.async_def": FOREGROUND.BLUE + ATTRIBUTE.ITALIC,
    "inspect.attr.dunder": FOREGROUND.YELLOW + ATTRIBUTE.ITALIC,
    "inspect.attr": FOREGROUND.YELLOW + ATTRIBUTE.ITALIC,
    "inspect.callable": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "inspect.class": FOREGROUND.BLUE + ATTRIBUTE.ITALIC,
    "inspect.def": FOREGROUND.BLUE + ATTRIBUTE.ITALIC,
    "inspect.doc": "none",
    "inspect.equals": "none",
    "inspect.error": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "inspect.help": FOREGROUND.BLUE,
    "inspect.value.border": FOREGROUND.GREEN,
    "iso8601.date": "none",
    "iso8601.time": "none",
    "iso8601.timezone": "none",
    "italic": ATTRIBUTE.ITALIC,
    "json.bool_false": FOREGROUND.RED + ATTRIBUTE.ITALIC,
    "json.bool_true": FOREGROUND.GREEN + ATTRIBUTE.ITALIC,
    "json.brace": ATTRIBUTE.BOLD,
    "json.key": FOREGROUND.BLUE + ATTRIBUTE.BOLD,
    "json.null": FOREGROUND.RED + ATTRIBUTE.ITALIC,
    "json.number": FOREGROUND.BLUE + ATTRIBUTE.BOLD + ATTRIBUTE.NOT_ITALIC,
    "json.str": FOREGROUND.GREEN + ATTRIBUTE.NOT_BOLD + ATTRIBUTE.NOT_ITALIC,
    "layout.tree.column": FOREGROUND.BLUE + ATTRIBUTE.NOT_DIM,
    "layout.tree.row": FOREGROUND.RED + ATTRIBUTE.NOT_DIM,
    "live.ellipsis": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "log.level": "none",
    "log.message": "none",
    "log.path": "none",
    "log.time": "none",
    "logging.keyword": FOREGROUND.YELLOW + ATTRIBUTE.BOLD,
    "logging.level.critical": FOREGROUND.RED + ATTRIBUTE.BOLD + ATTRIBUTE.REVERSE,
    "logging.level.debug": FOREGROUND.GREEN,
    "logging.level.error": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "logging.level.info": FOREGROUND.BLUE,
    "logging.level.notset": "none",
    "logging.level.warning": FOREGROUND.YELLOW,
    "magenta": FOREGROUND.RED,
    "markdown.block_quote": FOREGROUND.RED,
    "markdown.code_block": FOREGROUND.BLUE + BACKGROUND.BLACK,
    "markdown.code": FOREGROUND.BLUE + BACKGROUND.BLACK + ATTRIBUTE.BOLD,
    "markdown.em": ATTRIBUTE.ITALIC,
    "markdown.emph": ATTRIBUTE.ITALIC,
    "markdown.h1.border": "none",
    "markdown.h1": ATTRIBUTE.BOLD,
    "markdown.h2": ATTRIBUTE.BOLD,
    "markdown.h3": ATTRIBUTE.BOLD,
    "markdown.h4": ATTRIBUTE.BOLD,
    "markdown.h5": ATTRIBUTE.BOLD,
    "markdown.h6": ATTRIBUTE.BOLD,
    "markdown.h7": ATTRIBUTE.BOLD,
    "markdown.hr": FOREGROUND.YELLOW,
    "markdown.item.bullet": FOREGROUND.YELLOW + ATTRIBUTE.BOLD,
    "markdown.item.number": FOREGROUND.YELLOW + ATTRIBUTE.BOLD,
    "markdown.item": "none",
    "markdown.link_url": FOREGROUND.BLUE + ATTRIBUTE.UNDERLINE,
    "markdown.link": FOREGROUND.BLUE + ATTRIBUTE.NOT_DIM,
    "markdown.list": FOREGROUND.BLUE,
    "markdown.paragraph": "none",
    "markdown.s": ATTRIBUTE.STRIKE,
    "markdown.strong": ATTRIBUTE.BOLD,
    "markdown.text": "none",
    "none": "none",
    "pretty": "none",
    "progress.data.speed": FOREGROUND.WHITE,
    "progress.description": FOREGROUND.WHITE,
    "progress.download": FOREGROUND.WHITE,
    "progress.elapsed": FOREGROUND.BLUE,
    "progress.filesize.total": FOREGROUND.WHITE,
    "progress.filesize": FOREGROUND.WHITE,
    "progress.percentage": FOREGROUND.WHITE,
    "progress.remaining": FOREGROUND.WHITE,
    "progress.spinner": FOREGROUND.ORANGE,
    "prompt.choices": FOREGROUND.YELLOW + ATTRIBUTE.BOLD,
    "prompt.default": FOREGROUND.BLUE + ATTRIBUTE.BOLD,
    "prompt.invalid.choice": FOREGROUND.RED,
    "prompt.invalid": FOREGROUND.RED,
    "prompt": FOREGROUND.WHITE,
    "red": FOREGROUND.RED,
    "repr.attrib_equal": ATTRIBUTE.BOLD,
    "repr.attrib_name": FOREGROUND.YELLOW + ATTRIBUTE.NOT_ITALIC,
    "repr.attrib_value": FOREGROUND.RED + ATTRIBUTE.NOT_ITALIC,
    "repr.bool_false": FOREGROUND.RED + ATTRIBUTE.ITALIC,
    "repr.bool_true": FOREGROUND.GREEN + ATTRIBUTE.ITALIC,
    "repr.brace": ATTRIBUTE.BOLD,
    "repr.call": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "repr.comma": ATTRIBUTE.BOLD,
    "repr.ellipsis": FOREGROUND.YELLOW,
    "repr.error": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "repr.eui48": FOREGROUND.GREEN + ATTRIBUTE.BOLD,
    "repr.eui64": FOREGROUND.GREEN + ATTRIBUTE.BOLD,
    "repr.filename": FOREGROUND.RED + ATTRIBUTE.NOT_DIM,
    "repr.indent": FOREGROUND.DARK_GRAY_1,
    "repr.ipv4": FOREGROUND.GREEN + ATTRIBUTE.BOLD,
    "repr.ipv6": FOREGROUND.GREEN + ATTRIBUTE.BOLD,
    "repr.none": FOREGROUND.RED + ATTRIBUTE.ITALIC,
    "repr.number_complex": FOREGROUND.BLUE + ATTRIBUTE.BOLD + ATTRIBUTE.NOT_ITALIC,
    "repr.number": FOREGROUND.BLUE + ATTRIBUTE.BOLD + ATTRIBUTE.NOT_ITALIC,
    "repr.path": FOREGROUND.RED,
    "repr.str": FOREGROUND.GREEN + ATTRIBUTE.NOT_BOLD + ATTRIBUTE.NOT_ITALIC,
    "repr.tag_contents": "none",
    "repr.tag_end": ATTRIBUTE.BOLD,
    "repr.tag_name": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "repr.tag_start": ATTRIBUTE.BOLD,
    "repr.url": FOREGROUND.BLUE
    + ATTRIBUTE.NOT_BOLD
    + ATTRIBUTE.NOT_ITALIC
    + ATTRIBUTE.UNDERLINE,
    "repr.uuid": FOREGROUND.YELLOW + ATTRIBUTE.NOT_BOLD,
    "reset": FOREGROUND.WHITE + BACKGROUND.BLACK + ATTRIBUTE.RESET,
    "reverse": ATTRIBUTE.REVERSE,
    "rule.line": FOREGROUND.GREEN,
    "rule.text": FOREGROUND.BLUE,
    "scope.border": FOREGROUND.BLUE,
    "scope.equals": FOREGROUND.RED,
    "scope.key.special": FOREGROUND.YELLOW + ATTRIBUTE.ITALIC,
    "scope.key": FOREGROUND.YELLOW + ATTRIBUTE.ITALIC,
    "status.spinner": FOREGROUND.GREEN,
    "strike": ATTRIBUTE.STRIKE,
    "strong": ATTRIBUTE.BOLD,
    "table.caption": ATTRIBUTE.ITALIC,
    "table.cell": "none",
    "table.footer": ATTRIBUTE.BOLD,
    "table.header": FOREGROUND.WHITE + ATTRIBUTE.BOLD,
    "table.title": ATTRIBUTE.ITALIC,
    "traceback.border.syntax_error": FOREGROUND.RED,
    "traceback.border": FOREGROUND.RED,
    "traceback.error_range": ATTRIBUTE.BOLD + ATTRIBUTE.NOT_DIM,
    "traceback.error": FOREGROUND.RED + ATTRIBUTE.ITALIC,
    "traceback.exc_type": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "traceback.exc_value": "none",
    "traceback.offset": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "traceback.text": "none",
    "traceback.title": FOREGROUND.RED + ATTRIBUTE.BOLD,
    "tree.line": "none",
    "tree": "none",
    "underline": ATTRIBUTE.UNDERLINE,
    "white": FOREGROUND.WHITE,
    "yellow": FOREGROUND.YELLOW,
}


class MonokaiTheme(Theme):

    def __init__(self):
        super().__init__(styles=STYLES)


class SimpleProgress(Progress):
    """Simplified, single-task Progress bar."""

    def __init__(
        self,
        console: Type[MonokaiConsole],
        remaining_column: ProgressColumn,
        bar_width: int = 40,
        refresh_per_second: int = 1,
    ):
        super().__init__(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=bar_width),
            remaining_column,
            console=console,
            refresh_per_second=refresh_per_second,
        )
        self.task_id = None

    def AddTask(self, description: str, total: int):
        if self.task_id is None:
            self.task_id = self.add_task(description, start=True, total=total)

    def Advance(self, advance=1):
        if self.task_id is not None:
            self.advance(self.task_id, advance=advance)

    def Reset(self):
        if self.task_id is not None:
            self.reset(self.task_id)


class NumericProgress(SimpleProgress):

    def __init__(self, console: Type[MonokaiConsole], **kwargs):
        super().__init__(console, MofNCompleteColumn(), **kwargs)


class DataProgress(SimpleProgress):

    def __init__(self, console: Type[MonokaiConsole], **kwargs):
        super().__init__(console, DownloadColumn(), **kwargs)


class MonokaiConsole(DefaultConsole):

    def __init__(self, highlight: bool = False, *args, **kwargs):
        kwargs["theme"] = MonokaiTheme()
        super().__init__(*args, **kwargs)

    def PrintWithLabel(
        self, label: str, message: str, label_fg: Style = FOREGROUND.WHITE
    ):
        self.print(f"{label}:", style=label_fg, end=" ")
        self.print(f"{message}", style=FOREGROUND.WHITE + ATTRIBUTE.NOT_BOLD, end="\n")

    def PrintException(self, ex: Exception):
        self.PrintFailure(ex.__class__.__name__, str(ex))

    def PrintFailure(self, label: str, message: str):
        self.PrintWithLabel(label, message, label_fg=FOREGROUND.RED)

    def PrintStatus(self, label: str, message: str):
        self.PrintWithLabel(label, message, label_fg=FOREGROUND.BLUE)

    def PrintSuccess(self, label: str, message: str):
        self.PrintWithLabel(label, message, label_fg=FOREGROUND.GREEN)

    def Status(self, message: str):
        style = FOREGROUND.ORANGE + ATTRIBUTE.BOLD
        return self.status(Text(message, style=style), spinner_style=style)

    @contextmanager
    def NumericProgressBar(self, description: str, total: int) -> Iterator[None]:
        with NumericProgress(self) as progress:
            progress.AddTask(description, total)
            yield progress

    @contextmanager
    def DataProgressBar(self, description: str, total: int) -> Iterator[None]:
        with DataProgress(self) as progress:
            progress.AddTask(description, total)
            yield progress

    def Track(self, sequence: Iterable[object], description: str) -> object:
        for item in track(
            sequence, description=description, console=self, show_speed=False
        ):
            yield item


if __name__ == "__main__":

    console = MonokaiConsole(highlight=False)
    table = Table("Name", "Styling")

    for style_name, style in STYLES.items():
        table.add_row(Text(style_name, style=style), str(style))

    console.print(table)
