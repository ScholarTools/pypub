Code summary
==============

This code is currently under development. The goal is to bring together APIs and/or scrapers for working with publication websites (and related material).

When I have some functional examples of this in action I'll add them!

Roadmap:

- expose Pubmed (started)
- CrossRef
- ElSevier API
- other publishers?
- Mendeley Client

Code source
===================
This is a fork from Heather Piwowar's pypub repo. Although I think Heather and I have the same goals in mind, I'm starting fresh and slowly incorporating her code, as well as code from others, into the repo.

Package Requirements
=======================

**Biopython:** https://github.com/biopython/biopython

| For interacting with Pubmed
| I might eventually get rid of this because installing Biopython can be a bit of a pain
| NOTE: I've also had to manually install several DTDs which will supposedly be fixed soon.


**Requests:** https://github.com/kennethreitz/requests

| For doing http requests
| pip install requests
| NOTE: I'm not actually using Requests yet

Coding Standards
==================================

Documentation Standards, I'm trying to follow this:
https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

Encapsulation! Encapsulation! Encapsulation!
Ideally each module should have a well defined purpose that doesn't work with data that is not its own.

TODO: Define variable naming conventions

