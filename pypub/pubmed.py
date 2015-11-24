# -*- coding: utf-8 -*-
"""
Status:
- Started, working on parsing results of search

Tasks/Examples:
---------------
1) ****** Perform a generic pubmed search ******

from pypub import pubmed as pm
search_result = pm.search('Sydney Brenner',field=pm.C_SearchField.AUTHOR_FULL)

search_result = pm.search('Brenner, Sydney[Full Author Name]')


2) ****** Return information about an id ******

from pypub import pubmed as pm

search_result = pm.search('Brenner, Sydney[Full Author Name]')

entry_info = pm.Entry(search_result.ids[0])



Design Decision:
----------------
This code wraps the extensive Biopython code base for interfacing with the Entrez API.
Specifically it exposes (or will expose) the aspects related to Pubmed. 
From some brief searching Biopython has the best support for API, although
I don't really like it's interface.

At this time I'm simply wrapping the Biopython code. I may change the backend
at a later time, but at this point I'd rather move onto more interesting things.
Biopython in particular is very heavy given what I'm using.

Thre is a smaller version which might be relevant, I'm just not sure how well
it will continue to be maintained, see:
https://github.com/jmaupetit/Bio_Eutils

Entrez API:
-----------
The official Entrez API documentation is at:
http://www.ncbi.nlm.nih.gov/books/NBK25501/

Definitions of fields can be found at:
http://www.nlm.nih.gov/bsd/mms/medlineelements.html

NOTE: Pubmed is only one aspect of the Entrez API.

Biopython:
----------
This code relies on BioPython. That code base is relatively large for what I
need but it seems to work fairly well so I'm using it for now.

Biopython is on GitHub at:
https://github.com/biopython

Biopython Documentation:
Entrez - http://biopython.org/DIST/docs/tutorial/Tutorial.html#sec118


API Functions: 
--------------
The code relies on 



(Exposed in BioPython)


epost

efetch - provides formatted data records for a list of input uids
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EFetch_

esearch - list of uids matching a text query
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_ESearch_

elink - 


einfo - provides a list of the names of all valid Entrez databases
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EInfo_

esummary - provides summary for list of input ids
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_ESummary_

espell

egquery - provides the number of records retreived in all Entrez databases by a single text query
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EGQuery_

ecitmatch - Retrieves PubMed IDs (PMIDs) that correspond to a set of input citation strings.
http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_ECitMatch_

Functions to implement:
===============================================================================
- What types of search should we support?
  - get info for single pubmed ID
  - advanced search builder



Tables to use:
===============================================================================
http://www.nlm.nih.gov/bsd/language_table.html

"""

"""
TODOS:
- create config class
- redo search field code
- fix unicode vs str to be compatible with Python 3 - from __future__ ...


"""


#Use https://github.com/jmaupetit/Bio_Eutils instead????
from Bio import Entrez as _Entrez
from . import utils as _utils
from . import config

#Pubmed asks that you provide a email address for requests
#so they know who is using their services
_Entrez.email = config.user_email
_Entrez.tool  = config.app_name


class C_SearchField():

    """
    Constants for advanced searching or for a simple search 
    where the query is applied to a single field.
    """

    AFFILIATION = 'Affiliation'
    AUTHOR = 'Author'
    AUTHOR_CORPORATE = 'Author - Corporate'
    AUTHOR_FIRST = 'Author - First'
    AUTHOR_FULL = 'Author - Full'
    AUTHOR_IDENTIFIER = 'Author - Identifier'
    AUTHOR_LAST = 'Author - Last'
    BOOK = 'Book'
    DATE_COMPLETION = 'Date - Completion'
    DATE_CREATE = 'Date - Create'
    DATE_ENTREZ = 'Date - Entrez'
    DATE_MESH = 'Date - MeSH'
    DATE_MODIFICATION = 'Date - Modification'
    DATE_PUBLICATION = 'Date - Publication'
    EC_RN_NUMBER = 'EC/RN Number'
    EDITOR = 'Editor'
    FILTER = 'Filter'
    GRANT_NUMBER = 'Grant Number'
    ISBN = 'ISBN'
    INVESTIGATOR = 'Investigator'
    INVESTIGATOR_FULL = 'Investigator - Full'
    ISSUE = 'Issue'
    JOURNAL = 'Journal'
    LANGUAGE = 'Language'
    LOCATION_ID = 'Location ID'
    MESH_MAJOR_TOPIC = 'MeSH Major Topic'
    MESH_SUBHEADING = 'MeSH Subheading'
    MESH_TERMS = 'MeSH Terms'
    OTHER_TERM = 'Other Term'
    PAGINATION = 'Pagination'
    PHARMACOLOGICAL_ACTION = 'Pharmacological Action'
    PUBLICATION_TYPE = 'Publication Type'
    PUBLISHER = 'Publisher'
    SECONDARY_SOURCE_ID = 'Secondary Source ID'
    SUPPLEMENTARY_CONCEPT = 'Supplementary Concept'
    TEXT_WORD = 'Text Word'
    TITLE = 'Title'
    TITLE_ABSTRACT = 'Title/Abstract'
    TRANSLITERATED_TITLE = 'Transliterated Title'
    VOLUME = 'Volume'
    
