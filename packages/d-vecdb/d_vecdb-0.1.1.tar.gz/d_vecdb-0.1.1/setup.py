#!/usr/bin/env python3
"""
d-vecDB: High-Performance Vector Database
A comprehensive vector database system with Python API interface.
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

# Read requirements from python-client
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'python-client', 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        "httpx>=0.24.0",
        "grpcio>=1.50.0", 
        "grpcio-tools>=1.50.0",
        "protobuf>=4.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "numpy>=1.21.0",
    ]

setup(
    name="d-vecdb",
    version="0.1.1",
    author="Durai",
    author_email="durai@infinidatum.com",
    description="High-performance vector database written in Rust with Python client",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/rdmurugan/d-vecDB",
    packages=find_packages(where="python-client"),
    package_dir={"": "python-client"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
        "examples": [
            "jupyter>=1.0.0",
            "matplotlib>=3.5.0",
            "scikit-learn>=1.1.0",
            "pandas>=1.4.0",
        ],
        "server": [
            "uvicorn>=0.18.0",
            "fastapi>=0.95.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "d-vecdb=vectordb_client.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/rdmurugan/d-vecDB/issues",
        "Source": "https://github.com/rdmurugan/d-vecDB",
        "Documentation": "https://github.com/rdmurugan/d-vecDB#readme",
    },
    keywords="vector database, similarity search, machine learning, embeddings, HNSW, rust",
    include_package_data=True,
    zip_safe=False,
)