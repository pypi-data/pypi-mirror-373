import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thin_osm_api_wrapper",
    version="0.0.5",
    author="Mateusz Konieczny",
    description="thin wrapper of https://wiki.openstreetmap.org/wiki/API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matkoniecz/thin_osm_api_python_wrapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # for dependencies syntax see https://python-packaging.readthedocs.io/en/latest/dependencies.html
) 
