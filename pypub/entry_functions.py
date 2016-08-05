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

    if doi is not None:
        publisher = pub_resolve.publisher_from_doi(doi)
        paper_info = publisher.get_paper_info(doi=doi)
    elif url is not None:
        publisher = pub_resolve.publisher_from_url(url)
        paper_info = publisher.get_paper_info(url=url)
    else:
        raise Exception

    '''
    # Resolve DOI or URL through PyPub pub_resolve methods
    publisher_base_url, full_url = pub_resolve.get_publisher_urls(doi=doi, url=url)

    pub_dict = pub_resolve.get_publisher_site_info(publisher_base_url)

    # Create a PaperInfo object to hold all information and call appropriate scraper
    paper_info = PaperInfo(doi=doi, scraper_obj=pub_dict['object'], url=full_url)
    paper_info.populate_info()
    '''

    return paper_info

def get_references():
    pass

def get_publisher(doi=None, url=None):
    #This could return the publisher given this information.
    #This function is low priority
    pass
