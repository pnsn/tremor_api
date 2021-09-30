from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="TremorApi",
    version="1.0.",
    author="Kyla Marczewski",
    author_email="marczk@uw.edu",
    description="A simple API to return GeoJSON tremor data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnsn/tremor_api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
