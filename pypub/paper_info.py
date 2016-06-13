

class PaperInfo:
    def __init__(self, **kwargs):
        self.idnum = kwargs.get('idnum')
        self.entry = kwargs.get('entry_dict')
        self.references = kwargs.get('refs_dicts')
        self.doi = kwargs.get('doi')
        self.doi_prefix = kwargs.get('doi_prefix')
        self.url = kwargs.get('url')
        self.pdf_link = kwargs.get('pdf_link')
        self.scraper_obj = kwargs.get('scraper_obj')
        self.scraper = self.make_scraper_object()


    def make_scraper_object(self):
        # Get appropriate scraper object
        if self.scraper_obj is None:
            return None
        mod = __import__('pypub.publishers.pub_objects', fromlist=[self.scraper_obj])
        scraper = getattr(mod, self.scraper_obj)
        return scraper