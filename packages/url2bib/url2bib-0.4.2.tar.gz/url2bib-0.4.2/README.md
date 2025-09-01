# URL to BibTeX Converter (url2bib)

`url2bib` is a commandline tool for converting URLs of papers into into BibTeX citations. It tries to use the publication information rather than the arXiv url.

![screenshot.png](screenshot.png)

## Installation
```bash
pip install url2bib
```

## Using as a Commandline Tool
```bash
url2bib https://arxiv.org/abs/2006.11477
```

## Using as a Library
You can also use `url2bib` as a Python library with several key functions:

```python
from url2bib import url2bibtex, doi2bibtex, isbn2bibtex, parse_bibtex

# Convert a URL to BibTeX
bibtex: str = url2bibtex('https://arxiv.org/abs/2006.11477')

# Convert a DOI to BibTeX
bibtex: str = doi2bibtex('10.1145/3447548.3467160')

# Convert an ISBN to BibTeX
bibtex: str = isbn2bibtex('9780123456789')

# Parse a BibTeX string into a dictionary
bib_dict: dict = parse_bibtex(bibtex)
```

### Additional Library Features
- `set_verbosity(True)`: Enable verbose logging
- `get_dblp_bibtexs(paper_title)`: Search for publications on DBLP

## Features
- Extracts DOIs from URLs and retrieves BibTeX citations for those DOIs.
- Searches for publications of the paper.
- Generates a BibTeX entry with a unified ID in the format `{firstAuthorSurname}_{year}_{titleFirstWord}`.

## Contributing
Contributions to this project are welcome. If you have any suggestions or want to report issues, please open an issue or submit a pull request.

## License
This project is under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0) license.

## Acknowledgments
This script uses the `bibtexparser` library for parsing and generating BibTeX entries.
It also relies on external data sources such as doi.org and dblp.org to fetch BibTeX entries.

## Disclaimer
This script is provided as-is, and the accuracy of the generated BibTeX entries depends on the availability and quality of external data sources. Always double-check and edit citations as needed for your research papers and publications.

Happy citing with `url2bib`!
