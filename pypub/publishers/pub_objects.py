# -*- coding: utf-8 -*-
"""

"""
# Third party imports
import requests
from bs4 import BeautifulSoup

# Local imports
from pypub_errors import *
from pypub.publishers import pub_resolve


class Publisher:
    def __init__(self, **kwargs):
        # The following attributes are taken from the site_features.csv file.
        # These are used if a row of that file was used to populate this class.
        self.provider_abbrev = kwargs.get('provider_abbrev')
        self.provider_root_url = kwargs.get('provider_root_url')
        self.need_mobile = kwargs.get('need_mobile')
        self.req_cookies = kwargs.get('req_cookies')
        self.page_type = kwargs.get('page_type')
        self.dynamically_loaded = kwargs.get('dynamically_loaded')
        self.fulltext_link = kwargs.get('fulltext_link')
        self.pdf_link = kwargs.get('pdf_link')
        self.recommended_articles = kwargs.get('recommended_articles')
        self.url_prefix = kwargs.get('url_prefix')
        self.article_page_suffix = kwargs.get('article_page_suffix')
        self.references_link = kwargs.get('references_link')
        self.entry_info_tag = kwargs.get('entry_info_tag')
        self.references_tag = kwargs.get('references_tag')
        self.scraper = kwargs.get('scraper')
        self.object = kwargs.get('object')

        # The following attributes are if an instance of the publisher is
        # created without the site_features.csv file.
        self.doi_or_url = kwargs.get('doi_or_url')

    def get_entry_info(self, doi_or_url=None, verbose=False):
        if doi_or_url is None:
            doi_or_url = self.doi_or_url
        return self.scraper.get_entry_info(doi_or_url, verbose=verbose)

    def get_references(self, doi_or_url=None, verbose=False):
        if doi_or_url is None:
            doi_or_url = self.doi_or_url
        return self.scraper.get_references(doi_or_url, verbose=verbose)

    def get_pdf_link(self, doi_or_url=None):
        if doi_or_url is None:
            doi_or_url = self.doi_or_url
        return self.scraper.get_pdf_link(doi_or_url)


class Wiley(Publisher):
    def __init__(self):
        super().__init__()

        # Import the appropriate scraper and set it as self.scraper
        import pypub.scrapers.wiley as wy
        self.scraper = wy

    def get_pdf_content(self, file_url=None, doi_or_url=None):
        if doi_or_url is None and self.doi_or_url is not None:
            doi_or_url = self.doi_or_url

        if file_url is None:
            if doi_or_url is None:
                raise InputError('get_pdf_content() requires a DOI or URL')
            else:
                file_url = self.get_pdf_link(doi_or_url)

        # Change file URL ending from /epdf to /pdf
        if file_url.find('/epdf') != -1:
            file_url = file_url.replace('/epdf', '/pdf')

        resp = requests.get(file_url)
        soup_tag = ('iframe', {'id' : 'pdfDocument'})
        link_loc = 'src'

        return _extract_content(resp, soup_tag, link_loc)


class ScienceDirect(Publisher):
    def __init__(self):
        super().__init__()

        # Import the appropriate scraper and set it as self.scraper
        import pypub.scrapers.sciencedirect as sd
        self.scraper = sd

    # Need to overload these functions because ScienceDirect scraper
    # can't handle DOI inputs - needs either PII or URL
    def get_entry_info(self, doi_or_url=None, verbose=False):
        if 'sciencedirect' not in doi_or_url:
            doi_or_url = self._doi_to_link(doi_or_url)
        return self.scraper.get_entry_info(doi_or_url, verbose=verbose)

    def get_references(self, doi_or_url=None, verbose=False):
        if 'sciencedirect' not in doi_or_url:
            doi_or_url = self._doi_to_link(doi_or_url)
        return self.scraper.get_references(doi_or_url, verbose=verbose)

    def get_pdf_link(self, doi_or_url=None):
        if 'sciencedirect' not in doi_or_url:
            doi_or_url = self._doi_to_link(doi_or_url)
        return self.scraper.get_pdf_link(doi_or_url)

    def get_pdf_content(self, file_url=None, doi_or_url=None):
        if doi_or_url is None and self.doi_or_url is not None:
            doi_or_url = self.doi_or_url

        if file_url is None:
            if doi_or_url is None:
                raise InputError('get_pdf_content() requires a DOI or URL')
            else:
                file_url = self.get_pdf_link(doi_or_url)

        resp = requests.get(file_url)
        soup_tag = ('a', {'id' : 'pdfLink'})
        link_loc = 'src'

        return _extract_content(resp, soup_tag, link_loc)

    def _doi_to_link(self, doi):
        _, link = pub_resolve.get_publisher_urls(doi=doi)
        return link


class Springer(Publisher):
    def __init__(self):
        super().__init__()

        # Import the appropriate scraper and set it as self.scraper
        import pypub.scrapers.springer as sp
        self.scraper = sp

    def get_pdf_content(self, file_url=None, doi_or_url=None):
        if doi_or_url is None and self.doi_or_url is not None:
            doi_or_url = self.doi_or_url

        if file_url is None:
            if doi_or_url is None:
                raise InputError('get_pdf_content() requires a DOI or URL')
            else:
                file_url = self.get_pdf_link(doi_or_url)

        resp = requests.get(file_url)

        if hasattr(resp, 'headers'):
            if 'text/html' in resp.headers['Content-Type']:
                soup = BeautifulSoup(resp.text)
                #pdf_link = soup.find('a', {'id' : 'pdfLink'})['href']
                #resp2 = requests.get(pdf_link)
                raise KeyError('HTML response not implemented in pub_objects')
            elif 'application/pdf' in resp.headers['Content-Type']:
                return resp.content
            else:
                raise LookupError('Response not HTML or a PDF.')
        else:
            raise LookupError('Could not get headers from web response.')


class NatureNRG(Publisher):
    def __init__(self):
        super().__init__()

        # Import the appropriate scraper and set it as self.scraper
        import pypub.scrapers.nature_nrg as nt_nrg
        self.scraper = nt_nrg

    def get_pdf_content(self, file_url=None, doi_or_url=None):
        # This one is nice because it doesn't return HTML.
        if doi_or_url is None and self.doi_or_url is not None:
            doi_or_url = self.doi_or_url

        if file_url is None:
            if doi_or_url is None:
                raise InputError('get_pdf_content() requires a DOI or URL')
            else:
                file_url = self.get_pdf_link(doi_or_url)
        resp = requests.get(file_url)
        return resp.content


def _extract_content(resp, soup_tag, link_location):
    if hasattr(resp, 'headers'):
        if 'text/html' in resp.headers['Content-Type']:
            soup = BeautifulSoup(resp.text)
            pdf_link = soup.find(soup_tag)[link_location]
            resp2 = requests.get(pdf_link)
            return resp2.content
        elif 'application/pdf' in resp.headers['Content-Type']:
            return resp.content
        else:
            raise LookupError('Response not HTML or a PDF.')
    else:
        raise LookupError('Could not get headers from web response.')
