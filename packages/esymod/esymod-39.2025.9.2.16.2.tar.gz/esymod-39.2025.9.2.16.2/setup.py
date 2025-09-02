# -*- coding:utf-8 -*-
import sys
sys.argv.append('sdist')
from distutils.core import setup
from setuptools import find_packages

setup(name='esymod',
            version='39.2025.9.2.16.2',
            packages=['esymod',],
            description='a python lib for project files',
            long_description='',
            author='Quanfa',
            include_package_data = True,
            author_email='quanfa@tju.edu.cn',
            url='http://www.xxxxx.com/',
            license='MIT',
            )

            