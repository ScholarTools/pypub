# -*- coding: utf-8 -*-
"""
For an example page see:
http://www.jneurosci.org/content/23/10/4355.long#ref-list-1

Note that JNeuroscience seems to be part of a consortium with J Physiology,
J Neurophysiology, PNS, etc

perhaps check out HighWire Press?


"""

import requests
from bs4 import BeautifulSoup

class JNeuroscienceRef(object):
    
    def __init__(self):
        pass        


    """
    <li><span class="ref-label ref-label-empty"></span>
    <a class="rev-xref-ref" href="#xref-ref-40-1" id="ref-40" title="View reference in text">â†µ</a>
    <div class="cit ref-cit ref-other" id="cit-23.10.4355.40">
    <div class="cit-metadata"><cite>Yoshimura N, Seki S, 
    de Groat WC (<span class="cit-pub-date">2001b</span>) 
    Nitric oxide  modulates Ca<sup>2</sup><sup>+</sup> channels in 
    dorsal root ganglion neurons  innervating rat urinary bladder. 
    <span class="cit-source">J Neurophysiol</span> <span class="cit-vol">86
    </span>: <span class="cit-fpage">304</span>â€“311.</cite></div>
    <div class="cit-extra"><a class="cit-ref-sprinkles cit-ref-sprinkles-ijlinks" 
    href="/cgi/ijlink?linkType=ABST&amp;journalCode=jn&amp;resid=86/1/304">
    <span class="cit-reflinks-abstract">Abstract</span><span class="cit-sep 
    cit-reflinks-variant-name-sep">/</span><span class="cit-reflinks-full-text">
    <span class="free-full-text">FREE </span>Full Text</span></a></div>
    </div>
    </li>
    """


def get_references(url):
    
    r = requests.get(url)     
            
    soup = BeautifulSoup(r.text)
    
    ref_section = soup.find('div',{'class':'section ref-list'})
    
    ref_entries = ref_section.find_all('li')
    import pdb
    pdb.set_trace()
    pass