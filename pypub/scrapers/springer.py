# -*- coding: utf-8 -*-
"""
http://link.springer.com/article/10.1186/s12984-016-0150-9

Module: pypub.scrapers.springer

Status: In progress

Note about Springer version:
----------------------------
As of the making of this scraper (May 12, 2016), many article pages on SpringerLink contain a banner
stating "We're trialling a new version of this page". This scraper corresponds to this new page layout,
and does not work for the old SpringerLink pages (which can right now still be reached by appending
'?view=classic' to the URL for those articles that automatically go to the new format).



#TODO: Add tests, this stuff will break!
#TODO: Allow extraction of the refs as a csv,json,xml, etc - this might go into utils

#TODO: STANDARDIZE THE FUNCTION INPUTS!!!
     - Either get references and get entry info both using a URL as the input, or
       both using a DOI/PII as an input. Different inputs for each is confusing.

Tasks/Examples:
---------------
1) ****** Get references given a doi value *******
from pypub.scrapers import springer as sp

refs = sp.get_references('0006899387903726',verbose=True)

refs = sp.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a Springer Link URL.

"""

import sys
import os

#TODO: Move this into a compatability module
#-----------------------------------------------------
PY2 = sys.version_info.major == 2

if PY2:
    from urllib import unquote as urllib_unquote
    from urllib import quote as urllib_quote
else:
    from urllib.parse import unquote as urllib_unquote
    from urllib.parse import quote as urllib_quote
#-----------------------------------------------------

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ScholarTools.pypub.pypub.utils import get_truncated_display_string as td
from ScholarTools.pypub.pypub.utils import findValue

from ScholarTools.pypub.pypub import errors

import re
#-------------------
import requests
from bs4 import BeautifulSoup

_SP_URL = 'http://www.link.springer.com'

class SpringerAuthorAffiliations(object):

    def __init__(self, li_tag):
        self.id = li_tag['id']
        self.raw = li_tag.contents[1]

    def __repr__(self):
        return u'' + \
        ' id: %s\n' % self.id + \
        'raw: %s\n' % td(self.raw)


class SpringerAuthor(object):

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

        Improvements
        ------------
        1) Allow retrieval of icon info:
            - corresponding author info
            - email author
        2) Split name into parts

        """

        # Get author name
        self.raw = li_tag.contents[0]

        # Extract all integers from the superscripted text
        # This way each author object has a list of superscripts
        # corresponding to the affiliation list indices.
        super = li_tag.find('sup').text
        self.superscripts = re.findall(r'\d+', super)

        if super.find('*') != -1:
            self.contact = 1
        else:
            self.contact = None

        self.email = None

    #
    def populate_affiliations(self,aff_labels):
        self.affiliations = [aff_labels[int(x)-1] for x in self.superscripts]

    def __repr__(self):
        return u'' + \
                'name: %s\n' % self.raw + \
        'affiliations: %s\n' % self.affiliations + \
             'email: %s\n' % self.email


class SpringerEntry(object):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper.

    Attributes
    ----------
    doi : string
        The unique identifier

    See Also
    ----------
    SpringerRef

    Examples
    ----------
    from pypub.scrapers import springer as sp
    url = 'http://link.springer.com/article/10.1186/s12984-016-0150-9'
    wye = sp.SpringerEntry(url,verbose=True)

    Improvements
    ----------
    - Add citing articles

    """
    def __init__(self, url, verbose=False, session=None):

        self.url = url

        # Extract the DOI from the URL
        articlestart = url.find('article/') # Find the occurrence of 'article/' in the url
        self.doi = url[(articlestart+8):]

        # Web page retrieval
        #-------------------
        if session is None:
            s = requests.Session()
        else:
            s = session

        if verbose:
            print('Requesting main page for doi: %s' % self.doi)

        # Get webpage
        r = s.get(url)

        soup = BeautifulSoup(r.text)
        self.soup = soup

        #
        # Some newer journals/articles are using an updated, minimalistic page layout.
        # This isn't compatible with the HTML tags of the old version, so we need to
        # check for that and use the old site view if necessary.
        #
        backlink = soup.find('a', {'id' : 'wol1backlink'})
        if backlink is not None:
            url = _SP_URL + '/wol1/doi/' + self.doi + '/abstract'
            r = s.get(url)
            soup = BeautifulSoup(r.text)



        mainContent = soup.find('div', {'id' : 'mainContent'})
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
        keybox = soup.find('ul', {'class' : 'keywordList'})
        #if keybox is None:
        #    raise errors.ParseException('Unable to find keywords')
        #wordlist = keybox.find_all('li')
        #self.keywords = [w.text for w in wordlist]
        self.keywords = None

        # DOI Retrieval:
        #---------------
        # This might be more reliable than assuming we have the DOI in the title
        self.doi = findValue(mainContent, 'p', 'doi', 'id')
        self.doi = self.doi[5:] # to get rid of 'DOI: ' at the beginning


        # Authors:
        #---------
        # Find list items within the ordered list with id 'authors'
        authorList = mainContent.find('ol', {'id':'authors'}).find_all('li')
        self.authors = [SpringerAuthor(x) for x in authorList]

        # Find all list items with the 'affiliation' class
        # The content is kept in a <p> tag within each list item
        aff_tags = mainContent.find_all('li', {'class' : 'affiliation'})
        self.affiliations = [a.find('p').text for a in aff_tags]

        # Clean up strings - Not sure if necessary
        for a in range(len(self.affiliations)):
            self.affiliations[a] = self.affiliations[a].replace(', and ', '')
            self.affiliations[a] = self.affiliations[a].replace('            ', '')

        corr = mainContent.find('p', {'id' : 'correspondence'})
        email = findValue(corr, 'a', 'Link to email address', 'title')

        # Assign affiliations to authors
        for author in self.authors:
            author.populate_affiliations(self.affiliations)
            if author.contact == 1:
                author.email = email



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
    def from_doi(doi):
        entry = SpringerEntry(_SP_URL + '/doi/' + str(doi) + '/abstract')
        return entry


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class SpringerRef(object):
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
        if (firstp is not None) and (lastp is not None):
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
                    self.crossref = _SP_URL + href
                elif 'pubmed' in label:
                    self.pubmed_id = re.search('[^id=]+$',href).group(0)
                    self.pubmed_id = urllib_unquote(self.pubmed_id)[1:]
                    self.pubmed = _SP_URL + href
                elif 'web ' in label:
                    self.citetimes = re.search('[^: ]+$',label).group(0)
                elif label in ('cas', 'cas,'):
                    self.cas = _SP_URL + href
                elif 'abstract' in label:
                    self.abstract = _SP_URL + href
                elif 'pdf' in label:
                    self.pdf_link = _SP_URL + href
                elif 'references' in label:
                    self.ref_references = _SP_URL + href


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




