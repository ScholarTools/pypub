'''
NOTE: CHANGE FILENAME IN LAST FEW LINES FOR EACH NEW SCRAPER
'''

import requests
from bs4 import BeautifulSoup
import json

#from pathlib import Path
from ScholarTools.pypub.pypub.scrapers import sciencedirect as scraper

link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'

'''
s = requests.session()
r = s.get(link)
soup = BeautifulSoup(r.text)
'''

entry = scraper.get_entry_info(link)
refs = scraper.get_references('S0006899313013048')

entry_dict = entry.__dict__

refs_dicts = []
for x in range(len(refs)):
    refs_dicts.append(refs[x].__dict__)


# Change all author info from [scraper]Author objects to str objects
for x in range(len(entry_dict['authors'])):
    entry_dict['authors'][x] = str(entry_dict['authors'][x])
    #entry_dict['authors'][x] = entry_dict['authors'][x].__dict__


print(entry_dict.keys())
print(refs_dicts[0].keys())


print(json.dumps(entry_dict))
print(json.dumps(refs_dicts))


'''
# NOTE: CHANGE FILENAMES FOR EACH NEW SCRAPER
with open('saved_sites/sd_entry.txt', 'w') as fe:
    fe.write(json.dumps(entry_dict))

with open('saved_sites/sd_references.txt', 'w') as fr:
    fr.write(json.dumps(refs_dicts))
'''


