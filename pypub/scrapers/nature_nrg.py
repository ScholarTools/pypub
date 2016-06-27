# -*- coding: utf-8 -*-
"""
http://www.nature.com/nature/journal/v482/n7385/full/nature10886.html

Module: pypub.scrapers.nature

Status: In progress

#TODO: Add tests, this stuff will break!
#TODO: Allow extraction of the refs as a csv,json,xml, etc - this might go into utils

#TODO: STANDARDIZE THE FUNCTION INPUTS!!!
     - Either get references and get entry info both using a URL as the input, or
       both using a DOI/PII as an input. Different inputs for each is confusing.

Tasks/Examples:
---------------
1) ****** Get references given a doi value *******
from pypub.scrapers import nature as nt

refs = nt.get_references('0006899387903726',verbose=True)

refs = nt.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a Nature URL.


"""
# Standard
import sys
import os
import re

# Third party
import requests
from bs4 import BeautifulSoup

# Local
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pypub.utils import get_truncated_display_string as td
from pypub.utils import findValue
from pypub.utils import convert_to_dict
from pypub_errors import *
from pypub.scrapers.base_objects import *

_NT_URL = 'http://nature.com'


class NatureAuthor(BaseAuthor):

    def __init__(self, li_tag):

        """

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
        self.name = li_tag.find('span', {'class' : 'fn'}).text


        # Extract all integers from the superscripted text
        # This way each author object has a list of superscripts
        # corresponding to the affiliation list indices.
        # For some reason, the superscripts aren't actually visible
        # on the Nature site. But they exist in the HTML.

        sup = li_tag.find_all('sup')

        sups = []
        for x in sup:
            # Get text of superscripts
            text = x.text

            '''
            # Check if there are linked footnotes
            # Footnotes are different from affiliations and do
            # not correspond to any text in the affiliations list.
            footnotes = x.find_all('a')
            if footnotes is not None:
                for footnote in footnotes:
                    if footnote.text != '':
                        text = text.replace(footnote.text, '')
            '''

            # Clean up text and extract the numbers
            text = text.replace(' ', '')
            splitlist = text.split(',')
            for num in splitlist:
                if num != '':
                    sups.append(num)

        self.supers = sups
        #self.affiliations = []
        self.email = None

    #
    def populate_affiliations(self,aff_labels):
        self.affiliations = [aff_labels[int(x)-1] for x in self.sups]

    def __repr__(self):
        return u'' + \
                'name: %s\n' % self.name + \
        'affiliations: %s\n' % self.affiliations + \
             'email: %s\n' % self.email


class NatureEntry(BaseEntry):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper.

    Attributes
    ----------
    doi : string
        The unique identifier

    See Also
    ----------
    NatureRef

    Examples
    ----------
    from pypub.scrapers import nature as nt
    url = 'http://www.nature.com/nature/journal/v482/n7385/full/nature10886.html'
    nte = nt.NatureEntry(url,verbose=True)

    Improvements
    ----------
    - Add citing articles

    """
    def __init__(self, soup, verbose=False):
        super().__init__()

        # Get entry content information
        content = soup.find('div', {'id' : 'content'})
        mainContent = content.find('header')
        if mainContent is None:
            raise ParseException('Unable to find main content of page')


        # Metadata:
        # ---------
        self.title = findValue(mainContent, 'h1', 'article-heading', 'class')

        # Isolate the entry citation line
        citation = mainContent.find('dl', {'class' : 'citation'})

        self.publication = findValue(citation, 'dd', 'journal-title', 'class')

        # For old journal issues, two dates are given: original publication date and
        # online publication date. This returns the original journal pub date.
        self.date = citation.find('time').text[1:-1] # Get rid of parentheses surrounding it
        self.year = self.date[-4:]

        # Get rid of commas and whitespace from volume
        vol = findValue(citation, 'dd', 'volume', 'class').replace(',', '')
        self.volume = vol.replace('\n', '')

        self.pages = findValue(citation, 'dd', 'page', 'class')

        # Nature pages for some reason don't list keywords...
        self.keywords = None

        # DOI Retrieval:
        # --------------
        # This might be more reliable than assuming we have the DOI in the title
        self.doi = findValue(citation, 'dd', 'doi', 'class')
        self.doi = self.doi[4:] # to get rid of 'DOI:' at the beginning

        # Abstract:
        # ---------
        self.abstract = ''
        abstract_section = soup.find('div', {'id' : 'abstract'})
        abstract_content = abstract_section.find('p')
        if abstract_content is not None:
            self.abstract = self.abstract + abstract_content.text

        # Authors:
        # --------
        # Find list items within the ordered list with id 'authors'
        authorList = mainContent.find('ul', {'class':'authors'}).find_all('li')
        self.authors = [NatureAuthor(x) for x in authorList]

        # Get list of affiliations from bottom of page
        author_info = soup.find('div', {'id' : 'author-information'})
        aff_section = author_info.find('ol', {'class' : 'affiliations'})
        aff_tags = aff_section.find_all('li', recursive=False)
        self.affiliations = [a.find('h3').text for a in aff_tags]

        corr = author_info.find('a', {'class' : 'contact'})
        corr_name = corr.text
        email = _NT_URL + corr['href']


        # Assign affiliations to authors
        for author in self.authors:
            author.populate_affiliations(self.affiliations)
            if author.name == corr_name:
                author.email = email



    def __repr__(self):
        return u'' + \
            'title: %s\n' % td(self.title) + \
            'authors: %s\n' % self.authors + \
            'keywords: %s\n' % self.keywords + \
            'publication: %s\n' % self.publication + \
            'date: %s\n' % self.date + \
            'volume: %s\n' % self.volume + \
            'pages: %s\n' % self.pages + \
            'doi: %s\n' % self.doi + \
            'abstract: %s\n' % self.abstract


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class NatureRef(BaseRef):
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
        self.title = findValue(ref_tags, 'span', 'title', 'class')
        authorlist = ref_tags.find_all('span', {'class' : 'author'})
        self.authors = [x.text for x in authorlist]

        # Note: we can also get individual authors if we would like.
        #
        # Each reference author is given a separate <span> tag with the class 'author'
        # so individual authors can be extracted
        #

        self.publication = findValue(ref_tags, 'span', 'source-title', 'class')
        self.volume = findValue(ref_tags, 'span', 'volume', 'class')
        self.date = findValue(ref_tags, 'span', 'year', 'class')

        firstp = findValue(ref_tags, 'span', 'start-page', 'class')
        lastp = findValue(ref_tags, 'span', 'end-page', 'class')
        if (firstp is not None) and (lastp is not None):
            self.pages = firstp + '-' + lastp
        else:
            self.pages = None


        # Reference Meta Section:
        #------------------------------

        self.crossref = None
        self.pubmed = None
        self.doi = None
        self.cas = None
        self.isi = None
        self.ads = None


        # All links are kept in a ul tag with the class 'cleared'
        links = ref_tags.find('ul', {'class' : 'cleared'})

        # Only proceed if links are found
        if links is not None:
            links = links.find_all('li')

            # Check against all possible link options and save links.
            #
            for link in links:
                label = link.text.lower()
                href = link.find('a', href=True)['href']

                if 'article' in label:
                    self.doi = href[href.find('10.'):] # Grab everything starting with '10.' in link
                    if self.doi == -1:
                        self.doi = None
                    # Called 'Article' link, but url is http://dx.doi.org/10.######
                    # Redirects to article page
                    self.crossref = href
                elif 'pubmed' in label:
                    self.pubmed = href
                elif 'cas' in label:
                    self.cas = href
                elif 'isi' in label:
                    self.isi = href
                elif 'ads' in label:
                    self.ads = href


    def __repr__(self):
        return u'' + \
        'ref_id: %s\n' % self.ref_id + \
        'title: %s\n' % td(self.title) + \
        'authors: %s\n' % self.authors + \
        'publication: %s\n' % self.publication + \
        'volume: %s\n' % self.volume + \
        'date: %s\n' % self.date + \
        'pages: %s\n' % self.pages + \
        'pubmed_link: %s\n' % self.pubmed + \
        'crossref_link: %s\n' % self.crossref + \
        'CAS_link: %s\n' % self.cas + \
        'ISI_link: %s\n' % self.isi + \
        'ADS_link: %s\n' % self.ads + \
        'doi: %s\n' % self.doi


