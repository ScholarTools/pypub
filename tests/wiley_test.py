# Standard imports
import os
import sys
import pickle

# Third party imports
import nose

# Local imports
from pypub.scrapers import wiley as wy
from pypub.paper_info import PaperInfo


class TestWiley(object):
    def __init__(self):
        self.curpath = str(os.path.dirname(os.path.abspath(__file__)))
        self.link = 'http://onlinelibrary.wiley.com/doi/10.1002/biot.201400046/references'
        self.doi = '10.1002/biot.201400046'

        # Make a PaperInfo object from the live site information
        try:
            pi = PaperInfo(url=self.link, doi=self.doi, scraper_obj='wiley')
            pi.populate_info()
        except Exception:
            self.pi = None
            self.entry_dict = None
        else:
            self.pi = pi
            self.entry_dict = self.pi.entry.__dict__

        # Load saved version of the PaperInfo object
        saved_dir = os.path.join(self.curpath, 'saved_info')
        saved_file_path = os.path.join(saved_dir, 'wy_info.txt')
        self.saved_pi = pickle.load(open(saved_file_path, 'rb'))

        # Make the saved versions into dicts
        self.saved_entry_dict = self.saved_pi.entry.__dict__

    # Testing return types
    def test_entry_type(self):
        assert type(self.pi.entry) is wy.WileyEntry

    def test_references_type(self):
        assert type(self.pi.references) is list

    def test_reflist_type(self):
        assert type(self.pi.references[0]) is wy.WileyRef

    # Testing scraped soup against saved site version
    def test_wiley_saved_entry(self):
        for x in self.saved_entry_dict.keys():
            if x == 'authors':
                continue
            if self.saved_entry_dict[x] != self.entry_dict[x]:
                print('\nDifference found.')
                print('Key: ' + str(x))
                print('Saved value: ' + str(self.saved_entry_dict[x]))
                print('Live value: ' + str(self.entry_dict[x]))
                assert False

        # Compare authors separately
        live_authors = self.pi.entry.authors
        saved_authors = self.saved_pi.entry.authors

        # First check number of authors
        if len(live_authors) != len(saved_authors):
            assert False

        # Then make sure the values of each author object are equal
        for z in enumerate(live_authors):
            live = z[1]
            saved = saved_authors[z[0]]
            if live.__dict__ != saved.__dict__:
                print('\nDifference found.')
                print('Key: authors')
                print('Saved value: ' + str(saved))
                print('Live value: ' + str(live))
                assert False
        assert True

    def test_wiley_saved_refs(self):
        for y in range(len(self.pi.references)):
            saved_ref_dict = self.saved_pi.references[y].__dict__
            live_ref_dict = self.pi.references[y].__dict__
            for x in live_ref_dict.keys():
                if saved_ref_dict[x] != saved_ref_dict[x]:
                    print('\nDifference found.')
                    print('Key: ' + str(x))
                    print('Saved value: ' + str(self.saved_pi.references[y]))
                    print('Live value: ' + str(self.pi.references[y]))
                    print('Specific difference:')
                    print('Saved value: ' + str(saved_ref_dict[x]))
                    print('Live value: ' + str(live_ref_dict[x]))
                    assert False
        assert True

    def test_wiley_pdf_link(self):
        if self.pi.pdf_link != self.saved_pi.pdf_link:
            assert False
        else:
            assert True


if __name__ == '__main__':
    module_name = sys.modules[__name__].__file__

    result = nose.run(argv=[sys.argv[0], module_name, '-v'])
