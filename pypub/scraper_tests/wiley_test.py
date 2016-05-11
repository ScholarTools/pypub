import pytest

from ..scrapers import wiley as wy
import requests
from bs4 import BeautifulSoup

# Sample journal article
link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
pii = '10.1002/biot.201400046'

# Retrieve soup of content and references from live site
s = requests.session()
r = s.get(link)
soup = BeautifulSoup(r.text)
content = soup.find('div', {'id' : 'mainContent'})
references = soup.find('div', {'class' : 'bibliography'})

# Run scraper on live site
entry = wy.get_entry_info(link)
refs = wy.get_references(pii)

# Load cached version of content and references
fc = open('wy_content.txt')
saved_content = fc.read()
fc.close()
fr = open('wy_references.txt')
saved_refs = fr.read()
fr.close()

#assert 0

# Testing return types
def test_entry_type():
    assert type(entry) is wy.WileyEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is wy.WileyRef


# Testing scraped soup against saved site version
def test_saved_content():
    assert str(content) == saved_content

def test_saved_refs():
    assert str(references) == saved_refs


