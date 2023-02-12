import hikari
import constants
import aiohttp
import sanic
import jwt
import asyncio

from sanic_session import Session, InMemorySessionInterface
from bs4 import BeautifulSoup
from sanic_ext import render
from sanic import Sanic, Blueprint, text, html
from sanic.response import file, json, redirect
from sanic.exceptions import InvalidUsage
from bson.binary import Binary
from pymongo import MongoClient

app = Sanic("MyApp")
session = Session(app, interface=InMemorySessionInterface())
rest_client = hikari.RESTApp()
cluster = MongoClient("connection")
db = cluster['Discord']['ghost_mention']

def has_manage_guild(guild: hikari.OwnGuild) -> bool:
	return hikari.permissions.Permissions.MANAGE_GUILD in guild.my_permissions or guild.is_owner

@app.before_server_start
async def start_discord_rest(app: sanic.Sanic) -> None:
	discord_rest = rest_client
	await discord_rest.start()

	app.ctx.discord_rest = discord_rest

@app.after_server_stop
async def close_discord_rest(app: sanic.Sanic) -> None:
	await app.ctx.discord_rest.stop()

@app.route('/')
async def handler(request):
	return await render('index.html', context={'session_login': request.ctx.session})


@app.route('/oauth/callback')
async def callback(request):
	args = request.args
	code = args.get("code")
	print(args)
	if not code:
		raise InvalidUsage("Invalid Request")

	try:
		async with aiohttp.ClientSession() as session:
			data = {
				'client_id': 848384657774084107,
				'client_secret': 'secret',
				'grant_type': 'authorization_code',
				'code': code,
				'redirect_uri': constants.REDIRECT_URI
			}
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
			async with session.post("https://discord.com/api/oauth2/token", data=data, headers=headers) as response:
				data = await response.json()
				#logins[]
	except hikari.errors.UnauthorizedError:
		raise InvalidUsage("Invalid Request")

	if not request.ctx.session.get(data.get('access_token')):
		request.ctx.session[data.get('access_token')] = 0

	request.ctx.session['_token'] = data.get('access_token')

	if request.ctx.session['_token'] == None:
		return redirect('https://discord.com/api/oauth2/authorize?client_id=848384657774084107&redirect_uri=https%3A%2F%2Fchillbot.xyz%2Foauth%2Fcallback&response_type=code&scope=identify%20guilds')
	print(data)

	return redirect('/servers')

	#return json({'access_token': data.get('access_token')})

@app.route('/servers')
async def get_servers(request):
	token = request.ctx.session.get('_token')
	print(request.ctx.session)
	li = {}
	li2 = {}
	if request.ctx.session:
		discord_rest = app.ctx.discord_rest

		async with discord_rest.acquire(token) as client:
			guild = await client.fetch_my_guilds().filter(has_manage_guild)
			avatar = await client.fetch_my_user()

		async with discord_rest.acquire('token', hikari.TokenType.BOT) as rest:
			spec_guild = await rest.fetch_my_guilds()


		for x in guild:
			if x.icon_url:
				li[str(x.id)] = x.icon_url.url
			else:
				li[str(x.id)] = "https://cdn.discordapp.com/embed/avatars/0.png"

		return await render('servers.html', context={'users': li, 'image': avatar.avatar_url, 'gray': [str(x.id) for x in spec_guild]})
		# return await file('./templates/servers.html')
	else:
		return redirect(constants.OAUTH_URI)

@app.route('/servers/<y>')
async def manage_server(request, y):
	token = request.ctx.session.get('_token')
	if request.ctx.session:
		discord_rest = app.ctx.discord_rest

		async with discord_rest.acquire(token) as client:
			guild = await client.fetch_my_guilds().filter(has_manage_guild)
			avatar = await client.fetch_my_user()

		async with discord_rest.acquire('token', hikari.TokenType.BOT) as rest:
			spec_guild = await rest.fetch_my_guilds()
			spec = await rest.fetch_guild(y)
		if str(y) in [str(x.id) for x in guild]:
			if str(y) in [str(x.id) for x in spec_guild]:
				return await render('manage_server.html', context={'image': avatar.avatar_url, 'x': str(y), "spec": spec.icon_url, "name": spec.name})
			else:
				return redirect('https://discord.com/oauth2/authorize?client_id=848384657774084107&permissions=281541732550&scope=bot%20applications.commands')
		else:
			return redirect('/servers')
	else:
		return redirect(constants.OAUTH_URI)

@app.route('/servers/<y>/moderation')
async def moderation_config(request, y):
	token = request.ctx.session.get('_token')
	if request.ctx.session:
		discord_rest = app.ctx.discord_rest

		async with discord_rest.acquire(token) as client:
			guild = await client.fetch_my_guilds().filter(has_manage_guild)
			avatar = await client.fetch_my_user()

		async with discord_rest.acquire('token', hikari.TokenType.BOT) as rest:
			spec_guild = await rest.fetch_my_guilds()

		if str(y) in [str(x.id) for x in guild]:
			if str(y) in [str(x.id) for x in spec_guild]:
				print(request.files.get('container'))
				return await render('moderation.html', context={'image': avatar.avatar_url, 'x': str(y), 'get_count': db.count_documents({str(y): True})})
			else:
				return redirect('https://discord.com/oauth2/authorize?client_id=848384657774084107&permissions=281541732550&scope=bot%20applications.commands')
		else:
			return redirect('/servers')
	else:
		return redirect(constants.OAUTH_URI)


@app.route('/main.css')
async def main_css(request):
	return await file('./templates/main.css')

@app.route('/static/js/main.js')
async def main_js(request):
	return await file('./templates/static/js/main.js')

@app.route('/static/js/jquery.min.js')
async def jquery_min(request):
	return await file('./templates/static/js/jquery.min.js')

@app.route('/static/js/jquery.scrollex.min.js')
async def scrollex(request):
	return await file('./templates/static/js/jquery.scrollex.min.js')

@app.route('/static/js/jquery.scrolly.min.js')
async def scrolly(request):
	return await file('./templates/static/js/jquery.scrolly.min.js')

@app.route('/static/js/browser.min.js')
async def browser(request):
	return await file('./templates/static/js/browser.min.js')

@app.route('/static/js/util.js')
async def util(request):
	return await file('./templates/static/js/util.js')

@app.route('/static/js/breakpoints.min.js')
async def breakpoints(request):
	return await file('./templates/static/js/breakpoints.min.js')

@app.route('/webfonts/fa-solid-900.woff')
async def webfont(request):
	return await file('./templates/webfonts/fa-solid-900.woff')

@app.route('/webfonts/fa-solid-900.woff2')
async def webfont2(request):
	return await file('./templates/webfonts/fa-solid-900.woff2')

@app.route('/fontawesome-all.min.css')
async def fontawesome(request):
	return await file('./templates/fontawesome-all.min.css')

@app.route('/images/intro.svg')
async def intro(request):
	return await file('./templates/images/intro.svg')

@app.route('/chillbot.webp')
async def avatar_webp(request):
	return await file('./templates/chillbot.webp')

@app.route('/robots.txt')
async def robots(request):
	return await file('./templates/robots.txt')

if __name__ == '__main__':
	app.run(port=1234)
