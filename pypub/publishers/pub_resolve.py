"""

from pypub.publishers import pub_resolve

"""

# Standard imports
#--------------------------
import csv

# Third party imports
#--------------------------
import requests

# Local imports
#--------------------------
from pypub.pypub_errors import *
from pypub import utils

from . import site_features_file_path

from crossref import doi as xref

'''
def get_publisher_urls(doi=None, url=None):
    """
    
    Returns
    -------
    (base_url, pub_url)
    
    base_url :
    pub_url : 
    """
    
    # JAH: This looks inefficient as we first request the entire page,
    # and then presumably later we request the entire page again

    # KSA: Using xref.is_valid() also seems inefficient here though,
    # because it makes a get request to make sure the DOI is valid,
    # and then makes another one to get the publisher URL. Is there
    # a better way I should do this?
    
    # Get or make CrossRef link, then follow it to get article URL
    if url is not None:
        resp = requests.get(url)
        pub_url = resp.url
    elif doi is not None:
        #JAH: Patch into Crossref => see crossref.doi module
        #This fails silently on an invalid DOI
        if xref.is_valid(doi):
            resp = requests.get('http://dx.doi.org/' + doi)
            pub_url = resp.url
        else:
            return None, None
    else:
        return None, None

    base_url = _extract_base_url(pub_url)

    return base_url, pub_url
'''


def publisher_from_doi_or_url(doi=None, url=None):
    if doi is not None:
        return publisher_from_doi(doi)
    elif url is not None:
        return publisher_from_url(url)
    else:
        raise KeyError('Need to enter a DOI or URL to retrieve publisher information.')


def publisher_from_doi(doi):
    if xref.is_valid(doi):
        resp = requests.get('http://dx.doi.org/' + doi)
        pub_url = resp.url
    else:
        raise InvalidDOIError('DOI could not be resolved to a publisher site.')

    base_url = _extract_base_url(pub_url)

    publisher = _create_publisher_interface(base_url)
    return publisher


def publisher_from_url(url):
    """
    

    Parameters
    ----------
    url : TYPE
        DESCRIPTION.

    Returns
    -------
    publisher : TYPE
        DESCRIPTION.
        
    Example
    -------
    from pypub.publishers import pub_resolve
    url = 'https://onlinelibrary.wiley.com/doi/10.1002/nau.1930090206'
    publisher = pub_resolve.publisher_from_url(url)


    """
    resp = requests.get(url)
    pub_url = resp.url
    base_url = _extract_base_url(pub_url)

    publisher = _create_publisher_interface(base_url)
    return publisher


def _extract_base_url(full_url):
    # Extract the 'base URL' from the full url.
    # This will be everything before the third instance of '/'
    # I.e. for the site http://example.com/site/path, the base
    # URL will be 'http://example.com'
    end_index = utils.find_nth(full_url, '/', 3)
    base_url = full_url[:end_index]

    # Nature sites are specific to the different journals
    # I.e. http://nature.com/nrg is for Nature Reviews Genetics
    if 'nature' in base_url:
        nature_end_index = utils.find_nth(full_url, '/', 4)
        base_url = full_url[:nature_end_index]

    base_url = base_url.replace('www.', '')

    return base_url


def _create_publisher_interface(base_url):
    pub_dict = get_publisher_site_info(base_url)
    scraper_name = pub_dict.get('object')
    if scraper_name is None:
        raise UnsupportedPublisherError('DOI could not be resolved to a supported publisher.')
    else:
        module = __import__('pypub.publishers.pub_objects', fromlist=['pub_objects'])
        class_ = getattr(module, scraper_name)
        publisher = class_()
        return publisher


def get_publisher_site_info(base_url):
    """
    
    Parameters
    ----------
    base_url : TYPE
        What is this?

    Raises
    ------
    UnsupportedPublisherError
        DESCRIPTION.

    Returns
    -------
    pub_dict : TYPE
        DESCRIPTION.

    """
    # Search the site_features.csv file to get information relevant to that provider
    with open(site_features_file_path) as f:
        reader = csv.reader(f)
        headings = next(reader)  # Save the first line as the headings
        values = None
        for row in enumerate(reader):
            if base_url in row[1]:
                # Once the correct row is found, save it as values.
                # The [1] here is needed because 'row' is a list where
                # the first value is the row number and the second is
                # the entire list of headings.
                values = row[1]
                break

    if values is None:
        raise UnsupportedPublisherError('Publisher with URL %s is unsupported.' % base_url)

    # Turn the headings and values into a callable dict
    pub_dict = dict(zip(headings, values))

    return pub_dict
