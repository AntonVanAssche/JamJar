#!/usr/bin/env python

"""
Module to configure the setup for the JamJar CLI.
"""

from setuptools import find_packages, setup

setup(
    author="Anton Van Assche",
    author_email="vanasscheanton@gmail.com",
    description="A CLI tool to store and manage Spotify playlist data in a database.",
    license="MIT",
    name="jamjar",
    packages=find_packages(),
    url="https://www.github.com/AntonVanAssche/jamjar",
    version="0.2.0",
    install_requires=[
        "requests",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "jamjar=jamjar.__init__:cli",
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
)
