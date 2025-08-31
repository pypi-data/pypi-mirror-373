from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pytica",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.7.0",
        "openpyxl>=3.1.0"
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="you@example.com",
    description="Python Learning Analytics Toolkit for Teachers and Schools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bjaspel63/pytica",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
