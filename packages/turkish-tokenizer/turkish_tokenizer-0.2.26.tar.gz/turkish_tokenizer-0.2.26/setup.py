#!/usr/bin/env python3

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Turkish tokenizer"

setup(
    name="turkish-tokenizer",
    version="0.2.26",
    description="Turkish tokenizer for Turkish language processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="M. Ali Bayram",
    author_email="malibayram20@gmail.com",
    url="https://github.com/malibayram/turkish-tokenizer",
    packages=find_packages(include=["turkish_tokenizer", "turkish_tokenizer.*"]),
    package_data={
        "turkish_tokenizer": ["*.json"],
    },
    include_package_data=True,
    install_requires=[        
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.0",
            "black",
            "flake8",
            "mypy",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    keywords="tokenizer turkish nlp transformer language-model",
    license="MIT",
)
