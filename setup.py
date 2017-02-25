#!/usr/bin/env python3
from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 5, 0):
    sys.exit("You need at least Python 3.5 to run this package.")

setup(
    name='strangelove',
    version='0.0.1',
    description="Monitor movie releases.",
    packages=find_packages(),
    install_requires=['aiocron', 'aiohttp', 'beautifulsoup4', 'irc3',
                      'sqlalchemy'],
    entry_points=dict(
        console_scripts=['strangelove=strangelove.__main__:main']
    ),
)
