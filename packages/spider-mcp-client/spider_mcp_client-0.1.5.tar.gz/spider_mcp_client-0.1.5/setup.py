#!/usr/bin/env python3
"""
Setup script for spider-mcp-client
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from __init__.py
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'spider_mcp_client', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="spider-mcp-client",
    version=get_version(),
    author="Spider MCP Team",
    author_email="support@spider-mcp.com",
    description="Official Python client for Spider MCP web scraping API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/spider-mcp/spider-mcp-client",
    packages=find_packages(),
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
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
    },
    keywords="web scraping, spider, mcp, api client, html parsing, data extraction",
    project_urls={
        "Bug Reports": "https://github.com/spider-mcp/spider-mcp-client/issues",
        "Source": "https://github.com/spider-mcp/spider-mcp-client",
        "Documentation": "https://spider-mcp.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)
