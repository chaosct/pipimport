import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pipimport",
    version = "0.1",
    author = "Carles F. Julia",
    author_email = "carles@fjulia.name",
    description = ("Automatically install missing modules using pip at import time.",
                    "Best used with virtualenv."),
    license = "MIT",
    keywords = "pip virtualenv import hook",
    url = "https://github.com/chaosct/pipimport",
    packages=['pipimport'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Software Distribution",
        "License :: OSI Approved :: MIT License",
    ],
)