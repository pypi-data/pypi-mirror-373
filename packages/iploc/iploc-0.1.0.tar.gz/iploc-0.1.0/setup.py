from setuptools import setup, find_packages

setup(
    name="iploc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.30.0",
    ],
    python_requires=">=3.8",
    description="Python client for IP lookup",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ip-loc-dev",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
