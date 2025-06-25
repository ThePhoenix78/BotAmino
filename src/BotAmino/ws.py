from __future__ import annotations

import abc
import collections.abc
import contextlib
import json
import logging
import threading
import time
import typing
import typing_extensions
import urllib.parse
import websocket
from .objects import Channel, Object, PlayList
from .types import (
    BlogType,
    ChannelJoinRole,
    ChannelType,
    ChatMembership,
    ChatType,
    LiveLayerAction,
    LiveLayerTopic,
    MessageType,
    NotificationType,
    ObjectType,
    WsMessageType,
)
from .typing import JsonDict, Proxies
from .utils import build_ndtopic, build_signature, build_target, objectTypeName, urljoin

__all__ = ("WSBase", "WSClient", "WSSubClient")

P = typing_extensions.ParamSpec("P")
C = typing.TypeVar("C", bound=collections.abc.Callable[..., typing.Any])
T = typing.TypeVar("T")

EventCallback = collections.abc.Callable[P, typing.Any]
Converter = collections.abc.Callable[[JsonDict], T]

# logger
logger = logging.getLogger("BotAmino.ws")
logger.addHandler(logging.NullHandler())

# others
payloadIdsCount = 0
payloadIdsLock = threading.Lock()


def build_payload_id():
    global payloadIdsCount
    with payloadIdsLock:
        payloadIdsCount += 1
    return str(int(time.monotonic() + payloadIdsCount))


class Event(typing.Generic[T]):
    def __init__(self, callback: EventCallback[T], converter: Converter[T]) -> None:
        self.callback = callback
        self.converter = converter

    def __hash__(self) -> int:
        return hash((self.callback, self.converter))

    def __repr__(self) -> str:
        try:
            return f"<{self.callback.__name__.lower()!r} event>"
        except AttributeError:
            return super().__repr__()

    def __call__(self, data: T | JsonDict) -> None:
        if isinstance(data, dict):
            data = typing.cast(JsonDict, data)
            data = self.converter(data)
        with contextlib.suppress(Exception):
            self.callback(data)


class WsEventListener:
    def __init__(self, requestId: str, timeout: float | None = None) -> None:
        self.requestId = requestId
        self.timeout = timeout
        self.response: JsonDict | None = None
        self._event = threading.Event()

    def __hash__(self) -> int:
        return hash(self.requestId)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, WsEventListener):
            return self.requestId == other.requestId
        return False

    def set_result(self, response: JsonDict) -> None:
        self.response = response
        self._event.set()

    @property
    def result(self) -> JsonDict:
        if not self._event.wait(self.timeout):
            raise TimeoutError(f"Unlistened event {self.requestId}")
        return typing.cast(JsonDict, self.response)


class LiveLayerReport:
    def __init__(
        self,
        ws: WSBase,
        comId: int,
        target: str,
        actions: collections.abc.Sequence[LiveLayerAction],
        params: JsonDict | None = None,
        eventSource: str | None = None,
        eventOrigin: str | None = None,
    ) -> None:
        self.ws = ws
        self.comId = comId
        self.target = target
        self.actions = list(actions)
        self.params = dict(params or {})
        self.eventSource = eventSource
        self.eventOrigin = eventOrigin
        self.startTime = 0.0
        self.endTime = 0.0

    def __enter__(self) -> typing_extensions.Self:
        self.start()
        return self

    def __exit__(self, *excinfo: typing.Any) -> bool:
        self.end()
        return not any(excinfo)

    def ended(self) -> bool:
        return self.endTime >= self.startTime

    def start(self) -> None:
        self.startTime = time.monotonic()
        self.ws.report_active(
            comId=self.comId,
            target=self.target,
            actions=self.actions,
            params=self.params,
            eventSource=self.eventSource,
            eventOrigin=self.eventOrigin,
        )

    def end(self) -> None:
        self.endTime = time.monotonic()
        duration = self.endTime - self.startTime
        self.params.update(duration=duration)
        self.ws.report_inactive(
            comId=self.comId,
            target=self.target,
            actions=self.actions,
            params=self.params,
            eventSource=self.eventSource,
            eventOrigin=self.eventOrigin,
        )


class WSBase(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def deviceId(self) -> str: ...
    @property
    @abc.abstractmethod
    def language(self) -> str: ...
    @property
    @abc.abstractmethod
    def proxies(self) -> Proxies | None: ...
    @property
    @abc.abstractmethod
    def sid(self) -> str | None: ...
    @property
    @abc.abstractmethod
    def userId(self) -> str | None: ...
    @property
    @abc.abstractmethod
    def connected(self) -> bool: ...
    @property
    @abc.abstractmethod
    def ws(self) -> websocket.WebSocket | None: ...

    @staticmethod
    def create_event(
        callback: EventCallback[T] | Event[T], converter: Converter[T] | None = None
    ) -> Event[T]:
        if not isinstance(callback, Event):
            assert callable(converter), (
                "converter must be a function when the callback is a function, not %r"
                % converter
            )
            callback = Event(callback, converter)
        return typing.cast(Event[T], callback)

    @typing.overload
    @abc.abstractmethod
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[True],
        timeout: float | None = None,
    ) -> None: ...
    @typing.overload
    @abc.abstractmethod
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[False] = False,
        timeout: float | None = None,
    ) -> JsonDict: ...
    @typing.overload
    @abc.abstractmethod
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None: ...
    @abc.abstractmethod
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None: ...

    def report_active(
        self,
        comId: int,
        target: str,
        actions: collections.abc.Sequence[str],
        params: JsonDict,
        eventSource: str | None = None,
        eventOrigin: str | None = None,
    ) -> None:
        # if topicIds: params["topicIds"] = topicIds
        self.send(
            WsMessageType.LIVE_LAYER_REPORT_ACTIVE_REQUEST,
            data=dict(
                ndcId=comId,
                actions=list(actions),
                params=dict(params),
                target=target,
                eventSource=eventSource,
                eventOrigin=eventOrigin,
            ),
        )

    def report_inactive(
        self,
        comId: int,
        target: str,
        actions: collections.abc.Sequence[str],
        params: JsonDict,
        eventSource: str | None = None,
        eventOrigin: str | None = None,
    ) -> None:
        self.send(
            WsMessageType.LIVE_LAYER_REPORT_INACTIVE_REQUEST,
            data=dict(
                ndcId=comId,
                actions=list(actions),
                params=dict(params),
                target=target,
                eventSource=eventSource,
                eventOrigin=eventOrigin,
            ),
        )


