import pathlib
from setuptools import find_packages, setup

from hestia_earth.earth_engine.version import VERSION

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

REQUIRES = (HERE / "requirements.txt").read_text().splitlines()

# This call to setup() does all the work
setup(
    name='hestia_earth_earth_engine',
    version=VERSION,
    description="Hestia's earth engine.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hestia-earth/hestia-earth-engine",
    author="Hestia Team",
    author_email="guillaume@hestia.earth",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("tests", "scripts")),
    include_package_data=True,
    install_requires=REQUIRES,
    extras_require={
        "geopandas": ["shapely", "geopandas"]
    }
)
