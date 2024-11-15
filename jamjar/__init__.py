#!/usr/bin/env python

__version__ = "0.1.0"

import json
import os

import click

from jamjar.cli.auth import auth


@click.group()
def cli():
    pass


cli.add_command(auth)

if __name__ == "__main__":
    cli()
