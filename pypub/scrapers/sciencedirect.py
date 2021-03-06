# -*- coding: utf-8 -*-
"""
Module: pypub.scrapers.sciencedirect

Status: In progress

#TODO: Allow extraction of the refs as a csv,json,xml, etc - this might go into utils

#TODO: STANDARDIZE THE FUNCTION INPUTS!!!
     - Either get references and get entry info both using a URL as the input, or
       both using a DOI/PII as an input. Different inputs for each is confusing.


Tasks/Examples:
---------------
1) ****** Get references given a pii value *******
from pypub.scrapers import sciencedirect as sd 

refs = sd.get_references('0006899387903726',verbose=True)

refs = sd.get_references('S1042368013000776',verbose=True)

df = refs[0].to_data_frame(refs)


Currently I am building something that allows extraction of references from
a Sciencedirect URL.

"""
# Standard imports
import sys

import os
import re

# TODO: Move this into a compatability module
# -----------------------------------------------------
PY2 = sys.version_info.major == 2

if PY2:
    from urllib import unquote as urllib_unquote
else:
    from urllib.parse import unquote as urllib_unquote
# -----------------------------------------------------

# Third party imports
import pandas as pd
import requests
from bs4 import BeautifulSoup
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# Local imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..utils import get_truncated_display_string as td
from ..utils import findValue
from pypub.pypub_errors import *
from pypub.scrapers.base_objects import *


_SD_URL = 'http://www.sciencedirect.com'


class ScienceDirectAuthor(BaseAuthor):
    def __init__(self, li_tag):
        """
        
        Example:
        <li class="author small" data-refs="aff1 aff2 aff3 cor1" id="au1">John Doe MD, MSc<sup> a,b,c,
        <a class="icon-correspondence-author" href="#cor1" id="r-cor1" title="Corresponding author contact information"> </a></sup></li>
        
        Improvements
        ------------
        1) Allow retrieval of icon info:
            - corresponding author info
            - email author
        2) Split name into parts

        """
        # class="author-group" id="augrp0010"
        # author small
        # author medium last

        # <li class='Author medium last" data-refs="cor1" id="au3">
        # <a class='icon-correspondance-author'
        # <a class="icon-email-author"
        #
        # class="author-affiliations" id="augrp0010"
        #   class="affiliation" id="aff1"        

        super().__init__()

        # 1st bit of text is the name, then we have
        self.name = li_tag.contents[0]
        # KeyError would mean that there are no superscripted affiliations.
        # In this case, just set self._data_refs to None and keep moving.
        try:
            self._data_refs = re.compile('[^\S]+').split(li_tag['data-refs'])
        except KeyError:
            self._data_refs = None
        # This is a list:
        # http://www.crummy.com/software/BeautifulSoup/bs4/doc/#multi-valued-attributes
        # self._class = li_tag['class']

        # Extract all integers from the superscripted text
        # This way each author object has a list of superscripts
        # corresponding to the affiliation list indices.


        sup = li_tag.find_all('sup')

        sups = []
        for x in sup:
            # Get text of superscripts
            text = x.text

            # Check if there are linked footnotes
            # Footnotes are different from affiliations and do
            # not correspond to any text in the affiliations list.
            footnotes = x.find_all('a')
            if footnotes is not None:
                for footnote in footnotes:
                    if footnote.text != '':
                        text = text.replace(footnote.text, '')

            # Clean up text and extract the numbers
            text = text.replace(' ', '')
            splitlist = text.split(',')
            for num in splitlist:
                if num != '':
                    sups.append(num)

        self.sups = sups

        contact = li_tag.find('a', {'class': 'icon-email-author'})
        if contact == None:
            self.email = None
        else:
            self.email = contact['href']
            self.email = self.email.replace('mailto:', '')  # Get rid of leading 'mailto: '
            self.email = self.email.strip()

    def populate_affiliations(self, aff_dict):
        self.affiliations = [aff_dict[x] for x in self.sups]

    def __repr__(self):
        return u'' + \
               'name: %s, ' % self.name + \
               'affiliations: %s\n' % self.affiliations + \
               'email: %s\n' % self.email


