#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import inspect

import setuptools
from setuptools import setup

if sys.version_info < (3, 9, 0):
    sys.stderr.write("FATAL: Zalando Kubectl needs to be run with Python 3.9+\n")
    sys.exit(1)
__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


def read_version(package):
    data = {}
    with open(os.path.join(package, "__init__.py"), "r") as fd:
        exec(fd.read(), data)
    return data["APP_VERSION"]


NAME = "zalando-kubectl"
MAIN_PACKAGE = "zalando_kubectl"
VERSION = read_version(MAIN_PACKAGE)
DESCRIPTION = "Kubectl wrapper in Python with OAuth token auth"
LICENSE = "Apache License 2.0"
AUTHOR = "Team Teapot"
EMAIL = "team-teapot@zalando.de"

# Add here all kinds of additional classifiers as defined under
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    "Environment :: Console",
    "Development Status :: 4 - Beta",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: CPython",
    "Operating System :: POSIX :: Linux",
    "Operating System :: MacOS :: MacOS X",
    "License :: OSI Approved :: Apache Software License",
]

CONSOLE_SCRIPTS = ["zkubectl = zalando_kubectl.main:main"]


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split("\\n") if req != ""]


def read(fname):
    return open(os.path.join(__location__, fname), encoding="utf-8").read()


def setup_package():
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=read("README.rst"),
        author=AUTHOR,
        author_email=EMAIL,
        license=LICENSE,
        keywords="kubectl kubernetes",
        classifiers=CLASSIFIERS,
        packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
        install_requires=get_install_requirements("requirements.txt"),
        setup_requires=[],
        include_package_data=True,
        entry_points={"console_scripts": CONSOLE_SCRIPTS},
    )


if __name__ == "__main__":
    setup_package()
