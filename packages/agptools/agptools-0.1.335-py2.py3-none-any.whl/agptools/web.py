from bs4 import BeautifulSoup


def html2text(raw: str) -> str:
    # Parse the HTML
    soup = BeautifulSoup(raw, "html.parser")

    # Extract all text from the HTML
    text = soup.get_text().strip()
    return text