def get_references(doi, verbose=False):
    """
    This function gets references for a Springer URL that is of the
    form:

        http://www.link.springer.com/article/####################

        e.g. http://link.springer.com/article/10.1186/s12984-016-0150-9

    """

    # TODO: Move this to WileyEntry - I'm thinking of making this its own
    # class as well
    #
    # TODO: Make this a class reference parser

    # If you view the references, they should be wrapped by a <ul> tag
    # with the attribute class="article-references"
    REFERENCE_SECTION_TAG =  ('div', {'class' : 'bibliography'})

    # TODO: check what this guest tag actually looks like
    # When we don't have proper access rights, this is present in the html
    GUEST_TAG = ('li', {'id' : 'menuGuest'})

    # Entries are "li" tags with ids of the form:
    #   b1, b2, b3, etc.
    # Hopefully this doesn't grab other random list items on the page
    REFERENCE_TAG = ('li', {'id' : re.compile('b*')})

    # This is the URL to the page that contains the document info, including
    # reference material
    BASE_URL = _SP_URL + '/doi/'

    # Ending with the references listed
    SUFFIX = '/references'


    # Step 1 - Make the request
    #--------------------------------------------------------------------------
    s = requests.Session()

    if verbose:
        print('Requesting main page for doi: %s' % doi)
    r = s.get(BASE_URL +  doi + SUFFIX)

    soup = BeautifulSoup(r.text)

    #
    # Some newer journals/articles are using an updated, minimalistic page layout.
    # This isn't compatible with the HTML tags of the old version, so we need to
    # check for that and use the old site view if necessary.
    #
    backlink = soup.find('a', {'id' : 'wol1backlink'})
    if backlink is not None:
        url = _SP_URL + '/wol1/doi/' + doi + '/references'
        r = s.get(url)
        soup = BeautifulSoup(r.text)


    # Step 2 - Get the references tags
    #--------------------------------------------------------------------------
    # The reference tags contain most of the information about references
    # They are however missing a lot of the linking information
    # e.g. link to the article, pdf download, etc

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
    ref_objects = [SpringerRef(ref_tag, ref_id) for \
                    ref_tag, ref_id in \
                    zip(ref_tags, range(n_refs))]


    #All done!
    #---------
    return ref_objects


def get_entry_info(url, verbose=False, session=None):
    return SpringerEntry(url, verbose, session)