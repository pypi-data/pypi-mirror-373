#!/usr/bin/env python
from setuptools import setup, find_packages
from codecs import open
import glob
import sys
import os


data_files = []
directories = glob.glob('xtls_client/dependencies/')
for directory in directories:
    files = glob.glob(directory+'*')
    data_files.append(('xtls_client/dependencies', files))

# 添加 tls_datas 目录中的指纹数据
tls_data_dirs = glob.glob('tls_datas/*/')
for directory in tls_data_dirs:
    subdirs = glob.glob(directory + '*/')
    for subdir in subdirs:
        files = glob.glob(subdir + '*.json')
        if files:
            relative_path = subdir.replace('\\', '/')
            data_files.append((relative_path, files))

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "xtls_client", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

with open("README.md", "r", "utf-8") as f:
    readme = f.read()

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    description=about["__description__"],
    license = "MIT",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*'],
        'tls_datas': ['**/*.json'],
    },
    data_files=data_files,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Source": "https://github.com/wang-zhibo/xtls-client",
    }
)