# setuptools version 80.8.0
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    version="0.1.2",
    name="lt-utils",
    description="Collection of utilities for file, type, and basic logic handling across Python projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gr1336/lt-utils/",
    install_requires=[
        "numpy>=1.26.4",
        "markdown2",
        "markdownify",
        "pyperclip>=1.8.2",
        "textblob>=0.18.0",
        "pyyaml>=6.0.0",
        "nltk==3.9.*",
        "scikit-learn>=1.4.0",
        "spacy>3.5,<4",
        "numba>=0.60.0,<0.70",
        "pandas",
        "plotly",
    ],
    author="gr1336",
    license="Apache Software License (Apache-2.0)",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
)
