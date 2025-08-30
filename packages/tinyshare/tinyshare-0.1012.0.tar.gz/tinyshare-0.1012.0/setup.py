from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tinyshare",
    version="0.1012.0",
    author="TinyShare Team",
    author_email="support@tinyshare.com",
    description="A lightweight wrapper for tushare financial data API (Multi-Version Bytecode Protected)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tinyshare",
    packages=find_packages(),
    package_data={
        "tinyshare": ["*/*.pyc", "*.pyc"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tushare>=1.2.0",
        "pandas>=1.0.0",
        "requests>=2.20.0",
    ],
    keywords="finance, stock, data, tushare, api, protected, bytecode, multi-version",
    zip_safe=False,
)