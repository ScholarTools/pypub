import pytest
import nose

from ..scrapers import wiley as wy


'''
import requests
from bs4 import BeautifulSoup
import re

#
# Get article from most recent edition of Biotechnology Journal to test
#
journal_url = 'http://onlinelibrary.wiley.com/journal/10.1002/(ISSN)1860-7314' # to journal homepage
base_url = 'http://onlinelibary.wiley.com'
s = requests.Session()
r = s.get(journal_url)

# Extract HTML
soup = BeautifulSoup(r.text)

# Get link to current issue
issuelist = soup.find('ul', {'class' : 'issues'})
first_issue = issuelist.find('li')
first_issue_link = first_issue.find('a', href=True)['href']

# Go to page for current issue
r = s.get(base_url + first_issue_link)
soup = BeautifulSoup(r.text)

# Get link for an article
random_article = soup.find_all('div', {'class' : 'tocArticle'})[7]
article_link = random_article.find('a', href=True)['href']

# URL for article
# of the form http://onlinelibrary.wiley.com/doi/################/abstract
link = base_url + article_link
pii = link.replace('/abstract', '')
pii = pii.replace('/doi/', '')
'''

# Actually, no. I'm not going to do that stuff above.
# Instead, I'm going to use one sample URL so that the inputs
# and outputs are always going to be standard.

# Sample journal article
link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
pii = '10.1002/biot.201400046'


entry = wy.get_entry_info(link)
refs = wy.get_references(pii)

# Testing return types
def test_entry_type():
    assert type(entry) is wy.WileyEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is wy.WileyRef

'''
# Testing correct entry information
def test_entry_info():
    if 'crispr/cas9-mediated' not in entry.title.lower():
        assert False
    elif 'Chronis Fatouros' not in entry.authors:
        assert False
    elif 'Biotechnology Journal' not in entry.publication:
        assert False
    elif 'November 2014' not in entry.date:
        assert False
    elif 'Volume 9' not in entry.volume:
        assert False
    elif '1402-1412' not in entry.pages:
        assert False
    elif pii != entry.doi:
        assert False
    else:
        assert True
'''



# Testing correct reference information



