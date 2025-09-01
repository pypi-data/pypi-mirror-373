#!/usr/bin/env python3
"""
Setup script for Clyrdia CLI
"""

from setuptools import setup, find_packages
import os

# Read the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="clyrdia-cli",
    version="1.1.5",
    description="Zero-Knowledge AI Benchmarking Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Clyrdia Team",
    author_email="team@clyrdia.com",
    url="https://clyrdia.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    py_modules=["clyrdia_cli"],
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "aiohttp>=3.8.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "psutil>=5.8.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.0",
        "plotly>=5.0.0"
    ],
    entry_points={
        'console_scripts': [
            'clyrdia-cli=clyrdia_cli:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["ai", "benchmarking", "machine learning", "testing", "evaluation", "openai", "anthropic"],
)

