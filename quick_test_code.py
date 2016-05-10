# -*- coding: utf-8 -*-
"""

JAH Status:


I'd like to move most of this code into the packages and then highlight
packages that people might be interested in.


"""



#Pubmed testing
#===================================================== 
if False: 
    from pypub import pubmed as pm
    
    #wtf = pm.search('Mountcastle')
    #wtf2 = pm.PubmedEntry(wtf.ids[1])
    
    wtf = pm.Entry('23594706') #Complex abstract
    #wtf = pm.Entry('19497827')
    
    #from pypub import utils
    
    #utils.print_object(wtf)


"""
#Crossref testing
from pypub import crossref as cr
DOI = '10.1007/s00221-009-1977-0'
wtf = cr.getMeta(DOI) 
"""

"""
from pypub import elsevier as evil
evil.search_scienceDirect('Mountcastle')
"""

'''
from pypub import elsevier as evil

evil.search_scopus('PMID(18430976)')

eid = evil.get_scopus_eid_from_pmid('18430976')


eid = '2-s2.0-84896533932'

raw_refs = evil.get_raw_references_from_eid(eid)

evil.parse_raw_references(raw_refs)
'''



from pypub.scrapers import sciencedirect as sd

'''
refs = sd.get_references('0006899387903726', verbose=True)
print(refs[0])
'''
'''
entry = sd.get_entry_info('http://www.sciencedirect.com/science/article/pii/0006899387903726')
print(entry)
'''

from pypub.scrapers import wiley as wy
entry = wy.get_entry_info('http://onlinelibrary.wiley.com/doi/10.1111/j.1464-4096.2004.04875.x/references')
print(entry)

refs = wy.get_references('10.1111/j.1464-4096.2004.04875.x', verbose=True)
print('%i references returned' % len(refs))
print(refs)


"""
from pypub.scrapers import jneuroscience as jn

refs = jn.get_references('http://www.jneurosci.org/content/23/10/4355.long#ref-list-1') 

import pdb
pdb.set_trace()

#sd.get_references('0006899367901205')
"""






"""
paper_url = 'http://www.scopus.com/inward/record.url?partnerID=HzOxMe3b&scp=47349118100'

#http://www.scopus.com/record/references.url?origin=recordpage&currentRecordPageEID=2-s2.0-47349118100
ref_url = 'http://www.scopus.com/record/references.url?origin=recordpage&currentRecordPageEID=2-s2.0-47349118100'

    header_dict = {
            'Referer':             ref_url}




import requests

s = requests.Session()

r1 = s.get(paper_url)
r2 = s.get(ref_url)

"""

#import requests
#r3 = requests.get(ref_url,)

#refDocs
#referenceLists
#referenceBlk