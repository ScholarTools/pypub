# -*- coding: utf-8 -*-
"""
http://onlinelibrary.wiley.com/doi/10.1111/j.1440-1681.1976.tb00619.x/abstract

Module: pypub.scrapers.wiley

Status: In progress

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
    from urllib3 import quote as urllib_quote
else:
    from urllib.parse import unquote as urllib_unquote
    from urllib.parse import quote as urllib_quote
#-----------------------------------------------------

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..utils import get_truncated_display_string as td
from ..utils import findValue

from .. import errors

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
    date : string
        This appears to always be the year
    doi : string
        Digital Object Identifier. May be None if not present. This is
        currently based on the presence of a link to fulltext via Crossref.
    pii               = None
        This is the ID used to identify an article on ScienceDirect.
        See also: https://en.wikipedia.org/wiki/Publisher_Item_Identifier
    pdf_link : string (default None)
        If not None, this link points to the pdf of the article.



    See Also:
    get_references

    """
    def __init__(self, ref_tags, ref_id):

        """

        Parameters:
        -----------
        ref_tags: bs4.element.Tag
            Html tags as soup of the reference. Information provided is that
            needed in order to form a citation for the given reference.
        ref_id: int
            The id of the reference as ordered in the citing entry. A value
            of 1 indicates that this object is the first reference in the bibliography.


        """

        self.ref_tags = ref_tags

        # Reference Bibliography Section:
        #--------------------------------
        self.ref_id = ref_id + 1 # Input is 0 indexed
        self.title = findValue(ref_tags, 'span', 'articleTitle', 'class')
        authorlist = ref_tags.find_all('span', 'author', 'class')
        self.authors = [x.text for x in authorlist]

        # Note: we can also get individual authors if we would like.
        #
        # On Wiley, each reference author is given a separate <span> tag with the class 'author'
        # so individual authors can be extracted
        #

        self.publication = findValue(ref_tags, 'span', 'journalTitle', 'class')
        self.volume = findValue(ref_tags, 'span', 'vol', 'class')
        self.date = findValue(ref_tags, 'span', 'pubYear', 'class')

        firstp = findValue(ref_tags, 'span', 'pageFirst', 'class')
        lastp = findValue(ref_tags, 'span', 'pageLast', 'class')
        self.pages = firstp + '-' + lastp


        # Reference Meta Section:
        #------------------------------

        self.crossref = None
        self.pubmed = None
        self.pubmed_id = None
        self.doi = None
        self.citetimes = None
        self.cas = None
        self.abstract = None
        self.pdf_link = None
        self.ref_references = None

        # External links (i.e. PubMed, CrossRef, CAS) are kept in a ul tag
        # Internal links (i.e. direct to abstract, references, etc.) are in a div
        # Need to check for both
        links = ref_tags.find('ul', 'externalReferences', 'class')
        if links is None:
            links = ref_tags.find('div', 'internalReferences', 'class')

        # Only proceed if either internal or external references were found
        if links is not None:
            links = links.find_all('li')

            # Check against all possible link options and save links.
            # href links are appended onto base URL ('http://onlinelibrary.wiley.com')
            #
            # NOTE: links are returned URL encoded (using urllib.quote(), but DOI
            # and PubMed IDs are not encoded. This means that if extracting the DOI
            # from one of the returned URLs, it needs to be first unquoted.
            #
            for link in links:
                label = link.text.lower()
                href = link.find('a', href=True)['href']
                href = urllib_quote(href)

                if 'crossref' in label:
                    self.doi = re.search('[^id=]+$',href).group(0)
                    self.doi = urllib_unquote(self.doi)[1:] # The [1:] is to get rid of the first '='
                    self.crossref = _WY_URL + href
                elif 'pubmed' in label:
                    self.pubmed_id = re.search('[^id=]+$',href).group(0)
                    self.pubmed_id = urllib_unquote(self.pubmed_id)[1:]
                    self.pubmed = _WY_URL + href
                elif 'web ' in label:
                    self.citetimes = re.search('[^: ]+$',label).group(0)
                elif label in ('cas', 'cas,'):
                    self.cas = _WY_URL + href
                elif 'abstract' in label:
                    self.abstract = _WY_URL + href
                elif 'pdf' in label:
                    self.pdf_link = _WY_URL + href
                elif 'references' in label:
                    self.ref_references = _WY_URL + href


    def __repr__(self):
        return u'' + \
        '                    ref_id: %s\n' % self.ref_id + \
        '                     title: %s\n' % td(self.title) + \
        '                   authors: %s\n' % self.authors + \
        '               publication: %s\n' % self.publication + \
        '                    volume: %s\n' % self.volume + \
        '                      date: %s\n' % self.date + \
        '                     pages: %s\n' % self.pages + \
        '               pubmed_link: %s\n' % self.pubmed + \
        '                 pubmed_id: %s\n' % self.pubmed_id + \
        '             crossref_link: %s\n' % self.crossref + \
        '                  CAS_link: %s\n' % self.cas + \
        '             abstract_link: %s\n' % self.abstract + \
        '           references_link: %s\n' % self.ref_references + \
        '                  pdf_link: %s\n' % self.pdf_link + \
        '                       doi: %s\n' % self.doi + \
        'web of science times cited: %s\n' % self.citetimes




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

    """

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


    # Step 3 - Create reference objects
    #--------------------------------------------------------------------------
    # The reference objects parse out information for each reference
    # as well as external links.
    if verbose:
        print('Creating reference objects')
    ref_objects = [WileyRef(ref_tag, ref_id) for \
                    ref_tag, ref_id in \
                    zip(ref_tags, range(n_refs))]


    #All done!
    #---------
    return ref_objects


def get_entry_info(url):
    return WileyEntry(url, verbose=True)