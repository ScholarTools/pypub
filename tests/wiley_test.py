import pytest

from pypub.scrapers import wiley as wy
from pypub.utils import convert_to_dict
import json
import os

curpath = str(os.path.dirname(os.path.abspath(__file__)))

# Sample journal article
link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
pii = '10.1002/biot.201400046'


# Run scraper on live site
entry = wy.get_entry_info(link)
refs = wy.get_references(pii)

# Make scraped entry into a dict
entry_dict = convert_to_dict(entry)

# Make a list of refs as dict objects
refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(convert_to_dict(refs[x]))


# Load saved version of content and references
with open(curpath + '/saved_sites/wy_entry.txt') as fe:
    saved_entry = fe.read()

with open(curpath + '/saved_sites/wy_references.txt') as fr:
    saved_refs = fr.read()

# Make the saved versions into dicts
saved_entry = json.loads(saved_entry)
saved_refs = json.loads(saved_refs)

# ----------------------

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
            print('\nDifference found.')
            print('Key: ' + str(x))
            print('Saved value: ' + str(saved_entry[x]))
            print('Live value: ' + str(entry_dict[x]))
            assert False
    assert True

def test_wiley_saved_refs():
    for y in range(len(saved_refs)):
        for x in saved_refs[y].keys():
            if saved_refs[y][x] != refs_dicts[y][x]:
                print('\nDifference found.')
                print('Key: ' + str(x))
                print('Saved value: ' + str(saved_refs[y][x]))
                print('Live value: ' + str(refs_dicts[y][x]))
                assert False
    assert True