class ScienceDirectEntry(BaseEntry):
    """
    This could be a step above the reference since it would, for example,
    contain all authors on a paper    
    
    Attributes
    ----------
    pii : string
        The unique identifier
        
    See Also
    --------
    ScienceDirectRef
    
    Examples
    --------
    from pypub.scrapers import sciencedirect as sd 
    url = 'http://www.sciencedirect.com/science/article/pii/S1042368013000776'
    #More affiliations
    url = 'http://www.sciencedirect.com/science/article/pii/S1042368013000818'
    sde = sd.ScienceDirectEntry(url,verbose=True)
    
    Improvements
    ------------
    - Add citing articles
    - Add Recommended Articles
    
    """

    def __init__(self, soup, verbose=False):
        super().__init__()

        # This div and id are mobile site specific
        article_abstract = soup.find('div', id='article-abstract')
        if article_abstract is None:
            raise ParseException('Unable to find abstract section of page')

        # Things to get:
        # --------------
        self.publication = findValue(article_abstract, 'a', 'publication-title', 'class')

        self.date = findValue(article_abstract, 'span', 'cover-date', 'class')
        self.year = self.date[-4:]

        temp = findValue(article_abstract, 'p', 'publication-volume-issue', 'class')
        self.volume = re.findall(', (.*?):', temp, re.DOTALL)
        self.volume = self.volume[0]

        self.first_page = findValue(article_abstract, 'span', 'first-page', 'class')
        self.last_page = findValue(article_abstract, 'span', 'last-page', 'class')
        self.pages = self.first_page + "-" + self.last_page
        # special_issue #p,publication-special-issue

        # Abstract
        # --------
        self.abstract = None
        abstract_sections = article_abstract.find_all('section', {'class' : 'article-abstract'})
        for a in abstract_sections:
            if a.find('li') is not None:
                continue
            paragraph = a.find('p', {'class' : 'para'})
            if paragraph is not None:
                self.abstract = paragraph.text
                break

        # DOI retrieval
        # -------------
        # Could also graph href inside of the class and strip http://dx.doi.org/
        # This might be more reliable than assuming we have doi:asdfasdf
        self.doi = findValue(article_abstract, 'span', 'article-doi', 'class')
        if self.doi is not None:
            self.doi = self.doi.replace('doi:', '')  # doi:10.######### => remove 'doi":'

        self.title = findValue(article_abstract, 'h1', 'article-title', 'class')

        # Authors:
        # -------
        # Look for <li> tags with class="author*"
        # TODO: Can move compiling to initialization
        self.authors = [ScienceDirectAuthor(x) for x in article_abstract.find_all('li', class_=re.compile('^author'))]

        aff_tags = article_abstract.find_all('li', {'class' : 'affiliation'})

        if len(aff_tags) != 1:
            # ScienceDirect uses letter superscripts for author affiliations rather than numbers, making them
            # annoying to index. This takes the footnote-style list of affiliated institutions and makes a
            # dict with the superscript letters as keys.
            superscripts = []
            aff_names = []
            for x in aff_tags:
                script = x.find('span')
                if script is None:
                    aff_names.append(str(x.contents[0]))
                else:
                    superscripts.append(x.find('span').text)
                    aff_names.append(str(x.contents[1]))

            aff_dict = dict(zip(superscripts, aff_names))

            # For each author, the aff_dict is used to assign the appropriate affiliation(s) to the author
            for author in self.authors:
                author.populate_affiliations(aff_dict)
        else:
            # If there is only one affiliation listed, all authors share that affiliation
            for author in self.authors:
                author.affiliations = aff_tags[0].text

        keyword_tags = article_abstract.find_all('li', {'class': 'article-keyword'})
        self.keywords = [x.text for x in keyword_tags]

    def __repr__(self):
        return u'' + \
            '      title: %s\n' % td(self.title) + \
            '    authors: %s\n' % self.authors + \
            '   keywords: %s\n' % self.keywords + \
            'publication: %s\n' % self.publication + \
            '       date: %s\n' % self.date + \
            '     volume: %s\n' % self.volume + \
            '      pages: %s\n' % self.pages + \
            '        doi: %s\n' % self.doi + \
            '   abstract %s \n' % self.abstract

    @classmethod
    def from_pii(pii):
        return ScienceDirectEntry(_SD_URL + '/science/article/pii/' + pii)


