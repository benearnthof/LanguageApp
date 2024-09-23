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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

class DictionaryParser():
    """
    Take a .csv file of words and look up their english translations and example quotes.
    Store everything in a dictionary and write a .json to disk.
    """
    def __init__(
        self, 
        csv_path: str,
        target_dict_path: Optional[str] = "french_dictionary.json",
        rooturl: str = "https://www.collinsdictionary.com/dictionary/french-english/"
        ):
        self.logger = logging.getLogger()
        self.csv_path = csv_path
        self.rooturl = rooturl
        self.target_dict_path = target_dict_path
        self.word_list = self.parse_csv()
        # TODO: Force user to provide valid cookie. Check if request works then continue with init
        self.requests = self.build_requests()
        self.target_dictionary = self.load_target_dictionary()

    def __len__(self):
        return len(self.word_list)

    def parse_csv(self):
        """Extract list of words from csv"""
        with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            french_words = [x[0] for x in reader]
        return french_words
    
    def build_requests(self):
        """Build all requests from list of target words."""
        requests = []
        for word in tqdm(self.word_list):
            target = unidecode(word)
            if " " in target:
                target.replace(" ", "-")
            req = Request(f"https://www.collinsdictionary.com/dictionary/french-english/{target}")
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8')
            req.add_header('Accept-Language', "en-US,en;q=0.5")
            req.add_header('Accept-Encoding', 'gzip, deflate, br, zstd')
            req.add_header('Referer', 'https://www.google.com/')
            req.add_header('Connection', 'keep-alive')
            # FIXME: Need logic to refresh cookie with browser input. Should be done upon init
            req.add_header('Cookie', "dictcode=french-english; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Sep+23+2024+16%3A12%3A13+GMT%2B0200+(Central+European+Summer+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=%3B; search=revenant; OptanonAlertBoxClosed=2024-09-23T14:12:13.796Z; _sp_id.a65e=89ae10bc-c518-4a54-b1ad-21915386119f.1704373384.31.1727100734.1727097640.c85ec6e4-eb22-40b3-886c-c844bcb8fc2f.7dfe78c7-feae-4e81-a226-230029b54f92.6c6f0337-9c7f-4573-bf13-f0261bcdfda0.1727100143259.23; searchPanelOpen=true; XSRF-TOKEN=156dcaff-c54b-4a7c-a4bb-2694a7c011a6; __cflb=02DiuFwNDm462z9fWfJeB58usqeie1xoT21wVKJV8LQWG; __cf_bm=MxGAomkVeMfc1LzqLpIyTMd9UdKjG1NKw8wITxhoNIo-1727100156-1.0.1.1-s.cTyZj_qgvaTqnp5KydMbvzbdUpaYal3ava7OxuGQ8DyJQQA489yWlXRRex5B8ozk52Nxe7MIgVsVbLAxqNeA; _sp_ses.a65e=*; cf_clearance=tFl.VhfQAeyAJn8_BoSirlKoAf8nS5.QNAXnAtD6QqE-1727100157-1.2.1.1-qkXBIt1gSP69bBxugUWgKYX.KJsRXfYOClngAu5N1hg46nfRjqjkCcTBohCWQc.VtWHLV3oGAIPZ0_qNBn3BuXS0kV4sOBAB.p8TavNj8juv.j.1BVG0B0hCjg9ynqZoG6g1oX9x3nLCPebArSNXleEEi.GJaJwC0Tnrup1FKcLT8vUrzzW7LTsHFDVMH25reqSMH65nadmzKbbaf9NB28hsGWOipwfv_BOrHpHbS231d1XBVYDMI4Fi9siYLVkY6DIcTAppUfqjMUZqSqs1Gv79tJeArYvhNCnKoZKxifWorhJDzo8o2Z5o3l9ZszqV86zl04yI844cdwi3Ywmy.QDY0WvEXBenjaUiob4Nu_A")
            req.add_header('Upgrade-Insecure-Requests', 1)
            req.add_header('Sec-Fetch-Dest', "document")
            req.add_header('Sec-Fetch-Mode', "navigate")
            req.add_header('Sec-Fetch-Site', "cross-site")
            req.add_header('Sec-Fetch-User', "?1")
            req.add_header('Priority', "u=0, i")
            req.add_header('Pragma', "no-cache")
            requests.append(req)
        self.logger.info(msg=f"Built {len(requests)} requests from provided word list.")
        return requests

    @staticmethod
    def parse_resource(res):
        try:
            # Check if the content is gzip-encoded
            if res.info().get('Content-Encoding') == 'gzip':
                # Decompress the gzip content
                gzip_file = io.BytesIO(res.read())
                with gzip.GzipFile(fileobj=gzip_file) as decompressed:
                    content = decompressed.read()
            else:
                # If not gzip-encoded, read directly
                content = res.read()
            # Attempt to decode the content (adjust encoding if needed)
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # If UTF-8 fails, you might try other encodings
                return content.decode('iso-8859-1')  # or another encoding
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def save_and_parse_html(html_content, writefile=False, filename="output.html"):
        # Save the HTML content to a file
        if writefile:
            outdir = Path(gettempdir() / Path(filename))
            with open(outdir, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"HTML content saved to {outdir}")
        # Parse the HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    @staticmethod
    def extract_quote_pair(html_tag):
        french_quote = html_tag.find('span', class_='quote')
        english_translation = html_tag.find('span', class_='cit type-translation').find('span', class_='quote')
        if french_quote and english_translation:
            return {
                'french': normalize("NFKD", french_quote.get_text(strip=True)),
                'english': normalize("NFKD", english_translation.get_text(strip=True))
            }
        else:
            return None

    def get_quotes(self, html_content):
        """
        Extract quotes and translations for word
        """
        return [self.extract_quote_pair(x) for x in html_content]

    @staticmethod
    def extract_translations(html_tag):
        translation_span = html_tag.find("span", class_="cit type-translation")
        if translation_span:
            # Find the first anchor tag within this span
            translation_anchor = translation_span.find('a', class_='quote')
            if translation_anchor:
                # Extract the text from the anchor tag
                return translation_anchor.get_text(strip=True)
        return None  # Return None if no translation is found

    def get_translations(self, html_content):
        return list(set([x for x in [self.extract_translations(x) for x in html_content] if x]))

    def load_target_dictionary(self):
        if self.target_dict_path is None:
            self.logger.info("No target dictionary path given, initializing empty target dictionary.")
            return []
        elif Path(self.target_dict_path).exists():
            self.logger.info(f"Loading target dictionary from {Path(self.target_dict_path)}.")
            with open(self.target_dict_path) as f:
                target_dictionary = json.load(f)
                return target_dictionary
        else: 
            self.logger.info(f"No existing target dictionary found at {Path(self.target_dict_path)}. Initializing as empty list.")
            return []

    def save_target_dictionary(self):
        if self.target_dict_path is None:
            self.logger.info("No target dictionary path given, target dictionary was not saved.")
        elif Path(self.target_dict_path).exists() and self.target_dictionary is not None:
            self.logger.info(f"Found target dict at {Path(self.target_dict_path)}. Overwriting...")
            with open(self.target_dict_path, 'w') as f:
                json.dump(self.target_dictionary, f)
        else:
            self.logger.info(f"Creating new target dictionary at {Path(self.target_dict_path)}")
            with open(self.target_dict_path, 'w') as f:
                json.dump(self.target_dictionary, f)

    def parse_dictionary(self):
        """
        Use list of words and list of requests to build a dictionary.
        Dictionary keys are ids.
        Dictionary Values are words and their translations & quotes.
        Something like this: 
        {
            'id': word[0],
            'french': word[1],
            'translations': json.loads(word[2]),
            'examples': json.loads(word[3])
        }
        """        
        for index, req in enumerate(pbar := tqdm(self.requests)):
            word = self.word_list[index]
            hashid = hashlib.sha1((word + str(index)).encode("utf-8")).hexdigest()
            if self.target_dictionary and any([x['hashid'] == hashid for x in self.target_dictionary]):
                self.logger.info(f"Found {word} in dictionary, skipping...")
                continue
            try:
                # TODO: after about 3000 requests this fails
                resource = urlopen(req)
                content = self.parse_resource(resource)
                soup = self.save_and_parse_html(content, writefile=False)
                # Step 1: Obtain all quotes with collins dictionary
                div = soup.find_all("div", class_= "cit type-example")
                quotes = self.get_quotes(div)
                # Step 2: Obtain the correct translations instead of the shitty google translate ones
                div = soup.find_all("div", class_= "sense")
                translations = self.get_translations(div)
                output = {
                    'hashid': hashid,
                    'index': index,
                    'french': word,
                    'translations': translations,
                    'examples': quotes
                }
                (temp := translations[0] if translations else "None")
                pbar.set_description(f"In: {word} Out: {temp}")
                self.target_dictionary.append(output)
            except:
                self.logger.info(f"Unable to parse url for word {word} at position {index}.")
        self.save_target_dictionary()
        self.logger.info("Finished Parsing dictionary")

    def verify_dictionary(self):
        valid_entries = [x for x in self.target_dictionary if len(x["translations"]) > 0]
        self.logger.info(f"Removed {len(self.target_dictionary) - len(valid_entries)} invalid entries from dictionary")
        self.target_dictionary = valid_entries
        self.save_target_dictionary()

    def fill_in_missing_words(self):
        """Fill in missing values with deepl."""
        # TODO: Add to fill in missing words
        pass

    def fill_in_missing_examples(self):
        """Fill in missing examples with context.reverso.net"""
        # TODO: Add to fill in missing examples


# FIXME: Parallel scraping would be nice
