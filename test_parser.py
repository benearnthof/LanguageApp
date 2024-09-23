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


# there is something wrong with the requests we are sending
req = parser10k.requests[0]
resource = urlopen(req)

parser10k.parse_dictionary()
parser10k.verify_dictionary()


# investigating the failed requests:
infile = "debug.log"

with open(infile) as f:
    f = f.readlines()

failed_requests = [line for line in f if "Unable" in line]

# 45 requests fail, probably because of collins dictionary as the site varies for some words
# around 1000 words did not get a translation at all, we need to fix them.
# we have verified and word list. We can get missing translations and examples from deepl and context reverso


# which word has the most valid translations?
len(parser10k.target_dictionary)

synonyms = [(index, len(entry['translations'])) for index, entry in enumerate(parser10k.target_dictionary)]

current = (0, 0)
for tup in synonyms:
    if tup[1] > current[1]:
        current = tup

parser10k.target_dictionary[current[0]]["french"]
parser10k.target_dictionary[current[0]]["translations"]
