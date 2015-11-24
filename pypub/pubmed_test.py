# -*- coding: utf-8 -*-
"""

#TODO: Read http://docs.python.org/2/library/unittest.html

NOTE: I found it helpful to run Fiddler while doing these tests as this
allows for visualization of the requests being made to eutils.

"""

from pypub import pubmed as pm

import unittest

class TestPubmedFunctions(unittest.TestCase):
    
    def test_search_with_sort():
        #NOTE: We could iterate over the attributes
        s1 = pm.search('Mountcastle', sort=pm.C_SearchSort.FIRST_AUTHOR)
        s2 = pm.search('Mountcastle', sort=pm.C_SearchSort.LAST_AUTHOR)
        #TODO: Compare s1.ids and s2.ids to make sure that
        
    def test_search_with_less_results():
        #TODO: Check both number and string
        temp = pm.search('Mountcastle', retmax=10)
        temp = pm.search('Mountcastle', retmax='10')
        #TODO: Check that temp.ret_max is 10
        #TODO: Check that length of temp.ids is 10
        
    def test_search_with_spaces():
        #NOTE: It looks like spaces in the search term works just fine
        temp = pm.search('bladder pudendal')
        
    def test_search_with_plus():
        #The + gets escaped
        temp = pm.search('bladder+pudendal')
        
    def test_search_with_null_parameter():
        #Yes, empty values are not sent
        temp = pm.search('genes', retmax=[])
    
    def test_search_with_query_limited_to_field():
        s1 = pm.search('urology', field=pm.C_SearchField.JOURNAL)
        s2 = pm.search('urology')

        #TODO: Ensure s1 result is from journal
                
        