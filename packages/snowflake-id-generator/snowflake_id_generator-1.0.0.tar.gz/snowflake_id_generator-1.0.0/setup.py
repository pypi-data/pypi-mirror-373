#!/usr/bin/env python3
"""
简化的雪花算法ID生成器包安装脚本
"""

from setuptools import setup, find_packages

setup(
    name="snowflake-id-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="分布式雪花算法ID生成器",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/snowflake-id-generator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.7",
    install_requires=[],
    keywords="snowflake, id, generator, distributed, unique, uuid",
    license="MIT",
)
