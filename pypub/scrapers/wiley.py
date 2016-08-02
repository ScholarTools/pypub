# -*- coding: utf-8 -*-
"""
http://onlinelibrary.wiley.com/doi/10.1111/j.1440-1681.1976.tb00619.x/abstract

Module: pypub.scrapers.wiley

Status: In progress

#TODO: Add tests, this stuff will break!
#TODO: Allow extraction of the refs as a csv,json,xml, etc - this might go into utils

#TODO: STANDARDIZE THE FUNCTION INPUTS!!!
     - Either get references and get entry info both using a URL as the input, or
       both using a DOI/PII as an input. Different inputs for each is confusing.

Tasks/Examples:
---------------
1) ****** Get references given a doi value *******
from pypub.scrapers import wiley as wy

refs = wy.get_references('0006899387903726',verbose=True)

refs = wy.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a Wiley URL.


"""
# Standard imports
import sys

import os
import re

if sys.version_info.major == 2:
    from urllib import unquote as urllib_unquote
    from urllib import quote as urllib_quote
else:
    from urllib.parse import unquote as urllib_unquote
    from urllib.parse import quote as urllib_quote

# Third party imports
import requests
from bs4 import BeautifulSoup

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pypub.utils import get_truncated_display_string as td
from pypub.utils import findValue
from pypub.utils import convert_to_dict
from pypub.pypub_errors import *
from pypub.scrapers.base_objects import *

_WY_URL = 'http://onlinelibrary.wiley.com'

class WileyAuthor(BaseAuthor):

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
        super().__init__()

        # Get author name
        self.name = li_tag.contents[0]

        self.contact = None
        self.superscripts = []
        self.email = None

        # Extract all integers from the superscripted text
        # This way each author object has a list of superscripts
        # corresponding to the affiliation list indices.
        sup = li_tag.find('sup')

        if sup is not None:
            sup = sup.text
            self.superscripts = re.findall(r'\d+', sup)

            if sup.find('*') != -1:
                self.contact = 1
            else:
                self.contact = None

    #
    def populate_affiliations(self,aff_labels):
        self.affiliations = [aff_labels[int(x)-1] for x in self.superscripts]

    def __repr__(self):
        return u'' + \
                'name: %s\n' % self.name + \
        'affiliations: %s\n' % self.affiliations + \
             'email: %s\n' % self.email