#------------------------------------------------------------------------------    
#NOTE: This might be better as a function for getting selection options
#
#Matlab code for getting above nearly automatically.
#1) From http://www.ncbi.nlm.nih.gov/pubmed/advanced
#2) right click on the selection elements
    
#values = regexp(str,'value="[^"]+">([^<]+)','tokens');
#wtf    = cellfun(@(x) x{1},values,'un',0)
#wtf2 = cellfun(@(x,y) sprintf('%s = ''%s''',x,y),regexprep(upper(wtf),'\s','_'),wtf,'un',0)
#for i = 1:length(wtf2); disp(wtf2{i}); end    
#------------------------------------------------------------------------------    
    
    
class C_SearchSort():

    """
    Constants for how to sort search results. The strings are mapped to attributes so that tab complete will work
    via the class.

    i.e. sort = C_SearchSort.PUB_DATE - sort by publication date
    """

    RECENTLY_ADDED = 'recently added'
    PUB_DATE       = 'pub date'
    FIRST_AUTHOR   = 'first author'
    LAST_AUTHOR    = 'last author'
    JOURNAL        = 'journal'
    TITLE          = 'title'
    RELEVANCE      = 'relevance'


#def create_advanced_search_string():
#    
#    """
#    The idea with this function is to replicate the advanced search
#    of pubmed by linking terms with fields and combining using logic:
#    (and,or,not)
#    
#    This gets a bit tricky with getting parens in place properly
#    
#    LOW PRIORITY
#    """
#    pass


def search(query_string, retstart=None, retmax=None, sort=None, field=None):

    """
    Exposes generic Pubmed search.
    
    Parameters:
    -----------
    query_string : string
            Search string for Pubmed. All characters are escaped by the calling 
        functions. The results will be invalid if the input string has the 
        characters escaped (e.g. has spaces replaced with '+' characters).
        Include quotes to get an exact match.
            The query string supports Pubmed style query notations.        
        
    retstart: string or integer (default 0)
         Index of the first value to return. Zero indicates that the first 
         record should be returned (0 based indexing).
    retmax: str or int (default 20)
        Maximum # of ids to return
    sort: attribute from class C_SearchSort
        Determines the sort order of the IDs returned.
        Examples:
            sort = C_SearchSort.FIRST_AUTHOR
            sort = C_SearchSort.RELEVANCE
    field: string
        Limits query string to matching in a specified field. It seems
        that this might not work properly with query strings that have spaces.
        Field examples can be found at
    
    Returns:
    --------
    _SearchResult
        Class with results of the search.
    
    Full documentation of underlying method is at:
    http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_ESearch_
    
    Design Decision:
    ---------------------------------------------------------------------
    Some input parameters would cause problems with how this function is
    expected to work. Instead of filtering out all bad parameters I've just
    decided to limit the # of parameters that can be used, instead of using 
    keywords (i.e. instead of **keywds)

    Examples:
    ---------
    >>> from pypub import pubmed as pm
    >>> search_result = pm.search('Hokanson Weber')
    >>> search_result = pm.search('urology',field=pm.C_SearchField.JOURNAL)
    >>> search_result = pm.search('Brenner, Sydney[Full Author Name]')


    #See BioPython code specifics in:
    #https://github.com/biopython/biopython/blob/master/Bio/Entrez/__init__.py
    

    """      
         
    handle = _Entrez.esearch("pubmed", query_string, retstart=retstart, retmax=retmax, sort=sort, field=field)
    record = _Entrez.read(handle)
    handle.close()
   
    return _SearchResult(record)   


