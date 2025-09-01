from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="quadrant-gen",
    version="0.2.0",
    description="A library for creating quadrant charts with base64 output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Francesco",
    author_email="falanga.fra@gmail.com",  # Replace with your email
    url="https://github.com/ceccode/quadrant-gen",  # Replace with your repo URL
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords="quadrant, chart, visualization, matplotlib, csv",
    project_urls={
        "Bug Reports": "https://github.com/ceccode/quadrant-gen/issues",
        "Source": "https://github.com/ceccode/quadrant-gen",
    },
)