class WileyEntry(BaseEntry):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper.

    Attributes
    ----------
    doi : string
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
    def __init__(self, soup, verbose=False):
        super().__init__()
        # Get entry content information
        mainContent = soup.find('div', {'id' : 'mainContent'})
        if mainContent is None:
            raise ParseException('Unable to find main content of page')

        # Check for 'Page Not Found'
        error404 = mainContent.find('div', {'id' : 'error'})
        if error404 is not None:
            raise ParseException('Article was not found.')

        # Metadata:
        #---------------
        self.title = findValue(mainContent, 'span', 'mainTitle', 'class').title()
        if self.title is not None:
            self.title = self.title.title()

        self.publication = findValue(mainContent, 'h2', 'productTitle', 'id')

        # For old journal issues, two dates are given: original publication date and
        # online publication date. This returns the original journal pub date.
        self.date = findValue(mainContent, 'span', 'issueDate', 'id')
        if self.date is not None:
            self.year = self.date[-4:]

        vol = findValue(mainContent, 'span', 'volumeNumber', 'id')
        if vol is not None:
            vol = vol.lower().replace('volume ', '')
        issue = findValue(mainContent, 'span', 'issueNumber', 'id')
        if issue is not None:
            issue = issue.lower().replace('issue ', '')
        self.volume = vol
        self.issue = issue

        self.pages = findValue(mainContent, 'span', 'issuePages', 'id')
        if self.pages is not None:
            self.pages = self.pages[6:] # to get rid of 'pages: ' at the beginning


        # Keywords and Abstract:
        #----------
        productContent = soup.find('div', {'id' : 'productContent'})
        keybox = productContent.find('div', {'class' : 'keywordLists'})
        if keybox is None:
            self.keywords = None
        else:
            wordlist = keybox.find_all('li')
            self.keywords = [w.text for w in wordlist]

        abstract_section = productContent.find('div', {'id' : 'abstract'})
        if abstract_section is not None:
            self.abstract = abstract_section.text
        else:
            self.abstract = None


        # DOI Retrieval:
        #---------------
        # This might be more reliable than assuming we have the DOI in the title
        self.doi = findValue(mainContent, 'p', 'doi', 'id')
        self.doi = self.doi[5:] # to get rid of 'DOI: ' at the beginning


        # Authors:
        #---------
        # Find list items within the ordered list with id 'authors'
        authorList = mainContent.find('ol', {'id':'authors'}).find_all('li')
        self.authors = [WileyAuthor(x) for x in authorList]

        # Find all list items with the 'affiliation' class
        # The content is kept in a <p> tag within each list item
        aff_tags = mainContent.find_all('li', {'class' : 'affiliation'})
        self.affiliations = [a.find('p').text for a in aff_tags]

        # Clean up strings - Not sure if necessary
        for a in range(len(self.affiliations)):
            self.affiliations[a] = self.affiliations[a].replace(', and ', '')
            self.affiliations[a] = self.affiliations[a].replace('            ', '')

        corr = mainContent.find('p', {'id' : 'correspondence'})
        if corr is not None:
            email = findValue(corr, 'a', 'Link to email address', 'title')
        else:
            email = ''

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
        '      issue: %s\n' % self.issue + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi + \
        '   abstract: %s\n' % self.abstract


    @classmethod
    def from_doi(doi):
        return WileyEntry(_WY_URL + '/doi/' + str(doi) + '/abstract')


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class WileyRef(BaseRef):
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
        super().__init__()
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
        else:
            self.pages = None


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
            for link in links:
                label = link.text.lower()
                href = link.find('a', href=True)['href']
                href = urllib_quote(href)

                if 'crossref' in label:
                    self.doi = href[href.find('10.'):] # Grab everything starting with '10.' in link
                    if self.doi == -1:
                        self.doi = None
                    self.doi = urllib_unquote(self.doi)
                    # CrossRef link is in the form of _WY_URL/resolve/reference/XREF?id=10.#######
                    self.crossref = _WY_URL + urllib_unquote(href)
                elif 'pubmed' in label:
                    self.pubmed_id = re.search('[^id=]+$',href).group(0)[1:] # the [1:] is to get rid of leading '='
                    self.pubmed_id = urllib_unquote(self.pubmed_id)
                    self.pubmed = _WY_URL + urllib_unquote(href)
                elif 'web ' in label:
                    self.citetimes = re.search('[^: ]+$',label).group(0)
                elif label in ('cas', 'cas,'):
                    self.cas = _WY_URL + urllib_unquote(href)
                elif 'abstract' in label:
                    self.abstract = _WY_URL + urllib_unquote(href)
                elif 'pdf' in label:
                    self.pdf_link = _WY_URL + urllib_unquote(href)
                elif 'references' in label:
                    self.ref_references = _WY_URL + urllib_unquote(href)


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


def get_references(input, verbose=False):
    """
    This function gets references for a Wiley URL that is of the
    form:

        http://www.onlinelibrary.wiley.com/doi/####################/references

        (ending could also be /abstract or /citedby)

        e.g. http://onlinelibrary.wiley.com/doi/10.1111/j.1464-4096.2004.04875.x/references

    """

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

    # Step 1 - Make the request
    #--------------------------------------------------------------------------
    soup = make_soup(input, 'references', verbose)

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
            #We might have no references ...
            return []
            #raise ParseException("References were not found")
        else:
            raise InsufficientCredentialsException("Insufficient access rights to get referencs, requires certain IP addresses (e.g. university based IP)")

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


