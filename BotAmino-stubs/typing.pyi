from typing_extensions import Any, Callable, Concatenate, Literal, TypeVar
from .parameters import Parameters

__all__ = (
    'Callback', 
    'LiteCallback',
    'CallbackCategory',
    'Condition',
    'Events',
    'ParserFeature',
)

# types
LiteCallback = Callable[[Parameters], Any]
Callback = Callable[Concatenate[Parameters, ...], Any]
Condition = Callable[[Parameters], bool]

# type-vars
LiteCallbackT = TypeVar("LiteCallbackT", bound=LiteCallback)
CallbackT = TypeVar("CallbackT", bound=Callback)

CallbackCategory = Literal[
    "answer",
    "command",
    "on_all",
    "on_delete",
    "on_event",
    "on_member_join_chat",
    "on_member_leave_chat",
    "on_message",
    "on_other",
    "on_remove"
]

Events = Literal[
    "on_avatar_chat_end",
    "on_avatar_chat_not_answered",
    "on_avatar_chat_not_cancelled",
    "on_avatar_chat_not_declined",
    "on_avatar_chat_start",
    "on_chat_background_changed",
    "on_chat_content_changed",
    "on_chat_host_transfered",
    "on_chat_icon_changed",
    "on_chat_invite",
    "on_chat_pin_announcement",
    "on_chat_removed_message",
    "on_chat_tip",
    "on_chat_tipping_disabled",
    "on_chat_tipping_enabled",
    "on_chat_title_changed",
    "on_chat_unpin_announcement",
    "on_chat_view_only_disabled",
    "on_chat_view_only_enabled",
    "on_delete_message",
    "on_group_member_join",
    "on_group_member_leave",
    "on_image_message",
    "on_invite_message",
    "on_screen_room_end",
    "on_screen_room_start",
    "on_sticker_message",
    "on_strike_message",
    "on_text_message",
    "on_text_message_force_removed",
    "on_text_message_removed_by_admin",
    "on_timestamp_message",
    "on_video_chat_end",
    "on_video_chat_not_answered",
    "on_video_chat_not_cancelled",
    "on_video_chat_not_declined",
    "on_video_chat_start",
    "on_voice_chat_end",
    "on_voice_chat_not_answered",
    "on_voice_chat_not_cancelled",
    "on_voice_chat_not_declined",
    "on_voice_chat_permission_invite_only",
    "on_voice_chat_permission_invited_and_requested",
    "on_voice_chat_permission_open_to_everyone",
    "on_voice_chat_start",
    "on_voice_message",
    "on_welcome_message",
    "on_youtube_message"
]

ParserFeature = Literal[
    'default',
    'quotedkey',
]
