#!/usr/bin/env python3
"""Setup script for commons-cli package."""

from setuptools import setup, find_packages

setup(
    name="commons-cli",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