class WSClient(WSBase):
    @property
    def socket_url(self) -> str:
        return "wss://ws1.aminoapps.com/"

    @property
    def connected(self) -> bool:
        return bool(self.ws and self.ws.connected)

    @property
    def ws_task_active(self) -> bool:
        return getattr(self, "_ws_task_active")

    @ws_task_active.setter
    def ws_task_active(self, value: bool) -> None:
        setattr(self, "_ws_task_active", value)

    @property
    def ws(self) -> websocket.WebSocket | None:
        return getattr(self, "_ws")

    @ws.setter
    def ws(self, value: websocket.WebSocket | None) -> None:
        setattr(self, "_ws", value)

    @property
    def ws_listeners(self) -> dict[str, WsEventListener]:
        return getattr(self, "_ws_listeners")

    @ws_listeners.setter
    def ws_listeners(self, value: dict[str, WsEventListener]) -> None:
        setattr(self, "_ws_listeners", value)

    @property
    def ws_handlers(
        self,
    ) -> collections.abc.Mapping[
        WsMessageType | int, collections.abc.Callable[[JsonDict], None]
    ]:
        return getattr(self, "_ws_handlers")

    @ws_handlers.setter
    def ws_handlers(
        self,
        value: collections.abc.Mapping[
            WsMessageType | int, collections.abc.Callable[[JsonDict], None]
        ],
    ) -> None:
        setattr(self, "_ws_handlers", value)

    @property
    def channel_events(self) -> dict[WsMessageType, set[Event[typing.Any]]]:
        return getattr(self, "_channel_events")

    @channel_events.setter
    def channel_events(
        self, value: dict[WsMessageType, set[Event[typing.Any]]]
    ) -> None:
        return setattr(self, "_channel_events", value)

    @property
    def chat_events(self) -> dict[MessageType, set[Event[typing.Any]]]:
        return getattr(self, "_chat_events")

    @chat_events.setter
    def chat_events(self, value: dict[MessageType, set[Event[typing.Any]]]) -> None:
        setattr(self, "_chat_events", value)

    @property
    def error_events(self) -> dict[WsMessageType, set[Event[typing.Any]]]:
        return getattr(self, "_error_events")

    @error_events.setter
    def error_events(self, value: dict[WsMessageType, set[Event[typing.Any]]]) -> None:
        setattr(self, "_error_events", value)

    @property
    def live_layer_events(self) -> dict[WsMessageType, set[Event[typing.Any]]]:
        return getattr(self, "_live_layer_events")

    @live_layer_events.setter
    def live_layer_events(
        self, value: dict[WsMessageType, set[Event[typing.Any]]]
    ) -> None:
        setattr(self, "_live_layer_events", value)

    @property
    def live_layer_active_events(self) -> dict[LiveLayerAction, set[Event[typing.Any]]]:
        return getattr(self, "_live_layer_active_events")

    @live_layer_active_events.setter
    def live_layer_active_events(
        self, value: dict[LiveLayerAction, set[Event[typing.Any]]]
    ) -> None:
        setattr(self, "_live_layer_active_events", value)

    @property
    def live_layer_inactive_events(
        self,
    ) -> dict[LiveLayerAction, set[Event[typing.Any]]]:
        return getattr(self, "_live_layer_inactive_events")

    @live_layer_inactive_events.setter
    def live_layer_inactive_events(
        self, value: dict[LiveLayerAction, set[Event[typing.Any]]]
    ) -> None:
        setattr(self, "_live_layer_inactive_events", value)

    @property
    def notification_events(self) -> dict[NotificationType, set[Event[typing.Any]]]:
        return getattr(self, "_notification_events")

    @notification_events.setter
    def notification_events(
        self, value: dict[NotificationType, set[Event[typing.Any]]]
    ) -> None:
        setattr(self, "_notification_events", value)

    def __init__(self) -> None:
        self.ws_handlers = {
            # errors
            WsMessageType.ERROR_MESSAGE: self.resolve_error,
            WsMessageType.USER_PROFILE_BANNED: self.resolve_error,
            WsMessageType.MULTI_DEVICE_ERROR: self.resolve_error,
            WsMessageType.CHANNEL_MEMBERSHIP_BANNED: self.resolve_error,
            WsMessageType.CHANNEL_NOT_AVAILABLE: self.resolve_error,
            WsMessageType.CHANNEL_NO_PRESENTER: self.resolve_error,
            # channel
            WsMessageType.CHANNEL_ORGANIZER_LEFT: self.resolve_channel_message,
            WsMessageType.CHANNEL_PRIVATE_NOT_ACCEPT: self.resolve_channel_message,
            WsMessageType.CHANNEL_FORCE_UPDATE_USER_ROLE_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_FORCE_QUIT_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_STATUS_CHANGED_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_USER_STATUS_CHANGED_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_USER_JOINED_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_USER_LEFT_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_WAIT_LIST_APPROVE_MESSAGE: self.resolve_channel_message,
            WsMessageType.CHANNEL_WAIT_LIST_CHANGED_MESSAGE: self.resolve_channel_message,
            WsMessageType.AGORA_TOKEN_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_UPDATE_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_UPDATE_JOIN_ROLE_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_FORCE_UPDATE_USER_ROLE_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_JOIN_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_LEAVE_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_USER_LIST_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_USER_PING_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_WAIT_LIST_CLEAN_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_APPROVE_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_CANCEL_RESPONSE: self.resolve_response,
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_RESPONSE: self.resolve_response,
            WsMessageType.SCREEN_ROOM_PLAY_LIST_RESPONSE: self.resolve_response,
            WsMessageType.SCREEN_ROOM_PLAY_LIST_UPDATE_RESPONSE: self.resolve_response,
            # dto
            WsMessageType.PUSH_NOTIFICATION_DTO: self.resolve_notification_message,
            WsMessageType.CHAT_MESSAGE_DTO: self.resolve_chat_message,
            # live layer
            WsMessageType.LIVE_LAYER_SUBSCRIBE_RESPONSE: self.resolve_response,  # self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_UNSUBSCRIBE_RESPONSE: self.resolve_response,  # self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_USER_JOINED_EVENT: self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_USER_LEFT_EVENT: self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_REPORT_ACTIVE_RESPONSE: self.resolve_response,  # self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_REPORT_ACTIVE_REQUEST: self.resolve_live_layer_active,
            WsMessageType.LIVE_LAYER_REPORT_INACTIVE_RESPONSE: self.resolve_response,  # self.resolve_live_layer_message,
            WsMessageType.LIVE_LAYER_REPORT_INACTIVE_REQUEST: self.resolve_live_layer_inactive,
        }
        self.ws = None
        self.ws_task_active = False
        self.ws_listeners = {}
        self.channel_events = {}
        self.chat_events = {}
        self.error_events = {}
        self.live_layer_events = {}
        self.live_layer_active_events = {}
        self.live_layer_inactive_events = {}
        self.notification_events = {}

    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[True],
        timeout: float | None = None,
    ) -> None: ...
    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[False] = False,
        timeout: float | None = None,
    ) -> JsonDict: ...
    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None: ...
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None:
        if not self.ws:
            raise RuntimeError("Websocket is not running")
        if "id" not in data:
            data.update(id=build_payload_id())
        requestId = data["id"]
        self.ws.send(json.dumps(dict(o=data, t=requestType)))
        if ignoreResponse:
            return None
        listener = WsEventListener(requestId, timeout)
        listener = self.ws_listeners.setdefault(requestId, listener)
        return listener.result

    def ws_task(self) -> None:
        if self.ws_task_active:  # duplicated task prevention
            return
        self.ws_task_active = True
        while self.ws:
            if not self.ws.connected:
                continue
            try:
                data = self.ws.recv()
            except websocket.WebSocketConnectionClosedException:
                try:
                    self.connect()
                except websocket.WebSocketException as exc:
                    self.ws = None
                    logger.error("reconnection error caused by %r", exc)
                    break
            else:
                self.resolve_ws_message(json.loads(data))
        self.ws_task_active = False

    def disconnect(self) -> None:
        if self.ws:
            if self.ws.connected:
                self.ws.close()
            self.ws = None

    def connect(self) -> None:
        proxy_host = proxy_port = proxy_auth = None
        if self.proxies:
            proxy_string = self.proxies.get("https", self.proxies.get("http"))
            if proxy_string:
                proxy = urllib.parse.urlparse(proxy_string)
                proxy_host = proxy.hostname
                proxy_port = proxy.port
                proxy_auth = (
                    (proxy.username, proxy.password)
                    if proxy.username or proxy.password
                    else None
                )
        data = f"{self.deviceId}|{int(time.time() * 1000)}"
        headers: typing.Dict[str, typing.Any] = {
            "AUID": self.userId,
            "NDCDEVICEID": self.deviceId,
            "NDCAUTH": f"sid={self.sid}",
            "NDC-MSG-SIG": build_signature(data),
            "NDCLANG": self.language,
            "Accept-Language": "en-US",
        }
        self.ws = websocket.create_connection(  # type: ignore
            url=f"{self.socket_url}?signbody={data.replace('|', '%7C')}",
            header=headers,
            http_proxy_host=proxy_host,
            http_proxy_port=proxy_port,
            http_proxy_auth=proxy_auth,
        )
        threading.Thread(target=self.ws_task).start()

    def resolve_error(self, payload: JsonDict) -> None:
        for event in self.error_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_notification_message(self, payload: JsonDict) -> None:
        for event in self.notification_events.get(
            payload["payload"]["notifType"], set()
        ):
            threading.Thread(target=event, args=(payload["payload"],)).start()

    def resolve_chat_message(self, payload: JsonDict) -> None:
        for event in self.chat_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_channel_message(self, payload: JsonDict) -> None:
        for event in self.channel_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_response(self, payload: JsonDict) -> None:
        listener = self.ws_listeners.pop(payload["o"]["id"], None)
        if not listener:
            return
        listener.set_result(payload["o"])

    def resolve_live_layer_message(self, payload: JsonDict) -> None:
        for event in self.live_layer_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_live_layer_active(self, payload: JsonDict) -> None:
        for event in self.live_layer_active_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_live_layer_inactive(self, payload: JsonDict) -> None:
        for event in self.live_layer_inactive_events.get(payload["t"], set()):
            threading.Thread(target=event, args=(payload["o"],)).start()

    def resolve_ws_message(self, payload: JsonDict) -> None:
        payloadType = WsMessageType(payload["t"])
        handler = self.ws_handlers.get(payloadType)
        if not handler:
            logger.critical("unparsed event -> %r", payload)
            return
        logger.debug("resolved event -> %r", payload)
        handler(payload)

    def create_channel_event(
        self,
        eventType: WsMessageType,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.channel_events.setdefault(eventType, set()).add(event)
        return event

    def remove_channel_event(
        self, eventType: WsMessageType, event: Event[typing.Any]
    ) -> None:
        self.channel_events.setdefault(eventType, set()).remove(event)

    def create_chat_event(
        self,
        eventType: MessageType,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.chat_events.setdefault(eventType, set()).add(event)
        return event

    def remove_chat_event(
        self, eventType: MessageType, event: Event[typing.Any]
    ) -> None:
        self.chat_events.setdefault(eventType, set()).remove(event)

    def create_error_event(
        self,
        eventType: WsMessageType,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.error_events.setdefault(eventType, set()).add(event)
        return event

    def remove_error_event(
        self, eventType: WsMessageType, event: Event[typing.Any]
    ) -> None:
        self.error_events.setdefault(eventType, set()).remove(event)

    def create_live_layer_event(
        self,
        eventType: WsMessageType,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.live_layer_events.setdefault(eventType, set()).add(event)
        return event

    def remove_live_layer_event(
        self, eventType: WsMessageType, event: Event[typing.Any]
    ) -> None:
        self.live_layer_events.setdefault(eventType, set()).remove(event)

    def create_live_layer_active_event(
        self,
        eventType: LiveLayerAction,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.live_layer_active_events.setdefault(eventType, set()).add(event)
        return event

    def remove_live_layer_active_event(
        self, eventType: LiveLayerAction, event: Event[typing.Any]
    ) -> None:
        self.live_layer_active_events.setdefault(eventType, set()).remove(event)

    def create_live_layer_inactive_event(
        self,
        eventType: LiveLayerAction,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.live_layer_inactive_events.setdefault(eventType, set()).add(event)
        return event

    def remove_live_layer_inactive_event(
        self, eventType: LiveLayerAction, event: Event[typing.Any]
    ) -> None:
        self.live_layer_inactive_events.setdefault(eventType, set()).remove(event)

    def create_notification_event(
        self,
        eventType: NotificationType,
        callback: EventCallback[T] | Event[T],
        converter: Converter[T] | None = None,
    ) -> Event[T]:
        event = self.create_event(callback, converter)
        self.notification_events.setdefault(eventType, set()).add(event)
        return event

    def remove_notification_event(
        self, eventType: NotificationType, event: Event[typing.Any]
    ) -> None:
        self.notification_events.setdefault(eventType, set()).remove(event)

    def on_channel_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_channel_status_changed(event)
        self.on_channel_member_status_changed(event)
        self.on_channel_force_quit(event)
        self.on_wait_list_approve(event)
        self.on_wait_list_changed(event)
        self.on_channel_member_join(event)
        self.on_channel_member_left(event)
        self.on_channel_organizer_left(event)
        self.on_voice_participant_force_removed(event)
        return event

    def on_notification_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        for eventType in NotificationType:
            self.create_notification_event(eventType, event)
        return event

    def on_error_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_error(event)
        self.on_user_banned_error(event)
        self.on_multi_device_error(event)
        self.on_channel_membership_banned_error(event)
        self.on_channel_not_available_error(event)
        self.on_channel_no_presenter_error(event)
        return event

    def on_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(WsMessageType.ERROR_MESSAGE, callback)

    def on_user_banned_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(WsMessageType.USER_PROFILE_BANNED, callback)

    def on_multi_device_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(
            WsMessageType.MULTI_DEVICE_ERROR, callback, Object
        )

    def on_channel_membership_banned_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(
            WsMessageType.CHANNEL_MEMBERSHIP_BANNED, callback
        )

    def on_channel_not_available_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(WsMessageType.CHANNEL_NOT_AVAILABLE, callback)

    def on_channel_no_presenter_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_error_event(WsMessageType.CHANNEL_NO_PRESENTER, callback)

    def on_channel_status_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_STATUS_CHANGED_MESSAGE, callback, Object
        )

    def on_channel_member_status_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_USER_STATUS_CHANGED_MESSAGE, callback, Object
        )

    def on_channel_force_quit(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_FORCE_QUIT_MESSAGE, callback, Object
        )

    def on_wait_list_approve(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_WAIT_LIST_APPROVE_MESSAGE, callback, Object
        )

    def on_wait_list_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_WAIT_LIST_CHANGED_MESSAGE, callback, Object
        )

    def on_channel_member_join(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_USER_JOINED_MESSAGE, callback, Object
        )

    def on_channel_member_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_USER_LEFT_MESSAGE, callback, Object
        )

    def on_channel_organizer_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_ORGANIZER_LEFT, callback, Object
        )

    def on_voice_participant_force_removed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_channel_event(
            WsMessageType.CHANNEL_FORCE_UPDATE_USER_ROLE_MESSAGE, callback, Object
        )

    # chat message events
    def on_chat_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = Event(callback, Object)
        for eventType in MessageType:
            self.create_chat_event(eventType, event)
        return event

    def on_text_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.TEXT, callback, Object)

    def on_strike_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.STRIKE, callback, Object)

    def on_voice_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VOICE, callback, Object)

    def on_sticker_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.TEXT, callback, Object)

    def on_video_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VIDEO, callback, Object)

    def on_shared_exurl_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.SHARE_EXURL, callback, Object)

    def on_shared_user_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.SHARE_USER, callback, Object)

    def on_timestamp_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.TIMESTAMP, callback, Object)

    def on_welcome_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.WELCOME_MESSAGE, callback, Object)

    def on_deleted_message_by_mod(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.DELETED_BY_MOD, callback, Object)

    def on_deleted_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.DELETED, callback, Object)

    def on_forced_deleted_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.FORCED_DELETED, callback, Object)

    def on_voice_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_voice_call_start(event)
        self.on_voice_call_no_answered(event)
        self.on_voice_call_cancelled(event)
        self.on_voice_call_declined(event)
        self.on_voice_call_end(event)
        return event

    def on_voice_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VOICE_CALL_START, callback, Object)

    def on_voice_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VOICE_CALL_NO_ANSWERED, callback, Object
        )

    def on_voice_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VOICE_CALL_CANCELLED, callback, Object
        )

    def on_voice_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VOICE_CALL_DECLINED, callback, Object)

    def on_voice_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VOICE_CALL_END, callback, Object)

    def on_video_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_video_call_start(event)
        self.on_video_call_no_answered(event)
        self.on_video_call_cancelled(event)
        self.on_video_call_declined(event)
        self.on_video_call_end(event)
        return event

    def on_video_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VIDEO_CALL_START, callback, Object)

    def on_video_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VIDEO_CALL_NO_ANSWERED, callback, Object
        )

    def on_video_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VIDEO_CALL_CANCELLED, callback, Object
        )

    def on_video_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VIDEO_CALL_DECLINED, callback, Object)

    def on_video_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VIDEO_CALL_END, callback, Object)

    def on_avatar_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_avatar_call_start(event)
        self.on_avatar_call_no_answered(event)
        self.on_avatar_call_cancelled(event)
        self.on_avatar_call_declined(event)
        self.on_avatar_call_end(event)
        return event

    def on_avatar_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.AVATAR_CALL_START, callback, Object)

    def on_avatar_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.AVATAR_CALL_NO_ANSWERED, callback, Object
        )

    def on_avatar_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.AVATAR_CALL_CANCELLED, callback, Object
        )

    def on_avatar_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.AVATAR_CALL_DECLINED, callback, Object
        )

    def on_avatar_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.VIDEO_CALL_END, callback, Object)

    def on_screen_room(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_screen_room_start(event)
        self.on_screen_room_end(event)
        return event

    def on_screen_room_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.SCREENING_ROOM_START, callback, Object
        )

    def on_screen_room_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.SCREENING_ROOM_END, callback, Object)

    def on_chat_member_join(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.MEMBER_JOIN, callback, Object)

    def on_chat_member_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.MEMBER_LEFT, callback, Object)

    def on_chat_created(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.CHAT_CREATED, callback, Object)

    def on_chat_removed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.CHAT_REMOVED, callback, Object)

    def on_chat_invite(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.INVITE_MESSAGE, callback, Object)

    def on_chat_edited(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_chat_background_changed(event)
        self.on_chat_title_changed(event)
        self.on_chat_icon_changed(event)
        self.on_chat_content_changed(event)
        return event

    def on_chat_background_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.BACKGROUND_CHANGE, callback, Object)

    def on_chat_title_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.TITLE_CHANGE, callback, Object)

    def on_chat_icon_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.ICON_CHANGE, callback, Object)

    def on_chat_content_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.CONTENT_CHANGE, callback, Object)

    def on_chat_host_transferred(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.HOST_TRANSFERRED, callback, Object)

    def on_chat_tip(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.TIPPING, callback, Object)

    def on_chat_tip_permission_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_chat_tip_permission_enabled(event)
        self.on_chat_tip_permission_disabled(event)
        return event

    def on_chat_tip_permission_enabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.ENABLE_TIP_PERMISSION, callback, Object
        )

    def on_chat_tip_permission_disabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.DISABLE_TIP_PERMISSION, callback, Object
        )

    def on_chat_announcement_pinned(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.PIN_ANNOUNCEMENT, callback, Object)

    def on_chat_announcement_unpinned(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.UNPIN_ANNOUNCEMENT, callback, Object)

    def on_chat_view_only_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_chat_view_only_enabled(callback)
        self.on_chat_view_only_disabled(callback)
        return event

    def on_chat_view_only_enabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.ENABLE_VIEW_ONLY, callback, Object)

    def on_chat_view_only_disabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(MessageType.DISABLE_VIEW_ONLY, callback, Object)

    def on_voice_permission_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_voice_permission_open_to_everyone(event)
        self.on_voice_permission_approval_required(event)
        self.on_voice_permission_invite_only(event)
        return event

    def on_voice_permission_open_to_everyone(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VOICE_PERMISSION_OPEN_TO_EVERYONE, callback, Object
        )

    def on_voice_permission_approval_required(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VOICE_PERMISSION_APPROVAL_REQUIRED, callback, Object
        )

    def on_voice_permission_invite_only(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.create_chat_event(
            MessageType.VOICE_PERMISSION_INVITE_ONLY, callback, Object
        )

    def ping_channel(self, timeout: float | None = None):
        return self.send(
            WsMessageType.CHANNEL_USER_PING_REQUEST,
            data=dict(threadChannelUserInfoList=[]),
            timeout=timeout,
        )

    def fetch_channel(
        self, chatId: str, comId: int = 0, timeout: float | None = None
    ) -> Channel:
        return Channel(
            self.send(
                WsMessageType.AGORA_TOKEN_REQUEST,
                data=dict(ndcId=comId, threadId=chatId),
                timeout=timeout,
            )
        )

    def fetch_channel_users(
        self, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.CHANNEL_USER_LIST_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def wait_list_clean(
        self, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.CHANNEL_WAIT_LIST_CLEAN_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def wait_list_join_approve(
        self, userId: str, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_APPROVE_REQUEST,
            data=dict(ndcId=comId, threadId=chatId, uid=userId),
            timeout=timeout,
        )

    def wait_list_join_cancel(
        self, userId: str, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_CANCEL_REQUEST,
            data=dict(ndcId=comId, threadId=chatId, uid=userId),
            timeout=timeout,
        )

    def wait_list_join(self, chatId: str, comId: int = 0, timeout: float | None = None):
        return self.send(
            WsMessageType.CHANNEL_WAIT_LIST_JOIN_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def join_channel(self, chatId: str, comId: int = 0, timeout: float | None = None):
        return self.send(
            WsMessageType.CHANNEL_JOIN_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def leave_channel(self, chatId: str, comId: int = 0, timeout: float | None = None):
        return self.send(
            WsMessageType.CHANNEL_LEAVE_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def remove_voice_participant(
        self, userId: str, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.CHANNEL_FORCE_UPDATE_USER_ROLE_REQUEST,
            data=dict(
                ndcId=comId,
                threadId=chatId,
                joinRole=ChannelJoinRole.AUDIENCE,
                targetUid=userId,
            ),
            timeout=timeout,
        )

    def update_join_role(
        self,
        joinRole: ChannelJoinRole | int,
        chatId: str,
        comId: int = 0,
        timeout: float | None = None,
    ):
        return self.send(
            WsMessageType.CHANNEL_UPDATE_JOIN_ROLE_REQUEST,
            data=dict(ndcId=comId, threadId=chatId, joinRole=joinRole),
            timeout=timeout,
        )

    def update_channel_type(
        self,
        channelType: ChannelType | int,
        chatId: str,
        comId: int = 0,
        timeout: float | None = None,
    ):
        return self.send(
            WsMessageType.CHANNEL_UPDATE_REQUEST,
            data=dict(ndcId=comId, threadId=chatId, channelType=channelType),
            timeout=timeout,
        )

    def send_message_ack(
        self,
        chatId: str,
        messageId: str,
        createdTime: str,
        markHasRead: bool = False,
        comId: int = 0,
    ):
        self.send(
            WsMessageType.CHAT_MESSAGE_ACK_DTO,
            data=dict(
                ndcId=comId,
                threadId=chatId,
                messageId=messageId,
                markHasRead=markHasRead,
                createdTime=createdTime,
            ),
        )

    def fetch_play_list(
        self, chatId: str, comId: int = 0, timeout: float | None = None
    ):
        return self.send(
            WsMessageType.SCREEN_ROOM_PLAY_LIST_REQUEST,
            data=dict(ndcId=comId, threadId=chatId),
            timeout=timeout,
        )

    def update_play_list(
        self,
        chatId: str,
        playlist: PlayList,
        comId: int = 0,
        timeout: float | None = None,
    ):
        return self.send(
            WsMessageType.SCREEN_ROOM_PLAY_LIST_UPDATE_REQUEST,
            data=dict(ndcId=comId, threadId=chatId, playlist=playlist.to_json()),
            timeout=timeout,
        )

    def subscribe_topic(
        self,
        topic: LiveLayerTopic | str,
        objectId: str | None = None,
        comId: int = 0,
        timeout: float | None = None,
    ):
        self.send(
            WsMessageType.LIVE_LAYER_SUBSCRIBE_REQUEST,
            data=dict(ndcId=comId, topic=build_ndtopic(topic, objectId, comId)),
            timeout=timeout,
        )

    def unsubscribe_topic(
        self,
        topic: LiveLayerTopic | str,
        objectId: str | None = None,
        comId: int = 0,
        timeout: float | None = None,
    ):
        self.send(
            WsMessageType.LIVE_LAYER_UNSUBSCRIBE_REQUEST,
            data=dict(ndcId=comId, topic=build_ndtopic(topic, objectId, comId)),
            timeout=timeout,
        )

    def browsing(
        self, comId: int, path: str, params: JsonDict | None = None
    ) -> LiveLayerReport:
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(path, comId),
            actions=[LiveLayerAction.BROWSING],
            params=params,
        )

    def browsing_blog(self, comId: int, blogId: str, blogType: int) -> LiveLayerReport:
        return self.browsing(
            comId=comId,
            path=urljoin(objectTypeName(ObjectType.BLOG), blogId),
            params=dict(blogType=blogType),
        )

    def browsing_profile(self, comId: int, userId: str) -> LiveLayerReport:
        return self.browsing(
            comId=comId,
            path=urljoin(objectTypeName(ObjectType.USER), userId),
            params=None,
        )

    def browsing_comments(
        self, comId: int, objectId: str, objectType: int
    ) -> LiveLayerReport:
        return self.browsing(
            comId=comId,
            path=f"comment-list?parent-type={objectType}&parent-id={objectId}",
            params=None,
        )

    def browsing_featured(self, comId: int) -> LiveLayerReport:
        return self.browsing(comId=comId, path="featured", params=None)

    def chatting(
        self,
        comId: int,
        chatId: str,
        chatType: int,
        membershipStatus: int = ChatMembership.JOINED,
    ) -> LiveLayerReport:
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(
                urljoin(objectTypeName(ObjectType.CHAT), chatId), comId
            ),
            actions=[LiveLayerAction.CHATTING],
            params=dict(threadType=chatType, membershipStatus=membershipStatus),
        )

    def commenting(self, comId: int, objectType: int, objectId: str) -> LiveLayerReport:
        # experimental
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(urljoin(objectTypeName(objectType), objectId), comId),
            actions=[LiveLayerAction.COMMENTING],
            params=None,
        )

    def polling(self, comId: int, pollId: str) -> LiveLayerReport:
        # experimental
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(
                urljoin(objectTypeName(ObjectType.BLOG), pollId), comId
            ),
            actions=[LiveLayerAction.POLLING],
            params=dict(blogType=BlogType.POLL),
        )

    def voting(self, comId: int, objectType: int, objectId: str) -> LiveLayerReport:
        # experimental
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(urljoin(objectTypeName(objectType), objectId), comId),
            actions=[LiveLayerAction.VOTING],
            params=None,
        )

    def playing(self, comId: int, quizId: str) -> LiveLayerReport:
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(
                urljoin(objectTypeName(ObjectType.BLOG), quizId), comId
            ),
            actions=[LiveLayerAction.PLAYING],
            params=dict(blogType=BlogType.QUIZ),
        )

    def recording(
        self, comId: int, chatId: str, chatType: ChatType | int
    ) -> LiveLayerReport:
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(
                urljoin(objectTypeName(ObjectType.CHAT), chatId), comId
            ),
            actions=[LiveLayerAction.RECORDING],
            params=dict(threadType=chatType),
        )

    def typing(
        self, comId: int, chatId: str, chatType: ChatType | int
    ) -> LiveLayerReport:
        return LiveLayerReport(
            ws=self,
            comId=comId,
            target=build_target(
                urljoin(objectTypeName(ObjectType.CHAT), chatId), comId
            ),
            actions=[LiveLayerAction.TYPING],
            params=dict(threadType=chatType),
        )


