#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

from setuptools import find_packages, setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py'), 'rb') as init_py:
        src = init_py.read().decode('utf-8')
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", src).group(1)


version = get_version('entrez')


with open('README.md') as readme:
    long_description = readme.read()


install_requires = [
    'setuptools',
    'pytest==3.4.2',
    'pytest-cov==2.5.1',
    'requests==2.18.4',
]

setup(
    name='entrez',
    version='0.1.0',
    description='Entrez Library, api for the GenBank databases',
    long_description=long_description,
    url='https://github.com/kaiser0906/entrez',
    author='Dave Cho',
    author_email='kaiser0906@gmail.com',
    license='MIT License',
    packages=find_packages(exclude=['tests']),
    test_suite='tests.tests',
    install_requires=install_requires,
    extras_require={
        ':python_version == "2.7"': [
            'mock==2.0.0',
        ],
    },
    entry_points={'console_scripts': [
        'entrez=entrez.api:main'
    ]},
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Anonymous',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ]
)
