from aiohttp import web
from random import randint

async def driver_status(request):
    status = ['angry', 'tired', 'drunk',
              'discracted', 'normal']
    n = randint(0, 4)
    stat = status[n]
    return web.Response(text = stat)

app = web.Application()
app.add_routes([web.get('/', driver_status)])

web.run_app(app, port=8888)