# TODO: Inherit from some abstract ref class
# I think the abstract class should only require conversion to a common standard
class ScienceDirectRef(BaseRef):
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

    def __init__(self, ref_tags, ref_id, ref_link_info=None):
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
        super().__init__()

        # Reference Bibliography Section:
        # -------------------------------

        # Example str: <span class="r_volume">Volume 47</span>
        self.ref_id = ref_id + 1  # Input is 0 based
        self.title = findValue(ref_tags, 'li', 'reference-title', 'class')
        all_authors = ref_tags.find_all('span', {'class' : 'reference-author'})
        self.authors = [x.text for x in all_authors]
        #self.authors = findValue(ref_tags, 'li', 'reference-author', 'class')
        # NOTE: We can also get individual authors if we would like.
        #        
        #   Search would be on: 
        #       <span class="reference-author">
        #   instead of on the list.

        # Unfortunately r_publication is found both for the title and for
        # the publication. Some custom code is needed to first go into a r_series
        # span and then to the publication
        self.publication = None
        r_source_tag = ref_tags.find('span', {'class': 'r_series'})

        if r_source_tag is not None:
            pub_tag = r_source_tag.find('span', {'class': 'r_publication'})
            if pub_tag is not None:
                self.publication = pub_tag.text.replace('\\xa0', ' ')

        temp_volume = findValue(ref_tags, 'span', 'r_volume', 'class')
        if temp_volume is None:
            self.volume = None
        else:
            self.volume = temp_volume.replace('Volume ', '')

        self.issue = findValue(ref_tags, 'span', 'r_issue', 'class')
        self.series = findValue(ref_tags, 'span', 'r_series', 'class')
        self.date = findValue(ref_tags, 'span', 'r_pubdate', 'class')

        temp_pages = findValue(ref_tags, 'span', 'r_pages', 'class')
        if temp_pages is None:
            self.pages = None
        else:
            # TODO: is the unicode working properly ??? 576â€“577 and ideally 576-577
            self.pages = temp_pages.replace('pp. ', '')

        # Reference Meta Section:
        # -----------------------
        self.scopus_link = None
        self.doi = None
        self._data_sceid = None
        self.pii = None
        self.pdf_link = None
        self.scopus_cite_count = None
        self.aps_full_text = None

        if ref_link_info is not None:
            link_soup = BeautifulSoup(ref_link_info)

            # Each section is contained a div tag with the class boxLink, although
            # some classes have more text in the class attribute, thus the *)
            #box_links = link_soup.find_all('div', {'class': re.compile('boxLink*')})
            box_links = link_soup.find_all('div', {'class' : 'boxLink'})

            # This code is a bit hard to read but each 'if statement' shows what
            # is needed in order to resolve the item.
            for box_link in box_links:
                div_class_values = box_link.attrs['class']
                link_tag = box_link.find('a')
                if 'SC_record' in div_class_values:
                    # "View Record in Scopus"
                    # They changed to returning a full link
                    # I should really use a library to resolve based on both
                    # although the input should be the current page, not the base
                    # self.scopus_link = _SD_URL + link_tag.attrs['href']
                    self.scopus_link = link_tag.attrs['href']
                elif 'class' in link_tag.attrs and 'S_C_pdfLink' in link_tag.attrs['class']:
                        # Link to PDF
                        self.pdf_link = _SD_URL + link_tag.attrs['href']
                elif 'class' in link_tag.attrs and 'cLink' in link_tag.attrs['class']:
                        # Article Link
                        temp = link_tag.attrs['href']
                        match = re.search('/pii/(.*)', temp)
                        self.pii = match.group(1)
                        self.doi = self.doi_from_crossref(self.pii)
                elif 'CrossRef' in box_link.text:
                    # CrossRef link provides DOI as href
                    # In old code it was a query parameter but this
                    # has now moved to a "data-url" attribute
                    temp = link_tag.attrs['href']
                    # http://dx.doi.org/10.1037%2Fh0075243
                    match = re.search('dx\.doi\.org/(.*)', temp)
                    # Unquote removes %xx escape characters
                    self.doi = urllib_unquote(match.group(1))
                elif "Purchase" in box_link.text:
                    # New link added to Purchase pdf. It was throwing errors
                    pass
                elif 'aps full text' in box_link.text.lower():
                    self.aps_full_text = link_tag.attrs['href']
                else:
                    span_tag = link_tag.find('span')
                    if 'citedBy_' in span_tag.attrs['class']:
                        # Cited By Scopus Count
                        #
                        # NOTE: Apparently the citedByScopus doesn't get added
                        # until later so we need to look for the scan tag. Let's
                        # do this only if all else fails.
                        self._data_sceid = span_tag.attrs['data-sceid']
                    else:
                        raise Exception('Failed to match link')

        # Finally, update if it is not an article
        tag_class = ref_tags.get('class')[0]
        if tag_class == 'article-reference-other-ref':
            publication = ref_tags.find('em')
            if publication is not None:
                self.publication = publication.text
            self.title = ref_tags.text

    def doi_from_crossref(self, pii):
        url = 'http://search.crossref.org/?q=' + pii
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text)
        first_entry = soup.find('td', {'class' : 'item-data'})
        if first_entry is None:
            return None
        entry_links = first_entry.find('div', {'class' : 'item-links'})
        links = entry_links.find_all('a')
        doi = ''
        for link in links:
            if 'dx.doi.org' in link['href']:
                doi_link = link['href']
                doi = doi_link[doi_link.find('dx.doi.org/') + 11:]
        return doi

    def to_data_frame(self, all_entries):
        """
        Return a Pandas DataFrame
        
        Parameters
        ----------
        all_entries : [ScienceDirectRef]        
        
        Testing
        -------
        wtf = refs[0].to_data_frame(refs)
        """

        c_attr = ['ref_id', 'title', 'authors', 'publication', 'volume', 'issue',
                  'series', 'date', 'pages', 'volume', 'scopus_link', 'doi', 'pii',
                  'pdf_link', 'scopus_cite_count']
        all_data = []
        for entry in all_entries:
            all_data.append([getattr(entry, x) for x in c_attr])

        return pd.DataFrame(all_data, columns=c_attr)

    def get_simple_string(self):
        # TODO: Implement
        # The goal is to represent the object as a single string
        # Essentially as a citation
        pass

    def __repr__(self):
        return u'' + \
               '           ref_id: %s\n' % self.ref_id + \
               '            title: %s\n' % td(self.title) + \
               '          authors: %s\n' % self.authors + \
               '      publication: %s\n' % self.publication + \
               '           volume: %s\n' % self.volume + \
               '            issue: %s\n' % self.issue + \
               '           series: %s\n' % self.series + \
               '             date: %s\n' % self.date + \
               '            pages: %s\n' % self.pages + \
               '      scopus_link: %s\n' % td(self.scopus_link) + \
               '              doi: %s\n' % self.doi + \
               '              pii: %s\n' % self.pii + \
               '         pdf_link: %s\n' % td(self.pdf_link) + \
               'scopus_cite_count: %s\n' % self.scopus_cite_count + \
               '    aps full text: %s\n' % self.aps_full_text


