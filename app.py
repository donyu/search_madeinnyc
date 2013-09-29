from flask import *

app = Flask()

@app.route('/', methods=['GET'])
def home():
	return make_response(open('static/base.html').read())

if __name__ == "__main__":
	app.run()