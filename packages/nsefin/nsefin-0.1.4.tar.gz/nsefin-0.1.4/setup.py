from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="nsefin",
    version="0.1.4",
    author="Vinod Bhadala",
    author_email="vinodbhadala@gmail.com",
    description="A Python library to download publicly available historical candlestick data from NSE India",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vbhadala/nsefin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
        "volg>=0.1.5"
    ],
    keywords="nse, stock market, financial data, india, trading, candlestick data",
)