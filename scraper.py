"""
scraper.py

scrapes http://nytm.org/made-in-nyc/ for a list of all made in nyc startups
"""
from urllib2 import *
from bs4 import BeautifulSoup as BS
import re, json, startupDAO, pymongo

# crunchbase API
API_KEY = "5eb9tz5c9yam2cc7s6akqrey"

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
	except HTTPError, e:
		return None

class Startup():

	def __init__(self, name, web_link):
		self.name = name
		self.web_link = web_link
		self.crunch_url = None
		self.hiring_link = None
		self.image_src = None
		self.overview = None
		self.category = None
		self.description = None

	def set_hiring(self, hiring_link):
		self.hiring_link = hiring_link

	def set_image(self, image_src):
		self.image_src = image_src

	def set_crunchbase(self, overview=None, category=None, crunch_url=None, description=None):
		self.overview = overview
		self.category = category
		self.crunch_url = crunch_url
		self.description = description

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

def parse_crunch_page(content):
	"""parse crunch page for additional info"""
	soup = BS(content)


# scrape the most current made in nyc list
nyc_url = "http://nytm.org/made-in-nyc/"
startups = get_startups(get_page(nyc_url))

# use crunchbase api to get further info
for startup in startups[:10]:
	search_query = "query=" + startup.web_link.replace('http://', '').replace('www.', '').rsplit('/')[0]
	search_query += "&entity=company&field=homepage_url"
	page = get_page("http://api.crunchbase.com/v/1/search.js?" + 
			search_query + "&api_key=" + API_KEY)
	if page:
		# if search is successful
		json_resp = json.load(page)
		if json_resp['total'] > 0:
			result_info = json_resp['results'][0]
			startup.set_crunchbase(result_info['overview'], result_info['category_code'],
				result_info['crunchbase_url'], result_info['overview'])
		else:
			# try different approach to search
			name_query = "name=" + startup.name
			page = get_page("http://api.crunchbase.com/v/1/companies/permalink?" +
				name_query + "&api_key=" + API_KEY)
			if page:
				json_resp = json.load(page)
				startup.set_crunchbase(crunch_url=json_resp['crunchbase_url'])

# now scrape crunchbase page for more info
for startup in startups:
	if startup.crunch_url:
		crunch_page = parse_crunch_page(get_page(startup.crunch_url))

# save everything into MongoDB
connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.madenyc

startupsDB = startupDAO.StartupDAO(database)
for startup in startups:
	startupsDB.add_startup(startup)