class _SearchResult():

    """ 
    
    Result from calling pubmed.search() 

    Attributes:
    -----------
    n_results_total : int
        Number of total results from the search.
    ids : [str]
        Pubmed IDs returned from the search. There will generally be less 
        IDs returned due to defaults on the # of IDs to return from a search.
    translated_query : str
        How Pubmed interpreted the query parameters given to it. This will be
        in the same format as the advanced query strings that are present
        in the Pubmed Advanced Search Builder.
    return_start : int
        0 based counting. 
        Not all ids are necessarily returned for a given search. Instead the
        search returns a subset of ids at a time. For example the search might
        return the first 10 ids or ids 11 - 20. This property indicates
        which ids have been returned by indicating the starting index, such as 
        0 or 10 above.
    raw : dict
        The raw returned output from the underlying API I am using. Normally
        this should not be accessed but I am including it just in case people
        are curious.
        
    TODOs:
    ------
    1) Return information about a given id
    2) Return more ids if present
    3) Create an indicator that indicates whether more ids are present
    
    """
    
    def __init__(self, r):
        """

        Result of a search.        
        
        Parameters:
        -----------
        r : dict
            Result of the search from the underlying
        
        See Also:
        ---------
        search()
        
        """
        
        #NOTE: There are other parameters returned. These values
        #seemed the most relevant
        self.n_results_total = int(r['Count'])
        self.ids     = [str(x) for x in r['IdList']]
        self.translated_query = str(r['QueryTranslation'])
        self.return_start = int(r['RetStart'])
        self.raw = r
        
    def __repr__(self):
        return _utils.print_object(self) 
        
     
#JAH NOTE:
#As I was tinkering I came to fully appreciate the difference between
#esummary and efetch (still haven't check out ecquery)
#
#As such these functions below are now quite messy and unfinished       
    
""" 
class EntrySummary():
    
    def __init__(self, pmid):
        #Call to Biopython
        #-----------------------------
        #handle = Entrez.esummary(db="pubmed", id=pmid, version='2.0')
        handle = _Entrez.esummary(db="pubmed", id=pmid)
        temp   = _Entrez.read(handle)
        handle.close()
      
        #TODO: What about invalid pubmed ids????      
      
        #NOTE: Returned value is a list, as id could be a comma-delimited
        #set of ids
        entry = temp[0]      
      
      
              #DTDs
        #----------------------------
        #esummary-v1.dtd

      
        #Assignment of class attributes
        #---------------------------------   
        self.raw = entry

        prop_key_info = [
            ['DOI'      ,   'DOI'],
            ['author_list', 'AuthorList']
            ['title'    ,   'Title'],
            ['pub_date' ,   'PubDate'],  #Make object
            ['volume'   ,   'Volume'],   
            ['issue'    ,   'Issue'],
            ['pages'    ,   'Pages'],    #Make object, start, stop
            ['ISSN'     ,   'ISSN'],
            ['ESSN'     ,       'ESSN'],
            ['has_abstract',    'HasAbstract'],
            ['pub_status',      'PubStatus']
            ['pmc_ref_count',   'PmcRefCount']
            ['references',      'References']]
            
            
        for pk in prop_key_info:
            #NOTE: Using this approach we can handle null values
            #We could also add on conversion functions 
            cur_attr = pk[0]
            cur_key  = pk[1]
            try:
                setattr(self,cur_attr,entry[cur_key])
            except KeyError:
                setattr(self,cur_attr,None)
    
    def __repr__(self):
        return _utils.print_object(self)
"""

