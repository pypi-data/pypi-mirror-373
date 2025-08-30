"""
Setup script for Distilled - Data stream reduction middleware
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="distilled",
    version="0.1.0",
    author="Distilled Team",
    author_email="team@distilled.dev",
    description="A data stream reduction middleware that maintains proportional representation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/distilled",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/distilled/issues",
        "Documentation": "https://github.com/yourusername/distilled#readme",
        "Source Code": "https://github.com/yourusername/distilled",
        "Changelog": "https://github.com/yourusername/distilled/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line scripts here if needed
        ],
    },
) 