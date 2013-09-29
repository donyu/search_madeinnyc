import pymongo

class StartupDAO():
	"""Data Access Object handles all interactions of scraped startups and DB"""
	def __init__(self, db):
		self.db = db
		self.startups = self.db.startups

	def add_startup(self, startup):
		startup = {'name': startup.name, 'web_link': startup.web_link, 
		'crunch_url': startup.crunch_url, 'category': startup.category}
		self.startups.insert(startup)