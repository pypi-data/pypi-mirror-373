#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter

import bibtexparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from . import venues

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"

verbose = False


def set_verbosity(verbose_: bool) -> None:
    global verbose
    verbose = verbose_


def maybeprint(*args, **kwargs) -> None:
    """
    Print a message only if verbose mode is enabled.
    """
    if verbose:
        print(*args, **kwargs)


def parse_bibtex(bibtex: str) -> dict:
    """Parse a BibTeX string into a dictionary."""
    if bibtex is None:
        return dict()
    return bibtexparser.loads(bibtex).entries[0]


def build_bibtex(bibdict: dict) -> str:
    """Convert a bibliography dictionary into a BibTeX string."""
    new_lib = bibtexparser.bibdatabase.BibDatabase()
    new_lib.entries = [bibdict]
    return bibtexparser.dumps(new_lib)


def create_bib_id(bibdict: dict) -> str:
    """Create a BibTeX ID from a bibliography dictionary."""
    # Extract first author
    if "author" in bibdict:
        authors = bibdict["author"].replace("\n", " ").split("and")
        first_author_fullname = authors[0].strip()
        if "," in first_author_fullname:
            first_author_surname = first_author_fullname.split(",")[0].strip()
        elif " " in first_author_fullname:
            first_author_surname = first_author_fullname.split(" ")[-1].strip()
        else:
            first_author_surname = first_author_fullname.strip()
    else:
        maybeprint("\033[93mWARNING: No author found in BibTeX entry\033[0m")
        first_author_surname = "Unk"

    # Clean first author surname
    first_author_surname = re.sub(r"[^\w-]", "", first_author_surname)
    first_author_surname = re.split(r"-| ", first_author_surname)
    first_author_surname = list(filter(None, first_author_surname))
    first_author_surname = first_author_surname[-1]

    if "year" in bibdict:
        year = bibdict["year"]
    else:
        maybeprint("\033[93mWARNING: No year found in BibTeX entry\033[0m")
        year = "0000"
    title_firstword = [word for word in bibdict["title"].split(" ") if len(word) > 3][0]
    title_firstword = re.sub(r"[^\w-]", "", title_firstword)
    bib_id = f"{first_author_surname.lower()}_{year}_{title_firstword.lower()}"
    return bib_id


def preprocess_url(url: str) -> str:
    """Preprocess and normalize a URL."""
    url = url.strip()

    # Normalize arxiv URLs
    if re.match(r"https://arxiv\.org/pdf/[\d\.]+", url):
        url = url.replace("/pdf/", "/abs/").rstrip(".pdf")
    return url


def dois_from_html(html_content: str) -> list:
    """Extract DOIs from HTML content."""
    doi_pattern = r"(10.\d+/[^\s\>\"\<]+)"
    dois = re.findall(doi_pattern, html_content)
    dois = [re.split(r"[^0-9a-zA-Z\-./+_\(\)]", doi)[0] for doi in dois]
    return dois


def count_strings_in_list(strings_list: list[str]) -> dict:
    """Count occurrences of strings in a list."""
    string_counts = Counter(strings_list)
    return dict(string_counts)


def doi_from_html(html_content: str) -> str:
    """Extract the most common DOI from HTML content."""
    dois = dois_from_html(html_content)
    if len(dois) == 0:
        return None

    dois_counted = count_strings_in_list(dois)
    most_common_doi, most_common_count = max(dois_counted.items(), key=lambda x: x[1])

    maybeprint(f"DOI found: {most_common_doi}")
    return most_common_doi


