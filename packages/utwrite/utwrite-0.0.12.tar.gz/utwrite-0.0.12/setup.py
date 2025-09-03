#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name = 'utwrite',
    version = '0.0.12',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'utw = utwrite:main',
        ]},

    description='Auto[magically] write Python unittest files from docstrings.',
    long_description=description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ],
    url='https://codeberg.org/pbellini/utwrite'
)
