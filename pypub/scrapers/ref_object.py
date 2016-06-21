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
