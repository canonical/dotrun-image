#! /usr/bin/env python3

# Core
import sys
from setuptools import setup

assert sys.version_info >= (3, 8), "dotrun-docker requires Python 3.8 or newer"

setup(
    name="dotrun-docker",
    version="1.0.2",
    packages=["dotrun_docker"],
    install_requires=[
        "ipdb",
        "black",
        "flake8",
        "termcolor",
        "virtualenv",
        "python-dotenv",
    ],
    entry_points={"console_scripts": ["dotrun = dotrun_docker:cli"]},
)
