"""
Setup configuration for TokenRouter SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tokenrouter",
    version="1.0.1",
    author="TokenRouter Team",
    author_email="support@tokenrouter.io",
    description="Python SDK for TokenRouter - Intelligent LLM Routing API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tokenrouter/sdk-python",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.24.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/tokenrouter/sdk-python/issues",
        "Source": "https://github.com/tokenrouter/sdk-python",
        "Documentation": "https://docs.tokenrouter.io",
    },
)