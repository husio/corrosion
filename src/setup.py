#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='corrosion',
    version='0.1',
    description='Python light thread toy framework',
    author='Piotr Husiatyński',
    author_email='phusiatynski@gmail.com',
    url='http://github.com/husio/corrosion/',
    download_url='http://github.com/husio/corrosion/',
    license='GPLv2',
    packages=find_packages(),
    include_package_data = True,
)

