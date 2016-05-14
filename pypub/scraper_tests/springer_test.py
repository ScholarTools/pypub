import pytest

from ..scrapers import springer as sp
import requests
from bs4 import BeautifulSoup

# Sample journal article
link = 'http://link.springer.com/article/10.1186/s12984-016-0150-9'
pii = '10.1186/s12984-016-0150-9'

# Retrieve soup of content and references from live site
s = requests.session()
r = s.get(link)
soup = BeautifulSoup(r.text)

content = soup.find('div', {'class' : 'ArticleHeader'})
references = soup.find('ol', {'class' : 'BibliographyWrapper'})

# Run scraper on live site
entry = sp.get_entry_info(link)
refs = sp.get_references(pii)

# Load cached version of content and references
fc = open('saved_sites/sp_content.txt')
saved_content = fc.read()
fc.close()
fr = open('saved_sites/sp_references.txt')
saved_refs = fr.read()
fr.close()

#assert 0

# Testing return types
def test_entry_type():
    assert type(entry) is sp.SpringerEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is sp.SpringerRef


# Testing scraped soup against saved site version
def test_saved_content():
    assert str(content) == saved_content

def test_saved_refs():
    assert str(references) == saved_refs


