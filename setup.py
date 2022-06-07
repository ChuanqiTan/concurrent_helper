#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, Extension
import os


this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


setup(
    name='concurrent_helper',
    version='0.12',
    description='Very simple and powerfull concurrent helper.',
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
