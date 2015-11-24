# -*- coding: utf-8 -*-
"""

Examples
--------
1) 

    from pypub import google_scholar as gs
    
    s = gs.Scholar()
    
    s.check_signed_in()


Other Options
--------------
There are a few other options that exist. Some of these are pretty good.

1) scholar.py - https://github.com/ckreibich/scholar.py

This one is pretty good but I don't like its command line centric focus. It
will probably serve as a reference.

2) google_scholar - https://github.com/JimHokanson/google_scholar

Looking back it seems a bit brash that I took the most obvious name for a repo 
of this type. This is all Matlab code. I'll be relying heavily on this when
doing the Python code.

Issues
------
1) Submitting a form

    Could use mechanize, but I'm more comfortable with requests

http://www.pythonforbeginners.com/cheatsheet/python-mechanize-cheat-sheet

http://stackoverflow.com/questions/8377055/submit-data-via-web-form-and-extract-the-results

"""


#Old PyPub also has a google scholar entry
#https://github.com/JimHokanson/google_scholar


#import requests
#from bs4 import BeautifulSoup as soup

_GS_URL = 'https://scholar.google.com'

class ParseError(Exception):
    """Assumptions made about the web content were incorrect"""
    pass

class Scholar:
    
    """
    Attributes
    ----------
    s : 
        The session
    signed_in : logical
    user_name
    sign_in_link : string
        Populated via the check_signed_in method

    """
    def __init__(self):
        #TODO: Load session from disk ...
        self.s = requests.Session()
    
    def _get_page(self,url):
        #* We might change our use of requests and I'd like
        #to hide this aspect from the other methods in case I decide to switch
        temp = self.s.get(url)
        return soup(temp.text)

    def check_signed_in(self, gs_page = None):
        """
        
        Parameters
        ----------
        gs_page : some soup type ...
            This can be passed in to avoid needing to rerequest a page.
            
        Populates
        ---------
        signed_in
        sign_in_link
        signed_in_name
        """
        
        #This can be found by inspecting either sign_in or gmail
        #address on top
        SIGN_IN_TAG_TUPLE = ('div',{"id":"gs_gb_rt"})        
        SIGN_IN_TEXT = 'Sign in'        
        
        if gs_page is None:
            gs_page = self._get_page(_URL)
        
        temp = gs_page.find(*SIGN_IN_TAG_TUPLE)        
        
        if temp is None:
            raise ParseError('Unable to find sign_in tag')
        
        self.signed_in = temp.text == SIGN_IN_TEXT
        
        if self.signed_in:
            self.sign_in_link = temp.find('a')['href']
            self.signed_in_name = ''
        else:
            #This might be wrong, check once we've signed in ...
            self.user_name = temp.text
        
    
        
        import pdb
        pdb.set_trace()
        
        return self.signed_in
    
    def sign_in(self,user=None,pass=None):
        
        if not self.check_signed_in:
            sign_in_page = self._get_page(self.sign_in_link)
            
            #Now we need to construct a form ...


    
    def search(self):
        pass
    
def search():
    pass    
    