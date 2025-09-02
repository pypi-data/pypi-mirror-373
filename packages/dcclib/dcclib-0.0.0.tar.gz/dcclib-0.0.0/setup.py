
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# invalid email
# download url
# url
# project urls

setup(
    name ="dcclib",
    packages=[".",],
    version='0.0.0',
    description="This name has been reserved using Reserver",
    long_description="""
## Overview
dcclib is a Python library for doing awesome things.
This name has been reserved using [Reserver](https://github.com/openscilab/reserver).
""",
    long_description_content_type='text/markdown',
    author="Development Team",
    author_email="test@test.com",
    url="https://url.com",
    download_url="https://download_url.com",
    keywords="python3 python reserve reserver reserved",
    project_urls={
            'Source':"https://github.com/source",
    },
    install_requires="",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    license="MIT",
)

