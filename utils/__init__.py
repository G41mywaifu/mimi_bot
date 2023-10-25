"""
 - Author       : DiheChen
 - Date         : 2022-02-15 17:27:54
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-01 21:18:47
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from typing import Final

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.staticfiles import StaticFiles
from nonebot import get_driver
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from . import log, rule
from .patch import generate_forward_msg_node
from .res import RES_DIR, RHelper, app
from .util import Converter

R: Final[RHelper] = RHelper()


driver = get_driver()
config = driver.config
scheduler = AsyncIOScheduler()
templates = Jinja2Templates(R.html("template").path)
convert = Converter(R.database("zhcdict.json").loadjson()["zh2Hans"])


@driver.on_startup
async def _():
    if not scheduler.running:
        scheduler.configure(config.apscheduler_config)
        scheduler.start()


@driver.on_shutdown
async def _():
    if scheduler.running:
        scheduler.shutdown()


app.get("/favicon.ico")(lambda: Response())
app.mount("/static", StaticFiles(directory=R.html("static").path), name="static")
app.mount("/resource", StaticFiles(directory=RES_DIR), name="resource")