def ReferenceParser(object):
    # TODO: move code from get_references into here and have that method
    # initialize this object and call it ( .run()? )
    #
    # This would also swallow _update_counts
    pass


def get_references(input, verbose=False):
    """
    This function gets references for a Sciencedirect URL that is of the
    form:
    
        http://www.sciencedirect.com/science/article/pii/################
        
        e.g. http://www.sciencedirect.com/science/article/pii/0006899387903726
        
        
        
    
    Implementation Notes:
    ---------------------
    From what I can tell this information is not exposed via the Elsevier API.
    
    In order to minimize complexity, the mobile site is requested: via a cookie.


    
    Code Layout and Algorithm Notes:
    --------------------------------
    
    """

    # TODO: Make this a class reference parser

    # *** These tags are mobile-site specific

    # When we don't have proper access rights, this is present in the html
    GUEST_TAG_TUPLE = ("li", {"id": "menuGuest"})

    # Entries are "li" tags with classes of the form:
    #   article-reference-article
    #   article-reference-other-ref
    REFERENCE_TAG_TUPLE = ("li", {"class": re.compile('article-reference-*')})

    # This is the URL to the page that contains the document info, including
    # reference material
    BASE_URL = _SD_URL + '/science/article/pii/'

    # This URL was found first via Fiddler, then via closer inspection of the script
    # 'article_catalyst.js' under sciencedirect.com/mobile/js in the function
    # resolveReferences
    REF_RESOLVER_URL = _SD_URL + '/science/referenceResolution/ajaxRefResol'

    # Return the BeautifulSoup result, the requests session, and the requests response
    if _is_url(input):
        pii = _extract_pii(input)
    else:
        pii = input

    sess = requests.Session()

    if verbose:
        print('Requesting main page for pii: %s' % pii)
    resp = sess.get(BASE_URL + pii, cookies={'Site': 'Mobile'})

    # Step 2 - Get the reference tags

    soup = BeautifulSoup(resp.text)

    reference_section = soup.find("ol", {"class": "article-references"})

    if reference_section is None:
        # Then we might be a guest. In other words, we might not have sufficient
        # privileges to access the data we want. Generally this is protected via
        # IP mask. When I'm working from home I need to VPN into work so
        # that I can access the data :/
        print("reference_section is None")
        temp = soup.find(*GUEST_TAG_TUPLE)
        if temp is None:
            # We might have no references ... (Doubtful)
            raise ParseException("References were not found ..., code error likely")
        else:
            raise InsufficientCredentialsException(
                "Insufficient access rights to get referencs, requires certain IP addresses (e.g. university based IP)")

    ref_tags = reference_section.find_all(*REFERENCE_TAG_TUPLE)

    n_refs = len(ref_tags)

    if n_refs == 0:
        return None

    # Step 3 - Resolve reference links
    # --------------------------------------------------------------------------
    # The returned html code contains javascript which returns more information
    # about each reference, such as:
    #
    #   - links to the full text
    #   - DOI   


    # Step 3.1 - Make the request for the information
    # --------------------------------------------------------------------------
    # We need the eid of the current entry, it is of the form:
    #
    #   SDM.pm.eid = "1-s2.0-0006899387903726"
    #
    #   * I think this entry gets deleted after the requests so it may not be
    #   visible  if looking for it in Chrome. 
    match = re.search('SDM\.pm\.eid\s*=\s*"([^"]+)"', resp.text)
    #eid = match.group(1)

    # This list comes from the resolveReferences function in article_catalyst.js
    payload = {
        '_pii': pii,
        '_refCnt': n_refs,
        '_docType': 'article',  # yikes, this might change ...
        '_refRangeStart': '1',
        '_refRangeCount': str(n_refs)}  # This is normally in sets of 20's ...
    # I'm not sure if it is important to limit this. The browser then
    # makes a request fromr 1 count 20, 21 count 20, 41 count 20 etc,
    # It always goes by 20 even if there aren't 20 left

    if verbose:
        print('Requesting reference links')
    r2 = sess.get(REF_RESOLVER_URL, params=payload)

    # Step 3.2 - Parse the returned information into single entries
    # --------------------------------------------------------------------------
    # This could probably be optimized in terms of execution time. We basically
    # get back a single script tag. Inside is some sort of hash map for links
    # for each reference.
    #
    # The script tag is of the form:
    #   myMap['bibsbref11']['refHtml']= "<some html stuffs>"; 
    #   myMap['bibsbref11']['absUrl']= "http://www.sciencedirect.com/science/absref/sd/0018506X7790068X";
    #   etc.
    #
    #   - Each entry is quite long.
    #   - Normally contains html
    #   - can be empty i.e. myMap['bibsbref11']['refHtml'] = "";
    #   - the refHtml is quite interesting
    #   - the absolute url is not always present (and currently not parsed)
    more_soup = BeautifulSoup(r2.text)
    script_tag = more_soup.find('script')

    # We unquote the script text as it is transmitted with characters escaped
    # and we want the parsed data to contain the non-escaped text
    #
    # We might eventually want to move this to being after the regular expression ...
    script_text = urllib_unquote(script_tag.text)

    ref_match_result = re.findall("myMap\['bibsbref(\d+)'\]\['refHtml'\]=\s?" + '"([^"]*)";', script_text)
    # Tokens:
    # 0 - the # from bibsbref#
    # 1 - the html content from the 'refHtml' entry
    #    
    # NOTE: We don't really use the #, so we might remove the () around
    # \d+ which would shift the index from 1 to 0
    if verbose:
        print('Creating reference objects')

    if len(ref_match_result) > 0:
        zipped = zip(ref_tags, ref_match_result, range(n_refs))
        ref_objects = [ScienceDirectRef(ref_tag, ref_link_info[1], ref_id) for
                       ref_tag, ref_link_info, ref_id in zipped]
    else:
        zipped = zip(ref_tags, range(n_refs))
        ref_objects = [ScienceDirectRef(ref_tag, ref_id) for
                       ref_tag, ref_id in zipped]

    # Step 4:
    # --------------------------------------------------------------------------
    # TODO: Improve documentation for this step

    if verbose:
        print('Retrieving Scopus Counts')

    ref_scopus_eids = []  # The Scopus IDs of the references to resolve
    # but with a particular formatting ...
    ref_count = 0  # Number of references we haven't resolved

    ref_count_list = []
    # NOTE: Browser requests these in the reverse order ...
    for ref_id, ref in enumerate(ref_objects):

        if ref._data_sceid is not None:
            ref_scopus_eids.append(ref._data_sceid + ',' + str(ref_id + 1) + '~')
            ref_count += 1

            # If we've got enough, then update the counts
            # The 20 may be arbitrary but it was what was used in original JS
            if ref_count > 20:
                ref_count_list += _update_counts(sess, ref_scopus_eids, REF_RESOLVER_URL)
                ref_count = 0
                ref_scopus_eids = []

    # Get any remaining reference counts
    if ref_count != 0:
        ref_count_list += _update_counts(sess, ref_scopus_eids, REF_RESOLVER_URL)

        # Take the raw data and set the citation count for each object
    for ref_tuple in ref_count_list:
        ref_id = int(ref_tuple[0]) - 1
        ref_count = int(ref_tuple[1])
        ref_objects[ref_id].scopus_cite_count = ref_count

    # All done!
    # ---------
    return ref_objects


