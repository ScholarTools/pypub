# -*- coding: utf-8 -*-
"""

JAH Status 11/15/2015
This code is a complete mess and needs to be rewritten. I had a really
hard time understanding their API documentation.

See also:
pypub.scrapers.sciencedirect


#http://www.developers.elsevier.com/cms/index

#TODO: Describe how to get this code up and running

Authentication
-------------------------------------------------------------------------------
Authentication is roughly outlined at:
http://www.developers.elsevier.com/devcms/restful-api-authentication-new

This code base currently only supports institution based API access. To set
this up you need to:
TODO: Finish this list

Definitions
---------------------------------------------
This is primarily for development, not for users:
PRISM definitions:
http://www.prismstandard.org/specifications/2.0/PRISM_prism_namespace_2.0.pdf
Dublin Core:
http://dublincore.org/documents/2012/06/14/dcmi-terms/?v=elements#


"""

#TODO: Check this out:
#http://kitchingroup.cheme.cmu.edu/blog/2015/06/07/Getting-a-Scopus-EID-from-a-DOI/











#Search View Overview
#http://www.developers.elsevier.com/cms/index

#Content API Retrieval Request
#http://www.developers.elsevier.com/cms/index

#

"""
[Request headers]
X-ELS-APIKey: 
X-ELS-ResourceVersion: XOCS
Accept: text/xml OR applcation/json OR application/rdf+xml

"""

#XOCS????
#http://schema.elsevier.com/dtds/document/fulltext/xcr/xocs-common.xsd

"""
===============================================================================
===============================================================================
===============================================================================
                    Start of code ...
===============================================================================
===============================================================================
===============================================================================
"""


#TODO: Break out into search, retrieval, and meta modules

from . import config
import requests
from bs4 import BeautifulSoup

#Some more on the results:
#http://www.developers.elsevier.com/devcms/content-api-wadl-opensearch

"""
===============================================================================
===============================================================================
===============================================================================
                    Search functions
===============================================================================
http://www.developers.elsevier.com/devcms/content-api-search-request
===============================================================================
===============================================================================
"""


#TODO: It would be nice to support an advanced query builder:
#http://www.developers.elsevier.com/devcms/content/search-fields-overview

def search_scopus(query_str):

    """

    STATUS: Unfinished
    1) Needs to have parameters exposed
    2) Needs to have response parsed
    3) Documentation should be updated

    Documentation Source:
    http://api.elsevier.com/documentation/SCOPUSSearchAPI.wadl

    Parameters
    ---------------------------------------
    query_str : str
       See links below for more information.
       ex. KEY(mouse AND NOT cat OR dog)
       - documentation:
           http://api.elsevier.com/content/search/fields/scopus
       - search tips:
           http://api.elsevier.com/documentation/search/SCOPUSSearchTips.htm
    oa : str (true OR false)
        oa - Open Access. Can be used with subscribed=true to search for both
        subscribed content and also non-subscribed open access content.
    """

    base_url = 'http://api.elsevier.com/content/search/scopus'

    #TODO: We'll escape the query string

    header_dict = {
            "X-ELS-APIKey":             config.Elsevier.api_key,
            "X-ELS-ResourceVersion":    "XOCS" ,
            "Accept":                   "application/json"}


    query_dict = {
        'query': query_str,
        }


    #This old code was run over a variety of years

    #Example:
    #http://api.elsevier.com/documentation/search/scopusSearchResp.xml

    r = requests.get(base_url,params=query_dict,headers=header_dict)

    #<link ref="self" href="http://api.elsevier.com/content/abstract/scopus_id/84887964048"/>
    #<link ref="scopus" href="http://www.scopus.com/inward/record.url?partnerID=HzOxMe3b&scp=84887964048"/>
    #<link ref="scopus-citedby" href="http://www.scopus.com/inward/citedby.url?partnerID=HzOxMe3b&scp=84887964048"/>
    #<link ref="full-text" href="http://api.elsevier.com/content/article/eid/1-s2.0-S095656631300732X"/>

    #TODO:
    # get prism:url
    # get scopus
    json = r.json()
    sr = json['search-results']

    return sr


def get_scopus_eid_from_pmid(pmid):
    #TODO: Allow numbers as well ...
    query_str = 'PMID(%s)' % pmid
    sr = search_scopus(query_str)

    #TODO: Handle error


    #NOTE: Eventually parsing should not be necessary
    #or at least we should have more direct access

    entries     = sr['entry']
    first_entry = entries[0]

    return first_entry['eid']

