"""
scraper.py

scrapes http://nytm.org/made-in-nyc/ for a list of all made in nyc startups
"""
from urllib2 import *
from bs4 import BeautifulSoup as BS
import re

# remove annoying characters
chars = {
    '\xc2\x82' : ',',        # High code comma
    '\xc2\x84' : ',,',       # High code double comma
    '\xc2\x85' : '...',      # Tripple dot
    '\xc2\x88' : '^',        # High carat
    '\xc2\x91' : '\x27',     # Forward single quote
    '\xc2\x92' : '\x27',     # Reverse single quote
    '\xc2\x93' : '\x22',     # Forward double quote
    '\xc2\x94' : '\x22',     # Reverse double quote
    '\xc2\x95' : ' ',
    '\xc2\x96' : '-',        # High hyphen
    '\xc2\x97' : '--',       # Double hyphen
    '\xc2\x99' : ' ',
    '\xc2\xa0' : ' ',
    '\xc2\xa6' : '|',        # Split vertical bar
    '\xc2\xab' : '<<',       # Double less than
    '\xc2\xbb' : '>>',       # Double greater than
    '\xc2\xbc' : '1/4',      # one quarter
    '\xc2\xbd' : '1/2',      # one half
    '\xc2\xbe' : '3/4',      # three quarters
    '\xca\xbf' : '\x27',     # c-single quote
    '\xcc\xa8' : '',         # modifier - under curve
    '\xcc\xb1' : ''          # modifier - under line
}

def replace_chars(match):
    char = match.group(0)
    return chars[char]

def fix_string(text):
    return re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, text)

def get_page(url):
    """load the html from url"""
    try:
        page_html = urlopen(url)
        return page_html
    except URLError as e:
        print "INVALID URL"
        return None 

class Startup():

    def __init__(self, name, web_link):
        self.name = name
        self.web_link = web_link

    def set_hiring(self, hiring_link):
        self.hiring_link = hiring_link

    def __repr__(self):
        return self.name + " " + self.web_link

def get_startups(content):
    """get a list of nyc startup names and website links"""
    soup = BS(content)
    startups = []
    for startup_li in soup.article.ol.find_all('li'):
        startup_link = startup_li.contents[0]
        startup = Startup(startup_link.get_text().encode('utf-8'), startup_link.get('href').encode('utf-8'))
        if len(startup_li.contents) > 2:
            startup_hiring_link = startup_li.contents[2]
            startup.set_hiring(startup_hiring_link.get('href').encode('utf-8'))
        startups.append(startup)
    return startups

# scrape the most current made in nyc list
nyc_url = "http://nytm.org/made-in-nyc/"
startups = get_startups(get_page(nyc_url))

# use crunchbase api to get further info
print startups