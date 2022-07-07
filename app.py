from sanic import Sanic
from sanic.response import json
from sanic.exceptions import InvalidUsage

import constants

try:
	import uvloop
	uvloop.install()
except:
	pass

app = Sanic("App")
app.config.FORWARDED_SECRET = "zcTkMjWmhJ9njWJwhLKaMycS"

@app.route('/')
async def test(request):
	return json({'Hello': 'World!'})

@app.route('/oauth/callback')
async def callback(request):
	args = request.args

	if not args.get("code"):
		raise InvalidUsage("Invalid Request")

	return json({})

if __name__ == '__main__':
	app.run(port=5443, debug=True)
