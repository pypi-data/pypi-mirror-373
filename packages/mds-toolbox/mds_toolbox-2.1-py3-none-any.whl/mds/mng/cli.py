#!/usr/bin/env python

"""
CLI Interface for mds-toolbox.
"""

__author__ = "Antonio Mariani"
__email__ = "antonio.mariani@cmcc.it"

import click

from mds.mng.s3_group import s3_cli
from mds.mng.wrapper_group import wrapper_cli


@click.command(
    cls=click.CommandCollection,
    sources=[s3_cli, wrapper_cli],
    context_settings=dict(help_option_names=["-h", "--help"]),
)
def cli():
    pass


if __name__ == "__main__":
    cli()
