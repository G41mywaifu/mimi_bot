"""
 - Author       : DiheChen
 - Date         : 2022-02-24 01:22:08
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-02 13:37:09
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
import asyncio
from functools import wraps
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, Coroutine

from nonebot.adapters import MessageTemplate
from nonebot.consts import ARG_KEY
from nonebot.dependencies import Dependent
from nonebot.matcher import Matcher, current_bot
from nonebot.params import BotParam, Depends, EventParam, MatcherParam, StateParam

from src.bot import Bot
from src.event import Event, GroupMessageEvent, MessageEvent, PrivateMessageEvent
from src.message import Message, MessageSegment
from src.typing import T_Handler


@classmethod
def got(
    cls: Matcher,
    key: str,
    prompt: Optional[Union[str, Message, MessageSegment, MessageTemplate]] = None,
    args_parser: Optional[T_Handler] = None,
    parameterless: Optional[List[Any]] = None,
) -> Callable[[T_Handler], T_Handler]:

    if args_parser:
        args_parser = Dependent[Any].parse(
            call=args_parser,
            allow_types=[BotParam, EventParam, StateParam, MatcherParam],
        )

    async def _key_getter(event: Event, matcher: "Matcher"):
        matcher.set_target(ARG_KEY.format(key=key))
        if matcher.get_target() == ARG_KEY.format(key=key):
            if args_parser:
                bot: Bot = current_bot.get()
                await args_parser(
                    matcher=matcher, bot=bot, event=event, state=matcher.state
                )
            else:
                matcher.set_arg(key, event.get_message())
            return
        if matcher.get_arg(key, ...) is not ...:
            return
        await matcher.reject(prompt)

    _parameterless = (Depends(_key_getter), *(parameterless or tuple()))

    def _decorator(func: T_Handler) -> T_Handler:

        if cls.handlers and cls.handlers[-1].call is func:
            func_handler = cls.handlers[-1]
            new_handler = Dependent(
                call=func_handler.call,
                params=func_handler.params,
                parameterless=Dependent.parse_parameterless(
                    tuple(_parameterless), cls.HANDLER_PARAM_TYPES
                )
                + func_handler.parameterless,
            )
            cls.handlers[-1] = new_handler
        else:
            cls.append_handler(func, parameterless=_parameterless)

        return func

    return _decorator


def new_matcher_preprocessor(func: Callable):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        kwargs["module"].__name__ = kwargs["plugin"].name
        return func(cls, *args, **kwargs)

    return wrapper


Matcher.got = got
Matcher.new = new_matcher_preprocessor(Matcher.new)


def decorator(func: Callable):
    @wraps(func)
    async def wrapper(
        self: Bot,
        event: Event,
        message: Union[str, Message, MessageSegment],
        call_header: bool = False,
        auto_delete: int = 0,
        **kwargs,
    ) -> Any:
        if call_header and hasattr(event, "group_id"):
            if isinstance(event, MessageEvent):
                header = f"> {event.sender.title or event.sender.card or event.sender.nickname}"
            else:
                info = await self.get_group_member_info(
                    group_id=event.group_id, user_id=event.user_id
                )
                header = f"> {info['title'] or info['card'] or info['nickname']}"
            message = MessageSegment.text(header + "\n") + message
        ret = await func(self, event, message, **kwargs)
        if auto_delete:
            loop = asyncio.get_running_loop()
            loop.call_later(
                auto_delete,
                lambda: loop.create_task(self.delete_msg(message_id=ret["message_id"])),
            )
        return ret

    return wrapper


Bot.send = decorator(Bot.send)


def generate_forward_msg_node(
    msgs: Iterable, self_id: int, name: str = None
) -> List[Dict[str, Any]]:
    """
    生成自定义合并转发消息的节点, 需要传入两个参数:
    1. `msgs`: 可迭代的, 由字符串, 消息, 消息段, 或是自定义的合并转发消息节点组成
    2. `self_id`: 当前登录的QQ号
    """
    return [
        {
            "type": "node",
            "data": {
                "name": name or "老婆~",
                "uin": str(self_id),
                "content": Message(msg)
                if isinstance(msg, (str, Message, MessageSegment))
                else msg,
            },
        }
        for msg in msgs
    ]


def send_group_forward_msg(
    self: Bot,
    event: GroupMessageEvent,
    messages: Iterable[Union[str, Message, MessageSegment, List[Dict[str, Any]]]],
    **kwargs,
) -> Coroutine[Any, Any, Any]:
    return self.call_api(
        "send_group_forward_msg",
        group_id=event.group_id,
        messages=generate_forward_msg_node(messages, event.self_id),
        **kwargs,
    )


def send_private_forward_msg(
    self: Bot,
    event: PrivateMessageEvent,
    messages: Iterable[Union[str, Message, MessageSegment, List[Dict[str, Any]]]],
    **kwargs,
) -> Coroutine[Any, Any, Any]:
    return self.call_api(
        "send_private_forward_msg",
        user_id=event.user_id,
        messages=generate_forward_msg_node(messages, event.self_id),
        **kwargs,
    )


def send_forward_msg(
    self: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    messages: Iterable[Union[str, Message, MessageSegment, List[Dict[str, Any]]]],
) -> Coroutine[Any, Any, Any]:
    return (
        send_group_forward_msg(self, event, messages)
        if isinstance(event, GroupMessageEvent)
        else send_private_forward_msg(self, event, messages)
    )


Bot.send_forward_msg = send_forward_msg
