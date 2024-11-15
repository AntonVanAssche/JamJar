#!/usr/bin/env python

from setuptools import setup

setup(
    name="jamjar",
    version="0.1",
    packages=["jamjar"],
    install_requires=[
        "requests",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "jamjar=jamjar.__init__:cli",
        ],
    },
)
