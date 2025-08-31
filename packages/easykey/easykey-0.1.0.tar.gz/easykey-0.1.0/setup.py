#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file for the long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python wrapper for the easykey CLI - secure keychain access made easy."

setup(
    name="easykey",
    version="0.1.0",
    author="KingOfMac",
    author_email="",
    description="Python wrapper for the easykey CLI - secure keychain access",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/kingofmac/easykey",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    keywords="keychain, security, secrets, macOS, CLI, wrapper",
    project_urls={
        "Bug Reports": "https://github.com/kingofmac/easykey/issues",
        "Source": "https://github.com/kingofmac/easykey",
    },
    entry_points={
        # No CLI entry points - this is a library wrapper
    },
    include_package_data=True,
    zip_safe=False,
)
