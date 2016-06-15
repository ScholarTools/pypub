# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 14:35:23 2015

@author: RNEL
"""

class ParseException(Exception):
    pass

class InsufficientCredentialsException(Exception):
    pass

class InputError(Exception):
    pass

class ScraperError(Exception):
    pass

class UnsupportedPublisherError(Exception):
    pass
