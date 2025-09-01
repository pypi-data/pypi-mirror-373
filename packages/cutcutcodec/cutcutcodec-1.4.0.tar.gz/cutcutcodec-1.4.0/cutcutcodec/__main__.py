#!/usr/bin/env python3

"""Entry point of the cli interface."""

import sys

import click

from cutcutcodec import __version__
from cutcutcodec.doc import main as main_doc
from cutcutcodec.testing.__main__ import main as main_test
from cutcutcodec.utils import get_project_root


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Display the version of cutcutcodec.")
def main(ctx=None, version: bool = False):
    """Run the main ``cutcutcodec`` command line interface."""
    if version:
        click.echo(__version__)
    elif not ctx.invoked_subcommand:
        readme = get_project_root().parent / "README.rst"
        title = f"* cutcutcodec {__version__} *"
        click.echo(
            f"{'*'*len(title)}\n{title}\n{'*'*len(title)}\n\n"
            f"For a detailed description, please refer to {readme} "
            "or https://framagit.org/robinechuca/cutcutcodec.\n"
            f"Type `{sys.executable} -m cutcutcodec --help` to see all the cli options.\n"
        )


main.add_command(main_doc, "doc")
main.add_command(main_test, "test")


if __name__ == "__main__":
    main()
