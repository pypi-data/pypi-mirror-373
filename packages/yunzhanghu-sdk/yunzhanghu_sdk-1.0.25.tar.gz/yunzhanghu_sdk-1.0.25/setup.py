#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (C) 云账户
# All rights reserved.

"""
Setup script for log service SDK.
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from yunzhanghu_sdk import __version__

requirements = [
    "requests>=2.19.1",
    "pycryptodome==3.10.1",
]

packages = [
    "yunzhanghu_sdk",
    "yunzhanghu_sdk.client",
    "yunzhanghu_sdk.client.api",
    "yunzhanghu_sdk.client.api.model",
]

setup(
    name="yunzhanghu_sdk",
    version=__version__,
    description="云账户官方 SDK for Python",
    author="yunzhanghu",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=packages,
    long_description=open("云账户SDK-for-Python-pypi.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
