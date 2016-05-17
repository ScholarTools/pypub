from pypub.scrapers import sciencedirect as sd
from pypub.utils import convert_to_dict
import json
import os

curpath = str(os.path.dirname(os.path.abspath(__file__)))

# Sample journal article
link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'
pii = 'S0006899313013048'

# Run scraper on live site
entry = sd.get_entry_info(link)
refs = sd.get_references(pii)

# Make scraped entry into a dict
entry_dict = convert_to_dict(entry)

# Make a list of refs as dict objects
refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(convert_to_dict(refs[x]))

# Load cached version of content and references
with open(curpath + '/saved_sites/sd_entry.txt') as fe:
    saved_entry = fe.read()

with open(curpath + '/saved_sites/sd_references.txt') as fr:
    saved_refs = fr.read()

# Make the saved versions into dicts
saved_entry = json.loads(saved_entry)
saved_refs = json.loads(saved_refs)

# ----------------------

# Testing return types
def test_entry_type():
    assert type(entry) is sd.ScienceDirectEntry

def test_references_type():
    assert type(refs) is list

def test_reflist_type():
    assert type(refs[0]) is sd.ScienceDirectRef


# Testing scraped soup against saved site version
def test_sd_saved_entry():
    for x in saved_entry.keys():
        if saved_entry[x] != entry_dict[x]:
            print(type(saved_entry[x][0]))
            print(type(entry_dict[x][0]))
            print(x)
            assert False
    assert True

def test_sd_saved_refs():
    for y in range(len(saved_refs)):
        for x in saved_refs[y].keys():
            if saved_refs[y][x] != refs_dicts[y][x]:
                assert False
    assert True




