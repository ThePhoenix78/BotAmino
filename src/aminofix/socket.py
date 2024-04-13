import time
import json
import threading
import urllib.parse

import websocket

from .lib.util import Event, gen_deviceId, signature

__all__ = ("Callbacks", "SocketHandler",)

class SocketHandler:
    def __init__(self, socket_trace=False, debug=False):
        self.socket_url = "wss://ws1.aminoapps.com"
        self.debug = debug
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None
        self.reconnectTime = 180
        self.reconnect_thread = None
        websocket.enableTrace(socket_trace)

    def reconnect_handler(self):
        # Made by enchart#3410 thx
        # Fixed by The_Phoenix#3967
        while self.active:
            time.sleep(self.reconnectTime)
            if self.active:
                if self.debug is True:
                    print(f"[socket][reconnect_handler] Reconnecting Socket")
                self.close()
                self.run_amino_socket()

    def on_open(self, ws):
        self.active = True

    def on_close(self, ws, code, msg):
        self.active = False

    def handle_message(self, ws, data):
        pass

    def send(self, data):
        if self.debug is True:
            print(f"[socket][send] Sending Data : {data}")
        if not self.socket_thread:
            self.run_amino_socket()
            time.sleep(5)
        if self.socket:
            self.socket.send(data)

    def run_amino_socket(self):
        try:
            if self.debug is True:
                print(f"[socket][start] Starting Socket")
            if self.sid is None:
                return
            final = f"{self.device_id}|{int(time.time() * 1000)}"
            self.headers = {
                "NDCDEVICEID": gen_deviceId() if self.autoDevice else self.device_id,
                "NDCAUTH": f"sid={self.sid}",
                "NDC-MSG-SIG": signature(final)
            }
            self.socket = websocket.WebSocketApp(
                f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
                on_message=self.handle_message,
                on_open=self.on_open,
                on_close=self.on_close,
                header=self.headers
            )
            kwargs = {
                "ping_interval": 60,
                "ping_timeout": None,
                "reconnect": self.reconnectTime
            }
            if self.proxies:
                proxy_url = None
                for protocol in ("socks5h", "socks5", "socks4a", "socks4", "https", "http"):
                    value = self.proxies.get(protocol)
                    if value:
                        proxy_url = value
                        break
                if proxy_url:
                    proxy = urllib.parse.urlparse(proxy_url)
                    kwargs["http_proxy_host"] = proxy.hostname
                    kwargs["http_proxy_port"] = proxy.port
                    kwargs["http_proxy_timeout"] = None
                    kwargs["proxy_type"] = "http" if proxy.scheme == "https" else proxy.scheme
                    if proxy.username or proxy.password:
                        kwargs["http_proxy_auth"] = (proxy.username, proxy.password)
            self.socket_thread = threading.Thread(target=self.socket.run_forever, kwargs=kwargs)
            self.socket_thread.start()
            while not self.socket.sock:
                pass
            while not self.active:
                if not self.socket_thread.is_alive() and not self.active:
                    raise websocket.WebSocketConnectionClosedException()
            if self.reconnect_thread is None:
                self.reconnect_thread = threading.Thread(target=self.reconnect_handler)
                self.reconnect_thread.start()
            if self.debug is True:
                print(f"[socket][start] Socket Started")
        except Exception as e:
            print(e)

    def close(self):
        if self.debug is True:
            print(f"[socket][close] Closing Socket")
        try:
            if self.socket:
                self.socket.close()
        except Exception as closeError:
            if self.debug is True:
                print(f"[socket][close] Error while closing Socket : {closeError}")

