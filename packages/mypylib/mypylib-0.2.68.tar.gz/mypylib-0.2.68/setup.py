import os
import subprocess
import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

from mypylib import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()


class bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.universal = False
        self.plat_name_supplied = True
        self.plat_name = 'manylinux2014_x86_64'


setup(
    name='mypylib',
    version=__version__,
    url='https://github.com/williamchen180/mypylib',
    author='William Chen',
    author_email='williamchen180@gmail.com',
    description='Your package description',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    package_data={'mypylib': ['data/alert.wav']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pandas', 'termcolor', 'requests', 'plotly', 'setuptools', 'matplotlib', 'numpy',
        'playsound', 'wheel', 'twine', 'cryptocode', 'line_notify', 'shioaji', 'pandasql', 'msgpack',
        'xlrd', 'lxml'
    ],
)
