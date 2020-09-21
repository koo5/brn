#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.
.. currentmodule:: brn.cli
.. moduleauthor:: koo <my_email@gmail.com>
"""
import logging
import click
from .__init__ import __version__
import pdb; pdb.set_trace()
from tau_testcase_parser import *


LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels


class Info(object):
    """An information object to pass data between CLI functions."""

    def __init__(self):  # Note: This object must have an empty constructor.
        """Create a new instance."""
        self.verbose: int = 0


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)



@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@pass_info
def cli(info: Info, verbose: int):
    """Run brn."""
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG
        )
        click.echo(
            click.style(
                f"Verbose logging is enabled. "
                f"(LEVEL={logging.getLogger().getEffectiveLevel()})",
                fg="yellow",
            )
        )
    info.verbose = verbose




@cli.command()
@pass_info
@click.argument('main_directory', type=click.Path())
def parse_tau_testcases(_: Info, main_directory):
    """Parse tau testcases in all subdirectories of main_directory.
    main_directory is probably tests/."""
    click.echo("scanning " + main_directory)
    print(subfolder_paths(AbsPath(main_directory)))



@cli.group()
def cli2():
    """Run cli2."""
    pass


@cli2.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))







