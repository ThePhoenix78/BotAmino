from __future__ import annotations

import time
import typing

from .client import Client
from .http import HTTPClient
from .typing import Proxies
from .types import ValidationType

__all__ = ("ACM",)


class ACM(HTTPClient):
    @property
    def comId(self) -> int:
        return getattr(self, "_comId")

    @comId.setter
    def comId(self, value: int) -> None:
        setattr(self, "_comId", value)

    def __init__(
        self,
        comId: int,
        *,
        client: Client,
        deviceId: str | None = None,
        smdeviceId: str | None = None,
        proxies: Proxies | None = None,
        certificatePath: str | None = None,
        agent: str | None = None,
        language: str | None = None,
        timeout: float | None = None,
        timezone: int | None = None,
    ) -> None:
        super().__init__(
            deviceId=deviceId or client.deviceId,
            smdeviceId=smdeviceId or client.smdeviceId,
            proxies=proxies or client.proxies,
            certificatePath=certificatePath if proxies else client.certificatePath,
            agent=agent or client.agent,
            language=language or client.language,
            timeout=timeout or client.timeout,
            timezone=timezone or client.timezone,
        )
        self.comId = comId

    def create_community(
        self,
        name: str,
        tagline: str,
        icon: typing.BinaryIO | str,
        themeColor: str,
        joinType: int = 0,
        primaryLanguage: str = "en",
    ):
        if not isinstance(icon, str):
            icon = self.upload_media(icon, "image")
        return self.request(
            "POST",
            "community",
            data=dict(
                icon=dict(
                    height=512.0,
                    width=512.0,
                    imageMatrix=[1.6875, 0.0, 108.0, 0.0, 1.6875, 497.0, 0.0, 0.0, 1.0],
                    path=icon,
                    x=0.0,
                    y=0.0,
                ),
                joinType=joinType,
                name=name,
                primaryLanguage=primaryLanguage,
                tagline=tagline,
                templateId=9,
                themeColor=themeColor,
                timestamp=int(time.time() * 1000),
            ),
        )

    def delete_community(self, email: str, password: str, verificationCode: str):
        return self.request(
            "POST",
            "community/delete-request",
            data=dict(
                secret=f"0 {password}",
                validationContext=dict(
                    data=dict(code=verificationCode),
                    type=ValidationType.EMAIL,
                    identity=email,
                ),
                deviceID=self.deviceId,
            ),
            comId=self.comId,
            scope=True,
        )

    def list_communities(self, start: int = 0, size: int = 25):
        return self.request(
            "GET", "community/managed", params=dict(start=start, size=size)
        )

    def get_categories(self, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            "blog-category",
            params=dict(start=start, size=size),
            comId=self.comId,
        )

    def change_sidepanel_color(self, color: str):
        return self.request(
            "POST",
            "community/configuration",
            data=dict(
                path="appearance.leftSidePanel.style.iconColor",
                value=color,
                timestamp=int(time.time() * 1000),
            ),
            comId=self.comId,
        )

    def upload_themepack_raw(self, file: typing.BinaryIO):
        return self.request(
            "POST",
            "media/upload/target/community-theme-pack",
            data=file.read(),
            comId=self.comId,
        )

    def promote(self, userId: str, rank: typing.Literal["agent", "curator", "leader"]):
        fpath = rank.replace("agent", "transfer-agent")
        return self.request("POST", f"user-profile/{userId}/{fpath}", comId=self.comId)

    def get_join_requests(self, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            f"community/membership-request",
            params=dict(status="pending", start=start, size=size),
            comId=self.comId,
        )

    def accept_join_request(self, userId: str):
        return self.request(
            "POST",
            f"community/membership-request/{userId}/accept",
            data=dict(timestamp=int(time.time() * 1000)),
            comId=self.comId,
        )

    def reject_join_request(self, userId: str):
        return self.request(
            "POST",
            f"community/membership-request/{userId}/reject",
            data=dict(timestamp=int(time.time() * 1000)),
            comId=self.comId,
        )

    def get_community_stats(self):
        self.request(
            "GET",
            f"community/stats",
            data=dict(timestamp=int(time.time() * 1000)),
            comId=self.comId,
        )

    def get_community_user_stats(
        self, type: typing.Literal["curator", "leader"], start: int = 0, size: int = 25
    ):
        return self.request(
            "GET",
            "community/stats/moderation",
            params=dict(type=type, start=start, size=size),
            comId=self.comId,
        )

    def change_welcome_message(
        self, message: str | None = None, isEnabled: bool = True
    ):
        return self.request(
            "POST",
            "community/configuration",
            data=dict(
                path="general.welcomeMessage",
                value=dict(enabled=isEnabled, text=message),
                timestamp=int(time.time() * 1000),
            ),
            comId=self.comId,
        )

    def change_guidelines(self, message: str):
        return self.request(
            "POST",
            f"community/guideline",
            data=dict(content=message, timestamp=int(time.time() * 1000)),
            comId=self.comId,
        )

    def edit_community(
        self,
        name: str | None = None,
        description: str | None = None,
        aminoId: str | None = None,
        primaryLanguage: str | None = None,
        themePackUrl: str | None = None,
    ):
        data: typing.Dict[str, typing.Any] = dict(timestamp=int(time.time() * 1000))
        if name:
            data.update(name=name)
        if description:
            data.update(content=description)
        if aminoId:
            data.update(endpoint=aminoId)
        if primaryLanguage:
            data.update(primaryLanguage=primaryLanguage)
        if themePackUrl:
            data.update(themePackUrl=themePackUrl)
        return self.request("POST", "community/settings", data=data, comId=self.comId)

    def change_module(
        self,
        module: typing.Literal[
            "catalog",
            "chat",
            "externalcontent",
            "featured",
            "featuredchats",
            "featuredposts",
            "featuredusers",
            "influencer",
            "leaderboards",
            "livechat",
            "posts",
            "publicchats",
            "ranking",
            "sharedfolder",
            "screeningroom",
            "topiccategories",
        ],
        isEnabled: bool,
    ):
        fullpath = {
            "chat": "module.chat.enabled",
            "livechat": "module.chat.avChat.videoEnabled",
            "screeningroom": "module.chat.avChat.screeningRoomEnabled",
            "publicchats": "module.chat.publicChat.enabled",
            "posts": "module.post.enabled",
            "ranking": "module.ranking.enabled",
            "leaderboards": "module.ranking.leaderboardEnabled",
            "featured": "module.featured.enabled",
            "featuredposts": "module.featured.postEnabled",
            "featuredusers": "module.featured.memberEnabled",
            "featuredchats": "module.featured.publicChatRoomEnabled",
            "sharedfolder": "module.sharedFolder.enabled",
            "influencer": "module.influencer.enabled",
            "catalog": "module.catalog.enabled",
            "externalcontent": "module.externalContent.enabled",
            "topiccategories": "module.topicCategories.enabled",
        }.get(module)
        if not fullpath:
            raise ValueError("Invalid module %r" % module)
        return self.request(
            "POST",
            f"community/configuration",
            data=dict(
                path=fullpath, value=isEnabled, timestamp=int(time.time() * 1000)
            ),
            comId=self.comId,
        )

    def add_influencer(self, userId: str, monthlyFee: int):
        return self.request(
            "POST",
            f"influencer/{userId}",
            data=dict(monthlyFee=monthlyFee, timestamp=int(time.time() * 1000)),
            comId=self.comId,
        )

    def remove_influencer(self, userId: str):
        return self.request("DELETE", f"influencer/{userId}", comId=self.comId)

    def get_notice_list(self, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            "notice",
            params=dict(type="management", status=1, start=start, size=size),
            comId=self.comId,
        )

    def delete_pending_role(self, noticeId: str):
        return self.request("DELETE", f"notice/{noticeId}", comId=self.comId)