def _update_counts(s, eids, resolve_url):
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
    payload = {'_updateCitedBy': ''.join(eids)}
    r = s.get(resolve_url, params=payload)
    # TODO: Check for 200
    data = urllib_unquote(r.text)

    # myXabsCounts['citedBy_26']='Citing Articles (41)';
    cited_by_results = re.findall("myXabsCounts\['citedBy_(\d+)'\]='[^\(]+\((\d+)", data)

    # TODO: parse response
    # ????? Why is the order scrambled - this seems to be on their end ...????
    '''
    NOTE: This is now Citing Articles, references to Scopus have been dropped
    myXabsCounts['citedBy_16']='Cited By in Scopus (128)';
    myXabsCounts['citedBy_15']='Cited By in Scopus (25)';
    myXabsCounts['citedBy_1']='Cited By in Scopus (2)';
    myXabsCounts['citedBy_3']='Cited By in Scopus (29)';
    '''
    # TODO: go through refs and apply new values ...

    return cited_by_results


def get_entry_info(input, verbose=False, soup=None):
    if soup is None:
        soup = _make_soup(input, verbose)
    return ScienceDirectEntry(soup, verbose)


def get_pdf_link(input, verbose=False, soup=None):
    if soup is None:
        soup, _, _ = _make_soup(input, verbose)

    navbar = soup.find('ul', {'class' : 'navigation'})
    pdf_link = navbar.find('a', {'id' : 'pdfLink'})['href']
    return pdf_link


