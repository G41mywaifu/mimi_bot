"""
 - Author       : DiheChen
 - Date         : 2022-02-22 01:54:06
 - LastEditors  : DiheChen
 - LastEditTime : 2022-05-01 00:20:25
 - Description  : None
 - GitHub       : https://github.com/DiheChen
"""
from nonebot.adapters.onebot.v11.adapter import Adapter
from nonebot.adapters.onebot.v11.event import (
    Event,
    FriendAddNoticeEvent,
    FriendRecallNoticeEvent,
    FriendRequestEvent,
    GroupAdminNoticeEvent,
    GroupBanNoticeEvent,
    GroupDecreaseNoticeEvent,
    GroupIncreaseNoticeEvent,
    GroupRecallNoticeEvent,
    GroupRequestEvent,
    GroupUploadNoticeEvent,
    HonorNotifyEvent,
    LuckyKingNotifyEvent,
    NoticeEvent,
    PokeNotifyEvent,
)
from nonebot.adapters.onebot.v11.event import (
    MessageEvent as _MessageEvent,
    GroupMessageEvent as _GroupMessageEvent,
    PrivateMessageEvent as _PrivateMessageEvent,
)
from src.typing import T_State, overrides

from src.message import Message


class MessageEvent(_MessageEvent):
    """
    消息事件
    """

    def _remove_command_segment(self, state: T_State) -> Message:
        """
        移除消息段中的命令部分
        """
        msg = self.message
        if state:
            try:
                _command = state["_prefix"]["raw_command"]
                msg = Message(str(msg).replace(_command, "", 1).strip())
            except (KeyError, TypeError):
                pass
        return msg

    @overrides(_MessageEvent)
    def get_message(self, state: T_State = None) -> Message:
        _msg = self._remove_command_segment(state)
        return _msg

    @overrides(_MessageEvent)
    def get_plaintext(self, state: T_State = None) -> str:
        _msg = self._remove_command_segment(state)
        return _msg.extract_plain_text()


class GroupMessageEvent(_GroupMessageEvent, MessageEvent):
    """
    群消息
    """


class PrivateMessageEvent(_PrivateMessageEvent, MessageEvent):
    """
    私聊消息
    """


Adapter.add_custom_model(MessageEvent)
Adapter.add_custom_model(GroupMessageEvent)
Adapter.add_custom_model(PrivateMessageEvent)