def get_references(input, verbose=False):
    """
    This function gets references for a Nature URL

        e.g. http://www.nature.com/nature/journal/v482/n7385/full/nature10886.html

    """

    # Step 1 - Make the request
    #--------------------------------------------------------------------------
    soup = make_soup(input, verbose)

    # Step 2 - Get the references tags
    #--------------------------------------------------------------------------
    # The reference tags contain most of the information about references
    # They are however missing a lot of the linking information
    # e.g. link to the article, pdf download, etc

    # Ordered list of references will be within a div with the id 'references'
    reference_section = soup.find('div', {'id' : 'references'})
    ref_list = reference_section.find('ol', {'class' : 'references'})

    if ref_list is None:
        # Then we might be a guest. In other words, we might not have sufficient
        # privileges to access the data we want. Generally this is protected via
        # IP mask. When I'm working from home I need to VPN into work so
        # that I can access the data :/
        print("reference_section is None")

        # TODO: check what this guest tag actually looks like
        # When we don't have proper access rights, this is present in the html
        guest_tag = ('li', {'id' : 'menuGuest'})

        temp = soup.find(*guest_tag)
        if temp is None:
            #We might have no references ... (Doubtful)
            raise ParseException("References were not found ..., code error likely")
        else:
            raise InsufficientCredentialsException("Insufficient access rights to get referencs, requires certain IP addresses (e.g. university based IP)")

    ref_tags = ref_list.find_all('li', recursive=False)

    n_refs = len(ref_tags)

    if n_refs == 0:
        return None


    # Step 3 - Create reference objects
    #--------------------------------------------------------------------------
    # The reference objects parse out information for each reference
    # as well as external links.
    if verbose:
        print('Creating reference objects')
    ref_objects = [NatureRef(ref_tag, ref_id) for \
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

    soup = make_soup(input)

    # Get entry content information
    toolbar = soup.find('div', {'id' : 'download-links'})
    if toolbar is None:
        raise ParseException('Unable to find download section of page')

    link = toolbar.find('li', {'class' : 'articlepdf'})
    href = link.find('a')['href']
    pdf_link = _NT_URL + href

    return pdf_link


def get_entry_info(input, verbose=False, soup=None):
    if soup is None:
        soup = make_soup(input, verbose)
    return NatureEntry(soup, verbose)


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


def make_soup(input, verbose=False):
    # Check if the input is a DOI or URL
    if is_url(input):
        soup = connect(input, isLink=True, verbose=verbose)
    elif is_doi(input):
        soup = connect(input, isLink=False, verbose=verbose)
    else:
        raise ValueError('Input not recognized as a valid DOI or Nature URL')

    return soup


def is_url(input):
    if input.find('nature') != -1:
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


def connect(input, isLink=False, verbose=None):

    # Construct valid Nature URL from given DOI
    # TODO: figure out how to get URL from DOI

    if isLink:
        url = input
    else:
        url = 'http://dx.doi.org/' + input


    # Web page retrieval
    #-------------------
    s = requests.Session()

    if verbose:
        print('Requesting main page for: %s' % url)

    resp = s.get(url)
    soup = BeautifulSoup(resp.text)

    #with open('test_site.html', 'wb') as file:
    #    file.write(resp.content)


    return soup
