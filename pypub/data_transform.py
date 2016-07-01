# Third party imports
import pandas

# Local imports
from pypub.paper_info import PaperInfo
from pypub.scrapers.base_objects import *

def df_to_paper_info(df_row):
    df_dict = df_row.to_dict()
    paper_info = PaperInfo()

    entry = BaseEntry()
    entry.title = df_dict.get('title')
    entry.publication = df_dict.get('publisher')



    return paper_info
