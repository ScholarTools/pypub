import pytest

from ..scrapers import sciencedirect as sd
import requests
from bs4 import BeautifulSoup

# Sample journal article
link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'
pii = 'S0006899313013048'

# Retrieve soup of content and references from live site
s = requests.session()
r = s.get(link, cookies={'Site':'Mobile'})
soup = BeautifulSoup(r.text)
content = soup.find('div', {'id' : 'article-abstract'})
references = soup.find('ol', {'class' : 'article-references'})

# Run scraper on live site
entry = sd.get_entry_info(link)
refs = sd.get_references(pii)

# Load cached version of content and references
fc = open('sd_content.txt')
saved_content = fc.read()
fc.close()
fr = open('sd_references.txt')
saved_refs = fr.read()
fr.close()

#assert 0

# Testing return types
def test_entry_type():
    assert type(entry) is sd.ScienceDirectEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is sd.ScienceDirectRef


# Testing scraped soup against saved site version
def test_saved_content():
    assert str(content) == saved_content

def test_saved_refs():
    assert str(references) == saved_refs


