#!/usr/bin/env python

from os import path

from setuptools import find_packages, setup


# read the contents of your README file
def read_readme():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name="swiggy_analytics",
    version="1.6",
    description="A CLI for fetching past orders from Swiggy and performing basic stats in the terminal",
    long_description=read_readme(),
    # long_description_content_type='text/markdown',
    author="Karan Sharma",
    author_email="karansharma1295@gmail.com",
    url="https://github.com/mr-karan/swiggy-analytics",
    install_requires=requirements(),
    include_package_data=True,
    packages=find_packages(),
    download_url="https://github.com/mr-karan/swiggy-analytics",
    license="MIT License",
    entry_points={
        'console_scripts': [
            'swiggy-analytics = swiggy_analytics.swiggy_analytics:main',
        ],
    },
    classifiers=[
        "Topic :: Utilities",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