def isbn_from_html(html: str) -> str:
    """Extract ISBN from HTML content."""
    # Remove whitespace and newlines
    html = " ".join(html.split())

    # Try to find ISBN-13
    isbn_pattern = (
        r"(?:ISBN[- ]?13|ISBN)?[:]?\s*(?=[0-9]{13}|(?=(?:[0-9]+[- ]){4})[0-9-]{17})97[89][- ]?(?:[0-9]{1}[- ]?){9}[0-9]"
    )
    match = re.search(isbn_pattern, html, re.I)

    if match:
        isbn = match.group()
        # Keep only numbers
        isbn = re.sub(r"[^0-9]", "", isbn)
        maybeprint(f"ISBN found: {isbn}")
        return isbn

    # If ISBN-13 not found, try ISBN-10
    isbn_pattern = (
        r"(?:ISBN[- ]?10|ISBN)?[:]?\s*(?=[0-9]{10}|(?=(?:[0-9]+[- ]){3})[0-9-]{13})[0-9][- ]?(?:[0-9]{1}[- ]?){8}[0-9X]"
    )
    match = re.search(isbn_pattern, html, re.I)

    if match:
        isbn = match.group()
        # Keep only numbers and X
        isbn = re.sub(r"[^0-9X]", "", isbn)
        maybeprint(f"ISBN found: {isbn}")
        return isbn

    return None


def doi2bibtex(doi: str) -> str:
    """Convert a DOI to BibTeX format."""
    url = f"https://doi.org/{doi}"
    headers = {"Accept": "application/x-bibtex", "User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.text
    return None


def isbn2bibtex(isbn: str) -> str:
    """Convert an ISBN to BibTeX format."""
    url = f"https://www.ebook.de/{isbn}"
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code == 200:
        return r.text  # This needs to be implemented properly
    return None


def url2bibtex(url: str) -> str:
    """Convert a URL to BibTeX.

    When use_dblp is True, try DBLP title search first and prefer
    non-CoRR / non-arXiv entries before falling back to DOI / ISBN.
    """
    url = preprocess_url(url)
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(url, headers=headers, verify=False)
        if r.status_code != 200:
            return None

        html_text = r.text

        # ——— Try DOI —————————————————————————————————————————————
        doi = doi_from_html(html_text)
        if doi:
            return doi2bibtex(doi)

        # ——— Try ISBN ————————————————————————————————————————————
        isbn = isbn_from_html(html_text)
        if isbn:
            return isbn2bibtex(isbn)

    except Exception as e:
        maybeprint(f"Error processing URL: {str(e)}")
    return None


def get_dblp_bibtexs(paper_title: str) -> list:
    """Search for publications on DBLP and return their BibTeX entries."""
    # Prepare the search URL
    search_url = f"https://dblp.org/search/publ/api?q={urllib.parse.quote(paper_title)}&format=xml"

    try:
        # Make the request
        response = requests.get(search_url)
        response.raise_for_status()

        # Parse the XML response
        root = ET.fromstring(response.content)

        # Extract hit elements
        hits = root.findall(".//hit")
        bibtexs = []
        for hit in hits:
            info = hit.find("info")
            if info is None:
                continue

            doi_element = info.find("doi")
            venue_element = info.find("venue")

            # Get bibtex via DOI if available
            if doi_element is not None and doi_element.text:
                bibtex = doi2bibtex(doi_element.text)
                if bibtex:
                    bibtexs.append(bibtex)
                    continue

            # Otherwise try to get bibtex via venue (e.g. neurips has no doi)
            elif venue_element is not None and venue_element.text.lower() in venues.venue_funcs:
                url_element = info.find("ee")
                if url_element is not None:
                    bibtex = venues.venue_funcs[venue_element.text.lower()](url_element.text)
                    if bibtex:
                        print(f"Got bibtex from venue: {url_element.text}\n")
                        bibtexs.append(bibtex)
                        continue

            # Otherwise get bibtex from DBLP
            else:
                dblp_url = info.find("url")
                if dblp_url is not None:
                    dblp_bib_url = dblp_url.text.split(".html")[0] + ".bib"
                    print(f"Got bibtex from DBLP: {dblp_bib_url}\n")
                    req = requests.get(dblp_bib_url)
                    if not req.ok:
                        continue
                    bibtex = req.text
                    bibtexs.append(bibtex)
                    continue

        return bibtexs
    except Exception as e:
        maybeprint(f"Error searching DBLP: {str(e)}")
        return []
