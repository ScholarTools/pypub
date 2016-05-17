'''
NOTE: CHANGE FILENAME IN LAST FEW LINES FOR EACH NEW SCRAPER
'''

import json
import os

from pypub.scrapers import wiley as scraper
from pypub.utils import convert_to_dict

link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'

curpath = str(os.getcwd())

entry = scraper.get_entry_info(link)
refs = scraper.get_references(link)

entry_dict = convert_to_dict(entry)

refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(convert_to_dict(refs[x]))

print(json.dumps(entry_dict))
print(json.dumps(refs_dicts))

'''
# NOTE: CHANGE FILENAMES FOR EACH NEW SCRAPER
with open(curpath + '/../tests/saved_sites/wy_entry.txt', 'w') as fe:
    fe.write(json.dumps(entry_dict))

with open(curpath + '/../tests/saved_sites/wy_references.txt', 'w') as fr:
    fr.write(json.dumps(refs_dicts))
'''
