# -*- coding: utf-8 -*-
import pathlib
from setuptools import setup
from healthcard import __version__

DIR = pathlib.Path(__file__).parent

README = (DIR / "README.rst").read_text()


setup(
    name="python-healthcard",
    version=__version__,
    description="A module to read german health insurance cards with python",
    url="https://github.com/Blueshoe/python-healthcard/",
    author="Blueshoe",
    author_email="robert@blueshoe.de",
    license="MIT",
    long_description=README,
    long_description_content_type="text/x-rst",
    packages=["healthcard"],
    install_requires=["pyscard==1.9.6", "lxml==4.6.5"],
    zip_safe=False,
)
