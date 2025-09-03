#!/usr/bin/env python3
"""
setup.py for pdf-font-checker package.
This is primarily for backward compatibility - the main configuration
is in pyproject.toml following modern Python packaging standards.
"""

from setuptools import setup, find_packages
import os

# Read the long description from README.md
def read_long_description():
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="pdf-font-checker",
    version="0.1.0",
    description="Tiny helper that lists fonts used in a PDF via MuPDF (mutool).",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    url="https://example.com/pdf-font-checker",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "pdf-font-checker=pdf_font_checker.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Utilities",
    ],
    keywords="pdf fonts mutool mupdf font-detection typography",
    project_urls={
        "Bug Reports": "https://github.com/genie360s/pdf-font-checker/issues",
        "Source": "https://github.com/genie360s/pdf-font-checker",
    },
)
