# -*- coding: utf-8 -*-
"""

Module: pypub.scrapers.taylorfrancis


NOTE: THIS IS FOR A DEPRECATED VERSION OF T&F!! THE HTML TAGS NEED TO BE CHANGED.



Tasks/Examples:
---------------
1) ****** Get references given a doi value *******
from pypub.scrapers import ________ as __

refs = __.get_references('0006899387903726',verbose=True)

refs = __.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a URL.

"""
# Standard imports
import sys
import os

# Third party imports
import requests
from bs4 import BeautifulSoup

# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pypub.utils import get_truncated_display_string as td
from pypub.utils import findValue
from pypub.pypub_errors import *
from pypub.scrapers.base_objects import *

_TF_URL = 'http://tandfonline.com/'


class TaylorFrancisAuthor(BaseAuthor):

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
        self.name = li_tag.contents[0].text

        self.affiliations = []
        self.email = None
        self.superscripts = []

        self.affmap = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}

        # TODO: THIS DOESN'T WORK. FIX IT.
        # The superscripts are siblings of the li_tag, not children!
        # Need to figure out how to get them and separate them by author.
        # Parse superscripts
        supers = li_tag.find_all('sup')
        for x in supers:
            if x.text != '*':
                self.superscripts.append(x.text)

    def populate_affiliations(self, aff_labels):
        self.affiliations = [aff_labels[self.affmap[x]] for x in self.superscripts]

    def __repr__(self):
        return u'' + \
                'name: %s\n' % self.name + \
        'affiliations: %s\n' % self.affiliations + \
             'email: %s\n' % self.email