class WSSubClient(WSBase):
    @property
    @abc.abstractmethod
    def comId(self) -> int: ...
    @property
    @abc.abstractmethod
    def client(self) -> WSClient: ...

    @property
    def ws(self) -> websocket.WebSocket | None:
        return self.client.ws

    @property
    def connected(self) -> bool:
        return self.client.connected

    @property
    def ws_listeners(self) -> dict[str, WsEventListener]:
        return self.client.ws_listeners

    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[True],
        timeout: float | None = None,
    ) -> None: ...
    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: typing.Literal[False] = False,
        timeout: float | None = None,
    ) -> JsonDict: ...
    @typing.overload
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None: ...
    def send(
        self,
        requestType: WsMessageType,
        data: JsonDict,
        ignoreResponse: bool = False,
        timeout: float | None = None,
    ) -> JsonDict | None:
        return self.client.send(
            requestType=requestType,
            data=data,
            ignoreResponse=ignoreResponse,
            timeout=timeout,
        )

    def on_channel_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_message(callback)

    def on_notification_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_notification_message(callback)

    def on_error_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_error_message(callback)

    def on_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_error(callback)

    def on_user_banned_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_user_banned_error(callback)

    def on_multi_device_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_multi_device_error(callback)

    def on_channel_membership_banned_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_membership_banned_error(callback)

    def on_channel_not_available_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_not_available_error(callback)

    def on_channel_no_presenter_error(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_no_presenter_error(callback)

    def on_channel_status_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_status_changed(callback)

    def on_channel_member_status_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_member_status_changed(callback)

    def on_channel_force_quit(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_force_quit(callback)

    def on_wait_list_approve(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_wait_list_approve(callback)

    def on_wait_list_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_wait_list_changed(callback)

    def on_channel_member_join(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_member_join(callback)

    def on_channel_member_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_member_left(callback)

    def on_channel_organizer_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_channel_organizer_left(callback)

    def on_voice_participant_force_removed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_participant_force_removed(callback)

    # chat message events
    def on_chat_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_message(callback)

    def on_text_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_text_message(callback)

    def on_strike_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_strike_message(callback)

    def on_voice_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_message(callback)

    def on_sticker_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_sticker_message(callback)

    def on_video_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_message(callback)

    def on_shared_exurl_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_shared_exurl_message(callback)

    def on_shared_user_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_shared_user_message(callback)

    def on_timestamp_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_timestamp_message(callback)

    def on_welcome_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_welcome_message(callback)

    def on_deleted_message_by_mod(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_deleted_message_by_mod(callback)

    def on_deleted_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_deleted_message(callback)

    def on_forced_deleted_message(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_forced_deleted_message(callback)

    def on_voice_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call(callback)

    def on_voice_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call_start(callback)

    def on_voice_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call_no_answered(callback)

    def on_voice_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call_cancelled(callback)

    def on_voice_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call_declined(callback)

    def on_voice_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_call_end(callback)

    def on_video_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call(callback)

    def on_video_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call_start(callback)

    def on_video_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call_no_answered(callback)

    def on_video_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call_cancelled(callback)

    def on_video_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call_declined(callback)

    def on_video_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_video_call_end(callback)

    def on_avatar_call(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call(callback)

    def on_avatar_call_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call_start(callback)

    def on_avatar_call_no_answered(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call_no_answered(callback)

    def on_avatar_call_cancelled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call_cancelled(callback)

    def on_avatar_call_declined(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call_declined(callback)

    def on_avatar_call_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_avatar_call_end(callback)

    def on_screen_room(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        event = self.create_event(callback, Object)
        self.on_screen_room_start(event)
        self.on_screen_room_end(event)
        return event

    def on_screen_room_start(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_screen_room_start(callback)

    def on_screen_room_end(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_screen_room_end(callback)

    def on_chat_member_join(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_member_join(callback)

    def on_chat_member_left(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_member_left(callback)

    def on_chat_created(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_created(callback)

    def on_chat_removed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_removed(callback)

    def on_chat_invite(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_invite(callback)

    def on_chat_edited(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.on_chat_edited(callback)

    def on_chat_background_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_background_changed(callback)

    def on_chat_title_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_title_changed(callback)

    def on_chat_icon_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_icon_changed(callback)

    def on_chat_content_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_content_changed(callback)

    def on_chat_host_transferred(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_host_transferred(callback)

    def on_chat_tip(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_tip(callback)

    def on_chat_tip_permission_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_tip_permission_changed(callback)

    def on_chat_tip_permission_enabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_tip_permission_enabled(callback)

    def on_chat_tip_permission_disabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_tip_permission_disabled(callback)

    def on_chat_announcement_pinned(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_announcement_pinned(callback)

    def on_chat_announcement_unpinned(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_announcement_unpinned(callback)

    def on_chat_view_only_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_view_only_changed(callback)

    def on_chat_view_only_enabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_view_only_enabled(callback)

    def on_chat_view_only_disabled(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_chat_view_only_disabled(callback)

    def on_voice_permission_changed(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_permission_changed(callback)

    def on_voice_permission_open_to_everyone(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_permission_open_to_everyone(callback)

    def on_voice_permission_approval_required(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_permission_approval_required(callback)

    def on_voice_permission_invite_only(
        self, callback: EventCallback[Object] | Event[Object]
    ) -> Event[Object]:
        return self.client.on_voice_permission_invite_only(callback)

    def ping_channel(self):
        return self.client.ping_channel()

    def fetch_channel(self, chatId: str):
        return self.client.fetch_channel(chatId=chatId, comId=self.comId)

    def fetch_channel_users(self, chatId: str):
        return self.client.fetch_channel_users(chatId=chatId, comId=self.comId)

    def wait_list_clean(self, chatId: str):
        return self.client.wait_list_clean(chatId=chatId, comId=self.comId)

    def wait_list_join_approve(self, userId: str, chatId: str):
        return self.client.wait_list_join_approve(
            userId=userId, chatId=chatId, comId=self.comId
        )

    def wait_list_join_cancel(self, userId: str, chatId: str):
        return self.client.wait_list_join_cancel(
            userId=userId, chatId=chatId, comId=self.comId
        )

    def wait_list_join(self, chatId: str):
        return self.client.wait_list_join(chatId=chatId, comId=self.comId)

    def join_channel(self, chatId: str):
        return self.client.join_channel(chatId=chatId, comId=self.comId)

    def leave_channel(self, chatId: str):
        return self.client.leave_channel(chatId=chatId, comId=self.comId)

    def remove_voice_participant(self, userId: str, chatId: str):
        return self.client.remove_voice_participant(
            userId=userId, chatId=chatId, comId=self.comId
        )

    def update_join_role(self, joinRole: ChannelJoinRole | int, chatId: str):
        return self.client.update_join_role(
            joinRole=joinRole, chatId=chatId, comId=self.comId
        )

    def update_channel_type(self, channelType: ChannelType | int, chatId: str):
        return self.client.update_channel_type(
            channelType=channelType, chatId=chatId, comId=self.comId
        )

    def send_message_ack(
        self, chatId: str, messageId: str, createdTime: str, markHasRead: bool = False
    ):
        return self.client.send_message_ack(
            chatId=chatId,
            messageId=messageId,
            createdTime=createdTime,
            markHasRead=markHasRead,
            comId=self.comId,
        )

    def fetch_play_list(self, chatId: str):
        return self.client.fetch_play_list(chatId=chatId, comId=self.comId)

    def update_play_list(self, chatId: str, playlist: PlayList):
        return self.client.update_play_list(
            chatId=chatId, playlist=playlist, comId=self.comId
        )

    def subscribe_topic(
        self, topic: LiveLayerTopic | str, objectId: str | None = None
    ) -> None:
        return self.client.subscribe_topic(topic, objectId, comId=self.comId)

    def unsubscribe_topic(
        self, topic: LiveLayerTopic | str, objectId: str | None = None
    ):
        return self.client.unsubscribe_topic(topic, objectId, comId=self.comId)

    def browsing(self, path: str, params: JsonDict | None = None) -> LiveLayerReport:
        return self.client.browsing(comId=self.comId, path=path, params=params)

    def browsing_blog(self, blogId: str, blogType: int) -> LiveLayerReport:
        return self.client.browsing_blog(
            comId=self.comId, blogId=blogId, blogType=blogType
        )

    def browsing_profile(self, userId: str) -> LiveLayerReport:
        return self.client.browsing_profile(comId=self.comId, userId=userId)

    def browsing_comments(self, objectId: str, objectType: int) -> LiveLayerReport:
        return self.client.browsing_comments(
            comId=self.comId, objectId=objectId, objectType=objectType
        )

    def browsing_featured(self, comId: int) -> LiveLayerReport:
        return self.client.browsing_featured(comId=comId)

    def chatting(
        self, chatId: str, chatType: int, membershipStatus: int = ChatMembership.JOINED
    ) -> LiveLayerReport:
        return self.client.chatting(
            comId=self.comId,
            chatId=chatId,
            chatType=chatType,
            membershipStatus=membershipStatus,
        )

    def commenting(self, objectType: int, objectId: str) -> LiveLayerReport:
        return self.client.commenting(
            comId=self.comId, objectType=objectType, objectId=objectId
        )

    def polling(self, pollId: str) -> LiveLayerReport:
        return self.client.polling(comId=self.comId, pollId=pollId)

    def voting(self, objectType: int, objectId: str) -> LiveLayerReport:
        return self.client.voting(
            comId=self.comId, objectType=objectType, objectId=objectId
        )

    def playing(self, quizId: str) -> LiveLayerReport:
        return self.client.playing(comId=self.comId, quizId=quizId)

    def recording(self, chatId: str, chatType: ChatType | int) -> LiveLayerReport:
        return self.client.recording(comId=self.comId, chatId=chatId, chatType=chatType)

    def typing(self, chatId: str, chatType: ChatType | int) -> LiveLayerReport:
        return self.client.typing(comId=self.comId, chatId=chatId, chatType=chatType)
