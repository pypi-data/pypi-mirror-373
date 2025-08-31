# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

from colorama import Fore
from colorama import Style

WIDTH = 100
SYMBOL = '═'


def chapter(title: str) -> str:
    """Formats a chapter header with bold magenta text, uppercase, and padding."""
    full_title = f' {title.upper()} '
    pad_len = (WIDTH - len(full_title)) // 2
    padding = SYMBOL * pad_len
    line = f'{Fore.LIGHTMAGENTA_EX + Style.BRIGHT}{padding}{full_title}{padding}{Style.RESET_ALL}'
    if len(line) < WIDTH:
        line += SYMBOL
    return f'\n{line}'


def section(title: str) -> str:
    """Formats a section header with bold green text."""
    full_title = f'*** {title.upper()} ***'
    return f'\n{Fore.LIGHTGREEN_EX + Style.BRIGHT}{full_title}{Style.RESET_ALL}'


def paragraph(title: str) -> str:
    """Formats a subsection header with bold blue text while keeping quoted text unformatted."""
    import re

    parts = re.split(r"('.*?')", title)
    formatted = f'{Fore.LIGHTBLUE_EX + Style.BRIGHT}'
    for part in parts:
        if part.startswith("'") and part.endswith("'"):
            formatted += Style.RESET_ALL + part + Fore.LIGHTBLUE_EX + Style.BRIGHT
        else:
            formatted += part
    formatted += Style.RESET_ALL
    return f'\n{formatted}'


def error(title: str) -> str:
    """Formats an error message with red text."""
    return f'\n❌ {Fore.LIGHTRED_EX}Error{Style.RESET_ALL}\n{title}'


def warning(title: str) -> str:
    """Formats a warning message with yellow text."""
    return f'\n⚠️ {Fore.LIGHTYELLOW_EX}Warning{Style.RESET_ALL}\n{title}'


def info(title: str) -> str:
    """Formats an info message with cyan text."""
    return f'\nℹ️ {Fore.LIGHTCYAN_EX}Info{Style.RESET_ALL}\n{title}'
