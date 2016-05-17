# -*- coding: utf-8 -*-
"""

JAH Status:


I'd like to move most of this code into the packages and then highlight
packages that people might be interested in.


"""



#Pubmed
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
from pypub import elsevier as el
el.search_scienceDirect('Mountcastle')
"""

'''
from pypub import elsevier as el

el.search_scopus('PMID(18430976)')

eid = el.get_scopus_eid_from_pmid('18430976')


eid = '2-s2.0-84896533932'

raw_refs = el.get_raw_references_from_eid(eid)

el.parse_raw_references(raw_refs)
'''


# Science Direct
#=====================================================

from pypub.scrapers import sciencedirect as sd

#sd_link = 'http://www.sciencedirect.com/science/article/pii/0006899387903726'
sd_link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'
sd_pii = 'S0006899313013048'

entry = sd.get_entry_info(sd_link, verbose=True)
print(entry)

#refs = sd.get_references(sd_link, verbose=True)
#print(refs[0])


# Wiley
#=====================================================
'''
from pypub.scrapers import wiley as wy

wiley_link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
wiley_doi = '10.1002/biot.201400046'

entry = wy.get_entry_info(wiley_link, verbose=True)
print(entry)

refs = wy.get_references(wiley_link, verbose=True)
print('%i references returned' % len(refs))
print(refs[0])
'''

'''
wiley_link = 'http://onlinelibrary.wiley.com/doi/10.1111/j.1464-4096.2004.04875.x/abstract'
wiley_doi = '10.1111/j.1464-4096.2004.04875.x'
'''

'''
# New example with more recent article
wiley_link = 'http://onlinelibrary.wiley.com/doi/10.1002/bit.25159/abstract'
wiley_doi = '10.1002/bit.25159'

entry = wy.get_entry_info(wiley_link, verbose=True)
print(entry)

refs = wy.get_references(wiley_link, verbose=True)
print('%i references returned' % len(refs))
print(refs[0])
'''


# Springer - doesn't work yet
#=====================================================
'''
from pypub.scrapers import springer as sp

sp_link = 'http://link.springer.com/article/10.1186/s12984-016-0150-9'
sp_doi = '10.1186/s12984-016-0150-9'

entry = sp.get_entry_info(sp_link, verbose=True)
print(entry)

refs = sp.get_references(sp_link, verbose=True)
print('%i references returned' % len(refs))
print(refs[0])
'''
'''
import json
print(json.dumps(refs[0]))
'''



"""
from pypub.scrapers import jneuroscience as jn

refs = jn.get_references('http://www.jneurosci.org/content/23/10/4355.long#ref-list-1')

#sd.get_references('0006899367901205')
"""



"""
paper_url = 'http://www.scopus.com/inward/record.url?partnerID=HzOxMe3b&scp=47349118100'

#http://www.scopus.com/record/references.url?origin=recordpage&currentRecordPageEID=2-s2.0-47349118100
ref_url = 'http://www.scopus.com/record/references.url?origin=recordpage&currentRecordPageEID=2-s2.0-47349118100'

    header_dict = {
            'Referer':             ref_url}

"""
