"""
Setup script for the Antonnia Conversations Python SDK.

This is provided as an alternative to pyproject.toml for compatibility with older build systems.
"""

from setuptools import setup, find_namespace_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from conversations __init__.py
def read_version():
    here = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(here, "antonnia", "conversations", "__init__.py")
    
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    
    raise RuntimeError("Unable to find version string")

setup(
    name="antonnia-conversations",
    version=read_version(),
    author="Antonnia",
    author_email="support@antonnia.com",
    description="Python SDK for Antonnia Conversations API v2",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/antonnia/antonnia-python",
    project_urls={
        "Homepage": "https://antonnia.com",
        "Documentation": "https://docs.antonnia.com/conversations",
        "Bug Tracker": "https://github.com/antonnia/antonnia-python/issues",
    },
    packages=find_namespace_packages(include=["antonnia.*"]),
    package_data={
        "antonnia.conversations": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0,<1.0.0",
        "pydantic>=2.7.0,<3.0.0",
        "pytz>=2023.3",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-httpx>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
    },
    keywords=["antonnia", "conversations", "api", "chat", "messaging", "sdk"],
    zip_safe=False,
) 