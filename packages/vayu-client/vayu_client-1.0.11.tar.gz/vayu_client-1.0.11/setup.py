import os

from setuptools import find_packages, setup

from vayu_sdk import __version__


def read_requirements():
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt') as req:
            requirements = req.read().splitlines()
    return requirements

setup(
    name="vayu-client",
    version=__version__,
    packages=find_packages(),
    install_requires=read_requirements(),
    python_requires=">=3.7",
    description="The Vayu API client library in Python",
    author="Vayu Team",
    author_email="team@withvayu.com",
    url="https://github.com/weft-finance/vayu-py",
)