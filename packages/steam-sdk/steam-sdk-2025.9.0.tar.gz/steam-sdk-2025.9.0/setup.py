from setuptools import setup
from setuptools import find_packages

with open("Readme.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

docs_require = [
    "Markdown==3.8",
    "markdown-include==0.8.1",
    "MarkupSafe==2.1.5",
    "mkdocs==1.6.1",
    "mkdocs-autorefs==1.4.1",
    "mkdocs-git-revision-date-localized-plugin==1.4.5",
    "mkdocs-include-markdown-plugin==7.1.5",
    "mkdocs-material==9.6.14",
    "mkdocs-material-extensions==1.3.1",
    "mkdocstrings==0.29.0",
    "mkdocstrings-python==1.16.10",
    "Pygments==2.17.2",
    "pymdown-extensions==10.7.1",
]

tests_require = [
    "coverage==7.4.3",
    "coverage-badge==1.1.0",
    "griffe==1.7.3",
    "pytest==8.1.1",
    "pytest-cov==4.1.0",
]

build_require = ["setuptools==69.2.0",
                 "twine==6.1.0"]

all_requirements = required + docs_require + tests_require + build_require

setup(
    name="steam-sdk",
    version="2025.9.0",
    author="STEAM Team",
    author_email="steam-team@cern.ch",
    description="Source code for APIs for STEAM tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/steam/steam_sdk",
    keywords={"STEAM", "API", "SDK", "CERN"},
    install_requires=required,
    extras_require={
        "all": all_requirements,
        "docs": docs_require,
        "test": tests_require,
        "build": build_require,
    },
    python_requires=">=3.11",
    include_package_data=True,
    packages=find_packages(),
    classifiers=["Programming Language :: Python :: 3.11"],
)
