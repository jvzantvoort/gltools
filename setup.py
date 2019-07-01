#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import io
import os
import re

setup_path = os.path.abspath(__file__)
setup_path_dir = os.path.dirname(setup_path)

exec(open(os.path.join(setup_path_dir, 'gltools', 'version.py')).read())

long_description = open(os.path.join(setup_path_dir, 'README.md')).read()

setup(
    name='gltools',
    version=__version__,
    description='GitLab Tools',
    keywords='gitlab,gltools',
    long_description=long_description,
    author='John van Zantvoort',
    author_email='john.van.zantvoort@proxy.nl',
    url='https://github.com/jvzantvoort/gltools',
    packages=find_packages(exclude=['docs', 'docs-src', 'tests']),
    install_requires=['requests'],
    scripts=['bin/gl-export-group', 'bin/gl-setup-group'],
    license='MIT',
    test_suite="tests",
    classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Office/Business',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
    ]
)
