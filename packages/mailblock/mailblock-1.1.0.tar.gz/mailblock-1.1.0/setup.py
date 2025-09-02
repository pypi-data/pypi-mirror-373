#!/usr/bin/env python3
"""
MailBlock Python SDK Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mailblock",
    version="1.1.0",
    author="MailBlock",
    author_email="support@mailblock.com",
    description="Official Python SDK for MailBlock email service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/5ysc4ll/mailblock-python",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "isort>=5.10.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/5ysc4ll/mailblock-python/issues",
        "Source": "https://github.com/5ysc4ll/mailblock-python",
        "Documentation": "https://docs.mailblock.com/python",
    },
)