# -*- coding: utf-8 -*-
"""
http://onlinelibrary.wiley.com/doi/10.1111/j.1440-1681.1976.tb00619.x/abstract

Module: pypub.scrapers.wiley

Status: In progress

#TODO: Add a verbose printout so I can see what's happening
#TODO: Profile usage, why is this sooooooo slow
#TODO: Add tests, this stuff will break!
#TODO: Allow extraction of the refs as a csv,json,xml, etc - this might go into utils



Tasks/Examples:
---------------
1) ****** Get references given a pii value *******
from pypub.scrapers import wiley as wy

refs = wy.get_references('0006899387903726',verbose=True)

refs = wy.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a Wiley URL.


"""

import sys
import os

#TODO: Move this into a compatability module
#-----------------------------------------------------
PY2 = sys.version_info.major == 2

if PY2:
    from urllib3 import unquote as urllib_unquote
else:
    from urllib.parse import unquote as urllib_unquote
#-----------------------------------------------------

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..utils import get_truncated_display_string as td
from ..utils import get_class_list_display_string as cld
from ..utils import findValue

from .. import errors

import pandas as pd
import urllib
import re
#-------------------
import requests
from bs4 import BeautifulSoup

_WY_URL = 'http://www.onlinelibrary.wiley.com'

class WileyAuthorAffiliations(object):

    def __init__(self, li_tag):
        self.id = li_tag['id']
        self.raw = li_tag.contents[1]

    def __repr__(self):
        return u'' + \
        ' id: %s\n' % self.id + \
        'raw: %s\n' % td(self.raw)


class WileyAuthor(object):

    def __init__(self, li_tag):

        """

        Example:
        <div id="articleMeta"><ol id="authors"><li id="cr1">J. Cleese<sup>*</sup> and</li><li id="cr2">G. Chapman</li>
        </ol> <div id="authorsDetail"><h4>Author Information</h4><ol id="authorsAffiliations" class="singleton"><li
            class="affiliation"><p> University</p></li></ol><p id="correspondence"><sup>*</sup>Correspondence: J. Cleese
            at University</p></div>

        Parameters
        ----------
        li_tag

        Returns
        -------

        """

        # TODO: Incorporate affiliations with each author

        self.raw = li_tag.contents[0]
        #self._data_refs = re.compile('[^\S]+').split(li_tag['data-refs'])

        #self._class = li_tag['class']

    def __repr__(self):
        return u'' + \
                'name: %s' % self.raw
        #'affiliations: %s\n' % self.affiliations[0].raw


