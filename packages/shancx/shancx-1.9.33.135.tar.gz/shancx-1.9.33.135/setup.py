#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
setup(
    name="shancx",
    version="1.9.33.135",
    packages=find_packages(),
    description="A simple timer decorator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="shancx",
    author_email="your.email@example.com",
    url="https://gitee.com/shancx",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
    'tqdm',
    'pandas',
    'matplotlib'
    ],
)

 

 
 
 
 
 


          