def get_pdf_link(input):
    """
    Takes a DOI or article URL and returns the link to the pdf.
    This function currently does this by scraping the website and finding
    the link used in the "Get PDF" button on the site, but Wiley is nice
    and an alternate way of getting it is to just make the URL suffix
    '/pdf' or '/epdf'. It seems like in the new version of the article
    pages, /epdf is preferred, though /pdf is still supported.

    Ex: https://onlinelibrary.wiley.com/doi/10.########/pdf

    Parameters
    ----------
    input : str
        Can be either a DOI or a URL to an article page.

    Returns
    -------
    pdf_link : str
        URL directly to the article pdf
    """
    '''
    soup = make_soup(input, 'entry')

    # Get entry content information
    toolbar = soup.find('div', {'id' : 'promosAndTools'})
    if toolbar is None:
        raise errors.ParseException('Unable to find toolbar section of page')

    links = toolbar.find('li', {'class' : 'readcubePdf'})
    href = links.find('a', {'class' : 'readcubePdfLink'})['href']
    pdf_link = _WY_URL + href
    '''
    if is_url(input):
        doi = extract_doi(input)
    elif is_doi(input):
        doi = input
    else:
        raise ValueError('Input not recognized as a valid DOI or Wiley URL')

    pdf_link = _WY_URL + '/doi/' + doi + '/pdf'

    return pdf_link


def get_entry_info(input, verbose=False, soup=None):
    if soup is None:
        soup = make_soup(input, 'entry', verbose)
    return WileyEntry(soup, verbose)


def get_all_info(input, verbose=False):
    """
    This function is so that all information can be returned at once.
    It handles calls to get pdf link, reference information, and entry
    information. This is generally in order to limit needing to make a
    requests call three times for each function.

    For the Wiley implementation, the number of requests calls can't
    be reduced because the entry and reference information are on
    separate pages. This function still organizes the return values.

    Parameters
    ----------
    input
    verbose

    Returns
    -------

    """
    entry_info = get_entry_info(input, verbose)
    references = get_references(input, verbose)
    pdf_link = get_pdf_link(input)

    entry_dict = convert_to_dict(entry_info)



    pass


def make_soup(input, type, verbose=False):
    # Check if the input is a DOI or URL
    if is_url(input):
        doi = extract_doi(input)
    elif is_doi(input):
        doi = input
    else:
        raise ValueError('Input not recognized as a valid DOI or Wiley URL')

    # Web page retrieval
    #-------------------
    soup = connect(doi, type, verbose)
    return soup


def is_url(input):
    if input.find('wiley') != -1:
        return True
    else:
        return False

def is_doi(input):
    if input.find('10.') == 0:
        return True
    else:
        return False


def extract_doi(url):
    # First check to see which version of the URL is being used, and get ending.
    # Wiley separates info into multiple tabs, each with a unique URL
    # ending in /abstract, /references, or /citedby.
    # This is used to get the DOI
    ending = re.search('[^/]+$',url).group(0)

    # Extract the DOI from the URL
    # Get everything between 'onlinelibrary.wiley.com/doi/' and the URL ending
    doi = re.findall('doi/(.*?)/%s' %ending, url, re.DOTALL)
    doi = doi[0]

    return doi


def connect(doi, type, verbose=None):
    # Add the correct URL suffix:
    if type == 'references':
        suffix = '/references'
    elif type == 'entry':
        suffix = '/abstract'
    else:
        suffix = None

    # Construct valid Wiley URL from given DOI
    url = _WY_URL + '/doi/' + doi + suffix

    # Web page retrieval
    #-------------------
    s = requests.Session()

    if verbose:
        print('Requesting main page for doi: %s' % doi)

    r = s.get(url)
    soup = BeautifulSoup(r.text)

    #
    # Some newer journals/articles are using an updated, minimalistic page layout.
    # This isn't compatible with the HTML tags of the old version, so we need to
    # check for that and use the old site view if necessary.
    #
    backlink = soup.find('a', {'id' : 'wol1backlink'})
    if backlink is not None:
        url = _WY_URL + '/wol1/doi/' + doi + suffix
        r = requests.session().get(url)
        soup = BeautifulSoup(r.text)

    #with open('wiley_test.html', 'wb') as file:
    #    file.write(r.content)

    return soup
