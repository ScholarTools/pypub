import pytest
import os
import sys
import pickle

from pypub.paper_info import PaperInfo

'''
This method is used to generate saved versions of test article pages from
the various supported publishers. This should only be run once, in order
to create the saved information that the real tests should run against.

This script should be able to be run as-is, because the function call is at
the bottom of the page.
'''

class PublisherTestSetup(object):
    def __init__(self):
        self.curpath = str(os.path.dirname(os.path.abspath(__file__)))

        # This next line is required so that each PaperInfo object
        # is able to be pickled and saved correctly.
        sys.setrecursionlimit(2000)

        # Check if saved_info directory exists, and if not, make it
        self.dirname = os.path.join(self.curpath, 'saved_info')
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def wiley(self):
        # Sample journal article
        wy_link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
        wy_doi = '10.1002/biot.201400046'

        # Make a PaperInfo object from the live site information
        # pi.publisher_interface needs to be set to None or else
        # the object could not be saved.
        pi = PaperInfo(url=wy_link, doi=wy_doi, scraper_obj='wiley')
        pi.populate_info()
        pi.publisher_interface = None

        # Write saved version of the PaperInfo object
        file_path_name = os.path.join(self.dirname, 'wy_info.txt')
        with open(file_path_name, 'wb') as file:
            pickle.dump(pi, file)

    def nature_nrg(self):
        # Sample journal article
        nrg_link = 'http://www.nature.com/nrg/journal/v15/n5/full/nrg3686.html'
        nrg_doi = '10.1038/nrg3686'

        # Make a PaperInfo object from the live site information
        pi = PaperInfo(url=nrg_link, doi=nrg_doi, scraper_obj='nature_nrg')
        pi.populate_info()
        pi.publisher_interface = None

        # Write saved version of the PaperInfo object
        file_path_name = os.path.join(self.dirname, 'nrg_info.txt')
        with open(file_path_name, 'wb') as file:
            pickle.dump(pi, file)

    def science_direct(self):
        # Sample journal article
        sd_link = 'http://www.sciencedirect.com/science/article/pii/S0006899313013048'

        # Make a PaperInfo object from the live site information
        pi = PaperInfo(url=sd_link, scraper_obj='sciencedirect_selenium')
        pi.populate_info()
        pi.publisher_interface = None

        # Write saved version of the PaperInfo object
        file_path_name = os.path.join(self.dirname, 'sd_info.txt')
        with open(file_path_name, 'wb') as file:
            pickle.dump(pi, file)

    def springer(self):
        # Sample journal article
        sp_link = 'http://link.springer.com/article/10.1007/s10237-015-0706-9'
        sp_doi = '10.1007/s10237-015-0706-9'

        # Make a PaperInfo object from the live site information
        pi = PaperInfo(url=sp_link, doi=sp_doi, scraper_obj='springer')
        pi.populate_info()
        pi.publisher_interface = None

        # Write saved version of the PaperInfo object
        file_path_name = os.path.join(self.dirname, 'sp_info.txt')
        with open(file_path_name, 'wb') as file:
            pickle.dump(pi, file)

    def taylor_francis(self):
        # NOTE: The current version of the T&F scraper is for a deprecated version
        # of the site. All of the HTML tags need to be changed.
        # Sample journal article
        tf_link = 'http://www.tandfonline.com/doi/full/10.1080/21624054.2016.1184390'
        tf_doi = '10.1080/21624054.2016.1184390'

        # Make a PaperInfo object from the live site information
        pi = PaperInfo(url=tf_link, doi=tf_doi, scraper_obj='taylorfrancis')
        pi.populate_info()
        pi.publisher_interface = None

        # Write saved version of the PaperInfo object
        file_path_name = os.path.join(self.dirname, 'tf_info.txt')
        with open(file_path_name, 'wb') as file:
            pickle.dump(pi, file)

    def get_all_information(self):
        self.wiley()
        self.nature_nrg()
        self.science_direct()
        self.springer()
        # self.taylor_francis()


test_setup = PublisherTestSetup()
test_setup.get_all_information()
