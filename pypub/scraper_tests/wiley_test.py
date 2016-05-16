import pytest

from ..scrapers import wiley as wy
import requests
from bs4 import BeautifulSoup
import json

# Sample journal article
link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
pii = '10.1002/biot.201400046'

# Retrieve soup of content and references from live site
#s = requests.session()
#r = s.get(link)
#soup = BeautifulSoup(r.text)

# Run scraper on live site
entry = wy.get_entry_info(link)
refs = wy.get_references(pii)



# Load saved version of content and references
with open('saved_sites/wy_entry.txt') as fe:
    saved_entry = fe.read()

with open('saved_sites/wy_references.txt') as fr:
    saved_refs = fr.read()

# Make the saved versions into dicts
saved_entry = json.loads(saved_entry)
saved_refs = json.loads(saved_refs)


# Make scraped entry into a dict
entry_dict = entry.__dict__

# Change all author info from [scraper]Author objects to str objects
for x in range(len(entry_dict['authors'])):
    entry_dict['authors'][x] = str(entry_dict['authors'][x])

#
refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(refs[x].__dict__)

#assert 0

# Testing return types
def test_entry_type():
    assert type(entry) is wy.WileyEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is wy.WileyRef


# Testing scraped soup against saved site version
def test_wiley_saved_entry():
    for x in saved_entry.keys():
        if saved_entry[x] != entry_dict[x]:
            print(saved_entry[x])
            print(entry_dict[x])
            assert False
    assert True

def test_wiley_saved_refs():
    for y in range(len(saved_refs)):
        for x in saved_refs[y].keys():
            if saved_refs[y][x] != refs_dicts[y][x]:
                assert False
    assert True