class Callbacks:
    def __init__(self):
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
            "53:0": self.on_voice_chat_cancelled,
            "54:0": self.on_voice_chat_declined,
            "55:0": self.on_video_chat_not_answered,
            "56:0": self.on_video_chat_cancelled,
            "57:0": self.on_video_chat_declined,
            "58:0": self.on_avatar_chat_not_answered,
            "59:0": self.on_avatar_chat_cancelled,
            "60:0": self.on_avatar_chat_declined,
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
        message_type = data.get('o', {}).get("chatMessage", {}).get("type", 0)
        media_type = data.get('o', {}).get("chatMessage", {}).get("mediaType", 0)
        key = f"{message_type}:{media_type}"
        return self.chat_methods.get(key, self.default)(data)

    def _resolve_chat_action_start(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_start.get(key, self.default)(data)

    def _resolve_chat_action_end(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_end.get(key, self.default)(data)

    def handle_message(self, ws, data):
        self.resolve(data)

    def resolve(self, data):
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(data)

    def event(self, type):
        if not hasattr(self, type) or not callable(getattr(self, type)) or not (type == "default" or type.startswith("on_")):
            raise ValueError(f"Unknown {type!r} event type")
        def registerHandler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler
        return registerHandler

    def on_text_message(self, data): self.call("on_text_message", Event(data.get("o", {})).Event)
    def on_image_message(self, data): self.call("on_image_message", Event(data.get("o", {})).Event)
    def on_youtube_message(self, data): self.call("on_youtube_message", Event(data.get("o", {})).Event)
    def on_strike_message(self, data): self.call("on_strike_message", Event(data.get("o", {})).Event)
    def on_voice_message(self, data): self.call("on_voice_message", Event(data.get("o", {})).Event)
    def on_sticker_message(self, data): self.call("on_sticker_message", Event(data.get("o", {})).Event)
    def on_voice_chat_not_answered(self, data): self.call("on_voice_chat_not_answered", Event(data.get("o", {})).Event)
    def on_voice_chat_cancelled(self, data): self.call("on_voice_chat_cancelled", Event(data.get("o", {})).Event)
    def on_voice_chat_declined(self, data): self.call("on_voice_chat_declined", Event(data.get("o", {})).Event)
    def on_video_chat_not_answered(self, data): self.call("on_video_chat_not_answered", Event(data.get("o", {})).Event)
    def on_video_chat_cancelled(self, data): self.call("on_video_chat_cancelled", Event(data.get("o", {})).Event)
    def on_video_chat_declined(self, data): self.call("on_video_chat_declined", Event(data.get("o", {})).Event)
    def on_avatar_chat_not_answered(self, data): self.call("on_avatar_chat_not_answered", Event(data.get("o", {})).Event)
    def on_avatar_chat_cancelled(self, data): self.call("on_avatar_chat_cancelled", Event(data.get("o", {})).Event)
    def on_avatar_chat_declined(self, data): self.call("on_avatar_chat_declined", Event(data.get("o", {})).Event)
    def on_delete_message(self, data): self.call("on_delete_message", Event(data.get("o", {})).Event)
    def on_group_member_join(self, data): self.call("on_group_member_join", Event(data.get("o", {})).Event)
    def on_group_member_leave(self, data): self.call("on_group_member_leave", Event(data.get("o", {})).Event)
    def on_chat_invite(self, data): self.call("on_chat_invite", Event(data.get("o", {})).Event)
    def on_chat_background_changed(self, data): self.call("on_chat_background_changed", Event(data.get("o", {})).Event)
    def on_chat_title_changed(self, data): self.call("on_chat_title_changed", Event(data.get("o", {})).Event)
    def on_chat_icon_changed(self, data): self.call("on_chat_icon_changed", Event(data.get("o", {})).Event)
    def on_voice_chat_start(self, data): self.call("on_voice_chat_start", Event(data.get("o", {})).Event)
    def on_video_chat_start(self, data): self.call("on_video_chat_start", Event(data.get("o", {})).Event)
    def on_avatar_chat_start(self, data): self.call("on_avatar_chat_start", Event(data.get("o", {})).Event)
    def on_voice_chat_end(self, data): self.call("on_voice_chat_end", Event(data.get("o", {})).Event)
    def on_video_chat_end(self, data): self.call("on_video_chat_end", Event(data.get("o", {})).Event)
    def on_avatar_chat_end(self, data): self.call("on_avatar_chat_end", Event(data.get("o", {})).Event)
    def on_chat_content_changed(self, data): self.call("on_chat_content_changed", Event(data.get("o", {})).Event)
    def on_screen_room_start(self, data): self.call("on_screen_room_start", Event(data.get("o", {})).Event)
    def on_screen_room_end(self, data): self.call("on_screen_room_end", Event(data.get("o", {})).Event)
    def on_chat_host_transfered(self, data): self.call("on_chat_host_transfered", Event(data.get("o", {})).Event)
    def on_text_message_force_removed(self, data): self.call("on_text_message_force_removed", Event(data.get("o", {})).Event)
    def on_chat_removed_message(self, data): self.call("on_chat_removed_message", Event(data.get("o", {})).Event)
    def on_text_message_removed_by_admin(self, data): self.call("on_text_message_removed_by_admin", Event(data.get("o", {})).Event)
    def on_chat_tip(self, data): self.call("on_chat_tip", Event(data.get("o", {})).Event)
    def on_chat_pin_announcement(self, data): self.call("on_chat_pin_announcement", Event(data.get("o", {})).Event)
    def on_voice_chat_permission_open_to_everyone(self, data): self.call("on_voice_chat_permission_open_to_everyone", Event(data.get("o", {})).Event)
    def on_voice_chat_permission_invited_and_requested(self, data): self.call("on_voice_chat_permission_invited_and_requested", Event(data.get("o", {})).Event)
    def on_voice_chat_permission_invite_only(self, data): self.call("on_voice_chat_permission_invite_only", Event(data.get("o", {})).Event)
    def on_chat_view_only_enabled(self, data): self.call("on_chat_view_only_enabled", Event(data.get("o", {})).Event)
    def on_chat_view_only_disabled(self, data): self.call("on_chat_view_only_disabled", Event(data.get("o", {})).Event)
    def on_chat_unpin_announcement(self, data): self.call("on_chat_unpin_announcement", Event(data.get("o", {})).Event)
    def on_chat_tipping_enabled(self, data): self.call("on_chat_tipping_enabled", Event(data.get("o", {})).Event)
    def on_chat_tipping_disabled(self, data): self.call("on_chat_tipping_disabled", Event(data.get("o", {})).Event)
    def on_timestamp_message(self, data): self.call("on_timestamp_message", Event(data.get("o", {})).Event)
    def on_welcome_message(self, data): self.call("on_welcome_message", Event(data.get("o", {})).Event)
    def on_invite_message(self, data): self.call("on_invite_message", Event(data.get("o", {})).Event)
    def on_user_typing_start(self, data): self.call("on_user_typing_start", Event(data.get("o", {})).Event)
    def on_user_typing_end(self, data): self.call("on_user_typing_end", Event(data.get("o", {})).Event)
    def default(self, data): self.call("default", data)
