# Pypub

## Code summary

[![Join the chat at https://gitter.im/ScholarTools/pypub](https://badges.gitter.im/ScholarTools/pypub.svg)](https://gitter.im/ScholarTools/pypub?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)     

This code is currently under development. The goal is to bring together APIs and/or scrapers for working with publication websites (and related material).

When I have some functional examples of this in action I'll add them!

Roadmap:

- expose Pubmed (started)
- CrossRef
- ElSevier API
- other publishers?
- Mendeley Client

## Supported publishers
Currently, Pypub supports information retrieval from ScienceDirect, Springer, Wiley Online, and Nature Reviews Genetics. Taylor & Francis recently moved to a new article page format, so the corresponding file needs to be updated. 


## Main usage
The easiest way to use this repo is with `get_paper_info`, a top-level function. It takes two optional keyword arguments, `url`, and `doi`. It can be called with `paper_info = pypub.get_paper_info(doi='enter_doi_here', url='or_enter_url_here')`.  

### Result format
The `get_paper_info` method returns a `PaperInfo` object, the details for which can be found in `paper_info.py`. A `PaperInfo` object has three main attributes of interest: `entry`, `references`, and `pdf_link`. `entry` will contain all descriptive information about the paper, such as title, authors, journal, year, etc. `references` is a list of references, and `pdf_link` is a string, which gives the direct link to the paper PDF, if it could be retrieved.

Within the `scrapers/base_objects.py` file, there are several classes that each publisher inherits from to return information. The `entry` attribute will be a `[Publisher]Entry` class, which inherits from `BaseEntry`. Similarly, the `references` attribute is a list of `[Publisher]Ref` class instances that inherit from `BaseRef`.


## Coding Standards

Documentation Standards, I'm trying to follow this:
https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Encapsulation! Encapsulation! Encapsulation!
Ideally each module should have a well defined purpose that doesn't work with data that is not its own.

## Testing
Within the `tests` folder, there are separate test modules for each of the scrapers. They are written for `nosetests`.