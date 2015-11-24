# -*- coding: utf-8 -*-
"""

Tools related to crossref (DOIs)

See:
http://www.crosscite.org/cn/
http://labs.crossref.org/



TODO: List relevant GitHub repos

List is Unfinished:
- https://github.com/MartinPaulEve/crossRefQuery
- https://github.com/total-impact/total-impact-core/blob/master/totalimpact/providers/crossref.py

CrossRef Organization:
https://github.com/CrossRef

===============================================================================
crossref help
http://help.crossref.org/#home

crossref SimpleText query:
----------------------------------
- http://www.crossref.org/SimpleTextQuery/
- cut and paste references into the box - returns DOIs
- requires registered email

OpenURL
----------------------------------
- http://help.crossref.org/#using_the_open_url_resolver
- 

HTTP
----------------------------------
- http://help.crossref.org/#using_http


"""

DOI_SEARCH = 'http://doi.crossref.org/search/doi'

import requests as requests

crossref_email = 'jim.hokanson@gmail.com'

#TODO: Support multiple dois ...
def getMeta(doi, format='unixsd'):
    
    """ 

    Given a doi, return article meta data 

    #Output formats:
    #-------------------------
    #1) xsd_xml - default - 'unixsd' - recommended for future use
    #http://help.crossref.org/#unixsd 
    #DOC: query_output3.0
    #http://www.crossref.org/schema/documentation/crossref_query_output3.0/query_output3.0.html
    #2) 'unixref'
    #http://help.crossref.org/#unixref-query-result-format

    #TODO: Document why unixref might be preferable
    #TODO: Finish parsing of xsd


    """
    
    #pid    - email
    #format - unixsd
    #doi    - doi
    payload = {'pid':crossref_email, 'format':format, 'doi':doi}
    r = requests.get(DOI_SEARCH, params=payload)    
    
    #XSD code generation
    #http://www.rexx.com/~dkuhlman/generateDS.html    
    #generateds_gui.py    
    
    import pdb
    pdb.set_trace()
    
    