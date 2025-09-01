# setup.py

from setuptools import setup, find_packages

setup(
    name="uhd_client",
    version="0.1.0",
    author="Your Name", # Feel free to change this
    description="A Python client for the Universal Hybrid Database (UHD)",
    long_description="A simple, intuitive client for interacting with a UHD server, handling SQL, NoSQL, Graph, and Vector operations.",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)