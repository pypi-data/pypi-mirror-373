#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from setuptools import setup, find_packages

full_version = ''

root_dir = os.path.abspath(os.path.dirname(__file__))

readme_file = os.path.join(root_dir, 'README.rst')
with open(readme_file, encoding='utf-8') as f:
    long_description = f.read()

version_module = os.path.join(root_dir, 'src', 'mattermostdriver', 'version.py')
with open(version_module, encoding='utf-8') as f:
    exec(f.read())

setup(
    name='nordmattermostdriver',
    version=full_version,
    description='A Python Mattermost Driver',
    long_description=long_description,
    url='https://github.com/i-mantuliak/python-mattermost-driver',
    author='Igor Mantuliak',
    author_email='igor.mantuliak@my.games',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    python_requires=">=3.6",
    install_requires=[
        'aiohttp>=3.8.1,<4.0.0',
        'httpx>=0.20.0,<0.28.0',
        'requests==2.32.5'
    ],
)
