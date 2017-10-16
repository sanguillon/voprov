#!/usr/local/Plone/Python-2.7/bin/python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'python-dateutil',
    'networkx',
    'lxml',
    'six>=1.9.0',
    'rdflib>=4.2.1'
]

test_requirements = [
    'pydotplus'
]

setup(
    name='voprov',
    version='1.5.0',
    description='A library for IVOA Provenance Data Model supporting PROV-JSON, '
                'PROV-XML and PROV-O (RDF)',
    long_description=readme + '\n\n' + history,
    author='Michele Sanguillon',
    author_email='michele.sanguillon@umontpellier.fr',
    url='https://github.com/sanguillon/voprov',
    packages=find_packages(),
    package_dir={
        'voprov': 'voprov'
    },
    scripts=['scripts/voprov-convert', 'scripts/voprov-compare'],
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'dot': ['pydotplus'],
    },
    license="MIT",
    zip_safe=False,
    keywords=[
        'provenance', 'graph', 'model', 'PROV', 'PROV-DM', 'PROV-JSON', 'JSON',
        'PROV-XML', 'PROV-N', 'PROV-O', 'RDF'
    ],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Security',
        'Topic :: System :: Logging',
    ],
    test_suite='voprov.tests',
    tests_require=test_requirements
)
