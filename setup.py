#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, Extension
import os


with open('README.md', "r") as file:
    long_description = file.read()


setup(
    name='concurrent_helper',
    version='1.0.1',
    description='The Simplest and Most Powerful Concurrent Helper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Chuanqi Tan',
    author_email='chuanqi.tan@gmail.com',
    url='https://github.com/ChuanqiTan/concurrent_helper',
    license='MIT',
    keywords='concurrent run_with_message_queue run_with_concurrent multithread multiprocess',
    packages=[
        'concurrent_helper',
    ],
)
