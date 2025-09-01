"""Setup script for PYYql."""

import os
from setuptools import setup, find_packages

# Read version from version.py
version = {}
with open(os.path.join("pyyql", "version.py")) as f:
    exec(f.read(), version)

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pyyql",
    version=version["__version__"],
    author="Your Name",
    author_email="your.email@example.com",
    description="Declarative PySpark SQL Engine using YAML configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyyql",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pyyql/issues",
        "Documentation": "https://pyyql.readthedocs.io",
        "Source Code": "https://github.com/yourusername/pyyql",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Engineers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
        "docs": [
            "mkdocs>=1.2",
            "mkdocs-material>=7.0",
            "mkdocstrings>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyyql=pyyql.cli:main",  # Optional CLI interface
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="pyspark sql yaml declarative data-engineering etl",
)