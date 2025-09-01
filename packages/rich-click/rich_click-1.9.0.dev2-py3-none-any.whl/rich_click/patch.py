"""The command line interface."""

from __future__ import annotations

# ruff: noqa: D103
from typing import Optional

import click

import rich_click
import rich_click.rich_command
from rich_click.decorators import command as _rich_command
from rich_click.decorators import group as _rich_group
from rich_click.rich_command import RichCommand, RichCommandCollection, RichGroup, RichMultiCommand
from rich_click.rich_help_configuration import RichHelpConfiguration


class _PatchedRichCommand(RichCommand):
    pass


class _PatchedRichMultiCommand(RichMultiCommand, _PatchedRichCommand):
    pass


class _PatchedRichCommandCollection(RichCommandCollection, _PatchedRichCommand):
    pass


class _PatchedRichGroup(RichGroup, _PatchedRichCommand):
    pass


def rich_command(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichCommand)
    kwargs["__rich_click_cli_patch"] = True
    return _rich_command(*args, **kwargs)


def rich_group(*args, **kwargs):  # type: ignore[no-untyped-def]
    kwargs.setdefault("cls", _PatchedRichGroup)
    kwargs["__rich_click_cli_patch"] = True
    return _rich_group(*args, **kwargs)


def patch(rich_config: Optional[RichHelpConfiguration] = None, *, patch_rich_click: bool = False) -> None:
    """Patch Click internals to use rich-click types."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)

        rich_click.rich_command.OVERRIDES_GUARD = True
        click.group = rich_group
        click.command = rich_command
        click.Group = _PatchedRichGroup  # type: ignore[misc]
        click.Command = _PatchedRichCommand  # type: ignore[misc]
        click.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]

        if hasattr(click, "MultiCommand"):
            click.MultiCommand = _PatchedRichMultiCommand  # type: ignore[assignment,misc,unused-ignore]
        if patch_rich_click:
            rich_click.group = rich_group
            rich_click.command = rich_command
            rich_click.Group = _PatchedRichGroup  # type: ignore[misc]
            rich_click.Command = _PatchedRichCommand  # type: ignore[misc]
            rich_click.CommandCollection = _PatchedRichCommandCollection  # type: ignore[misc]
            if hasattr(click, "MultiCommand"):
                rich_click.MultiCommand = _PatchedRichMultiCommand  # type: ignore[assignment,misc,unused-ignore]

    if rich_config is not None:
        rich_config.dump_to_globals()
