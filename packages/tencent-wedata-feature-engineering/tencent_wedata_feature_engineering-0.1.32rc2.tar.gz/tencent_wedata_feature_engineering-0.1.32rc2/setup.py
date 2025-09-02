from setuptools import setup, find_packages
import os

# Dynamically read version from wedata/__init__.py
version = {}
with open(os.path.join(os.path.dirname(__file__), 'wedata', '__init__.py')) as f:
    exec(f.read(), version)

setup(
    name="tencent-wedata-feature-engineering",
    version=version["__version__"],
    packages=find_packages(include=['wedata', 'wedata.*']),
    install_requires=[
        'pandas>=1.0.0'
    ],
    python_requires='>=3.7',
    author="meahqian",
    author_email="",
    description="Wedata Feature Engineering Library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
