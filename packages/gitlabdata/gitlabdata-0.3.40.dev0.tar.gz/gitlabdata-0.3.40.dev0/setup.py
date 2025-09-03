#!/usr/bin/env python
import pathlib
import pkg_resources
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name="gitlabdata",
    version="0.3.40.dev0",
    author="GitLab Data Team",
    author_email="data@gitlab.com",
    description="GitLab Data Utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gitlab-data/gitlab-data-utils",
    packages=find_packages(),
    install_requires=requirements,
)
