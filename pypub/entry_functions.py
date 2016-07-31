import pypub.publishers.pub_resolve as pub_resolve
from pypub.paper_info import PaperInfo


def get_paper_info(doi=None, url=None):
    """
    Parameters
    ----------
    doi :
    url :
    
    Returns
    -------
    
    
    Errors
    ------
    UnsupportedPublisherError : Retrieval of information from this publisher is not yet available
    
    """
    
    #JAH: This code is really confusing to me:
    #My steps: (in pseudocode)
    """
    if doi is not None:
        publisher = publishers.from_doi
        paper_info = publisher.get_paper_info(doi=doi)
    else:
        publisher = publishers.from_url
        paper_info = publisher.get_paper_info(url=url)
    """

    # Resolve DOI or URL through PyPub pub_resolve methods
    publisher_base_url, full_url = pub_resolve.get_publisher_urls(doi=doi, url=url)
    import pdb
    pdb.set_trace()
    
    pub_dict = pub_resolve.get_publisher_site_info(publisher_base_url)

    # Create a PaperInfo object to hold all information and call appropriate scraper
    paper_info = PaperInfo(doi=doi, scraper_obj=pub_dict['object'], url=full_url)
    paper_info.populate_info()

    return paper_info

def get_references():
    pass

def get_publisher(doi=None, url=None):
    #This could return the publisher given this information.
    #This function is low priority
    pass
