"""
This function is to parse all of the DOI prefixes and their associated publishers from the table kept at
http://www.crossref.org/06members/50go-live.html

This program is accessing the table on May 12, 2016. Website states 'last updated on May 12, 2016.'

Creates and saves three things:
    1) full_prefix_table.csv
        This is the entire CrossRef table saved as a CSV file.
    2) references_prefix_table.csv
        This is a CSV file of only those publishers listed as having references available.
    3) doi_prefix_dict.txt
        A dict saved as JSON with only the first two columns of references_prefix_table.csv.
        Keys = DOI prefixes; values = publisher names.

"""

from bs4 import BeautifulSoup
import requests
import csv
import json
from collections import defaultdict

url = 'http://www.crossref.org/06members/50go-live.html'

s = requests.session()
r = s.get(url)
soup = BeautifulSoup(r.text)

# Larger page table is the only one that has an identifying class name
parent_table = soup.find('table', {'class' : 'manic'})

# Find the main table holding the info within the larger table
table = parent_table.find_all('table')[1]

# Get heading names
headings = [td.text for td in table.find('tr').find_all('td')]

# Append all rows to 'full_prefix_table'
# Append only those rows with references available ('yes' in column 5) to references_prefix_table
full_prefix_table = []
references_prefix_table = []
for row in table.find_all('tr')[1:]:
    values = row.find_all('td')
    full_prefix_table.append([val.text for val in values])
    if values[5].text.lower() == 'yes':
        references_prefix_table.append([val.text for val in values])

# Save first two columns of the table as a dictionary
# DOI prefixes are the keys (i.e. 10.1111).
# Publisher names are the values
dict_keys = []
dict_values = []
for row in references_prefix_table:
    dict_keys.append(row[1])
    dict_values.append(row[0])

# Make a dictionary from the two lists
prefix_dict = defaultdict(list)
for x in range(len(dict_keys)):
    if len(prefix_dict[dict_keys[x]]) == 0:  # make sure only one item is stored
        prefix_dict[dict_keys[x]].append(dict_values[x])


# Write everything to files
#--------------------------

with open('doi_prefix_dict.txt', 'w') as f:
    json.dump(prefix_dict, f)

with open('full_prefix_table.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    writer.writerows(row for row in full_prefix_table if row)

with open('references_prefix_table.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    writer.writerows(row for row in references_prefix_table if row)
