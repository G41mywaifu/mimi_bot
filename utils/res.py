"""
 - Author       : DiheChen
 - Date         : 2022-02-15 21:57:52
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-03 08:02:23
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from io import UnsupportedOperation
from os import listdir, makedirs, path
from typing import List
from urllib.parse import urljoin
from urllib.request import pathname2url

import ujson as json
from loguru import logger
from nonebot import get_asgi, get_driver
from PIL import Image

from src.message import MessageSegment
from src.util.aiorequests import AioRequests

driver = get_driver()
config = driver.config
RES_DIR = path.abspath(config.res_dir)
BASE_URL: str = "http://127.0.0.1:{}/".format(config.port)
app = get_asgi()

makedirs(RES_DIR, exist_ok=True)


class RHelper(str):
    def __init__(self, path: str = None) -> None:
        if not path:
            self.__rpath = RES_DIR
        else:
            self.__rpath = path

    def __getattr__(self, key):
        _path = path.normpath(path.join(self.__rpath, key))
        if not path.isdir(_path) and not path.isfile(_path):
            logger.warning(
                f"{_path} is not a directory and a file!\nif {key}.* or *.{key} is file or dir,please use + or () opearator."
            )
        return __class__(_path)

    def __floordiv__(self, key):
        _path = path.join(self.__rpath, key)
        _path = path.normpath(_path)
        return __class__(_path)

    def __truediv__(self, key):
        _path = path.join(self.__rpath, key)
        _path = path.normpath(_path)
        return __class__(_path)

    def __add__(self, key):
        _path = path.join(self.__rpath, key)
        _path = path.normpath(_path)
        return __class__(_path)

    def __setattr__(self, name: str, value) -> None:
        if name != "_RHelper__rpath":
            raise UnsupportedOperation(
                f"unsupported operand type(s) for =: 'RHelper' and '{type(value)}'"
            )
        else:
            self.__dict__[name] = value

    def __imul__(self, key):
        raise UnsupportedOperation(
            f"unsupported operand type(s) for *=: 'RHelper' and '{type(key)}'"
        )

    def __mul__(self, key):
        raise UnsupportedOperation(
            f"unsupported operand type(s) for *: 'RHelper' and '{type(key)}'"
        )

    def __call__(self, fpath, *fpaths):
        key = path.join(fpath, *fpaths)
        _path = path.join(self.__rpath, key)
        _path = path.normpath(_path)
        return __class__(_path)

    @property
    def path(self) -> str:
        return path.abspath(self.__rpath)

    def __str__(self) -> str:
        return self.path

    @property
    def exist(self):
        return path.exists(self.path)

    def __bool__(self) -> bool:
        return self.exist

    def as_image(self) -> Image.Image:
        try:
            return Image.open(self.__rpath)
        except Exception as e:
            logger.exception(e)

    def loadjson(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.exception(e)

    def dumpjson(self, data, **kwargs):
        kwargs["ensure_ascii"] = kwargs.get("ensure_ascii", False)
        kwargs["indent"] = kwargs.get("indent", 4)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, **kwargs)
        except Exception as e:
            logger.exception(e)

    @property
    def url(self):
        return urljoin(
            urljoin(BASE_URL, "resource/"),
            pathname2url(path.relpath(self.__rpath, RES_DIR)),
        )

    @property
    def cqcode(self) -> MessageSegment:
        return MessageSegment.image(self.url)

    @property
    def listdir(self) -> List[str]:
        return listdir(self.path)


@driver.on_startup
async def base_url():
    global BASE_URL
    if str(config.host) == "0.0.0.0":
        headers = {"User-Agent": "curl/7.71.1"}
        host = (
            await AioRequests.get(
                "http://ip.sb", headers=headers, proxy=""  # 确保获取的是真实的 ip
            )
        ).text
        BASE_URL = "http://{}:{}/".format(host, config.port)
    logger.success("Static resource server on {}".format(BASE_URL))
    return BASE_URL


def get_base_url():
    return BASE_URL
