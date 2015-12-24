#!/usr/bin/env python
from distutils.core import setup

# README = "/".join([os.path.dirname(__file__), "README.md"])

# with open(README) as file:
#        long_description = file.read()

setup(
    name='graphitesend',
    version='0.5.0',
    description='A simple interface for sending metrics to Graphite',
    author='Danny Lawrence',
    author_email='dannyla@linux.com',
    url='https://github.com/daniellawrence/graphitesend',
    # package_dir={'': ''},
    packages=['graphitesend'],
    long_description="https://github.com/daniellawrence/graphitesend",
    entry_points={
        'console_scripts': [
            'graphitesend = graphitesend.graphitesend:cli',
        ],
    },
    extras_require={
        'asynchronous': ['gevent>=1.0.0'],
    }
)
