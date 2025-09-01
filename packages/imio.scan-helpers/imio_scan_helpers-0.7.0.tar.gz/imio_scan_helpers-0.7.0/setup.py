# setup.py
from imio.scan_helpers.config import get_current_version
from setuptools import find_packages
from setuptools import setup

import os


setup(
    name="imio.scan_helpers",
    version=get_current_version(),
    description="Various script files to handle local scan tool",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    author="Stephan Geulette (IMIO)",
    author_email="support@imio.be",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/imio.scan_helpers",
        "Source": "https://github.com/IMIO/imio.scan_helpers",
    },
    license="GPL version 3",
    keywords="Scan Windows",
    packages=find_packages(exclude=["ez_setup"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.12",
    install_requires=[
        "pyinstaller",
        "requests",
    ],
)
