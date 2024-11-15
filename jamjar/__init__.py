#!/usr/bin/env python

__version__ = "0.1.0"

import json
import os

import click

from jamjar.cli.auth import auth
from jamjar.cli.playlist import playlist


@click.group()
def cli():
    pass


cli.add_command(auth)
cli.add_command(playlist)

if __name__ == "__main__":
    cli()
