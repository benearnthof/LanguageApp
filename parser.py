from bs4 import BeautifulSoup
import gzip
import io
import urllib
from pathlib import Path
from tempfile import gettempdir

req = urllib.request.Request("https://www.collinsdictionary.com/dictionary/french-english/etre")
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


# Save the content and get the soup object

resource = urllib.request.urlopen(req)

content = parse_resource(resource)

soup = save_and_parse_html(content, writefile=True)

# Now you can use the soup object to parse the HTML
print(soup.title)  # Print the title of the page
print(soup.find_all('p'))  # Find all paragraph tags



div class="content definitions dictionary biling easy"

# Step 1: Obtain all translations with collins dictionary
div = soup.find_all("div", class_= "cit type-example")

def extract_quote_pair(html_tag):
    french_quote = html_tag.find('span', class_='quote')
    english_translation = html_tag.find('span', class_='cit type-translation').find('span', class_='quote')
    if french_quote and english_translation:
        return {
            'french': french_quote.get_text(strip=True).replace(u'\xa0', u' '),
            'english': english_translation.get_text(strip=True).replace(u'\xa0', u' ')
        }
    else:
        return None

test = extract_quote_pair(div[0])

# Step 2: Extract quotes and their translations
def get_quotes(html_content):
    """
    Extract quotes and translations for word
    """
    return [extract_quote_pair(x) for x in div]

quotes = get_quotes(div)

# Now we only need the correct translations instead of the shitty google translate ones
