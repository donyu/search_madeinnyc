"""
scraper.py

scrapes http://nytm.org/made-in-nyc/ for a list of all made in nyc startups
"""
from urllib2 import *
from bs4 import BeautifulSoup as BS
import re, json, startupDAO, pymongo, sys

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
		self.category = None

	def set_crunchbase(self, category=None, crunch_url=None):
		self.category = category
		self.crunch_url = crunch_url

	def __repr__(self):
		return self.name + " " + self.web_link

def get_startups(content):
	"""get a list of nyc startup names and website links"""
	soup = BS(content)
	startups = []
	for startup_li in soup.find(id="made-in-ny").ol.find_all('li'):
		startup_link = startup_li.contents[0]
		startup = Startup(startup_link.get_text().encode('utf-8'), startup_link.get('href').encode('utf-8'))
		startups.append(startup)
	return startups

def parse_crunch_page(content):
	"""parse crunch page for additional info"""
	soup = BS(content)


# scrape the most current made in nyc list
nyc_url = "http://wearemadeinny.com/made-in-ny-list/"
startups = get_startups(get_page(nyc_url))

# use crunchbase api to get further info
i = 0
for startup in startups[98:101]:
	print i
	i += 1
	search_query = "query=" + startup.web_link.replace('http://', '').rsplit('/')[0]
	search_query += "&entity=company&field=homepage_url"
	page = get_page("http://api.crunchbase.com/v/1/search.js?" + 
			search_query + "&api_key=" + API_KEY)
	if page:
		# if search is successful
		try:
			json_resp = json.load(page)
			if json_resp['total'] > 0:
				result_info = json_resp['results'][0]
				startup.set_crunchbase(result_info['category_code'], result_info['crunchbase_url'])
				print result_info['crunchbase_url']
			else:
				# try different approach to search
				search_query = "query=" + startup.web_link.replace('http://', '').replace('www','').rsplit('/')[0]
				search_query += "&entity=company&field=homepage_url"
				page = get_page("http://api.crunchbase.com/v/1/search.js?" + 
						search_query + "&api_key=" + API_KEY)
				if page:
					# if search is successful
					try:
						json_resp = json.load(page)
						if json_resp['total'] > 0:
							result_info = json_resp['results'][0]
							startup.set_crunchbase(result_info['category_code'], result_info['crunchbase_url'])
							print result_info['crunchbase_url']
						else:
							# try different approach to search
							search_query = "query=" + startup.name
							search_query += "&entity=company&field=name"
							page = get_page("http://api.crunchbase.com/v/1/search.js?" + 
									search_query + "&api_key=" + API_KEY)
							if page:
								# if search is successful
								try:
									json_resp = json.load(page)
									if json_resp['total'] > 0:
										result_info = json_resp['results'][0]
										startup.set_crunchbase(result_info['category_code'], result_info['crunchbase_url'])
										print result_info['crunchbase_url']
								except ValueError, e:
									continue
					except ValueError, e:
						continue
		except ValueError, e:
			continue

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