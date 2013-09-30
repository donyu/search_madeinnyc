from flask import *
import startupDAO

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
database = connection.madenyc
startupsDB = startupDAO.StartupDAO(database)

app = Flask()

@app.route('/startup/:startup', method=['GET'])
def get_startup():
	

@app.route('/', methods=['GET'])
def home():
	return make_response(open('static/base.html').read())

if __name__ == "__main__":
	app.run()