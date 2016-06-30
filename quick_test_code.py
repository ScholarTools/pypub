# -*- coding: utf-8 -*-
"""

JAH Status:


I'd like to move most of this code into the packages and then highlight
packages that people might be interested in.


"""



#Pubmed
# =====================================================
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
# =====================================================

from pypub.scrapers import sciencedirect as sd

sd_link = 'http://www.sciencedirect.com/science/article/pii/0006899387903726'
#sd_link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'
sd_pii = 'S0006899313013048'

#sd_link = 'http://www.sciencedirect.com/science/article/pii/S0092867413004674'
sd_link = 'http://www.sciencedirect.com/science/article/pii/S0012160613006453'

sd_link = 'http://www.sciencedirect.com/science/article/pii/S0006349513006176'

sd_link = 'http://www.sciencedirect.com/science/article/pii/S0304399100000760'

entry = sd.get_entry_info(sd_link, verbose=True)
print(entry)

refs = sd.get_references(sd_link, verbose=True)
print(refs[0])


# Wiley
# =====================================================
'''
from pypub.scrapers import wiley as wy

wiley_link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
wiley_doi = '10.1002/biot.201400046'

doi = '10.1002/prot.340120202'

entry = wy.get_entry_info(doi, verbose=True)
print(entry)

refs = wy.get_references(doi, verbose=True)
print('%i references returned' % len(refs))
print(refs[0])

#pdf_link = wy.get_pdf_link(wiley_link)
#print(pdf_link)
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

pdf_link = wy.get_pdf_link(wiley_link)
print(pdf_link)
'''


# Springer
# =====================================================
'''
from pypub.scrapers import springer as sp

sp_link = 'http://link.springer.com/article/10.1186/s12984-016-0150-9'
sp_doi = '10.1186/s12984-016-0150-9'

# This one works with dx.doi.org/ - the one above redirects to a specific journal page.
sp_link = 'http://link.springer.com/article/10.1007/s10237-015-0706-9'
sp_doi = '10.1007/s10237-015-0706-9'

sp_doi = '10.1007/s10237-006-0048-8'

entry = sp.get_entry_info(sp_doi, verbose=True)
print(entry)

refs = sp.get_references(sp_link, verbose=True)
print('%i references returned' % len(refs))
print(refs[0])
'''
'''
import json
print(json.dumps(refs[0]))
'''

# Nature
# =====================================================
'''
from pypub.scrapers import nature_nrg as nt_nrg

nt_link = 'http://www.nature.com/nrg/journal/v15/n5/full/nrg3686.html'
nt_doi = '10.1038/nrg3686'

nt_link = 'http://www.nature.com/nrg/journal/v11/n9/full/nrg2842.html'

entry = nt_nrg.get_entry_info(nt_link, verbose=True)
print(entry)

refs = nt_nrg.get_references(nt_link)
print(refs[0])
print(len(refs))

#nature_pdf_link = nt.get_pdf_link(nt_link)
#print(nature_pdf_link)
'''


# Taylor and Francis
# =====================================================
'''
from pypub.scrapers import taylorfrancis as tf

# This link is for the paper without full access
tf_link = 'http://www.tandfonline.com/doi/full/10.1080/2326263X.2015.1134958'
tf_doi = '10.1080/2326263X.2015.1134958'

# This link is for the open access paper
tf_link = 'http://www.tandfonline.com/doi/full/10.1080/21624054.2016.1184390'
tf_doi = '10.1080/21624054.2016.1184390'

entry = tf.get_entry_info(tf_link, verbose=True)
print(entry)

refs = tf.get_references(tf_link)
print(refs[0])
print(len(refs))

pdf_link = tf.get_pdf_link(tf_link)

from pypub.publishers.pub_objects import TaylorFrancis as TF
TFran = TF()
pdf_content = TFran.get_pdf_content(pdf_url=pdf_link)

import pdb
pdb.set_trace()
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
