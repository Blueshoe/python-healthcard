# -*- coding: utf-8 -*-
from setuptools import setup
from healthcard import __version__

try: # for pip >= 10
   from pip._internal.req import parse_requirements
   from pip._internal import main
except ImportError: # for pip <= 9.0.3
   from pip.req import parse_requirements
   from pip import main


install_reqs = parse_requirements("requirements.txt", session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(name='pythonhealthcard',
      version=__version__,
      description='A module to read german health insurance cards with python',
      url='https://gitlab.blueshoe.de/Blueshoe/python-healthcard/',
      author='Blueshoe',
      author_email='robert@blueshoe.de',
      license='MIT',
      packages=['healthcard'],
      install_requires=reqs,
      zip_safe=False
)
