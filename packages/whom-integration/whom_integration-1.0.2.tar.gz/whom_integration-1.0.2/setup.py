#!/usr/bin/env python3
"""
Setup script for Whom Integration Library
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="whom-integration",
    version="1.0.2",
    author="Doc9",
    author_email="cloud@doc9.com.br",
    description="Python library for Whom API integration, supporting multiple systems and web automation drivers",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/doc9/whom-integration",
    project_urls={
        "Bug Tracker": "https://github.com/doc9/whom-integration/issues",
        "Documentation": "https://github.com/doc9/whom-integration#readme",
        "Source Code": "https://github.com/doc9/whom-integration",
    },
    packages=find_packages(include=["app", "app.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "selenium": [
            "selenium>=4.0.0",
            "webdriver-manager>=3.8.0",
        ],
        "playwright": [
            "playwright>=1.30.0",
            "patchright>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "whom-integration=app.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "whom",
        "api",
        "integration",
        "automation",
        "selenium",
        "playwright",
        "ecac",
        "pje",
        "receita-federal",
        "judiciary",
        "web-scraping",
        "browser-automation",
    ],
) 
