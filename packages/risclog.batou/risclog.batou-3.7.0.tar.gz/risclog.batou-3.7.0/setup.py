#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

setup(
    version='3.7.0',
    author='riscLOG Solution GmbH',
    author_email='info@risclog.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: German',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description='batou extensions used by risclog',
    install_requires=[
        'requirements-parser<0.3',
        'six',
        'batou>=2.3b5',
        'batou_ext>=2.4.27',
    ],
    extras_require={
        'docs': [
            'Sphinx',
        ],
        'test': [
            'pytest-cache',
            'pytest-cov',
            'pytest-flake8',
            'pytest-rerunfailures',
            'pytest-sugar',
            'pytest',
            'coverage',
            # https://github.com/PyCQA/flake8/issues/1419#issuecomment-947243876
            'flake8<4',
            'mock',
        ],
    },
    long_description=(open('README.rst').read()),
    include_package_data=True,
    keywords='risclog.batou',
    name='risclog.batou',
    packages=find_packages('src'),
    namespace_packages=['risclog'],
    package_dir={'': 'src'},
    url='https://github.com/risclog-solution/risclog.batou',
    zip_safe=False,
)
