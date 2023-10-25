"""
 - Author       : DiheChen
 - Date         : 2022-05-01 20:33:12
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-01 22:08:25
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from os import makedirs, path

from nonebot.log import default_filter, default_format, logger

makedirs("logs", exist_ok=True)

# logger.remove()
logger.add(
    path.join("logs", "{time:YYYYMMDD}.log"),
    filter=default_filter,
    format=default_format,
    rotation="00:00",
    diagnose=False,
    retention="3 days",
)
logger.add(
    path.join("logs", "{time:YYYYMMDD}_error.log"),
    level="ERROR",
    rotation="00:00",
    diagnose=False,
    retention="14 days",
)
