import sanic
from sanic import Sanic, json, Blueprint
from sanic_ext import render
from sanic.exceptions import InvalidUsage, NotFound
from sanic.response import redirect

app = Sanic(__name__)
app.static("", "./static/")
app.config.CORS_ALLOW_HEADERS = "referer"

@app.on_request
async def run_before_handler(request):
	print(request.headers.referer)

@app.route("/")
async def front_page(request):
	print(request.headers.referer)
	return redirect("/index.html")

@app.route("/invite")
async def invite(request):
	return redirect("https://discord.com/api/oauth2/authorize?client_id=848384657774084107&permissions=1374627687526&scope=applications.commands%20bot")

#@app.route("/privacy")
#async def privacy_policy(request):
#	return "Coming Soon"

@app.route("/terms")
async def tos(request):
	return redirect("/terms.html")

@app.route("/users/4000781648/profile")
async def test(request):
	print(request.headers['cf-connecting-ip'])
	return redirect("https://www.roblox.com/users/4000781648/profile")

if __name__ == "__main__":
	app.run(port=3480)