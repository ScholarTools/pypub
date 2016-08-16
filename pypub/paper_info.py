from pypub.publishers import pub_resolve
from pypub.pypub_errors import *


class BasePaperInfo(object):
    def __init__(self):
        pass


class PaperInfo(BasePaperInfo):
    def __init__(self, **kwargs):
        super().__init__()
        self.entry = kwargs.get('entry_dict')
        self.references = kwargs.get('refs_dicts')
        self.doi = kwargs.get('doi')
        self.doi_prefix = ''
        if self.doi is not None:
            self.doi_prefix = self.doi[:7]
        self.url = kwargs.get('url')
        self.pdf_link = kwargs.get('pdf_link')
        self.scraper_obj = kwargs.get('scraper_obj')
        self.publisher_interface = kwargs.get('publisher_interface')

        self.make_interface_object()

    def make_interface_object(self):
        if self.publisher_interface is not None:
            return

        # Create publisher object and initialize with a DOI or URL
        if self.doi is not None:
            publisher = pub_resolve.publisher_from_doi(self.doi)
            publisher.doi_or_url = self.doi
        elif self.url is not None:
            publisher = pub_resolve.publisher_from_url(self.url)
            publisher.doi_or_url = self.url
        else:
            publisher = None

        self.publisher_interface = publisher
        return

    def populate_info(self):
        input = self._make_input()

        #self.entry = utils.convert_to_dict(self.publisher_interface.get_entry_info(input))
        #self.references = utils.refs_to_list(self.publisher_interface.get_references(input))
        self.entry = self.publisher_interface.get_entry_info(input)
        self.references = self.publisher_interface.get_references(input)
        self.pdf_link = self.publisher_interface.get_pdf_link(input)

    def _make_input(self):
        # Set 'input' to either DOI or URL, when present
        if self.publisher_interface is None:
            raise ScraperError('A scraper is required to get paper information')
        if self.doi is None:
            if self.url is None:
                raise InputError('A DOI or URL is needed to populate PaperInfo')
            else:
                input = self.url
        else:
            input = self.doi
        return input

    # @property
    def get_entry_info(self):
        input = self._make_input()
        if self.publisher_interface is not None:
            #entry = utils.convert_to_dict(self.publisher_interface.get_entry_info(input))
            entry = self.publisher_interface.get_entry_info(input)
            self.entry = entry
            return entry
        else:
            return None

    # @property
    def get_references(self):
        input = self._make_input()
        if self.publisher_interface is not None:
            #refs = utils.refs_to_list(self.publisher_interface.get_references(input))
            refs = self.publisher_interface.get_references(input)
            self.references = refs
            return refs
        else:
            return None

    # @property
    def get_pdf_link(self):
        input = self._make_input()
        if self.publisher_interface is not None:
            pdf_link = self.publisher_interface.get_pdf_link(input)
            self.pdf_link = pdf_link
            return pdf_link
        else:
            return None

    def __repr__(self):
        return '' + \
            'title: %s\n' % getattr(self.entry, 'title', None) + \
            'authors: %s\n' % [x.name for x in getattr(self.entry, 'authors', None)] + \
            'doi: %s\n' % self.doi + \
            'url: %s\n' % self.url + \
            'scraper_obj: %s\n' % self.scraper_obj

