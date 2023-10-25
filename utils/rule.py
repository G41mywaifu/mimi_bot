"""
 - Author       : DiheChen
 - Date         : 2022-02-15 19:00:35
 - LastEditors  : DiheChen
 - LastEditTime : 2022-02-15 19:18:47
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from datetime import date

from nonebot.rule import ArgumentParser, Rule, to_me

from src.bot import Bot
from src.event import Event
from src.typing import T_State

year = date.today().year
sensitive_date = [
    date(year, 10, 1),  # 十月一日
    date(year, 7, 1),  # 七月一日
    *[date(year, 3, d) for d in range(3, 11)],  # 两会期间
    *[date(year, 6, d) for d in range(1, 5)],  # 六四前后
    *[date(year, 10, d) for d in range(20, 28)],  # 十月底
]


def safe_date() -> Rule:
    async def _check_sensitive_date(bot: Bot, event: Event, state: T_State) -> bool:
        return date.today() not in sensitive_date

    return Rule(_check_sensitive_date)
