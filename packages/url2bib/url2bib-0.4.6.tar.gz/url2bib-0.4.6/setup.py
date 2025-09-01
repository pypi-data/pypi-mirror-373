import os

from setuptools import find_packages, setup

# Read version from version.py without importing
version_file = os.path.join(os.path.dirname(__file__), "url2bib", "version.py")
version_ns = {}
with open(version_file, "r") as f:
    exec(f.read(), version_ns)
__version__ = version_ns["__version__"]

readme = open("README.md", "r")
README_TEXT = readme.read()
readme.close()

setup(
    name="url2bib",
    version=__version__,
    packages=find_packages(),
    scripts=["url2bib/bin/url2bib"],
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    install_requires=["requests>=2.25.0", "bibtexparser>=1.2.0", "urllib3>=1.26.0", "beautifulsoup4>=4.9.0"],
    include_package_data=True,
    license="GNU General Public License v3 (GPLv3)",
    description="Convert URLs to BibTeX entries, with support for DOI and ISBN extraction",
    author="Paul Martin",
    author_email="p@ulmartin.com",
    keywords=["bibtex", "science", "scientific-journals", "crossref", "doi", "isbn"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Text Processing :: Markup :: LaTeX",
    ],
    python_requires=">=3.6",
    url="https://github.com/notpaulmartin/url2bib",
)