class Entry():

    """ 
    
    Information about a Pubmed Entry given a Pubmed ID.
    
    Implements EFetch:
    http://www.ncbi.nlm.nih.gov/books/NBK25499/#_chapter4_EFetch_
    
    #NOTE: This is a work in progress    
    
    Attributes
    -------------------------
    
    
    
    """    
    
    def __init__(self, pmid):
        
        """ 
        
        Parameters:
        -----------
        pmid : str
            Pubmed ID of which to get information
        
        
        Examples:
        ---------
        >>> from pypub import pubmed as pm
        >>> wtf = pm.Entry('19497827')
        
        """

        #TODO: Check that ID is a string not a number

        #TODO: id needs to be a singular value, if multiple values are present
        #should an array of objects be created?

        handle       = _Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        read_results = _Entrez.read(handle)
        handle.close()
        
        #TODO: What happens on PMID being wrong ...        
        
        first_entry = read_results[0] #Assuming 1 ID, grab it
        

        #----------------------------------------------------------------------
        """
        #Fields of MedlineCitation - 
        #------------------------------------------------------
        PMID                - getting from pubmed data, skipping here
        DateCreated         - http://www.nlm.nih.gov/bsd/licensee/catrecordxml_element_desc2.html#DateCreated
        DateCompleted?      - http://www.nlm.nih.gov/bsd/licensee/catrecordxml_element_desc2.html#DateCompleted
        DateRevised?        - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#daterevised
        x Article             - DONE - parsed separately
        MedlineJournalInfo  - DONE
        ChemicalList?       - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#chemicallist
        SupplMeshList?      - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#supplmesh
        CitationSubset*     - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#citationsubset
        CommentsCorrectionsList? - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#commentscorrections
        GeneSymbolList?     - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#genesymbollist
        x MeshHeadingList?    - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#meshheadinglist
        NumberOfReferences? - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#numberofreferences
        PersonalNameSubjectList? - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#personalnamesubjectlist
        OtherID*            - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#otherid
        OtherAbstract*      - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#otherabstract
        KeywordList*        - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#keywordlist
        SpaceFlightMission* - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#spaceflightmission
        InvestigatorList?   - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#investigatorlist
        GeneralNote*        - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#generalnote
        """
        #nlmmedlinecitationset_140101.dtd
        medline_citation = first_entry['MedlineCitation'] 
        
        prop_key_arg = [
        ['mesh_info',       'MeshHeadingList',      _mesh_parser]]

        _utils.assign_props_with_function(self,medline_citation,prop_key_arg)
        
        #----------------------------------------------------------------------    
        """
        #Fields of Article - PARSED
        #-------------------------------------------------------
        x Journal         - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#journal
        x ArticleTitle    - Done - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#articletitle
        TODO: (Pagination,ELocationID*)|ELocationID+
        x Abstract?       - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#abstract
        x AuthorList?     - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#authorlist
        x Language+       - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#language
        DataBankList?   - SKIP - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#databanklist
        x GrantList?      - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#grantlist
        PublicationTypeList - SKIP?? - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#publicationtypelist
            - I think this is part of MeSH as well        
        VernacularTitle?    - SKIP - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#verniculartitle
        x ArticleDate*        - DONE - http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#articledate
        """

        article = medline_citation['Article']  
        
        prop_key_arg = [
        ['abstract',        'Abstract',     _abstract_parser],
        ['article_date',    'ArticleDate',  str], #??? Correct conversion???
        ['author_list',     'AuthorList',   _author_parser],
        ['language',        'Language',     None], #Might be one or more
        ['title',           'ArticleTitle', str],
        ['grant_list',      'GrantList',    _grant_parser]]
        _utils.assign_props_with_function(self,article,prop_key_arg)    
                
        self.journal = _JournalInfo(medline_citation['MedlineJournalInfo'],article['Journal'])
        
        #----------------------------------------------------------------------
        """
        #PubmedData - PARSED
        #--------------------------
        x ArticleIdList - DONE
        History - NOT DONE
        x PublicationStatus - DONE
        """
        
        pubmed_data = first_entry['PubmedData']  
        prop_key_arg = [
        ['ids',             'ArticleIdList',        _IDList],
        ['pub_status',      'PublicationStatus',    str]]
        _utils.assign_props_with_function(self,pubmed_data,prop_key_arg)        
        
        
        #import pdb
        #pdb.set_trace()       
        
    def __repr__(self):
        return _utils.print_object(self)
        
    def to_bibtex(self):
        pass