def get_all_info(input, verbose=False):
    pass


def _make_soup(input, verbose=False):
    # Check if the input is a PII, DOI, or URL, and
    # use appropriate argument in web page retrieval
    if _is_url(input):
        soup = _connect(url=input, verbose=verbose)
    elif _is_doi(input):
        url = 'http://dx.doi.org/' + input
        soup = _connect(url=url, verbose=verbose)
    else:
        soup = _connect(pii=input, verbose=verbose)

    return soup


def _is_url(input):
    if input.find('sciencedirect') != -1:
        return True
    else:
        return False


def _is_doi(input):
    input = input.strip()
    if input[0:3] == '10.':
        return True
    else:
        return False


def _extract_pii(url):
    # Extract the PII from the URL
    # Get everything between 'sciencedirect.com/science/article/pii/' and the URL ending
    # pii = re.findall('pii/(.*?)', url, re.DOTALL)

    # We're grabbing everything after 'pii/'
    pii_index = url.find('pii/')
    pii = url[pii_index+4:]

    return pii


def _connect(pii=None, url=None, verbose=None):
    # Construct valid ScienceDirect URL from given DOI
    if pii is not None:
        article_url = _SD_URL + '/science/article/pii/' + pii
    elif url is not None:
        article_url = url
    else:
        raise LookupError('Need a valid PII or ScienceDirect URL')

    # Web page retrieval
    # -------------------
    '''
    sess = requests.Session()

    if verbose:
        print('Requesting main page for doi: %s' % pii)

    # Using the mobile version of ScienceDirect
    # This is to avoid dynamically loading page features on the desktop site
    # and because the mobile site has more cleanly organized information
    resp = sess.get(article_url, cookies={'Site': 'Mobile'})

    if not resp.ok:
        if resp.status_code == 404:
            raise ConnectionError('Could not locate page info - 404 Error')
        else:
            raise ConnectionError('Could not connect to article page.')
    '''

    page_content = _selenium_connect(url=article_url)

    # with open('sd_test.html', 'w') as file:
    #     file.write(page_content)

    soup = BeautifulSoup(page_content)

    return soup


def _selenium_connect(url):
    # Chromedriver executable must be in the user's home directory
    home = os.path.expanduser('~')
    chromedriver_path = home + '/chromedriver'

    # Create the webdriver
    driver = selenium.webdriver.Chrome(executable_path=chromedriver_path)

    # Navigate to the ScienceDirect article
    driver.get(url)

    # TODO: why does this not work
    # Add a cookie for the mobile site
    mobile_cookie = {'Site': 'Mobile'}
    driver.add_cookie(mobile_cookie)

    # This is so that the javascript within each of the references will run
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # TODO: figure out a trigger for stopping the wait.
    # Somehow detect if any of the relevant javascript elements
    # are even running?
    try:
        WebDriverWait(driver, 10)
        page_content = driver.page_source
    except TimeoutException:
        page_content = driver.page_source
        pass

    finally:
        driver.quit()

    return page_content
