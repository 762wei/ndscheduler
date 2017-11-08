#! /usr/bin/env python
# coding=utf-8
from setuptools import setup, find_packages
import sys
import os

if __name__ == '__main__':
    sys.argv.append('install')


pkg_name = 'ndscheduler'

setup(name=pkg_name,
      version='1.0',
      packages=find_packages(),
      include_package_data=True
      )

os.system('pause')