"""
Avachain - A lightweight AI agent library.

This setup script configures the package for distribution and installation.
It includes all necessary dependencies, metadata, and classifiers for PyPI.
"""

import os

from setuptools import find_packages, setup


# Read the README file for the long description
def read_long_description():
    """Read the README.md file for the package long description."""
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "A lightweight, efficient library for creating and running AI agents with tools."


setup(
    name="avachain",
    version="2.0.9",
    author="Salo Soja Edwin",
    author_email="salosoja@gmail.com",
    description="A lightweight library for creating and running AI agents with tools, supporting OpenAI-compatible APIs",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/OnlinePage/Avachain",
    project_urls={
        "Bug Reports": "https://github.com/OnlinePage/Avachain/issues",
        "Source": "https://github.com/OnlinePage/Avachain",
        "Documentation": "https://github.com/OnlinePage/Avachain#readme",
    },
    packages=find_packages(),
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        # Topic
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        # License
        "License :: OSI Approved :: MIT License",
        # Programming Language Support
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # Operating System
        "Operating System :: OS Independent",
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    keywords=[
        "ai",
        "agent",
        "llm",
        "openai",
        "tools",
        "chatbot",
        "automation",
        "artificial-intelligence",
        "machine-learning",
        "nlp",
        "conversational-ai",
        "function-calling",
        "streaming",
        "claude",
        "mistral",
        "gpt",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies with version specifications
        "pydantic>=2.6.1,<3.0.0",
        "requests>=2.31.0,<3.0.0",
        "tokenizers>=0.19.1,<1.0.0",
        "openai>=1.63.0,<2.0.0",
        "numpy>=1.21.0",
        "print-color>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=22.0.0",
            "isort[colors]>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
            "colorama>=0.4.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.17.0",
        ],
        "examples": [
            "jupyter>=1.0.0",
            "matplotlib>=3.5.0",
            "pandas>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [],
    },
    include_package_data=True,
    license="MIT",
    zip_safe=False,  # Set to False to ensure proper installation of package data
)
