#!/usr/bin/env python3
# type: ignore

from setuptools import setup, find_packages

setup(
    name="reproducible",
    version="0.0.1",
    description="Reproducible archive generator",
    author="Will Rouesnel <wrouesnel@wrouesnel.com>",
    py_modules=find_packages("."),
    setup_requires=[],
    install_requires=[],
    include_package_data=False,
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "reproducible=reproducible.__main__:main",
        ],
    },
)
