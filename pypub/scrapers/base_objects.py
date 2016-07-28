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
        self.pii = None
        self.eid = None
        self.abstract = None
        self.authors = None
        self.affiliations = None
        self.url = None
        self.pdf_link = None
        self.scraper_obj = None
        self.notes = None
        self.pubmed_id = None
        self.issn = None

        # Note that each entry in 'authors' is a separate author class
        # with self.name, self.affiliations, and self.email

    def __repr__(self):
        return u'' + \
        '      title: %s\n' % self.title + \
        '    authors: %s\n' % [x.name for x in self.authors] + \
        '   keywords: %s\n' % self.keywords + \
        'publication: %s\n' % self.publication + \
        '       date: %s\n' % self.date + \
        '        year %s\n' % self.year + \
        '     volume: %s\n' % self.volume.strip() + \
        '      issue: %s\n' % self.issue + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi + \
        '        url: %s\n' % self.url + \
        '   pdf_link: %s\n' % self.pdf_link


class BaseAuthor(object):
    def __init__(self):
        self.name = None
        self.affiliations = None
        self.email = None

    def __repr__(self):
        return u'' + \
        '        name: %s\n' % self.name + \
        'affiliations: %s\n' % self.affiliations + \
        '       email: %s\n' % self.email


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
        self.year = None
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

        # These are in Wiley
        self.pubmed_id = None
        self.abstract_link = None
        self.ref_references = None
        self.citetimes = None

    def get(self, attr):
        return getattr(self, attr)

    def __repr__(self):
        return u'' + \
        '     ref_id: %s\n' % self.ref_id + \
        '      title: %s\n' % self.title + \
        '    authors: %s\n' % self.authors + \
        'publication: %s\n' % self.publication + \
        '     volume: %s\n' % self.volume + \
        '      issue: %s\n' % self.issue + \
        '     series: %s\n' % self.series + \
        '       date: %s\n' % self.date + \
        '      pages: %s\n' % self.pages + \
        '        doi: %s\n' % self.doi + \
        '        pii: %s\n' % self.pii
