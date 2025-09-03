from setuptools import setup, find_packages
import os


version = "1.26.4"

setup(
    name="numpy-lite",
    version=version,
    description="Ultra-light minimal NumPy build (core functionality only) for AWS Lambda / serverless.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="JacquieAM", 
    url="https://github.com/JacquieAM/numpy-lite",
    packages=find_packages(include=["numpy", "numpy.*"]),
    include_package_data=True,  
    install_requires=[
      
    ],
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)