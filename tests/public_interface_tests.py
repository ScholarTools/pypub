# -*- coding: utf-8 -*-
"""
"""

import pypub

# 10.1159/000281893

#doi = '10.1159/000281893' - Karger.com - unimplemented
#doi = '10.3909/riu0653' #not valid - currently causes an invalid crash
doi = '10.1016/j.juro.2014.03.080' #uses javascript to redirect :/

result = pypub.get_paper_info(doi)
