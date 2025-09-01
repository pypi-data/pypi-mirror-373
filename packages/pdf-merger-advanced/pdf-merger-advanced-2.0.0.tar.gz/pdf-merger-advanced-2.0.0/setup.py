#!/usr/bin/env python3
"""
Setup script for PDF Merger Advanced
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pdf-merger-advanced",
    version="2.0.0",
    author="Gunjan Vaishnav",
    author_email="vaishnavgunjan786@gmail.com",  
    description="Modern PDF merger with dark mode, page ranges, and enhanced UI built with PyQt5",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Gunjan000/PDF-Merger-Advanced",
    packages=find_packages(),
    py_modules=["pdf_merger"],
    license="MIT",         
    license_files=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pdf-merger=pdf_merger:main",
        ],
        "gui_scripts": [
            "pdf-merger-gui=pdf_merger:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["assets/*.jpg", "*.md", "*.txt"],
    },
    keywords="pdf merger gui pyqt5 dark-mode page-ranges",
    project_urls={
        "Bug Reports": "https://github.com/Gunjan000/PDF-Merger-Advanced/issues",
        "Source": "https://github.com/Gunjan000/PDF-Merger-Advanced",
        "Documentation": "https://github.com/Gunjan000/PDF-Merger-Advanced#readme",
    },
) 