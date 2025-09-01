from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

venue_funcs = {"neurips": lambda url: extract_neurips_bibtex(url)}
venues = list(venue_funcs.keys())


def extract_neurips_bibtex(url: str) -> str | None:
    # Get the neurips paper page
    response = requests.get(url)
    if not response.ok:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    bibtex_link = soup.find("a", href=lambda x: x and "/bibtex" in x)
    if not bibtex_link:
        return None

    # Convert relative URL to absolute URL
    bibtex_url = urljoin(url, bibtex_link["href"])

    # Fetch the bibtex content
    bibtex_response = requests.get(bibtex_url)
    if not bibtex_response.ok:
        return None

    return bibtex_response.text.strip()
