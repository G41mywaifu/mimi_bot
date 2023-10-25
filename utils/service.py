"""
 - Author       : DiheChen
 - Date         : 2022-05-21 21:17:17
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-25 08:30:20
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from asyncio import sleep
from collections import defaultdict
from os import path
from re import RegexFlag
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type, Union

from loguru import logger
from nonebot.matcher import Matcher
from nonebot.plugin import MatcherGroup

from src import R, driver
from src.bot import Bot, get_bot, get_bots
from src.event import Event
from src.message import Message, MessageSegment
from src.permission import ADMIN, Permission
from src.rule import ArgumentParser, Rule, to_me
from src.typing import T_State


_loaded_services: Dict[str, "Service"] = {}
_saved_services: Dict[str, Dict[str, Any]] = {}
if _services_save_path := R.database("services.json"):
    _saved_services = _services_save_path.loadjson()


def _load_service(service_name: str) -> Dict[str, Any]:
    if service_name in _saved_services:
        return _saved_services[service_name]
    return {}


def _save_service(service: "Service"):
    _saved_services[service.name] = {
        "name": service.name,
        "description": service.description,
        "enable_group": list(service.enable_group),
        "disable_group": list(service.disable_group),
    }


class Service(MatcherGroup):
    def __init__(
        self,
        name: str,
        description: str,
        manager_permission: Permission = ADMIN,
        enable_default: bool = False,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.manager_permission = manager_permission
        self.enable_default = enable_default
        super().__init__(**kwargs)
        data = _load_service(self.name)
        self.enable_group = set(data.get("enable_group", []))
        self.disable_group = set(data.get("disable_group", []))
        _loaded_services[self.name] = self

    def set_enable(self, group_id: int) -> None:
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        _save_service(self)

    def set_disable(self, group_id: int) -> None:
        self.disable_group.add(group_id)
        self.enable_group.discard(group_id)
        _save_service(self)

    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_services

    async def get_enable_group(self) -> Dict[int, List[int]]:
        group_dict = defaultdict(list)
        for self_id, bot in get_bots().items():
            groups: Set[int] = set(
                group["group_id"]
                for group in await bot.get_group_list(self_id=int(self_id))
            )
            if self.enable_default:
                groups -= self.disable_group
            else:
                groups &= self.enable_group
            for group in groups:
                group_dict[int(self_id)].append(group)
        return dict(group_dict)

    def _check_enable(self, group_id: int) -> bool:
        return bool(
            (group_id in self.enable_group)
            or (self.enable_default and group_id not in self.disable_group)
        )

    def check_service(self, only_to_me: bool = False, only_group: bool = True) -> Rule:
        async def _check_service(bot: Bot, event: Event, state: T_State) -> bool:
            if "group_id" not in event.__dict__:
                return not only_group
            else:
                return self._check_enable(event.group_id)  # type: ignore

        rule = Rule(_check_service)
        if only_to_me:
            rule &= to_me()
        return rule

    def on_message(
        self, only_to_me: bool = False, only_group: bool = True, **kwargs
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        kwargs["priority"] = kwargs.pop("priority", 10)
        return super().on_message(**kwargs)

    def on_notice(
        self, only_to_me: bool = False, only_group: bool = True, **kwargs
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_notice(**kwargs)

    def on_request(self, only_group: bool = True, **kwargs) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(False, only_group) & rule
        return super().on_request(**kwargs)

    def on_startswith(
        self,
        msg: Union[str, Tuple[str, ...]],
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_startswith(msg, **kwargs)

    def on_endswith(
        self,
        msg: Union[str, Tuple[str, ...]],
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_endswith(msg, **kwargs)

    def on_fullmatch(
        self,
        msg: Union[str, Tuple[str, ...]],
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_fullmatch(msg, **kwargs)

    def on_keyword(
        self,
        keywords: Set[str],
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_keyword(keywords, **kwargs)

    def on_command(
        self,
        cmd: Union[str, Tuple[str, ...]],
        aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        kwargs["priority"] = kwargs.pop("priority", 1)
        kwargs["block"] = kwargs.pop("block", True)
        return super().on_command(cmd, aliases, **kwargs)

    def on_shell_command(
        self,
        cmd: Union[str, Tuple[str, ...]],
        aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
        parser: Optional[ArgumentParser] = None,
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_shell_command(cmd, aliases, parser, **kwargs)

    def on_regex(
        self,
        pattern: str,
        flags: Union[int, RegexFlag] = 0,
        only_to_me: bool = False,
        only_group: bool = True,
        **kwargs,
    ) -> Type[Matcher]:
        rule = kwargs.pop("rule", Rule())
        kwargs["rule"] = self.check_service(only_to_me, only_group) & rule
        return super().on_regex(pattern, flags, **kwargs)

    async def broadcast(self, messages: Iterable, interval: float = 1):
        if isinstance(messages, (str, Message, MessageSegment)):
            messages = (messages,)
        exceptions: List[Exception] = []
        for self_id, groups in (await self.get_enable_group()).items():
            bot: Bot = get_bot(str(self_id))
            for group_id in groups:
                for message in messages:
                    try:
                        await bot.send_group_msg(
                            self_id=self_id, group_id=group_id, message=message
                        ), await sleep(interval)
                    except Exception as e:
                        exceptions.append(e)
        return exceptions


@driver.on_shutdown
async def _():
    _services_save_path.dumpjson(_saved_services)
    logger.success("Service settings saved.")
