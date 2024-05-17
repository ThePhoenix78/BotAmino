import logging
import time
import json
import threading
import urllib.parse

import websocket

from .lib.util import (
    Channel,
    Event,
    gen_deviceId,
    signature
)

_logger = logging.getLogger("aminofix.socket")
_handler = logging.StreamHandler()
_handler.setLevel(logging.DEBUG)
_logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG)

__all__ = ("Callbacks", "SocketHandler",)

class SocketHandler:
    def __init__(self, socket_trace=False, debug=False):
        self.socket_url = "wss://ws1.aminoapps.com"
        self.debug = debug
        self.active = False
        self.socket = None
        self.socket_thread = None
        websocket.enableTrace(socket_trace)

    def handle_message(self, data):
        raise NotImplementedError

    def amino_socket_task(self):
        if self.active or not self.socket or not self.socket.connected:
            return
        self.active = True
        while self.socket and self.socket.connected:
            try:
                data = self.socket.recv()
            except websocket.WebSocketException:
                break
            else:
                self.handle_message(data)
        self.active = False
        if self.socket is None:
            return
        if self.socket.connected:
            self.socket.close()
            self.socket_thread = None
        self.run_amino_socket()

    def run_amino_socket(self):
        if getattr(self, "sid", None) is None:
            return
        socket = self.socket
        if not socket:
            socket = websocket.WebSocket()
        if socket.connected:
            if self.socket_thread and self.socket_thread.is_alive():
                return
            socket.close()
            self.socket = None
        if self.active:
            self.active = False
        if self.debug:
            _logger.debug("[socket][start] Starting Socket")
        self.socket_thread, kwargs = None, {}
        if getattr(self, "proxies", None):
            proxy_url = None
            for protocol in ("socks5h", "socks5", "socks4a", "socks4", "https", "http"):
                proxy_url = self.proxies.get(protocol)
                if proxy_url:
                    break
            if proxy_url:
                proxy = urllib.parse.urlparse(proxy_url)
                kwargs["http_proxy_host"] = proxy.hostname
                kwargs["http_proxy_port"] = proxy.port
                kwargs["http_proxy_timeout"] = None
                kwargs["proxy_type"] = proxy.scheme.removesuffix("s")
                if proxy.username or proxy.password:
                    kwargs["http_proxy_auth"] = (proxy.username, proxy.password)
        proxy_tries = 5
        while not socket.connected:
            data = f"{self.device_id}|{int(time.time() * 1000)}"
            kwargs.update({
                "header": {
                    "NDCDEVICEID": gen_deviceId() if self.autoDevice else self.device_id,
                    "NDCAUTH": f"sid={self.sid}",
                    "NDC-MSG-SIG": signature(data)
                },
                "url": f"{self.socket_url}/?signbody={data.replace('|', '%7C')}",
                "timeout": None,
                "host": None
            })
            try:
                socket.connect(**kwargs)
            except (
                websocket.WebSocketBadStatusException,
                websocket.WebSocketConnectionClosedException,
                websocket.WebSocketAddressException
            ):
                time.sleep(1)
                continue
            except websocket.WebSocketProxyException:
                if proxy_tries <= 0:
                    raise
                proxy_tries -= 1
                time.sleep(1.5)
                continue
            else:
                if self.debug:
                    _logger.debug("[socket][start] Socket Started")
                self.socket = socket
                time.sleep(0.3)
        self.socket_thread = threading.Thread(target=self.amino_socket_task)
        self.socket_thread.start()
        while not self.active:
            pass

    def send(self, data):
        if self.debug:
            _logger.debug(f"[socket][send] Sending Data : {data}")
        if not self.socket_thread:
            self.run_amino_socket()
            time.sleep(5)
        if not isinstance(data, (bytes, str)):
            data = json.dumps(data)
        if self.socket:
            self.socket.send(data)

    def close(self):
        if self.debug:
            _logger.debug(f"[socket][close] Closing Socket")
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except Exception as exc:
            if self.debug:
                _logger.debug(f"[socket][close] Error while closing Socket : {exc}")

class Callbacks:
    def __init__(self):
        self.handlers = {}
        self.methods = {
            201: self._resolve_agora_token_response,
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

    def _resolve_agora_token_response(self, data):
        self.on_fetch_channel(data)

    def handle_message(self, data):
        try:
            data = json.loads(data)
        except Exception:
            return
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
    def on_fetch_channel(self, data): self.call("on_fetch_channel", Channel(data.get("o", {})).Channel)
    def default(self, data): self.call("default", data)
