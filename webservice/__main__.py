import os
import aiohttp
from aiohttp import web
from gidgethub import routing, sansio
from gidgethub import aiohttp as gh_aiohttp

router = routing.Router()
routes = web.RouteTableDef()

@router.register("issues", action="opened")
async def issue_opened_event(event, gh, *args, **kwargs):
    url = event.data["issue"]["comments_url"]
    author = event.data["issue"]["user"]["login"]
    message = f"Thanks @{author} for reporting this issue! My human will start looking into it right away."
    await gh.post(url, data={"body": message})

@routes.get("/")
async def index(request):
    return web.Response(status=200, text="Hello World")

@routes.post("/")
async def main(request):
    body = await request.read()
    secret = os.environ.get("GH_SECRET")
    oauth = os.environ.get("GH_AUTH")
    event = sansio.Event.from_http(request.headers, body, secret=secret)
    async with aiohttp.ClientSession() as session:
        gh = gh_aiohttp.GitHubAPI(session, "kslupsky", oauth_token=oauth)
        await router.dispatch(event, gh)
    return web.Response(status=200)

if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    port = os.environ.get("PORT")
    if port is not None:
        port = int(port)
    web.run_app(app, port=port)