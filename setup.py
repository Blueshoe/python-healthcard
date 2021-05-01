# -*- coding: utf-8 -*-
from setuptools import setup
from healthcard import __version__

setup(
    name="python-healthcard",
    version=__version__,
    description="A module to read german health insurance cards with python",
    url="https://gitlab.blueshoe.de/Blueshoe/python-healthcard/",
    author="Blueshoe",
    author_email="robert@blueshoe.de",
    license="MIT",
    packages=["healthcard"],
    install_requires=["pyscard==1.9.6", "lxml==4.6.3"],
    zip_safe=False,
)
