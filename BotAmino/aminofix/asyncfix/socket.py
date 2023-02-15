import time
import json
import websocket
import contextlib

from threading import Thread
from sys import _getframe as getframe

from ..lib.util import objects, helpers
from ..lib.util.helpers import gen_deviceId

class SocketHandler:
    def __init__(self, client, socket_trace = False, debug = False):
        self.socket_url = "wss://ws1.narvii.com"
        self.client = client
        self.debug = debug
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None
        self.reconnectTime = 180
        self.socket_thread = None

        if self.socket_enabled:
            self.reconnect_thread = Thread(target=self.reconnect_handler)
            self.reconnect_thread.start()

        websocket.enableTrace(socket_trace)

    def reconnect_handler(self):
        # Made by enchart#3410 thx
        # Fixed by The_Phoenix#3967
        while True:
            time.sleep(self.reconnectTime)

            if self.active:
                if self.debug is True:
                    print(f"[socket][reconnect_handler] Reconnecting Socket")

                self.close()
                self.run_amino_socket()

    def handle_message(self, ws, data):
        self.client.handle_socket_message(data)
        return

    def send(self, data):
        if self.debug is True:
            print(f"[socket][send] Sending Data : {data}")
        
        if not self.socket_thread:
            self.run_amino_socket()
            time.sleep(5)

        self.socket.send(data)

    def run_amino_socket(self):
        try:
            if self.debug is True:
                print(f"[socket][start] Starting Socket")

            if self.client.sid is None:
                return

            final = f"{self.client.device_id}|{int(time.time() * 1000)}"

            self.headers = {
                "NDCDEVICEID": gen_deviceId() if self.client.autoDevice else self.client.device_id,
                "NDCAUTH": f"sid={self.client.sid}",
                "NDC-MSG-SIG": helpers.signature(final)
            }

            self.socket = websocket.WebSocketApp(
                f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
                on_message = self.handle_message,
                header = self.headers
            )

            self.active = True
            self.socket_thread = Thread(target=self.socket.run_forever)
            self.socket_thread.start()

            if self.reconnect_thread is None:
                self.reconnect_thread = Thread(target=self.reconnect_handler)
                self.reconnect_thread.start()
            
            if self.debug is True:
                print(f"[socket][start] Socket Started")
        except Exception as e:
            print(e)

    def close(self):
        if self.debug is True:
            print(f"[socket][close] Closing Socket")

        self.active = False
        try:
            self.socket.close()
        except Exception as closeError:
            if self.debug is True:
                print(f"[socket][close] Error while closing Socket : {closeError}")

        return

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

    def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
        return self.chat_methods.get(key, self.default)(data)

    def _resolve_chat_action_start(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_start.get(key, self.default)(data)

    def _resolve_chat_action_end(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_end.get(key, self.default)(data)

    def resolve(self, data):
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(data)

    def event(self, type):
        def registerHandler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler

        return registerHandler

    def on_text_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_image_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_youtube_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_strike_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_sticker_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_delete_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_group_member_join(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_group_member_leave(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_invite(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_background_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_title_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_icon_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_video_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_avatar_chat_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_content_changed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_screen_room_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_screen_room_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_host_transfered(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_text_message_force_removed(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_removed_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_text_message_removed_by_admin(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tip(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_pin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_open_to_everyone(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_invited_and_requested(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_voice_chat_permission_invite_only(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_view_only_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_view_only_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_unpin_announcement(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tipping_enabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_chat_tipping_disabled(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_timestamp_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_welcome_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_invite_message(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)

    def on_user_typing_start(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)
    def on_user_typing_end(self, data): self.call(getframe(0).f_code.co_name, objects.Event(data["o"]).Event)

    def default(self, data): self.call(getframe(0).f_code.co_name, data)