from parser import DictionaryParser
from bs4 import BeautifulSoup
import gzip
import io
from urllib.request import Request, urlopen
from pathlib import Path
from tempfile import gettempdir
from unicodedata import normalize
from unidecode import unidecode
from tqdm.auto import tqdm, trange
import csv
from typing import Optional
import logging
import sys
import hashlib
import json

# parser = DictionaryParser("test_words.csv")
# assert len(parser) == 9
# parser.parse_dictionary()
# parser.load_target_dictionary()

parser10k = DictionaryParser("french_words.csv", target_dict_path="french_dictionary.json")

len(parser10k.target_dictionary)

parser10k.verify_dictionary()


# there is something wrong with the requests we are sending
req = parser10k.requests[0]
resource = urlopen(req)





parser10k.parse_dictionary()





missing_translations = [x for x in parser10k.target_dictionary if len(x["translations"]) < 1]

valid_entries = [x for x in parser10k.target_dictionary if len(x["translations"]) > 0]
parser10k.target_dictionary = valid_entries
parser10k.save_target_dictionary()
