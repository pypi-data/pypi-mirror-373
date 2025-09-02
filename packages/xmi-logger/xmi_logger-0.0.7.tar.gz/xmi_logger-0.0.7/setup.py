#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author: gm.zhibo.wang
# E-mail: gm.zhibo.wang@gmail.com
# Date  :
# Desc  :

from setuptools import setup, find_packages
from codecs import open
import glob
import sys
import os


about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "xmi_logger", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'loguru==0.7.3',
        'requests',
        'aiohttp'
    ],
    project_urls={
        "Bug Reports": "https://github.com/wang-zhibo/xmi_logger/issues",
        "Source": "https://github.com/wang-zhibo/xmi_logger",
    },
)



