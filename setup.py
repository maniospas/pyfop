# python setup.py sdist bdist_wheel
# twine upload dist/*

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pyfop",
    version="0.0.2",
    author="Emmanouil Krasanakis",
    author_email="maniospas@hotmail.com",
    description=("A novel forward-oriented programming paradigm for Python."),
    license="Apache 2.0",
    keywords="metaprogramming, component-based programming, software as a service",
    url="https://github.com/maniospas/pyfop",
    packages=['pyfop', 'tests'],
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)