def search_scienceDirect(query_str):
    
    """

    STATUS: Unfinished
    1) Needs to have parameters exposed
    2) Needs to have response parsed
    3) Documentation should be updated

    There are two ScienceDirect search APIs. It is unclear as to what the 
    difference is. This needs to be cleared up.

    Documentation Source:
    http://api.elsevier.com/documentation/SCIDIRSearchAPI.wadl
    
    TODO: Summarize what this function does (or can do)

    Parameters
    ---------------------------------------
    query_str : str 
       See links below for more information.
       ex. KEY(mouse AND NOT cat OR dog)
       - documentation:
           http://api.elsevier.com/content/search/fields/scidir
       - search tips:
           http://api.elsevier.com/documentation/search/SCIDIRSearchTips.htm
    oa : str (true OR false)
        oa - Open Access. Can be used with subscribed=true to search for both 
        subscribed content and also non-subscribed open access content.
    """    
    
    #NOTE: neuroelectro using:
    #query
    #date
    #count
    #start
    #content=k
    
    
    base_url = 'http://api.elsevier.com/content/search/scidir'
    #base_url = 'http://api.elsevier.com/content/search/index:scidir'     
    
    #PARAMS
    #-----------------------------------------------

    #oa :
    
    #TODO: We'll escape the query string    
    
    header_dict = {
            "X-ELS-APIKey":             config.Elsevier.api_key,
            "X-ELS-ResourceVersion":    "XOCS" ,
            "Accept":                   "application/json"}
    

    query_dict = {
        'query': query_str,
        }
        
    
    #This old code was run over a variety of years

    #Example:
    #http://api.elsevier.com/documentation/search/scidirSearchResp.xml

    r = requests.get(base_url,params=query_dict,headers=header_dict)

    json_results = r.json()
    sr = json_results['search-results']

    return sr

    #TODO:
    #1) Determine how I want to expose the results
    #2)


    #return None
        
        #OLD CODE

"""
===============================================================================
===============================================================================
===============================================================================
                    Meta data functions
===============================================================================
http://www.developers.elsevier.com/devcms/content-api-metadata-request
===============================================================================
===============================================================================
"""


#Abstract Citations - just returns a count ... aaaaaahhhh!

def parse_raw_references(ref_page_raw):

    #This will eventually be merged with:
    #get_raw_references_from_eid

    soup = BeautifulSoup(ref_page_raw)


    #class="bold refAuthorTitle" - authors:
    #title with links
    #outwardLink - scopus
    #other parameters difficult to parse

    return None

    """

    Examined exporting:

    http://www.scopus.com/onclick/export.url?

    Parameters:
    ----------------------------------------------------
    oneClickExport	{"Format":"CSV","View":"CiteOnly"}
    src	            s
    origin	        reflist
    zone	        exportDropDown
    outputType	    export
    txGid	        DDEF4E0811DAAA00936880205F6DCBCF.fM4vPBipdL1BpirDq5Cw:15

    """


"""
===============================================================================
===============================================================================
===============================================================================
                   Scraping Functions
===============================================================================
http://www.developers.elsevier.com/devcms/content-api-metadata-request
===============================================================================
===============================================================================
"""

def get_raw_references_from_eid(eid):

    """
    This is a helper function and it might move.
    """

    """
    Currently nothing prior to 1996, this is changing ...
    http://blog.scopus.com/posts/scopus-to-add-cited-references-for-pre-1996-content
    """

    #http://www.scopus.com/record/display.url?eid=2-s2.0-84896533932&origin=resultslist
    paper_url    = 'http://www.scopus.com/record/display.url'
    paper_params = {'eid': eid, 'origin': 'resultslist'}

    #'http://www.scopus.com/record/references.url?origin=recordpage&currentRecordPageEID=2-s2.0-47349118100'
    ref_url    = 'http://www.scopus.com/record/references.url'
    ref_params = {'origin':'recordpage', 'currentRecordPageEID':eid}

    s = requests.Session()

    #TODO: Check succcess of requests ...

    r1 = s.get(paper_url,params=paper_params)
    r2 = s.get(ref_url,params=ref_params)

    return r2.text