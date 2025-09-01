#!/usr/bin/env python

"""The setup script for lognflow."""

from setuptools import setup, find_packages

__author__ = 'Alireza Sadri'
__email__ = 'arsadri@gmail.com'
__version__ = '0.13.15'

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['numpy', 'matplotlib']

test_requirements = ['pytest>=3', ]

setup(
    author=__author__,
    author_email=__email__,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="Log and Flow tracking made easy with Python",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description = readme + '\n\n' + history,
    long_description_content_type = 'text/markdown',
    include_package_data=True,
    keywords='lognflow',
    name='lognflow',
    packages=find_packages(include=['lognflow', 'lognflow.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/arsadri/lognflow',
    version=__version__,
    zip_safe=False,
)