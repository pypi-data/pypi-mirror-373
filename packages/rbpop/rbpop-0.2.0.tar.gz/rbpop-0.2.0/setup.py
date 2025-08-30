#!/usr/bin/env python
# coding:utf-8
import os
import sys
import ctypes
import tempfile
from setuptools import find_packages, setup
from setuptools.command.install import install



setup(
    name='rbpop',
    version='0.2.0',
    description='A lightweight, modern PyQt6 popup notification library with smooth animations, queue management, and multiple preset styles.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="Eagle'sBaby",
    author_email='2229066748@qq.com',
    maintainer="Eagle'sBaby",
    maintainer_email='2229066748@qq.com',
    url='https://github.com/EagleBaby/rbpop',
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Desktop Environment',
        'Topic :: Software Development :: User Interfaces',
    ],
    keywords=['pyqt6', 'popup', 'notification', 'toast', 'message', 'dialog', 'window'],
    python_requires='>=3.10',
    install_requires=[
        "PyQt6",
    ],
)
