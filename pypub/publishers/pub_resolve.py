import csv


def resolve_link(link):
    """
    Gets the paper and references information from a link (URL)
    to a specific journal article page.

    Parameters
    ----------
    link : str
        URL to journal article page on publisher's website.
        Example: http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references

    Returns
    -------
    pub_dict : dict
        See resolve_citation for description.

    """
    import os
    import inspect

    # First format the link correctly and determine the publisher
    # ---------------------
    # Make sure 'http://' and not 'www.' is at the beginning
    link = link.replace('www.', '')
    if link[0:4] != 'http':
        link = 'http://' + link

    base_url = link[:link.find('.com')+4]


    # Get absolute path to CSV file
    current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    file_path = os.path.join(current_dir, 'site_features.csv')
    pub_dict = None

    # Now search the site_features.csv file to get information relevant to that provider
    with open(file_path) as f:
        reader = csv.reader(f)
        headings = next(reader)  # Save the first line as the headings
        values = None
        for row in enumerate(reader):
            if base_url in row[1]:
                values = row[1]  # Once the correct row is found, save it as values
                pub_dict = dict(zip(headings, values))
                break

    if pub_dict is None:
        raise KeyError('No publisher information found. Publisher is not currently supported.')
    else:
        return pub_dict