#------------------------------------------------------------------------------
def _abstract_parser(abstract_dict):

    #TODO: This should eventually switch based on type
    #simple vs complex
    #See current switch in the constructor below
    return _Abstract(abstract_dict)
        
        
class _Abstract():

    def __init__(self,abstract_dict):
                
        #http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#abstract            
        
        temp = abstract_dict['AbstractText']     
        
        first_element = temp[0]

        self.background  = ""
        self.objective   = ""
        self.methods     = ""
        self.results     = ""
        self.conclusions = ""
                
        
        #TODO: Inherit the complex abstract from the simple ...
        if hasattr(first_element,'attributes'):

            for x in temp:
                #Format:
                #- string with attributes
                #- NlmCategory - official name
                #- Label - label by publisher
                cur_attributes = x.attributes
                prop_name = cur_attributes['NlmCategory'].lower()
                #TODO: Need attribute
                setattr(self,prop_name,str(x))
                
            #TODO: This doesn't handle missing entries well ..
            #Adds an extra space ...
            self.text = self.background + " " + self.objective + " " + self.methods + " " + self.results + " " + self.conclusions    
        else:
            self.text = str(first_element)
        
        #import pdb
        #pdb.set_trace()
        #List
        
        #BACKGROUND, OBJECTIVE, METHODS, RESULTS, CONCLUSIONS
    def __repr__(self):
        return _utils.print_object(self)        
        
#------------------------------------------------------------------------------
def _author_parser(author_list):
    
    return [_Author(x) for x in author_list if x.attributes['ValidYN'] == 'Y']

class _Author():
    
    def __init__(self,author):
        
        #http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#authorlist
        
        #(A) Valid - invalid indicates an error in the original publishing ...
        #LastName
        #ForeName?
        #Suffix?
        #Initials?
        #----------------
        #OR CollectiveName
        #---------------------
        #Identifier*
        #   (A) Source
        #Affiliation? - This can be really weird - not well defined ...
        
        if 'CollectiveName' in author:
            prop_key_arg = [['collective_name', 'CollectiveName', str]]
        else:
            prop_key_arg = [
            ['last_name',       'LastName',     str],
            ['fore_name',       'ForeName',     str],
            ['suffix',          'Suffix',       str],
            ['initials',        'Initials',     str]] 
        
        prop_key_arg.append(['affiliation', 'Affiliation', str])
        
        #TODO: Check for Identifier ...    
        
        _utils.assign_props_with_function(self,author,prop_key_arg) 
         
         #TODO: Create display method - format????
         # First Last, Initials ????
         # Last, First Initials ????
         
    def __repr__(self):
        return _utils.print_object(self)    
#------------------------------------------------------------------------------
def _grant_parser(grant_list):
            
    return [_Grant(x) for x in grant_list]
    
class _Grant():        
        
     def __init__(self,grant):
         #http://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#grantlist    
         #GrantID?
         #Acronym?
         #Agency
         #Country
         prop_key_arg = [
         ['grant_ID',    'GrantID',  str],
         ['acronym',     'Acronym',  str],
         ['agency',      'Agency',   str],
         ['country',     'Country',  str]]
         _utils.assign_props_with_function(self,grant,prop_key_arg)  
     
     def __repr__(self):
         return _utils.print_object(self)
        