class TaylorFrancisEntry(BaseEntry):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper.

    Attributes
    ----------
    doi : string
        The unique identifier

    See Also
    ----------
    TaylorFrancisRef

    Examples
    ----------
    from pypub.scrapers import taylorfrancis as tf
    url = ''
    tfe = __.TaylorFrancisEntry(url,verbose=True)

    Improvements
    ----------
    - Add citing articles

    """
    def __init__(self, soup, verbose=False):
        super().__init__()

        # Get entry content information
        mainContent = soup.find('div', {'id': 'journal_content'})
        if mainContent is None:
            mainContent = soup.find('div', {'id': 'pb-page-content'})
        if mainContent is None:
            raise ParseException('Unable to find main content of page')

        # Metadata:
        # ---------
        titlebox = mainContent.find('div', {'class': 'description'})
        if titlebox is not None:
            self.title = titlebox.find('h1').text.title()
        else:
            self.title = None

        import pdb
        pdb.set_trace()

        # This box contains the publication name as well as Volume and Issue
        pubbox = mainContent.find('div', {'class': 'borderedmodule'})
        pubbox = pubbox.find('td')
        self.publication = findValue(pubbox, 'h2')
        if self.publication is not None:
            self.publication = self.publication.strip()

        # Parsing out the integer values of the volume and issue
        vol_issue = pubbox.find('h3')
        if vol_issue is None:
            raise ParseException('Unable to find volume and issue data')
        else:
            vol_issue = vol_issue.text
            issue_index = vol_issue.find('Issue')

            # If an issue number is listed, extract it
            if issue_index != -1:
                vol_text = vol_issue[0:issue_index]
                all_issue_text = vol_issue[issue_index:]
                issue_text = all_issue_text[0:all_issue_text.find(',')]
                issue_num_text = [x for x in issue_text if x.isdigit()]
                self.issue = ''.join(issue_num_text)
            else:
                vol_text = vol_issue
                self.issue = None

            vol_num_text = [x for x in vol_text if x.isdigit()]
            self.volume = ''.join(vol_num_text)



        # Two dates are given: original publication date and
        # online publication date. This returns the original journal pub date.
        datebox = mainContent.find('div', {'class' : 'articleDates'})
        if datebox is None:
            raise ParseException('Unable to find publishing dates')
        alldates = datebox.find_all('li')
        full_date_text = alldates[-1].text
        date_index = full_date_text.find('Published online: ')
        if date_index > -1:
            date = full_date_text[(date_index + 18):]
        else: date = ''

        self.date = date
        self.year = self.date[-4:]

        # Keywords
        # TaylorFrancis keeps keywords below the abstract, separate from header info
        abstract_section = mainContent.find('div', {'class' : 'abstract'})
        keybox = abstract_section.find('ul', {'class' : 'keywords'})
        if keybox is None:
            raise ParseException('Unable to find keywords')
        wordlist = keybox.find_all('li')
        self.keywords = [w.text[0:w.text.find(',')] for w in wordlist]


        metabox = mainContent.find('div', {'class' : 'doiMeta'})

        self.pages = findValue(mainContent, 'div', label_type='class', label_name='pageRange')


        # DOI Retrieval:
        # --------------
        # This might be more reliable than assuming we have the DOI in the title
        self.doi = findValue(metabox, 'dd')
        doi_startindex = self.doi.find('10.')
        self.doi = self.doi[doi_startindex:]  # to get rid of whitespace at the beginning


        # Authors:
        # --------
        # Find list items within the ordered list with id 'authors'
        # Need to find only classless li's so that it doesn't also retrieve the child li's corresponding
        # to author affiliations at this stage.
        authorList = metabox.find_all('span', {'class' : 'hlFld-ContribAuthor'})
        self.authors = [TaylorFrancisAuthor(x) for x in authorList]

        # Find the list of affiliations from the tabbed module at the bottom of the page
        tabModule = mainContent.find('div', {'id' : 'tabModule'})
        aff_list = tabModule.find('ul', {'class' : 'affiliations'})
        affs = aff_list.find_all('li')
        affiliations = []
        for aff in affs:
            affiliations.append(aff.text[1:])  # Get rid of the leading superscript letter

        # Assign affiliations to authors
        for author in self.authors:
            author.populate_affiliations(affiliations)

    def __repr__(self):
        return u'' + \
        '       title: %s\n' % td(self.title) + \
        '     authors: %s\n' % self.authors + \
        '    keywords: %s\n' % self.keywords + \
        ' publication: %s\n' % self.publication + \
        '        date: %s\n' % self.date + \
        '      volume: %s\n' % self.volume + \
        '       issue: %s\n' % self.issue + \
        '       pages: %s\n' % self.pages + \
        '         doi: %s\n' % self.doi

    @classmethod
    def from_doi(doi):
        entry = TaylorFrancisEntry(_TF_URL + '/doi/abs/' + str(doi))
        return entry


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class TaylorFrancisRef(BaseRef):
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
        self.ref_tags = ref_tags

        # Reference Bibliography Section:
        #--------------------------------
        self.ref_id = ref_id + 1 # Input is 0 indexed

        self.volume = None
        self.pages = None

        all_text = ref_tags.find_all(text=True)
        self.citation = all_text[1]

        # 'all_text' is a list of the text segments within each citation.
        # If it is a short list, it means that the citation is likely a book,
        # and doesn't include page numbers, PMID, DOI, etc.
        if len(all_text) > 5:
            metadata = all_text[3]
            metadata = metadata[2:]  # Get rid of leading '; '
            divider = metadata.find(':')  # This divides volume number from page range
            self.volume = metadata[0:divider]
            self.pages = metadata[divider+1:metadata.find(';')]

        self.date = findValue(ref_tags, 'span')


        # Reference Link Section:
        #------------------------------

        self.crossref = None
        self.pubmed = None
        self.pubmed_id = None
        self.doi = None
        self.web_of_science = None

        # External links (i.e. PubMed, CrossRef) are kept in <a> tags,
        # while the IDs are conveniently kept in <pub-id> tags
        links = ref_tags.find_all('a')
        ids = ref_tags.find_all('pub-id')

        for link in ids:
            id_type = link['pub-id-type']
            if id_type == 'pmid':
                self.pubmed_id = link.text
            elif id_type == 'doi':
                self.doi = link.text

        if links is not None:
            for link in links:
                href = link['href'][1:]  # Get rid of leading '/'
                text = link.text.lower()

                if 'crossref' in text:
                    self.crossref = _TF_URL + href
                elif 'pubmed' in text:
                    self.pubmed = _TF_URL + href
                elif 'science' in text:
                    self.web_of_science = _TF_URL + href

    def __repr__(self):
        return u'' + \
        'ref_id: %s\n' % self.ref_id + \
        'citation: %s\n' % self.citation + \
        'date: %s \n' % self.date + \
        'crossref_link: %s\n' % self.crossref + \
        'pubmed: %s\n' % self.pubmed + \
        'pubmed_id: %s\n' % self.pubmed_id + \
        'doi: %s\n' % self.doi


def get_references(input, verbose=False):
    """
    This function gets references for a Taylor and Francis URL that is of the
    form:
    """

    # Step 1 - Make the request
    #--------------------------------------------------------------------------
    soup = _make_soup(input, 'references', verbose)

    # Step 2 - Get the references tags
    #--------------------------------------------------------------------------
    # The reference tags contain most of the information about references
    # They are however missing a lot of the linking information
    # e.g. link to the article, pdf download, etc

    reference_section = soup.find('ul', {'class' : 'references'})

    if reference_section is None:
        # Then we might be a guest. In other words, we might not have sufficient
        # privileges to access the data we want. Generally this is protected via
        # IP mask. When I'm working from home I need to VPN into work so
        # that I can access the data :/
        print("reference_section is None")
        # TODO: check what this guest tag actually looks like
        # When we don't have proper access rights, this is present in the html
        temp = soup.find('li', {'id' : 'menuGuest'})
        if temp is None:
            #We might have no references ... (Doubtful)
            raise ParseException("References were not found ..., code error likely")
        else:
            raise InsufficientCredentialsException("Insufficient access rights to get referencs, requires certain IP addresses (e.g. university based IP)")

    ref_tags = reference_section.find_all('li')

    n_refs = len(ref_tags)

    if n_refs == 0:
        return None


    # Step 3 - Create reference objects
    #--------------------------------------------------------------------------
    # The reference objects parse out information for each reference
    # as well as external links.
    if verbose:
        print('Creating reference objects')
    ref_objects = [TaylorFrancisRef(ref_tag, ref_id) for \
                    ref_tag, ref_id in \
                    zip(ref_tags, range(n_refs))]


    #All done!
    #---------
    return ref_objects


def get_entry_info(input, verbose=False):
    soup = _make_soup(input, 'entry', verbose)
    return TaylorFrancisEntry(soup, verbose)


def get_pdf_link(input, verbose=False, soup=None):
    if _is_url(input):
        doi = _extract_doi(input)
    elif _is_doi(input):
        doi = input
    else:
        raise ValueError('Input not recognized as a valid DOI or Taylor and Francis URL.')

    pdf_link = _TF_URL + 'doi/pdf/' + doi
    return pdf_link


def _make_soup(input, type, verbose=False):
    # Check if the input is a DOI or URL
    if _is_url(input):
        doi = _extract_doi(input)
    elif _is_doi(input):
        doi = input
    else:
        raise ValueError('Input not recognized as a valid DOI or Taylor and Francis URL.')

    # Web page retrieval
    #-------------------
    soup = _connect(doi, type, verbose)
    return soup


def _is_url(input):
    if input.find('tandfonline') != -1:
        return True
    else:
        return False


def _is_doi(input):
    if input.find('10.') == 0:
        return True
    else:
        return False


def _extract_doi(url):
    # DOI is used in Taylor and Francis URLs after the middle word, which
    # can be 'full', 'abs', or 'ref', i.e.
    # http://www.tandfonline.com/doi/full/10.1080/2326263X.2015.1134958
    # This finds the indices of the middle word and gets everything afterward
    if 'full' in url:
        articleindex = url.find('/full/')
        doi = url[articleindex+6:]
    elif 'ref' in url or 'abs' in url:
        articleindex = url.find('/ref/')
        doi = url[articleindex+5:]
    elif 'abs' in url:
        articleindex = url.find('/abs/')
        doi = url[articleindex+5:]
    elif 'figure' in url:
        articleindex = url.find('/figure/')
        doi = url[articleindex+8:]
    else:
        raise ParseException('DOI cannot be found in Taylor and Francis URL.')
    return doi


def _connect(doi, type, verbose=None):
    if type == 'entry':
        prefix = 'abs/'
    elif type == 'references':
        prefix = 'ref/'
    else:
        prefix = 'full/'

    # Construct valid Taylor and Francis URL from given DOI
    url = _TF_URL + 'doi/' + prefix + doi

    # Web page retrieval
    # -------------------
    s = requests.Session()

    if verbose:
        print('Requesting main page for doi: %s' % doi)

    resp = s.get(url)
    soup = BeautifulSoup(resp.text)

    with open('tf_test.html', 'wb') as file:
        file.write(resp.content)

    return soup
