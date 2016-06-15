import pypub.publishers.pub_resolve as pub_resolve
from pypub.paper_info import PaperInfo


def get_paper_info(doi=None, url=None):
    # Resolve DOI or URL through PyPub pub_resolve methods
    publisher_base_url, full_url = pub_resolve.get_publisher_urls(doi=doi, url=url)
    pub_dict = pub_resolve.get_publisher_site_info(publisher_base_url)

    # Create a PaperInfo object to hold all information and call appropriate scraper
    paper_info = PaperInfo(doi=doi, scraper_obj=pub_dict['object'], url=full_url)
    paper_info.populate_info()

    return paper_info
