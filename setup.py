import codecs
import os.path

import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


requires = [
    "shapely",
    "pyshp",
    "folium",
    "branca",
    "requests",
    "us",
]

long_description = read("README.md")

setuptools.setup(
    name="bbd",
    version=get_version("src/bbd/__init__.py"),
    author="Bluebonnet Data",
    author_email="info@bluebonnetdata.org",
    description="A toolset for political campaign data analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.bluebonnetdata.org/",
    package_dir={"": "src"},
    packages=setuptools.find_packages(
        where="src",
        exclude=["docs", "tests*"],
    ),
    install_requires=requires,
    extras_require={"dev": ["flake8", "black"]},
    tests_require=["pytest"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    project_urls={"Source": "https://github.com/bluebonnet-data/bbd"},
)
