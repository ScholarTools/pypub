class BaseEntry(object):
    def __init__(self):
        self.title = None
        self.publication = None
        self.date = None
        self.year = None
        self.volume = None
        self.issue = None
        self.pages = None
        self.keywords = None
        self.doi = None
        self.doi_prefix = None
        self.abstract = None
        self.authors = None
        self.affiliations = None
        self.url = None
        self.pdf_link = None
        self.scraper_obj = None
        # Note that each entry in 'authors' is a separate author class
        # with self.name, self.affiliations, and self.email


class BaseRef(object):
    def __init__(self):
        # Initialize standard reference information
        self.ref_id = None
        self.title = None
        self.authors = None
        self.publication = None
        self.volume = None
        self.issue = None
        self.series = None
        self.date = None
        self.pages = None
        self.doi = None
        self.pii = None
        self.citation = None

        # Initialize all possible external links
        self.crossref = None
        self.pubmed = None
        self.pubmed_central = None
        self.cas = None
        self.isi = None
        self.ads = None
        self.scopus_link = None
        self.pdf_link = None
        self.scopus_cite_count = None
        self.aps_full_text = None
