#!/usr/bin/env python3
import os
import setuptools


def read_file(filename) -> str:
    """
    Return the content of a file.
    """

    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def scripts() -> list:
    """
    Return list of scripts in scripts/ file

    :return: List of scripts.
    :rtype: list
    """

    scripts_list = os.listdir(os.curdir + "/scripts/")
    result = []
    for file in scripts_list:
        result = result + ["scripts/" + file]
    return result


setuptools.setup(
    name="qecore",
    version="4.0",
    author="Michal Odehnal",
    author_email="modehnal@redhat.com",
    license="GPLv3",
    url="https://gitlab.com/dogtail/qecore",
    description="DesktopQE Tool for unified test execution",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    scripts=scripts(),
    install_requires=[
        "behave>=1.3.0",
        "behave-html-formatter<=0.9.10",
        "behave-html-pretty-formatter",
        "dasbus<=1.7",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Testing :: BDD",
    ],
    python_requires=">=3.6",
    options={
        "build_scripts": {
            "executable": "/usr/bin/python3",
        }
    },
)
