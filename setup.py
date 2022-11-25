# python setup.py sdist bdist_wheel
# twine upload dist/*

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()\
        .replace(":brain: ", "").replace(":brain: ", "").replace(":hammer_and_wrench: ", "")\
        .replace(":fire: ", "").replace(":zap: ", "")


setup(
    name="pyfop",
    version="0.2.2",
    author="Emmanouil Krasanakis",
    author_email="maniospas@hotmail.com",
    description=("A forward-oriented programming paradigm for Python."),
    license="Apache 2.0",
    keywords="metaprogramming, component-based programming, software as a service",
    url="https://github.com/maniospas/pyfop",
    packages=['pyfop', 'tests'],
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    install_requires=['makefun'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
)