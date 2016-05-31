# -*- coding: utf-8 -*-
"""

"""

import requests
from bs4 import BeautifulSoup

class Publisher:
    def __init__(self, **kwargs):
        self.provider_abbrev = kwargs['provider_abbrev']
        self.provider_root_url = kwargs['provider_root_url']
        self.need_mobile = kwargs['need_mobile']
        self.req_cookies = kwargs['req_cookies']
        self.page_type = kwargs['page_type']
        self.dynamically_loaded = kwargs['dynamically_loaded']
        self.fulltext_link = kwargs['fulltext_link']
        self.pdf_link = kwargs['pdf_link']
        self.recommended_articles = kwargs['recommended_articles']
        self.url_prefix = kwargs['url_prefix']
        self.article_page_suffix = kwargs['article_page_suffix']
        self.references_link = kwargs['references_link']
        self.entry_info_tag = kwargs['entry_info_tag']
        self.references_tag = kwargs['references_tag']
        self.scraper = kwargs['scraper']
        self.object = kwargs['object']


class Wiley(Publisher):
    def extract_pdf(self, file_url):

        # Change file URL ending from /epdf to /pdf
        if file_url.find('/epdf') != -1:
            file_url = file_url.replace('/epdf', '/pdf')

        resp = requests.get(file_url)

        if hasattr(resp, 'headers'):
            if 'text/html' in resp.headers['Content-Type']:
                soup = BeautifulSoup(resp.text)
                pdf_link = soup.find('iframe', {'id' : 'pdfDocument'})['src']
                resp2 = requests.get(pdf_link)
                return resp2
            elif 'application/pdf' in resp.headers['Content-Type']:
                return resp
            else:
                raise LookupError('Response not HTML or a PDF.')
        else:
            raise LookupError('Could not get headers from web response.')


class ScienceDirect(Publisher):
    def extract_pdf(self, file_url):

        resp = requests.get(file_url)

        if hasattr(resp, 'headers'):
            if 'text/html' in resp.headers['Content-Type']:
                soup = BeautifulSoup(resp.text)
                pdf_link = soup.find('a', {'id' : 'pdfLink'})['href']
                resp2 = requests.get(pdf_link)
                return resp2
            elif 'application/pdf' in resp.headers['Content-Type']:
                return resp
            else:
                raise LookupError('Response not HTML or a PDF.')
        else:
            raise LookupError('Could not get headers from web response.')


class Springer(Publisher):
    def extract_pdf(self, file_url):

        resp = requests.get(file_url)

        if hasattr(resp, 'headers'):
            if 'text/html' in resp.headers['Content-Type']:
                soup = BeautifulSoup(resp.text)
                #pdf_link = soup.find('a', {'id' : 'pdfLink'})['href']
                #resp2 = requests.get(pdf_link)
                raise KeyError('HTML response not implemented in pub_objects')
            elif 'application/pdf' in resp.headers['Content-Type']:
                return resp
            else:
                raise LookupError('Response not HTML or a PDF.')
        else:
            raise LookupError('Could not get headers from web response.')


class Nature(Publisher):
    def extract_pdf(self, file_url):
        raise LookupError('Not yet implemented')