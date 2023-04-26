#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

requirements = [
    'prov>=1.5.3',
]

test_requirements = [
    'pydot>=1.2.0'
]

setup(
    name='voprov',
    version='0.0.2',
    description='A library for IVOA Provenance Data Model supporting PROV-JSON, '
                'PROV-XML and PROV-N',
    long_description=readme,
    author='Jean-Francois Sornay',
    author_email='jeanfrancois.sornay@gmail.com',
    url='https://github.com/sanguillon/voprov/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'dot': ['pydot>=1.2.0'],
    },
    license="MIT",
    zip_safe=False,
    keywords=[
        'provenance', 'graph', 'model', 'VOPROV', 'provenance-dm', 'PROVENANCE-DM', 'PROV-JSON', 'JSON',
        'PROV-XML', 'PROV-N'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    tests_require=test_requirements,
    python_requires='>=2',
)