class WileyEntry(object):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper.

    Attributes
    ----------
    pii : string
        The unique identifier

    See Also
    ----------
    WileyRef

    Examples
    ----------
    from pypub.scrapers import wiley as wy
    url = 'http://onlinelibrary.wiley.com/doi/10.1111/j.1440-1681.1976.tb00619.x/references'
    wye = wy.WileyEntry(url,verbose=True)

    Improvements
    ----------
    - Add citing articles

    """
    def __init__(self, url, verbose=False, session=None):

        # Check to see which version of the URL is being used, and go to abstract page.
        # Wiley separates info into multiple tabs, each with a unique URL
        #  ending in /abstract, /references, or /citedby.
        # Most relevant single entry information is in the /abstract URL.
        self.url = url
        ending = re.search('[^/]+$',self.url).group(0)
        if ending != 'abstract':
            self.url = self.url[:-len(ending)] + 'abstract'

        # Extract the DOI from the URL
        # Get everything between 'onlinelibrary.wiley.com/doi/' and '/abstract'
        self.pii = re.findall('doi/(.*?)/abstract', self.url, re.DOTALL)

        # Web page retrieval
        #-------------------
        if session is None:
            s = requests.Session()
        else:
            s = session

        if verbose:
            print('Requesting main page for pii: %s' % self.pii)

        # Get webpage
        r = s.get(url)

        soup = BeautifulSoup(r.text)
        self.soup = soup

        mainContent = soup.find('div', id='mainContent')
        if mainContent is None:
            raise errors.ParseException('Unable to find main content of page')


        # Metadata:
        #---------------
        self.title = findValue(mainContent, 'span', 'mainTitle', 'class').title()

        self.publication = findValue(mainContent, 'h2', 'productTitle', 'id')

        # For old journal issues, two dates are given: original publication date and
        # online publication date. This returns the original journal pub date.
        self.date = findValue(mainContent, 'span', 'issueDate', 'id')
        self.year = self.date[-4:]

        vol = findValue(mainContent, 'span', 'volumeNumber', 'id')
        issue = findValue(mainContent, 'span', 'issueNumber', 'id')
        self.volume = vol + ', ' + issue

        self.pages = findValue(mainContent, 'span', 'issuePages', 'id')
        self.pages = self.pages[6:] # to get rid of 'pages: ' at the beginning

        # TODO: Fix this keyword stuff
        keybox = soup.find('div', id='productContent')
        self.keywords = findValue(keybox, 'ul', 'keywordList', 'class')

        #import pdb
        #pdb.set_trace()

        # DOI Retrieval:
        #---------------
        # This might be more reliable than assuming we have the DOI in the title (same as pii)
        self.doi = findValue(mainContent, 'p', 'doi', 'id')
        self.doi = self.doi[5:] # to get rid of 'DOI: ' at the beginning


        # Authors
        authorList = mainContent.find('ol', {'id':'authors'}).find_all('li')
        self.authors = [WileyAuthor(x) for x in authorList]



    def __repr__(self):
        return u'' + \
        '      title: %s\n' % td(self.title) + \
        '    authors: %s\n' % self.authors + \
        '   keywords: %s\n' % self.keywords + \
        'publication: %s\n' % self.publication + \
        '       date: %s\n' % self.date + \
        '     volume: %s\n' % self.volume + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi


    @classmethod
    def from_pii(pii):
        return WileyEntry(_WY_URL + '/doi/' + str(pii) + '/abstract')


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class WileyRef(object):
    """
    This is the result class of calling get_references. It contains the
    bibliographic information about the reference, as well as additional meta
    information such as a DOI (if known).

    Attributes:
    -----------
    ref_id : int
        The index of the reference in the citing document. A value of 1
        indicates that the reference is the first reference in the citing
        document.
    title : string
    authors : string
        List of the authors. This list may be truncated if there are too many
        authors, e.g.: 'N. Zabihi, A. Mourtzinos, M.G. Maher, et al.'
    publication : string
        Abbreviated (typically?) form of the journal
    volume : string
    issue
    series
    date : string
        This appears to always be the year but I'm not sure. More
    pages

    scopus_link       = None
    doi : string
        Digital Object Identifier. May be None if not present. This is
        currently based on the presence of a link to fulltext via Crossref.
    _data_sceid       = None
        I believe this is the Scopus ID
    pii               = None
        This is the ID used to identify an article on ScienceDirect.
        See also: https://en.wikipedia.org/wiki/Publisher_Item_Identifier
    pdf_link : string (default None)
        If not None, this link points to the pdf of the article.
    scopus_cite_count = None

    Improvements
    ------------
    1) Allow resolving the DOI via the pii
    2) Some references are not parsed properly by SD. As such the raw
    information should be stored as well in those cases, along with a flag
    indicating that this has occurred (e.g. see #71 for pii: S1042368013000776)


    See Also:
    get_references

    """
    def __init__(self, ref_tags, ref_link_info, ref_id):

        """

        Parameters:
        -----------
        ref_tags: bs4.element.Tag
            Html tags as soup of the reference. Information provided is that
            needed in order to form a citation for the given reference.
        ref_link_info: str
            Html, not yet souped. Contains extra information such as links to
            a pdf (if known) and other goodies
        ref_id: int
            The id of the reference as ordered in the citing entry. A value
            of 1 indicates that this object is the first reference in the bibliography.


        """

        self.ref_tags = ref_tags


def get_references(pii, verbose=False):
    """
    This function gets references for a Wiley URL that is of the
    form:

        http://www.onlinelibrary.wiley.com/doi/####################/references

        (ending could also be /abstract or /citedby)

        e.g. http://onlinelibrary.wiley.com/doi/10.1111/j.1464-4096.2004.04875.x/references


    Implementation Notes:
    ---------------------
    From what I can tell this information is not exposed via the Elsevier API.

    In order to minimize complexity, the mobile site is requested: via a cookie.

    """

    # TODO: Finish this
    # - get references, extra step after page
    # - get reference counts, extra step after references


    # TODO: Move this to WileyEntry - I'm thinking of making this its own
    # class as well
    #
    # TODO: Make this a class reference parser

    # If you view the references, they should be wrapped by a <ul> tag
    # with the attribute class="article-references"
    REFERENCE_SECTION_TAG =  ('div', 'bibliography', 'class')

    # TODO: check what this guest tag actually looks like
    # When we don't have proper access rights, this is present in the html
    GUEST_TAG = ('li', 'menuGuest', 'id')

    # Entries are "li" tags with ids of the form:
    #   b1, b2, b3, etc.
    # Hopefully this doesn't grab other random list items on the page
    REFERENCE_TAG = ('li', {'id' : re.compile('b*')})



    # This is the URL to the page that contains the document info, including
    # reference material
    BASE_URL = _WY_URL + '/doi/'

    # Ending with the references listed
    SUFFIX = '/references'

    '''
    # This URL was found first via Fiddler, then via closer inspection of the script
    # 'article_catalyst.js' under sciencedirect.com/mobile/js in the function
    # resolveReferences
    REF_RESOLVER_URL = _SD_URL + '/science/referenceResolution/ajaxRefResol'
    '''


    # Step 1 - Make the request
    #--------------------------------------------------------------------------
    s = requests.Session()

    if verbose:
        print('Requesting main page for pii: %s' % pii)
    r = s.get(BASE_URL +  pii + SUFFIX)


    # Step 2 - Get the references tags
    #--------------------------------------------------------------------------
    # The reference tags contain most of the information about references
    # They are however missing a lot of the linking information
    # e.g. link to the article, pdf download, etc
    soup = BeautifulSoup(r.text)

    reference_section = soup.find(*REFERENCE_SECTION_TAG)

    if reference_section is None:
        # Then we might be a guest. In other words, we might not have sufficient
        # privileges to access the data we want. Generally this is protected via
        # IP mask. When I'm working from home I need to VPN into work so
        # that I can access the data :/
        print("reference_section is None")
        temp = soup.find(*GUEST_TAG)
        if temp is None:
            #We might have no references ... (Doubtful)
            raise errors.ParseException("References were not found ..., code error likely")
        else:
            raise errors.InsufficientCredentialsException("Insufficient access rights to get referencs, requires certain IP addresses (e.g. university based IP)")

    ref_tags = reference_section.find_all(*REFERENCE_TAG)

    n_refs = len(ref_tags)

    if n_refs == 0:
        return None

    '''
    # Step 3 - Resolve reference links
    #--------------------------------------------------------------------------

    # Step 3.1 - Make the request for the information
    #--------------------------------------------------------------------------
    # We need the eid of the current entry, it is of the form:
    #
    #   SDM.pm.eid = "1-s2.0-0006899387903726"
    #
    #   * I think this entry gets deleted after the requests so it may not be
    #   visible  if looking for it in Chrome.
    match = re.search('SDM\.pm\.eid\s*=\s*"([^"]+)"',r.text)
    eid   = match.group(1)

    # This list comes from the resolveReferences function in article_catalyst.js
    payload = {
        '_eid'           : eid,
        '_refCnt'        : n_refs,
        '_docType'       : 'article',
        '_refRangeStart' : '1',
        '_refRangeCount' : str(n_refs)} #This is normally in sets of 20's ...
        #I'm not sure if it is important to limit this. The browser then
        #makes a request fromr 1 count 20, 21 count 20, 41 count 20 etc,
        #It always goes by 20 even if there aren't 20 left

    if verbose:
        print('Requesting reference links')
    #r2 = s.get(REF_RESOLVER_URL,params=payload)

    #Step 3.2 - Parse the returned information into single entries
    #--------------------------------------------------------------------------
    #This could probably be optimized in terms of execution time. We basically
    #get back a single script tag. Inside is some sort of hash map for links
    #for each reference.
    #
    #The script tag is of the form:
    #   myMap['bibsbref11']['refHtml']= "<some html stuffs>";
    #   myMap['bibsbref11']['absUrl']= "http://www.sciencedirect.com/science/absref/sd/0018506X7790068X";
    #   etc.
    #
    #   - Each entry is quite long.
    #   - Normally contains html
    #   - can be empty i.e. myMap['bibsbref11']['refHtml'] = "";
    #   - the refHtml is quite interesting
    #   - the absolute url is not always present (and currently not parsed)
    more_soup   = BeautifulSoup(r2.text)
    script_tag  = more_soup.find('script')

    # We unquote the script text as it is transmitted with characters escaped
    # and we want the parsed data to contain the non-escaped text
    #
    # We might eventually want to move this to being after the regular expression ...
    script_text = urllib_unquote(script_tag.text)

    ref_match_result = re.findall("myMap\['bibsbref(\d+)'\]\['refHtml'\]=\s?" + '"([^"]*)";',script_text)
    '''

    # Tokens:
    # 0 - the # from bibsbref#
    # 1 - the html content from the 'refHtml' entry
    #
    # NOTE: We don't really use the #, so we might remove the () around
    # \d+ which would shift the index from 1 to 0
    if verbose:
        print('Creating reference objects')
    ref_objects = [WileyRef(ref_tag,ref_link_info[1],ref_id) for \
                    ref_tag,ref_link_info,ref_id in \
                    zip(ref_tags,ref_match_result,range(n_refs))]


    #Step 4:
    #--------------------------------------------------------------------------
    #TODO: Improve documentation for this step

    if verbose:
        print('Retrieving Scopus Counts')

    ref_scopus_eids  = [] #The Scopus IDs of the references to resolve
    #but with a particular formatting ...
    ref_count = 0 #Number of references we haven't resolved

    ref_count_list = []
    #NOTE: Browser requests these in the reverse order ...
    for ref_id, ref in enumerate(ref_objects):

        if ref._data_sceid is not None:
            ref_scopus_eids.append(ref._data_sceid + ',' + str(ref_id+1) + '~')
            ref_count += 1

            #If we've got enough, then update the counts
            #The 20 may be arbitrary but it was what was used in original JS
            if ref_count > 20:
                ref_count_list += _update_counts(s,ref_scopus_eids,REF_RESOLVER_URL)
                ref_count = 0
                ref_scopus_eids  = []

    #Get any remaining reference counts
    if ref_count != 0:
         ref_count_list += _update_counts(s,ref_scopus_eids,REF_RESOLVER_URL)

    #Take the raw data and set the citation count for each object
    for ref_tuple in ref_count_list:
        ref_id    = int(ref_tuple[0]) - 1
        ref_count = int(ref_tuple[1])
        ref_objects[ref_id].scopus_cite_count = ref_count


    #All done!
    #---------
    return ref_objects


def _update_counts(s,eids,resolve_url):

    """
    Helper for get_references()

    Parameters
    ----------
    s : Session
        The Requests Session
    eids : list
        List of eids but with a particular format
        e.g. ... TODO
    resolve_url : string
        This is a hardcoded value, eventually we'll pull this from the class

    Returns
    -------
    """
    payload = {'_updateCitedBy' : ''.join(eids)}
    r = s.get(resolve_url,params=payload)
    #TODO: Check for 200
    data = urllib_unquote(r.text)

    #myXabsCounts['citedBy_26']='Citing Articles (41)';
    cited_by_results = re.findall("myXabsCounts\['citedBy_(\d+)'\]='[^\(]+\((\d+)",data)

    return cited_by_results
    #TODO: parse response
    #????? Why is the order scrambled - this seems to be on their end ...????
    """
    NOTE: This is now Citing Articles, references to Scopus have been dropped
    myXabsCounts['citedBy_16']='Cited By in Scopus (128)';
    myXabsCounts['citedBy_15']='Cited By in Scopus (25)';
    myXabsCounts['citedBy_1']='Cited By in Scopus (2)';
    myXabsCounts['citedBy_3']='Cited By in Scopus (29)';
    """
    #TODO: go through refs and apply new values ...


def get_entry_info(url):
    return WileyEntry(url, verbose=True)