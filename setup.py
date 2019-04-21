"""Python installation definition for neolo"""
from setuptools import setup
from neolo import __version__

setup(
    name="neolo",
    version=__version__,
    description="Text Analysis Software",
    author="Joshua Crowgey",
    author_email="jcrowgey@uw.edu",
    url="https://github.com/jcrowgey/neolo",
    license="BSD",
    packages=["neolo"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.0",
    entry_points={"console_scripts": ["neolo = neolo.neolo:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Programming Language :: Python :: 3.5",
    ],
)
