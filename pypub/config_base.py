# -*- coding: utf-8 -*-
"""
This is the example file from which configurations should be created.
"""

#This email will be used anywhere that an email is tied to API usage. It was
#originally created for the Entrez API (Pubmed)
user_email = ''

#Name of the tool being used. If this repo is being used in conjunction with some "app" it is recommended that the app
#name is specified here. This will be sent to any APIs that request these names.
app_name = ''

#http://www.developers.elsevier.com/cms/index
#TODO: Describe how to get this info
class Elsevier:
    """ Information needed in order to work with the ElSevier API. """
    api_key = ''
