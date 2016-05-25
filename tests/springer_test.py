from pypub.scrapers import springer as sp
from pypub.utils import convert_to_dict
import json
import os

curpath = str(os.path.dirname(os.path.abspath(__file__)))

# Sample journal article
link = 'http://link.springer.com/article/10.1186/s12984-016-0150-9'
pii = '10.1186/s12984-016-0150-9'

# Run scraper on live site
entry = sp.get_entry_info(link)
refs = sp.get_references(pii)

# Make scraped entry into a dict
entry_dict = convert_to_dict(entry)

# Make a list of refs as dict objects
refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(convert_to_dict(refs[x]))

# Load cached version of content and references
with open(curpath + '/saved_sites/sp_entry.txt') as fe:
    saved_entry = fe.read()

with open(curpath + '/saved_sites/sp_references.txt') as fr:
    saved_refs = fr.read()

saved_entry = json.loads(saved_entry)
saved_refs = json.loads(saved_refs)

# ----------------------

# Testing return types
def test_entry_type():
    assert type(entry) is sp.SpringerEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is sp.SpringerRef


# Testing scraped soup against saved site version
def test_springer_saved_entry():
    for x in saved_entry.keys():
        if saved_entry[x] != entry_dict[x]:
            print('\nDifference found.')
            print('Key: ' + str(x))
            print('Saved value: ' + str(saved_entry[x]))
            print('Live value: ' + str(entry_dict[x]))
            assert False
    assert True

def test_springer_saved_refs():
    for y in range(len(saved_refs)):
        for x in saved_refs[y].keys():
            if saved_refs[y][x] != refs_dicts[y][x]:
                print('\nDifference found.')
                print('Key: ' + str(x))
                print('Saved value: ' + str(saved_refs[y][x]))
                print('Live value: ' + str(refs_dicts[y][x]))
                assert False
    assert True