#------------------------------------------------------------------------------
class _IDList():

    """ 
     
    This class holds ids.
     
    Attributes:
    ----------------------------------------
    doi : str (default None)
        The Digital Object Identifier. Ex. '10.1109/TNSRE.2009.2023295'    
    pubmed: str (default None)
        Pubmed ID. Ex. '19497827'
    pmc: str (default None)
        Pubmed Central ID: Ex. 'PMC3062993'
    pii: str (default None)
        Publisher controlled identifier. This can sometimes be used to directly
        request a resource from the publisher.
      
    """
     
    _HANDLED_IDS = ['doi','pubmed','pmc','pii']

    def __init__(self,id_list):
        self.doi    = None
        self.pubmed = None
        self.pmc    = None
        self.pii    = None

        other_ids = list()
        
        handled_ids_local = self._HANDLED_IDS        
        
        for str_elem in id_list:
            value = str(str_elem) #Conversion from StringElement class
            id_type = str_elem.attributes['IdType']
            if id_type in handled_ids_local:
                setattr(self,id_type,value)
            else:
                other_ids.append(id_type)
                
        self.other_ids = other_ids        
        
        #Skipping:
        #
        #   Details can be found at links through:
        #   http://www.ncbi.nlm.nih.gov/IEB/ToolBox/CPP_DOC/asn_spec/
        #------------------------------------------------------------------
        #pmcpid - Publisher Id supplied to PubMed Central
        #mid - http://www.nlm.nih.gov/bsd/mms/medlineelements.html#mid
        #sici ???
        #pmcbook
        #bookaccession
        
    """
    <!ENTITY % art.id.type.int "pubmed | medline | pmcid | pmcbook | bookaccession">
    							
    <!ENTITY % art.id.type "(doi | pii | pmcpid | pmpid | pmc | mid |
                                  sici | %art.id.type.int;)">
    """  
        
    def __repr__(self):
        return _utils.print_object(self)        
        
#------------------------------------------------------------------------------
class _JournalInfo():
    
    """
    Contains information about the journal from which an entry came.
    """    
    
    def __init__(self,medline_journal_info,journal):
        #Medline Journal Info - mji
        #----------------------------------------------------------------------
        #Country?
        #MedlineTA - http://www.nlm.nih.gov/bsd/licensee/catrecordxml_element_desc2.html#MedlineTA
        #NlmUniqueID? - http://www.nlm.nih.gov/bsd/licensee/catrecordxml_element_desc2.html#NLMUniqueID
        #ISSNLinking?
        #
        #Journal - journal
        #----------------------------------------------------------------------
        #ISSN?
        #   - (A) IssnType (Electronic|Print) Required
        #JournalIssue
        #   - Volume?
        #   - Issue?
        #   - PubDate - How does this differ from other pub date?????
        #   - (A) CitedMedium (Internet|Print) Required
        #Title?
        #ISOAbbreviation?
        prop_key_arg = [
        ['country',         'Country',      str],
        ['medline_abbreviation',    'MedlineTA',    str],
        ['NLM_id',          'NlmUniqueID',  str],
        ['ISSN_linking',    'ISSNLinking',  str]]
        _utils.assign_props_with_function(self,medline_journal_info,prop_key_arg)  

        prop_key_arg = [
        ['title',               'Title',  str],
        ['ISO_abbreviation',    'ISSNLinking',  str]]                
        _utils.assign_props_with_function(self,journal,prop_key_arg)  
   
        #TODO: Extract other ISSN values ...
        #TODO: Do we need to use pub date????

        journal_issue = journal['JournalIssue']
        
        prop_key_arg = [
        ['volume',      'Volume',   str],
        ['issue',       'Issue',    str]]                
        _utils.assign_props_with_function(self,journal_issue,prop_key_arg) 
   
        self.cited_medium = journal_issue.attributes['CitedMedium']
   
    def __repr__(self):
        return _utils.print_object(self)      
   
def _mesh_parser(mesh_heading_list):

    """ 
    Since there are multiple Mesh Entries I wanted something
    that would determine how many to create 
    
    This was an attempt at better encapsulation ...    
    
    """

    return [_MeshElement(x) for x in mesh_heading_list]

   
class _MeshElement():
    
    """
    
    See link for more on MeSH:
    http://www.nlm.nih.gov/mesh/meshhome.html
    
    Major Topics:
    http://www.nlm.nih.gov/bsd/disted/meshtutorial/principlesofmedlinesubjectindexing/majortopics/    
    
    """
    #consists of one ore more MeshHeading
    #MeshHeading - DescriptorName, qualifier name*)
    #DescriptorName - Major Topic (Y or No). Type (Geographic) - implied    
    
    
    def __init__(self,MeshHeadingList):
        temp = MeshHeadingList['DescriptorName']
        self.name = str(temp)
        self.is_major = temp.attributes['MajorTopicYN'] == 'Y'
        #qualifiers = MeshHeadingList['QualifierName']
        #TODO: Finish handling qualifier
        #TODO: Determine how to go from this to a representation
        #TODO: How do we extract numbers for these to allow easier searching?
        
    def __repr__(self):
        return _utils.print_object(self)