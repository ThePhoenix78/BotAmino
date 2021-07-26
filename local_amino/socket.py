import time
import json
import asyncio
import threading
import websockets

from sys import _getframe as getframe

from .lib.util import objects

class SocketHandler:
    def __init__(self, client, debug = False):
        self.socket_url = "wss://ws1.narvii.com"
        self.client = client
        self.debug = debug
        self.active = False
        self.headers = None
        self.socket: websockets.client.WebSocketClientProtocol

    async def handle_message(self, data):
        if self.debug is True:
            print(f"[socket][handle_message] Got Data : {data}")
        await self.client.handle_socket_message(data)

    async def send(self, data):
        if self.debug is True:
            print(f"[socket][send] Sending Data : {data}")
        await self.socket.send(data)

    async def run_amino_socket(self):
        self.headers = {
            "NDCDEVICEID": self.client.device_id,
            "NDCAUTH": f"sid={self.client.sid}"
        }

        async with websockets.connect(f"{self.socket_url}/?signbody={self.client.device_id}%7C{int(time.time() * 1000)}", extra_headers=self.headers) as websocket:
            self.socket = websocket
            self.active = True

            if self.debug is True:
                print(f"[socket][start] Socket Started")

            while True:
                await self.handle_message(await websocket.recv())

    async def startup(self):
        if self.debug is True:
            print(f"[socket][startup] Starting Socket")

        threading.Thread(target = asyncio.run, args = (self.run_amino_socket(), )).start()

    def close(self):
        if self.debug is True:
            print(f"[socket][close] Closing Socket")
        self.active = False
        try:
            self.socket.close()
        except Exception as closeError:
            if self.debug is True:
                print(f"[socket][close] Error while closing Socket : {closeError}")

class Callbacks:
    def __init__(self, client):
        self.client = client
        self.handlers = {}

        self.methods = {
            304: self._resolve_chat_action_start,
            306: self._resolve_chat_action_end,
            1000: self._resolve_chat_message
        }

        self.chat_methods = {
            "0:0": self.on_text_message,
            "0:100": self.on_image_message,
            "0:103": self.on_youtube_message,
            "1:0": self.on_strike_message,
            "2:110": self.on_voice_message,
            "3:113": self.on_sticker_message,
            "52:0": self.on_voice_chat_not_answered,
            "53:0": self.on_voice_chat_not_cancelled,
            "54:0": self.on_voice_chat_not_declined,
            "55:0": self.on_video_chat_not_answered,
            "56:0": self.on_video_chat_not_cancelled,
            "57:0": self.on_video_chat_not_declined,
            "58:0": self.on_avatar_chat_not_answered,
            "59:0": self.on_avatar_chat_not_cancelled,
            "60:0": self.on_avatar_chat_not_declined,
            "100:0": self.on_delete_message,
            "101:0": self.on_group_member_join,
            "102:0": self.on_group_member_leave,
            "103:0": self.on_chat_invite,
            "104:0": self.on_chat_background_changed,
            "105:0": self.on_chat_title_changed,
            "106:0": self.on_chat_icon_changed,
            "107:0": self.on_voice_chat_start,
            "108:0": self.on_video_chat_start,
            "109:0": self.on_avatar_chat_start,
            "110:0": self.on_voice_chat_end,
            "111:0": self.on_video_chat_end,
            "112:0": self.on_avatar_chat_end,
            "113:0": self.on_chat_content_changed,
            "114:0": self.on_screen_room_start,
            "115:0": self.on_screen_room_end,
            "116:0": self.on_chat_host_transfered,
            "117:0": self.on_text_message_force_removed,
            "118:0": self.on_chat_removed_message,
            "119:0": self.on_text_message_removed_by_admin,
            "120:0": self.on_chat_tip,
            "121:0": self.on_chat_pin_announcement,
            "122:0": self.on_voice_chat_permission_open_to_everyone,
            "123:0": self.on_voice_chat_permission_invited_and_requested,
            "124:0": self.on_voice_chat_permission_invite_only,
            "125:0": self.on_chat_view_only_enabled,
            "126:0": self.on_chat_view_only_disabled,
            "127:0": self.on_chat_unpin_announcement,
            "128:0": self.on_chat_tipping_enabled,
            "129:0": self.on_chat_tipping_disabled,
            "65281:0": self.on_timestamp_message,
            "65282:0": self.on_welcome_message,
            "65283:0": self.on_invite_message
        }

        self.chat_actions_start = {
            "Typing": self.on_user_typing_start,
        }

        self.chat_actions_end = {
            "Typing": self.on_user_typing_end,
        }

    async def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
        return await self.chat_methods.get(key, self.default)(data)

    async def _resolve_chat_action_start(self, data):
        key = data['o'].get('actions', 0)
        return await self.chat_actions_start.get(key, self.default)(data)

    async def _resolve_chat_action_end(self, data):
        key = data['o'].get('actions', 0)
        return await self.chat_actions_end.get(key, self.default)(data)

    def resolve(self, data):
        data = json.loads(data)
        return asyncio.create_task(self.methods.get(data["t"], self.default)(data))

    async def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                await handler(data)

    def event(self, type):
        def register_handler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler
        return register_handler

    async def on_text_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_image_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_youtube_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_strike_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_sticker_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_not_answered(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_not_cancelled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_not_declined(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_video_chat_not_answered(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_video_chat_not_cancelled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_video_chat_not_declined(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_avatar_chat_not_answered(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_avatar_chat_not_cancelled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_avatar_chat_not_declined(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_delete_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_group_member_join(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_group_member_leave(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_invite(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_background_changed(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_title_changed(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_icon_changed(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_start(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_video_chat_start(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_avatar_chat_start(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_end(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_video_chat_end(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_avatar_chat_end(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_content_changed(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_screen_room_start(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_screen_room_end(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_host_transfered(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_text_message_force_removed(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_removed_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_text_message_removed_by_admin(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_tip(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_pin_announcement(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_permission_open_to_everyone(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_permission_invited_and_requested(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_voice_chat_permission_invite_only(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_view_only_enabled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_view_only_disabled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_unpin_announcement(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_tipping_enabled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_chat_tipping_disabled(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_timestamp_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_welcome_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_invite_message(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_user_typing_start(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def on_user_typing_end(self, data): await self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    async def default(self, data): await self.call(getframe(0).f_code.co_name, data)
