#!/usr/bin/env python

from setuptools import setup, find_packages


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name="swiggy_analytics",
    version="1.1",
    description="A CLI for fetching past orders from Swiggy and performing basic stats in the terminal",
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
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
