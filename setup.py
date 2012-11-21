import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "sqltext",
    version = "0.0.1",
    author = "John Isaac Stone",
    author_email = "jisaacstone@gmail.com",
    description = ("If you use raw SQL in your projects then this may help "
                   "make it a bit more flexible."),
    license = "MIT",
    keywords = "sql",
    url = "https://github.com/jisaacstone/sqltext.py",
    long_description=read('README.md'),
)
