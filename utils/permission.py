"""
 - Author       : DiheChen
 - Date         : 2022-02-18 19:49:06
 - LastEditors  : DiheChen
 - LastEditTime : 2022-03-21 09:25:10
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GROUP, GROUP_ADMIN, GROUP_OWNER, PRIVATE
from nonebot.permission import SUPERUSER, Permission


class WhiteList:
    """
    检查当前事件是否属于白名单用户
    """

    __slots__ = ()

    async def __call__(self, bot: Bot, event: Event) -> bool:
        return (
            event.user_id in bot.config.white_list
            or event.get_user_id() in bot.config.white_list
        )


WHITE_LIST = SUPERUSER | Permission(WhiteList())
# 匹配任意白名单用户 / 超级管理员任意类型事件

ADMIN = WHITE_LIST | GROUP_ADMIN | GROUP_OWNER
OWNER = WHITE_LIST | GROUP_OWNER
POWNER = WHITE_LIST | GROUP_OWNER | PRIVATE
NORMAL = WHITE_LIST | GROUP | PRIVATE
