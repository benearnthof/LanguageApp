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

class DictionaryParser():
    """
    Take a .csv file of words and look up their english translations and example quotes.
    Store everything in a dictionary and write a .json to disk.
    """
    def __init__(
        self, 
        csv_path: str,
        rooturl: str = "https://www.collinsdictionary.com/dictionary/french-english/"
        ):
        self.csv_path = csv_path
        self.rooturl = rooturl
        self.word_list = self.parse_csv()
        self.requests = self.build_requests()


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
            req = Request(f"https://www.collinsdictionary.com/dictionary/french-english/{target}")
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8')
            req.add_header('Accept-Language', "en-US,en;q=0.5")
            req.add_header('Accept-Encoding', 'gzip, deflate, br, zstd')
            req.add_header('Referer', 'https://www.google.com/')
            req.add_header('Connection', 'keep-alive')
            req.add_header('Cookie', "dictcode=english; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Sep+22+2024+15%3A47%3A57+GMT%2B0200+(Central+European+Summer+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false&geolocation=%3B; search=tired; OptanonAlertBoxClosed=2024-09-22T13:47:57.194Z; _sp_id.a65e=89ae10bc-c518-4a54-b1ad-21915386119f.1704373384.24.1727012948.1725047739.19c4f032-0ece-4a62-9126-58666cda97b5.57993c83-cd25-4954-b1ec-5bc9928da09d.937055f8-123d-49fc-9235-819b9937ab46.1727009550798.33; XSRF-TOKEN=aa9cc3be-3fb8-40a8-8f6a-14a4a6688b57; __cf_bm=Q3t5713M.0dSuBcNfQiYjLrQ.XbopJoLX7w_YZe7aZc-1727012310-1.0.1.1-mThgLqatf9yVYnb9VrUj3tQ6SB61uPnjTe8z9Z3fRjN66Gp16D4EK1U99wfNy47ApM.6RSeNpTeg_P0sqvifCg; __cflb=02DiuFwNDm462z9fWfJeB58usqeie1xoSFfw8vtVHcfoA; _sp_ses.a65e=*; cf_clearance=Qsj16LdYDnbi89EmCuoFazU.Q26b8HvYXH_urmkqHho-1727012316-1.2.1.1-0Kich.LCajmMpiTQ7.NF2nOag37HzSYIFQ3eGZ65zOqv1rHiffqdr1no88f0KlJ77Wt5K2pJ_G9olK1Ukjlm0d8RGxX0GvQkgCX2I90Km5T1o_HMc49ZFher1vjIFZmVcFFPPkGYWJA5Z5Yhht3OZ43sUoTX9gMg0UhwGapGRAvQkjlXfUUerIKZg8r46bRt2EI4oAad.rU7ypZKIHKNWXpEKvTkeGE_6aEoGVQP7oNzFy9FZLQm_Ko5IcYx3BM.eX9.5WoWJ6UWf_V..E1.hAfJO2b5dF1YU.0hZ7W7QQNy.yYAHAqLhThSLFYgQyYHCR8WCd3dDTptJkb.yTOmqTQHsHtlAZ6E9qfMnyk14rs; JSESSIONID=94A6C7C1E28076C5BF87DDAD33DDE79A-n1")
            req.add_header('Upgrade-Insecure-Requests', 1)
            req.add_header('Sec-Fetch-Dest', "document")
            req.add_header('Sec-Fetch-Mode', "navigate")
            req.add_header('Sec-Fetch-Site', "cross-site")
            req.add_header('Sec-Fetch-User', "?1")
            req.add_header('Priority', "u=0, i")
            req.add_header('Pragma', "no-cache")
            requests.append(req)
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
        target_dictionary = []
        for index, req in enumerate(pbar := tqdm(self.requests)):
            word = self.word_list[index]
            # Save the content and get the soup object
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
                'id': index,
                'french': word,
                'translations': translations,
                'examples': quotes
            }
            target_dictionary.append(output)
            (temp := translations[0] if translations else "None")
            pbar.set_description(f"In: {word} Out: {temp}")
        return target_dictionary

# FIXME: URL can't contain control characters. '/dictionary/french-english/est-ce que' (found at least ' ')
# FIXME: Save target dictionary to disk
# FIXME: Parallel scraping would be nice
