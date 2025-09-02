# -*- coding: utf-8 -*-

# Setup module for the Data Manager Job Decoder module
#
# April 2022

import os
import setuptools


# Pull in the essential run-time requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

# Use the README.rst as the long description.
with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="im-data-manager-job-decoder",
    version=os.environ.get("GITHUB_REF_SLUG", "1.0.0"),
    author="Alan Christie",
    author_email="achristie@informaticsmatters.com",
    url="https://github.com/informaticsmatters/squonk2-data-manager-job-decoder",
    license="MIT",
    description="Job decoding logic",
    long_description=long_description,
    keywords="jinja2 decoder",
    platforms=["any"],
    python_requires=">=3.10",
    # Our modules to package
    packages=["decoder"],
    include_package_data=True,
    # Project classification:
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=requirements,
    zip_safe=False,
)
