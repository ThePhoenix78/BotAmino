import base64
import time
import typing
import typing_extensions
from .client import Client
from .http import HTTPClient
from .objects import (
    APIResponse,
    Account,
    ChatMemberResponse,
    Community,
    Thread,
    ThreadListResponse,
    ThreadMemberResponse,
    ThreadList,
    ThreadResponse,
    UserProfile,
    UserProfileListResponse,
    UserProfileLiteList,
    UserProfileResponse
)
from .types import APILiveLayerTopic, BlogType, ContentType, MessageType, ObjectType, PaymentType
from .typing import FileTypeInput, Proxies
from .utils import build_uuid, currentTimeMillis
from .ws import WSSubClient

__all__ = ("SubClient",)


class SubClient(HTTPClient, WSSubClient):
    @property
    def comId(self) -> int:
        return getattr(self, "_comId")

    @comId.setter
    def comId(self, value: int) -> None:
        setattr(self, "_comId", value)

    @property
    def community(self) -> Community:
        return getattr(self, "_community")

    @community.setter
    def community(self, value: Community) -> None:
        setattr(self, "_community", value)

    @property
    def client(self) -> Client:
        return getattr(self, "_client")

    @client.setter
    def client(self, value: Client) -> None:
        setattr(self, "_client", value)

    @property
    def account(self) -> Account:
        return self.client.account

    @account.setter
    def account(self, value: Account) -> None:
        self.client.account = value

    @property  # type: ignore
    def userId(self) -> str:
        return self.auid

    @userId.setter
    def userId(self, value: typing.Optional[str]) -> None:
        self.auid = value  # type: ignore

    @property  # type: ignore
    def auid(self) -> str:
        return getattr(self, "_auid")

    @auid.setter
    def auid(self, value: typing.Optional[str]) -> None:
        setattr(self, "_auid", value)

    def __init__(
        self,
        comId: typing.Optional[int] = None,
        aminoId: typing.Optional[str] = None,
        *,
        client: Client,
        deviceId: typing.Optional[str] = None,
        smdeviceId: typing.Optional[str] = None,
        proxies: typing.Optional[Proxies] = None,
        certificatePath: typing.Optional[str] = None,
        agent: typing.Optional[str] = None,
        language: typing.Optional[str] = None,
        timeout: typing.Optional[float] = None,
        timezone: typing.Optional[int] = None
    ) -> None:
        super().__init__(
            deviceId=deviceId or client.deviceId,
            smdeviceId=smdeviceId or client.smdeviceId,
            proxies=proxies or client.proxies,
            certificatePath=certificatePath if proxies else client.certificatePath,
            agent=agent or client.agent,
            language=language or client.language,
            timeout=timeout or client.timeout,
            timezone=timezone or client.timezone
        )
        self.client = client
        self.auid = typing.cast(str, client.auid)
        self.userId = typing.cast(str, client.userId)
        self.sid = client.sid
        if comId:
            self.comId = comId
        elif aminoId:
            link = "http://aminoapps.com/c/"
            self.comId = self.get_from_link(link + aminoId).comId
        else:
            raise ValueError("SubClient require comId or aminoId argument")
        self.community = self.get_community_info(self.comId).community
        self.profile = self.get_user_info(userId=self.profile.userId)

    def get_live_public_channels(self):
        return self.request("GET", "live-layer/public-vv-chats", comId=self.comId)

    def get_live_public_chats(self):
        return self.request("GET", "live-layer/public-chats", comId=self.comId)

    def get_live_layer(self, topic: typing.Union[APILiveLayerTopic, str] = APILiveLayerTopic.HOMEPAGE):
        return self.request("GET", "live-layer/" + topic, params=dict(v=2), comId=self.comId)

    def search_chat_member(self, chatId: str, q: str) -> UserProfileLiteList:
        return ChatMemberResponse(self.request("GET", f"chat/thread/{chatId}/member", params=dict(q=q, type="at"), comId=self.comId)).members

    def search_chat(self, q: str):
        return self.request("GET", "chat/thread", params=dict(
            type="public-keyword",
            q=q
        ), comId=self.comId)

    def search_joined_chats(self, q: str):
        return self.request("GET", "chat/thread", params=dict(
            q=q,
            action=0
        ), comId=self.comId)

    def get_live_layer_topic(self, ndtopic: str, start: int = 0, size: int = 25):
        # param stoptime: str
        return self.request("GET", "live-layer", params=dict(
            topic=ndtopic,
            start=start,
            size=size
        ), comId=self.comId)

    def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
        return self.request("GET", "community/invitation", params=dict(
            status=status,
            start=start,
            size=size
        ), comId=self.comId, scope=True)

    def generate_invite_code(self, duration: int = 0, force: bool = True):
        return self.request("POST", "community/invitation", data=dict(
            duration=duration,
            force=force,
            timestamp=currentTimeMillis()
        ), comId=self.comId, scope=True)

    def delete_invite_code(self, inviteId: str):
        return self.request("DELETE", "community/invitation/{inviteId}", comId=self.comId, scope=True)

    def get_vip_users(self):
        return self.request("GET", "influencer", comId=self.comId)

    def repost(self, content: typing.Optional[str] = None, blogId: typing.Optional[str] = None, wikiId: typing.Optional[str] = None):
        return self.request("POST", "blog", data=dict(
            content=content,
            refObjectId=blogId or wikiId,
            refObjectType=ObjectType.BLOG if blogId else ObjectType.WIKI,
            type=BlogType.REPOST,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def post_blog(
        self,
        title: str,
        content: str,
        imageList: typing.Optional[typing.List[typing.BinaryIO]] = None,
        captionList: typing.Optional[typing.List[typing.Optional[str]]] = None,
        categoriesList: typing.Optional[typing.List[str]] = None,
        backgroundColor: typing.Optional[str] = None,
        fansOnly: bool = False
    ):
        mediaList: typing.List[typing.List[typing.Any]] = []
        extensions: typing.Dict[str, typing.Any] = {}
        if captionList and imageList:
            for image, caption in zip(imageList, captionList):
                mediaList.append([ObjectType.IMAGE, self.upload_media(image, "image"), caption])
        elif imageList:
            for image in imageList:
                mediaList.append([ObjectType.IMAGE, self.upload_media(image, "image"), None])
        data: typing.Dict[str, typing.Any] = dict(
            address=None,
            content=content,
            eventSource="GlobalComposeMenu",
            extensions=extensions,
            latitude=0,
            longitude=0,
            mediaList=mediaList,
            taggedBlogCategoryIdList=categoriesList,
            timestamp=currentTimeMillis(),
            title=title
        )
        if fansOnly:
            extensions["fansOnly"]= fansOnly
        if backgroundColor:
            extensions["style"]= {"backgroundColor": backgroundColor}
        return self.request("POST", "blog", data=data, comId=self.comId)

    def edit_blog(
        self,
        blogId: str,
        title: typing.Optional[str] = None,
        content: typing.Optional[str] = None,
        imageList: typing.Optional[typing.List[typing.BinaryIO]] = None,
        categoriesList: typing.Optional[typing.List[str]] = None,
        backgroundColor: typing.Optional[str] = None,
        fansOnly: bool = False
    ):
        mediaList: typing.Optional[typing.List[typing.List[typing.Any]]] = None
        extensions: typing.Dict[str, typing.Any] = {}
        if imageList:
            mediaList = [[ObjectType.IMAGE, self.upload_media(image, "image"), None] for image in imageList]
        data: typing.Dict[str, typing.Any] = dict(
            address=None,
            mediaList=mediaList,
            latitude=0,
            longitude=0,
            eventSource="PostDetailView",
            timestamp=currentTimeMillis()
        )
        if title:
            data.update(title=title)
        if content:
            data.update(content=content)
        if fansOnly:
            extensions.update(fansOnly=fansOnly)
        if backgroundColor:
            extensions.update(style=dict(backgroundColor=backgroundColor))
        if categoriesList:
            data.update(taggedBlogCategoryIdList=categoriesList)
        if extensions:
            data.update(extensions=extensions)
        return self.request("POST", f"blog/{blogId}", data=data, comId=self.comId)

    def delete_blog(self, blogId: str):
        return self.request("DELETE", f"blog/{blogId}", comId=self.comId)

    def post_wiki(
        self,
        title: str,
        content: str,
        icon: typing.Optional[str] = None,
        imageList: typing.Optional[typing.List[typing.BinaryIO]] = None,
        keywords: typing.Optional[str] = None,
        backgroundColor: typing.Optional[str] = None,
        fansOnly: bool = False
    ):
        mediaList: typing.Optional[typing.List[typing.List[typing.Any]]] = None
        extensions: typing.Dict[str, typing.Any] = {}
        if imageList:
            mediaList = [[ObjectType.IMAGE, self.upload_media(image, "image"), None] for image in imageList]
        data: typing.Dict[str, typing.Any] = dict(
            content=content,
            eventSource="GlobalComposeMenu",
            label=title,
            mediaList=mediaList,
            timestamp=currentTimeMillis()
        )
        if icon:
            data.update(icon=icon)
        if keywords:
            data.update(keywords=keywords)
        if fansOnly:
            extensions.update(fansOnly=fansOnly)
        if backgroundColor:
            extensions.update(style=dict(backgroundColor=backgroundColor))
        if extensions:
            data.update(extensions=extensions)
        return self.request("POST", "item", data=data, comId=self.comId)

    def delete_wiki(self, wikiId: str):
        return self.request("DELETE", f"item/{wikiId}", comId=self.comId)

    def check_in(self, timezone: typing.Optional[int] = None):
        return self.request("POST", f"check-in", data=dict(
            timezone=timezone or self.timezone,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def repair_check_in(self, method: typing.Literal[1, 2] = 1):
        return self.request("POST", f"check-in/repair", data=dict(
            repairMethod=str(method), # 1: coins, 2: amino+
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def lottery(self, timezone: typing.Optional[int] = None):
        return self.request("POST", f"check-in/lottery", data=dict(
            timezone=timezone or self.timezone,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def edit_profile(
        self,
        nickname: typing.Optional[str] = None,
        content: typing.Optional[str] = None,
        icon: typing.Optional[typing.Union[typing.BinaryIO, str]] = None,
        backgroundColor: typing.Optional[str] = None,
        backgroundImage: typing.Optional[typing.Union[typing.BinaryIO, str]] = None,
        defaultBubbleId: typing.Optional[str] = None,
        chatRequestPrivilege: typing.Optional[int] = None,
        wallCommentPrivilege: typing.Optional[int] = None,
        imageList: typing.Optional[typing.List[typing.BinaryIO]] = None,
        captionList: typing.Optional[typing.List[str]] = None,
        titles: typing.Optional[typing.List[str]] = None,
        colors: typing.Optional[typing.List[typing.Optional[str]]] = None
    ) -> UserProfile:
        extensions: typing.Dict[str, typing.Any] = {}
        data: typing.Dict[str, typing.Any] = dict(
            timestamp=currentTimeMillis()
        )
        if captionList and imageList:
            data.update(mediaList=[[100, self.upload_media(image, "image"), caption] for image, caption in zip(imageList, captionList)])
        elif imageList:
            data.update(mediaList=[[100, self.upload_media(image, "image"), None] for image in imageList])
        if nickname:
            data.update(nickname=nickname)
        if icon:
            if not isinstance(icon, str):
                icon = self.upload_media(icon, "image")
            data.update(icon=icon)
        if content:
            data.update(content=content)
        if chatRequestPrivilege:
            extensions.update(privilegeOfChatInviteRequest=chatRequestPrivilege)
        if wallCommentPrivilege:
            extensions.update(privilegeOfCommentOnUserProfile=wallCommentPrivilege)
        if backgroundImage:
            if not isinstance(backgroundImage, str):
                backgroundImage = self.upload_media(backgroundImage, "image")
            extensions.update(style=dict(backgroundMediaList=[[100, backgroundImage, None, None, None]]))
        if backgroundColor:
            extensions.update(style=dict(backgroundColor=backgroundColor))
        if defaultBubbleId:
            extensions.update(defaultBubbleId=defaultBubbleId)
        if titles and colors:
            extensions.update(customTitles=[dict(title=title, color=color) for title, color in zip(titles, colors)])
        if extensions:
            data.update(extensions=extensions)
        response = UserProfileResponse(self.request("POST", f"user-profile/{self.userId}", comId=self.comId))
        self.profile = response.profile
        return response.profile

    def vote_poll(self, blogId: str, optionId: str):
        return self.request("POST", f"blog/{blogId}/poll/option/{optionId}/vote", data=dict(
            value=1,
            eventSource="PostDetailView",
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_poll_voters(self, blogId: str):
        return self.request("GET", f"blog/{blogId}/poll/options-active-voterssummary", comId=self.comId)

    @typing.overload
    def add_poll_option(
        self,
        blogId: str,
        question: str,
    ) -> typing.Any: ...
    @typing.overload
    def add_poll_option(
        self,
        *,
        refObjId: str,
        refObjType: int
    ) -> typing.Any: ...
    def add_poll_option(
        self,
        blogId: typing.Optional[str] = None,
        question: typing.Optional[str] = None,
        refObjId: typing.Optional[str] = None,
        refObjType: typing.Optional[int] = None
    ):
        data = dict(
            mediaList=None,
            title=question,
            type=0,
            timestamp=currentTimeMillis()
        )
        if refObjId and refObjType:
            data.update(type=1, refObjectType=refObjType, refObjectId=refObjId)
        return self.request("POST", f"blog/{blogId}/poll/option", data=data, comId=self.comId)

    def get_poll_options(self, blogId: str):
        return self.request("GET", f"blog/{blogId}/poll/options-joined", comId=self.comId)

    def get_poll_pending_options(self, blogId: str):
        return self.request("GET", f"blog/{blogId}/poll/options-pending", comId=self.comId)

    def approve_poll_option(self, blogId: str, optionId: str):
        return self.request("POST", f"blog/{blogId}/poll/option/{optionId}/settings", data=dict(
            opName=110,
            opValue=0,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def delete_poll_option(self, blogId: str, optionId: str):
        return self.request("DELETE", f"blog/{blogId}/poll/option/{optionId}", comId=self.comId)

    def comment(
        self,
        message: str,
        userId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        replyTo: typing.Optional[str] = None,
        isGuest: bool = False
    ):
        data = dict(
            content=message,
            eventSource="UserProfileView" if userId else "PostDetailView",
            stickerId=None,
            type=0,
            timestamp=currentTimeMillis()
        )
        if replyTo:
            data.update(respondTo=replyTo)
        commentpath = "g-comment" if isGuest else "comment"
        basepath = f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}"
        return self.request("POST", f"{basepath}/{commentpath}", data=data, comId=self.comId)

    def delete_comment(
        self,
        commentId: str,
        userId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        isGuest: bool = False,
        asStaff: bool = False,
        reason: typing.Optional[str] = None
    ):
        method = "POST" if asStaff else "DELETE"
        path = (f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}") + ("g-" if isGuest else "") + f"comment/{commentId}"
        if asStaff:
            path += "/admin"
        return self.request(method, path, data=dict(
            adminOpName=102,
            adminOpNote=reason
        ) if asStaff else None, comId=self.comId)

    def like_wiki(self, wikiId: str):
        return self.request("POST", f"item/{wikiId}/vote", data=dict(
            cv=1.2,
            eventSource="PostDetailView",
            timestamp=currentTimeMillis(),
            value=4
        ), comId=self.comId)

    def unlike_wiki(self, wikiId: str):
        return self.request("DELETE", f"item/{wikiId}/vote", params=dict(eventSource="PostDetailView"), comId=self.comId)

    def like_blog(self, blogId: typing.Union[typing.List[str], str]):
        data: typing.Dict[str, typing.Any] = dict(
            value=4,
            timestamp=currentTimeMillis()
        )
        if isinstance(blogId, str):
            data.update(eventSource="UserProfileView", cv=1.2)
            basepath = f"blog/{blogId}"
        else:
            data.update(targetIdList=blogId)
            basepath = "feed"
        return self.request("POST", f"{basepath}/vote", data=data, comId=self.comId)

    def unlike_blog(self, blogId: str):
        return self.request("DELETE", f"blog/{blogId}/vote", params=dict(eventSource="UserProfileView"), comId=self.comId)

    def like_wall_comment(self, commentId: str, userId: str):
        return self.request("POST", f"user-profile/{userId}/comment/{commentId}/vote", data=dict(
            cv=1.2,
            eventSource="UserProfileView",
            timestamp=currentTimeMillis(),
            value=1
        ), comId=self.comId)

    def like_blog_comment(self, commentId: str, blogId: str):
        return self.request("POST", f"blog/{blogId}/comment/{commentId}/vote", data=dict(
            cv=1.2,
            eventSource="PostDetailView",
            timestamp=currentTimeMillis(),
            value=1
        ), comId=self.comId)

    def like_wiki_comment(self, commentId: str, wikiId: str):
        return self.request("POST", f"item/{wikiId}/comment/{commentId}/g-vote", data=dict(
            cv=1.2,
            eventSource="PostDetailView",
            timestamp=currentTimeMillis(),
            value=1
        ), comId=self.comId)

    def like_comment(self, commentId: str, userId: typing.Optional[str] = None, blogId: typing.Optional[str] = None, wikiId: typing.Optional[str] = None):
        if userId:
            response = self.like_wall_comment(commentId, userId)
        elif blogId:
            response = self.like_blog_comment(commentId, blogId)
        elif wikiId:
            response = self.like_wiki_comment(commentId, wikiId)
        else:
            raise ValueError("argument not provided for userId, blogId or wikiId")
        return response

    def unlike_wall_comment(self, commentId: str, userId: str):
        return self.request("DELETE", f"user-profile/{userId}/comment/{commentId}/g-vote", params=dict(eventSource="UserProfileView"), comId=self.comId)

    def unlike_blog_comment(self, commentId: str, blogId: str):
        return self.request("DELETE", f"blog/{blogId}/comment/{commentId}/g-vote", params=dict(eventSource="PostDetailView"), comId=self.comId)

    def unlike_wiki_comment(self, commentId: str, wikiId: str):
        return self.request("DELETE", f"item/{wikiId}/comment/{commentId}/g-vote", params=dict(eventSource="PostDetailView"), comId=self.comId)

    def unlike_comment(self, commentId: str, userId: typing.Optional[str] = None, blogId: typing.Optional[str] = None, wikiId: typing.Optional[str] = None):
        if userId:
            response = self.unlike_wall_comment(commentId, userId)
        elif blogId:
            response = self.unlike_blog_comment(commentId, blogId)
        elif wikiId:
            response = self.unlike_wiki_comment(commentId, wikiId)
        else:
            raise ValueError("argument not provided for userId, blogId or wikiId")
        return response

    def vote_comment(self, blogId: str, commentId: str, value: typing.Literal[-1, 0, 1]):
        return self.request("POST", f"blog/{blogId}/comment/{commentId}/vote", data=dict(
            cv=1.2,
            eventSource="PostDetailView",
            value=value,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def upvote_comment(self, blogId: str, commentId: str):
        return self.vote_comment(blogId=blogId, commentId=commentId, value=1)

    def downvote_comment(self, blogId: str, commentId: str):
        return self.vote_comment(blogId=blogId, commentId=commentId, value=-1)

    def unvote_comment(self, blogId: str, commentId: str):
        return self.request("DELETE", f"blog/{blogId}/comment/{commentId}/vote", params=dict(eventSource="PostDetailView"), comId=self.comId)

    def send_active_obj(
        self,
        startTime: typing.Optional[int] = None,
        endTime: typing.Optional[int] = None,
        timezone: typing.Optional[int] = None,
        timers: typing.Optional[typing.List[typing.Dict[str, int]]] = None
    ): 
        data: typing.Dict[str, typing.Any] = dict(
            userActiveTimeChunkList=[dict(
                start=startTime,
                end=endTime
            )],
            timestamp=currentTimeMillis(),
            optInAdsFlags=2147483647,
            timezone=timezone or self.timezone
        )
        if timers:
            data.update(userActiveTimeChunkList=timers)
        return self.request("POST", "community/stats/user-active-time", data=data, minify=True, comId=self.comId)

    def change_mood_sticker(self, stickerId: typing.Optional[str] = None):
        return self.request("POST", f"user-profile/{self.userId}/online-status", data=dict(
            moodStickerId=stickerId,
            timestamp=currentTimeMillis()
        ))

    def activity_status(self, status: typing.Literal["on", "off"]):
        return self.request("POST", f"user-profile/{self.profile.userId}/online-status", data=dict(
            duration=86400,
            onlineStatus=1 if status == "on" else 2,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def check_notifications(self):
        return self.request("POST", "notification/checked", comId=self.comId)

    def delete_notification(self, notificationId: str):
        return self.request("DELETE", f"notification/{notificationId}", comId=self.comId)

    def clear_notifications(self):
        return self.request("DELETE", "notification", comId=self.comId)

    def start_chat(
        self,
        userId: typing.Optional[typing.Union[typing.Iterable[str], str]] = None,
        message: typing.Optional[str] = None,
        title: typing.Optional[str] = None,
        content: typing.Optional[str] = None,
        chatType: int = 0,
        isGlobal: bool = False,
        publishToGlobal: bool = False
    ):
        inviteUids = [userId] if isinstance(userId, str) else list(userId) if userId else None
        data = dict(
            title=title,
            inviteeUids=inviteUids,
            initialMessageContent=message,
            content=content,
            publishToGlobal=int(publishToGlobal),
            type=chatType,
            timestamp=currentTimeMillis()
        )
        if isGlobal:
            data.update(eventSource="GlobalComposeMenu", type=2)
        return self.request("POST", "chat/thread", data=data, comId=self.comId)

    def invite_to_chat(self, userId: typing.Union[typing.List[str], str], chatId: str):
        return self.request("POST", f"chat/thread/{chatId}/member/invite", data=dict(
            uids=[userId] if isinstance(userId, str) else userId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def add_to_favorites(self, userId: str):
        return self.request("POST", f"user-group/quick-access/{userId}", comId=self.comId)

    def tip_blog(self, coins: int, blogId: str, transactionId: typing.Optional[str] = None):
        if not transactionId:
            transactionId = build_uuid()
        return self.request("POST", f"blog/{blogId}/tipping", data=dict(
            coins=coins,
            tippingContext=dict(transactionId=transactionId),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def tip_chat(self, coins: int, chatId: str, transactionId: typing.Optional[str] = None):
        if not transactionId:
            transactionId = build_uuid()
        return self.request("POST", f"chat/thread/{chatId}/tipping", data=dict(
            coins=coins,
            tippingContext=dict(transactionId=transactionId),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def tip_wiki(self, coins: int, wikiId: str, transactionId: typing.Optional[str] = None):
        if not transactionId:
            transactionId = build_uuid()
        return self.request("POST", "tipping", data=dict(
            coins=coins,
            objectId=wikiId,
            objectType=2,
            tippingContext=dict(transactionId=transactionId),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def send_coins(self, coins: int, blogId: typing.Optional[str] = None, chatId: typing.Optional[str] = None, objectId: typing.Optional[str] = None, transactionId: typing.Optional[str] = None):
        if blogId:
            response = self.tip_blog(coins, blogId=blogId, transactionId=transactionId)
        elif chatId:
            response = self.tip_chat(coins, chatId=chatId, transactionId=transactionId)
        elif objectId:
            response = self.tip_wiki(coins, wikiId=objectId, transactionId=transactionId)
        else:
            raise ValueError("argument not provided for userId, blogId or wikiId")
        return response

    def thank_tip(self, chatId: str, userId: str):
        return self.request("POST", f"chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", comId=self.comId)

    def follow_users(self, userIds: typing.Iterable[str]):
        return self.request("POST", f"user-profile/{self.profile.userId}/joined", data=dict(
            targetUidList=list(userIds),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def follow(self, userId: str):
        return self.request("POST", f"user-profile/{userId}/member", comId=self.comId)

    def unfollow(self, userId: str):
        return self.request("DELETE", f"user-profile/{self.profile.userId}/joined/{userId}", comId=self.comId)

    def block(self, userId: str):
        return self.request("POST", f"block/{userId}", comId=self.comId)

    def unblock(self, userId: str):
        return self.request("DELETE", f"block/{userId}", comId=self.comId)

    def visit(self, userId: str):
        return self.request("GET", f"user-profile/{userId}", params=dict(action="visit"), comId=self.comId)

    def flag(
        self,
        reason: str,
        flagType: int,
        userId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        asGuest: bool = False
    ):
        return self.request("POST", "g-flag" if asGuest else "flag", data=dict(
            flagType=flagType,
            message=reason,
            objectId=userId or blogId or wikiId,
            objectType=0 if userId else 1 if blogId else 2,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def cancel_avatar_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.AVATAR_CALL_CANCELLED)

    def cancel_video_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VIDEO_CALL_CANCELLED)

    def cancel_voice_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VOICE_CALL_CANCELLED)

    def decline_avatar_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.AVATAR_CALL_DECLINED)

    def decline_video_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VIDEO_CALL_DECLINED)

    def decline_voice_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VOICE_CALL_DECLINED)

    def not_answer_avatar_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.AVATAR_CALL_NO_ANSWERED)

    def not_answer_video_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VIDEO_CALL_NO_ANSWERED)

    def not_answer_voice_call(self, chatId: str):
        return self.send_message(chatId, messageType=MessageType.VOICE_CALL_NO_ANSWERED)

    def send_text(
        self,
        chatId: str,
        message: str,
        messageType: int = 0,
        replyTo: typing.Optional[str] = None,
        mentionUserIds: typing.Optional[typing.Iterable[str]] = None
    ):
        return self.send_message(
            chatId=chatId,
            message=message,
            messageType=messageType,
            replyTo=replyTo,
            mentionUserIds=mentionUserIds
        )

    def send_embed(
        self,
        chatId: str,
        objectId: str,
        objectType: int,
        link: str,
        title: str,
        content: str,
        image: typing.Union[typing.Iterable[typing.BinaryIO], typing.BinaryIO],
        parentId: typing.Optional[str] = None,
        parentType: typing.Optional[str] = None
    ):
        return self.send_message(
            chatId=chatId,
            embedId=objectId,
            embedType=objectType,
            embedLink=link,
            embedTitle=title,
            embedContent=content,
            embedImage=image,
            embedParentId=parentId,
            embedParentType=parentType  # comment & chat-message
        )

    def send_audio(
        self,
        chatId: str,
        file: typing.BinaryIO
    ):
        return self.send_message(chatId, file=file, fileType="audio")

    def send_image(
        self,
        chatId: str,
        file: typing.BinaryIO
    ):
        return self.send_message(chatId, file=file, fileType="image")

    def send_gif(
        self,
        chatId: str,
        file: typing.BinaryIO
    ):
        return self.send_message(chatId, file=file, fileType="gif")

    def send_sticker(
        self,
        chatId: str,
        stickerId: str
    ):
        return self.send_message(chatId, stickerId=stickerId)

    def send_video(
        self,
        chatId: str,
        video: typing.BinaryIO,
        coverImage: typing.Optional[typing.BinaryIO] = None
    ):
        return self.send_message(chatId, file=video, fileType="video", coverImage=coverImage)

    def send_message(
        self,
        chatId: str,
        message: typing.Optional[str] = None,
        messageType: typing.Union[MessageType, int] = 0,
        file: typing.Optional[typing.BinaryIO] = None,
        fileType: typing.Optional[FileTypeInput] = None,
        coverImage: typing.Optional[typing.BinaryIO] = None,
        replyTo: typing.Optional[str] = None,
        mentionUserIds: typing.Optional[typing.Iterable[str]] = None,
        stickerId: typing.Optional[str] = None,
        embedId: typing.Optional[str] = None,
        embedType: typing.Optional[int] = None,
        embedLink: typing.Optional[str] = None,
        embedTitle: typing.Optional[str] = None,
        embedContent: typing.Optional[str] = None,
        embedImage: typing.Optional[typing.Union[typing.Iterable[typing.BinaryIO], typing.BinaryIO]] = None,
        embedParentId: typing.Optional[str] = None,
        embedParentType: typing.Optional[str] = None
    ):
        mentions: typing.Optional[typing.List[typing.Dict[str, str]]] = None
        embedMediaList: typing.Optional[typing.List[typing.List[typing.Any]]] = None
        files: typing.Optional[typing.Dict[str, typing.BinaryIO]] = None
        content_type: typing.Optional[str] = None
        if message is not None and file is None:
            message = message.replace("<$", "\u200e\u200f").replace("$>", "\u202c\u202d")
        if mentionUserIds:
            mentions = [{"uid": userId} for userId in mentionUserIds]
        data: typing.Dict[str, typing.Any] = dict(
            attachedObject=None,
            content=message,
            clientRefId=int(time.time() / 10 % 1000000000),
            extensions=dict(mentionedArray=mentions),
            timestamp=currentTimeMillis(),
            type=messageType
        )
        if any((embedId, embedType, embedLink, embedTitle, embedContent, embedImage)):
            if embedImage:
                embedMediaList = [[100, self.upload_media(img, "image"), None] for img in ([embedImage] if isinstance(embedImage, typing.BinaryIO) else embedImage)]
            data.update(attachedObject=dict(
                content=embedContent,
                link=embedLink,
                mediaList=embedMediaList,
                objectId=embedId,
                objectType=embedType,
                title=embedTitle,
                parentId=embedParentId,
                parentType=embedParentType
            ))
        if replyTo:
            data.update(replyMessageId=replyTo)
        if stickerId:
            data.update(content=None, stickerId=stickerId, type=3)
        if file:
            data.update(content=None)
            if fileType == "audio":
                data.update(type=2, mediaType=110)
            elif fileType == "image":
                data.update(mediaType=100, mediaUploadValueContentType="image/jpeg", mediaUhqEnabled=True)
            elif fileType == "gif":
                data.update(mediaType=100, mediaUploadValueContentType="image/gif", mediaUhqEnabled=True)
            elif fileType == "video":
                files = {"video.mp4": file}
                videoUpload = dict(
                    contentType="video/mp4",
                    video="video.mp4"
                )
                if coverImage:
                    videoUpload.update(cover="cover.jpg")
                    files["cover.jpg"] = coverImage
                data.update(videoUpload=videoUpload)
                content_type = ContentType.MULTIPART
            else:
                raise ValueError(f"Unsupported fileType: {fileType}")
            data.update(mediaUploadValue=base64.b64encode(file.read()).decode())
        return self.request("POST", f"chat/thread/{chatId}/message", data=data, comId=self.comId, files=files, content_type=content_type)

    def full_embed(
        self,
        link: str,
        image: typing.BinaryIO,
        message: str,
        chatId: str
    ):
        return self.request("POST", f"chat/thread/{chatId}/message", data=dict(
            attachedObject=None,
            clientRefId=int(time.time() / 10 % 100000000),
            content=message,
            extensions=dict(
                linkSnippetList=[dict(
                    link=link,
                    mediaType=100,
                    mediaUploadValue=base64.b64encode(image.read()).decode(),
                    mediaUploadValueContentType="image/png"
                )]
            ),
            timestamp=currentTimeMillis(),
            type=0
        ), comId=self.comId)

    def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: typing.Optional[str] = None):
        data: typing.Dict[str, typing.Any] = dict(
            adminOpName=102,
            timestamp=currentTimeMillis()
        )
        if asStaff and reason:
            data.update(adminOpNote=dict(content=reason))
        if not asStaff:
            return self.request("DELETE", f"chat/thread/{chatId}/message/{messageId}", comId=self.comId)
        else:
            return self.request("POST", f"chat/thread/{chatId}/message/{messageId}/admin", data=data, comId=self.comId)

    def mark_as_read(self, chatId: str, messageId: str):
        return self.request("POST", f"chat/thread/{chatId}/mark-as-read", data=dict(
            messageId=messageId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def mark_as_unread(self, chatId: str):
        return self.request("POST", f"chat/thread/{chatId}/mark-as-unread", comId=self.comId)

    def edit_chat(
        self,
        chatId: str,
        doNotDisturb: typing.Optional[bool] = None,
        pinChat: typing.Optional[bool] = None,
        title: typing.Optional[str] = None,
        icon: typing.Optional[typing.Union[typing.BinaryIO, str]] = None,
        backgroundImage: typing.Optional[typing.Union[typing.BinaryIO, str]] = None,
        content: typing.Optional[str] = None,
        announcement: typing.Optional[str] = None,
        coHosts: typing.Optional[typing.Iterable[str]] = None,
        keywords: typing.Optional[typing.Iterable[str]] = None,
        pinAnnouncement: typing.Optional[bool] = None,
        publishToGlobal: typing.Optional[bool] = None,
        canTip: typing.Optional[bool] = None,
        viewOnly: typing.Optional[bool] = None,
        canInvite: typing.Optional[bool] = None,
        fansOnly: typing.Optional[bool] = None
    ):
        extensions: typing.Dict[str, typing.Any] = {}
        data: typing.Dict[str, typing.Any] = dict(
            timestamp=currentTimeMillis()
        )
        if title:
            data.update(title=title)
        if content:
            data.update(content=content)
        if icon:
            if not isinstance(icon, str):
                icon = self.upload_media(icon, fileType="image")
            data.update(icon=icon)
        if keywords is not None:
            data.update(keywords=list(keywords))
        if isinstance(publishToGlobal, bool):
            data.update(publishToGlobal=int(publishToGlobal))
        if announcement:
            extensions.update(announcement=announcement)
        if isinstance(pinAnnouncement, bool):
            extensions.update(pinAnnouncement=pinAnnouncement)
        if isinstance(fansOnly, bool):
            extensions.update(fansOnly=fansOnly)
        res: typing.List[typing.Dict[str, typing.Any]] = []
        if doNotDisturb is not None:
            response = self.request("POST", f"chat/thread/{chatId}/member/{self.userId}/alert", data=dict(
                alertOption=int(doNotDisturb) + 1,
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if pinChat is not None:
            fpath = "pin" if pinChat else "unpin"
            response = self.request("POST", f"chat/thread/{chatId}/{fpath}", data=dict(
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if backgroundImage is not None:
            if not isinstance(backgroundImage, str):
                backgroundImage = self.upload_media(backgroundImage, fileType="image")
            response = self.request("POST", f"chat/thread/{chatId}/member/{self.profile.userId}/background", data=dict(
                media=[100, backgroundImage, None],
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if coHosts is not None:
            response = self.request("POST", f"chat/thread/{chatId}/co-host", data=dict(
                uidList=list(coHosts),
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if viewOnly is not None:
            fpath = "enable" if viewOnly else "disable"
            response = self.request("POST", f"chat/thread/{chatId}/view-only/{fpath}", data=dict(
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if canInvite is not None:
            fpath = "enable" if canInvite else "disable"
            response = self.request("POST", f"chat/thread/{chatId}/members-can-invite/{fpath}", data=dict(
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        if canTip is not None:
            fpath = "enable" if canTip else "disable"
            response = self.request("POST", f"chat/thread/{chatId}/tipping-perm-status/{fpath}", data=dict(
                timestamp=currentTimeMillis()
            ), comId=self.comId)
            res.append(response)
        response = self.request("POST", f"chat/thread/{chatId}", data=data, comId=self.comId)
        res.append(response)
        return res

    def transfer_host(self, chatId: str, userId: typing.Union[typing.List[str], str]):
        return self.request("POST", f"chat/thread/{chatId}/transfer-organizer", data=dict(
            uidList=[userId] if isinstance(userId, str) else userId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_transfer_host_candidates(self, chatId: str, q: typing.Optional[str] = None):
        return self.request("GET", f"chat/thread/{chatId}/member", params=dict(
            type="organizer-transfer-candidates",
            q=q
        ), comId=self.comId)

    def accept_host(self, chatId: str, requestId: str):
        return self.request("POST", f"chat/thread/{chatId}/transfer-organizer/{requestId}/accept", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def decline_host(self, chatId: str, requestId: str):
        return self.request("POST", f"chat/thread/{chatId}/transfer-organizer/{requestId}/decline", data=dict(
            timestamp=currentTimeMillis()
        ))

    def claim_host(self, chatId: str):
        return self.request("GET", f"chat/thread/{chatId}/transfer-organizer/apply")

    def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        return self.request("DELETE", f"chat/thread/{chatId}/member/{userId}", params=dict(
            allowRejoin=int(allowRejoin)
        ), comId=self.comId)

    def join_chat(self, chatId: str) -> ThreadMemberResponse:
        return ThreadMemberResponse(self.request("POST", f"chat/thread/{chatId}/member/{self.userId}", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId))

    def leave_chat(self, chatId: str) -> APIResponse:
        return APIResponse(self.request("DELETE", f"chat/thread/{chatId}/member/{self.userId}", comId=self.comId))
        
    def delete_chat(self, chatId: str):
        return self.request("DELETE", f"chat/thread/{chatId}", comId=self.comId)

    def subscribe(self, userId: str, autoRenew: bool = False, transactionId: typing.Optional[str] = None):
        return self.request("POST", f"influencer/{userId}/subscribe", data=dict(
            paymentContext=dict(
                transactionId=transactionId or build_uuid(),
                isAutoRenew=autoRenew
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def promotion(self, noticeId: str, type: str = "accept"):
        return self.request("POST", f"notice/{noticeId}/{type}", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def play_quiz_raw(self, quizId: str, quizAnswerList: typing.List[typing.Dict[str, typing.Any]], hellMode: bool = False):
        return self.request("POST", f"blog/{quizId}/quiz/result", data=dict(
            mode=int(hellMode),
            quizAnswerList=quizAnswerList,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def play_quiz(self, quizId: str, questionIdsList: typing.List[str], answerIdsList: typing.List[str], hellMode: bool = False):
        quizAnswerList: typing.List[typing.Dict[str, typing.Any]] = []
        for question, answer in zip(questionIdsList, answerIdsList):
            quizAnswerList.append(dict(
                optIdList=[answer],
                quizQuestionId=question,
                timeSpent=0.0
            ))
        return self.request("POST", f"blog/{quizId}/quiz/result", data=dict(
            mode=int(hellMode),
            quizAnswerList=quizAnswerList,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def vc_permission(self, chatId: str, permission: int):
        return self.request("POST", f"chat/thread/{chatId}/vvchat-permission", data=dict(
            vvChatJoinType=permission,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_vc_reputation_info(self, chatId: str):
        return self.request("GET", f"chat/thread/{chatId}/avchat-reputation", comId=self.comId)

    def claim_vc_reputation(self, chatId: str):
        return self.request("POST", f"chat/thread/{chatId}/avchat-reputation", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_all_users(
        self,
        type: typing.Literal["banned", "curator", "leader", "recent", "featured", "online", "summary"] = "recent",
        start: int = 0,
        size: int = 25
    ) -> UserProfileListResponse:
        # curator, leader, recent, featured
        return UserProfileListResponse(self.request("GET", "user-profile", params=dict(
            type=type,
            start=start,
            size=size
        ), comId=self.comId))

    def search_users(self, nickname: str, start: int = 0, size: int = 25):
        return self.request("GET", "user-profile", params=dict(
            type="name",
            q=nickname,
            start=start,
            size=size
        ), comId=self.comId)

    def get_online_users(self, start: int = 0, size: int = 25):
        return self.request("GET", "live-layer", params=dict(
            topic=f"ndtopic:x{self.comId}:online-members",
            start=start,
            size=size
        ), comId=self.comId)

    def get_favorite_users(self, start: int = 0, size: int = 25):
        return self.request("GET", "user-group/quick-access", params=dict(
            start=start,
            size=size
        ))

    def get_online_favorite_users(self, start: int = 0, size: int = 25):
        return self.request("GET", "user-group/quick-access", params=dict(
            type="online",
            start=start,
            size=size
        ), comId=self.comId)

    def get_user_info(self, userId: typing.Optional[str] = None) -> UserProfile:
        userId = userId or self.userId
        return UserProfileResponse(self.request("GET", f"user-profile/{userId}", params=dict(withAvatarFrame=1), comId=self.comId)).profile

    def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"user-profile/{userId}/joined", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"user-profile/{userId}/member", params=dict(
            start=start,
            size=size
        ),comId=self.comId)

    def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"user-profile/{userId}/visitors", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_user_checkins(self, userId: str, timezone: typing.Optional[int] = None):
        return self.request("GET", f"check-in/stats/{userId}", params=dict(
            timezone=timezone or self.timezone
        ), comId=self.comId)

    def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", "blog", params=dict(
            type="user",
            q=userId,
            start=start,
            size=size
        ), comId=self.comId)

    def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", "item", params=dict(
            type="user-all",
            start=start,
            size=size,
            cv=1.2,
            uid=userId
        ), comId=self.comId)

    def get_user_achievements(self, userId: str):
        return self.request("GET", f"user-profile/{userId}/achievements", comId=self.comId)

    def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"influencer/{userId}/fans", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_blocked_users(self, start: int = 0, size: int = 25):
        return self.request("GET", "block", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_blocker_users(self, start: int = 0, size: int = 25):
        return self.request("GET", f"block", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_saved_blogs(self, start: int = 0, size: int = 25):
        return self.request("GET", "bookmark", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_leaderboard_info(self, type: typing.Literal["check", "day", "hour", "rep", "quiz"], start: int = 0, size: int = 25):
        rankingType = 1 if type == "hour" else 2 if type == "day" else 3 if type == "rep" else 4 if type == "check" else 5
        return self.request("GET", "community/leaderboard", params=dict(
            rankingType=rankingType,
            start=start,
            size=size
        ), comId=self.comId, scope=True)

    def get_wiki_info(self, wikiId: str):
        return self.request("GET", f"item/{wikiId}", comId=self.comId)

    def get_recent_wikis(self, start: int = 0, size: int = 25):
        return self.request("GET", "item", params=dict(
            type="catalog-all",
            start=start,
            size=size
        ), comId=self.comId)

    def get_wiki_categories(self, start: int = 0, size: int = 25):
        return self.request("GET", "item-category", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"item-category/{categoryId}", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_blog_tipped_users(self, blogId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"blog/{blogId}/tipping/tipped-users-summary", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_wiki_tipped_users(self, wikiId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"item/{wikiId}/tipping/tipped-users-summary", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_chat_tipped_users(self, chatId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"chat/thread/{chatId}/tipping/tipped-users-summary", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_tipped_users(
        self,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        quizId: typing.Optional[str] = None,
        fileId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        start: int = 0,
        size: int = 25
    ):
        if blogId or quizId:
            return self.get_blog_tipped_users(typing.cast(str, blogId or quizId), start=start, size=size)
        elif wikiId:
            return self.get_wiki_tipped_users(wikiId, start=start, size=size)
        elif chatId:
            return self.get_chat_tipped_users(chatId, start=start, size=size)
        elif fileId:
            return self.get_shared_file_tipped_users(fileId, start=start, size=size)
        else:
            raise ValueError("argument required for blogId, quizId, fileId or chatId")

    def joined_chats(self, start: int = 0, size: int = 25) -> ThreadListResponse:
        return ThreadListResponse(self.request("GET", f"chat/thread", params=dict(
            type="joined-me",
            start=start,
            size=size
        )))

    @typing_extensions.deprecated("use joined_chats instead")
    def get_chat_threads(self, start: int = 0, size: int = 25) -> ThreadList:
        return self.joined_chats(start=start, size=size).chats

    def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
        return self.get_public_chats(type=type, start=start, size=size).chats

    def get_public_chats(self, type: str = "recommended", start: int = 0, size: int = 25) -> ThreadListResponse:
        return ThreadListResponse(self.request("GET", "chat/thread", params=dict(
            type="public-all",
            filterType=type,
            start=start,
            size=size
        ), comId=self.comId))

    def get_chat_info(self, chatId: str) -> Thread:
        """Get chat information.

        Parameters
        ----------
        chatId : `str`
            The chat ID to get information.

        Returns
        -------
        Thread
            The chat object.

        """
        return ThreadResponse(self.request("GET", f"chat/thread/{chatId}", comId=self.comId)).chat

    @typing_extensions.deprecated("use get_chat_info instead")
    def get_chat_thread(self, chatId: str) -> Thread:
        return self.get_chat_info(chatId)

    def get_wiki_comments(self, wikiId: str, sorting: typing.Literal["newest", "oldest", "top", "vote"] = "newest", start: int = 0, size: int = 25):
        return self.request("GET", f"item/{wikiId}/comment", params=dict(
            sort=sorting.replace("top", "vote"),
            start=start,
            size=size
        ), comId=self.comId)

    def get_chat_messages(self, chatId: str, start: int = 0, size: int = 25, pageToken: typing.Optional[str] = None):
        return self.request("GET", f"chat/thread/{chatId}/message", params=dict(
            pageToken=pageToken,
            pagingType="t",
            start=start,
            size=size,
            v=2
        ), comId=self.comId)

    def get_message_info(self, chatId: str, messageId: str):
        return self.request("GET", f"chat/thread/{chatId}/message/{messageId}", comId=self.comId)

    def get_blog_info(self, blogId: str):
        return self.request("GET", f"blog/{blogId}", comId=self.comId)

    def get_blog_comments(self, blogId: str, sorting: typing.Literal["newest", "oldest", "top", "vote"] = "newest", start: int = 0, size: int = 25):
        return self.request("GET", f"blog/{blogId}/comment", params=dict(
            sort=sorting.replace("top", "vote"),
            start=start,
            size=size
        ), comId=self.comId)

    def get_blog_categories(self, start: int = 0, size: int = 25):
        return self.request("GET", f"blog-category", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_blogs_by_category(self, categoryId: str,start: int = 0, size: int = 25):
        return self.request("GET", f"blog-category/{categoryId}/blog-list", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"blog/{quizId}/quiz/result", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_wall_comments(self, userId: str, sorting: typing.Literal["newest", "oldest", "top", "vote"] = "newest", start: int = 0, size: int = 25):
        return self.request("GET", f"user-profile/{userId}/comment", params=dict(
            sort=sorting.replace("top", "vote"),
            start=start,
            size=size
        ), comId=self.comId)

    def get_recent_blogs(self, pageToken: typing.Optional[str] = None, start: int = 0, size: int = 25):
        return self.request("GET", "feed/blog-all", params=dict(
            pagingType="t",
            pageToken=pageToken,
            start=start,
            size=size
        ), comId=self.comId)

    def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"chat/thread/{chatId}/member", params=dict(
            start=start,
            size=size,
            type="default",
            cv=1.2
        ), comId=self.comId)

    def get_notifications(self, start: int = 0, size: int = 25):
        return self.request("GET", "notification", params=dict(
            pagingType="t",
            start=start,
            size=size
        ), comId=self.comId)

    def get_notices(self, start: int = 0, size: int = 25):
        return self.request("GET", "notice", params=dict(
            type="usersV2",
            status=1,
            start=start,
            size=size
        ), comId=self.comId)

    def subscribe_product(self, productSku: str, paymentType: PaymentType, autoRenew: bool = True, couponId: typing.Optional[str] = None):
        return self.request("POST", "membership/product/subscribe", data=dict(
            sku=productSku,
            packageName=f"com.narvii.amino.x{self.comId}",
            paymentType=paymentType,
            transactionId=build_uuid(),
            paymentContext=dict(
                isAutoRenew=autoRenew,
                couponMappingIdList=[couponId] if couponId else None,
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def activate_store_sticker_collection(self, collectionId: str):
        return self.request("POST", f"sticker-collection/{collectionId}/activate", data=dict(
            timestamp=currentTimeMillis()
        ))

    def get_sticker_collection(self, collectionId: str):
        return self.request("GET", f"sticker-collection/{collectionId}", params=dict(
            includeStickers="true"
        ), comId=self.comId)

    def get_sticker_collections(self):
        return self.request("GET", "sticker-collection", params=dict(
            includeStickers="true",
            type="my-active-collection"
        ), comId=self.comId)

    def get_community_stickers(self):
        return self.request("GET", "sticker-collection", params=dict(
            type="community-shared"
        ), comId=self.comId)

    def get_bubble_info(self, bubbleId: str):
        return self.request("GET", f"chat/chat-bubble/{bubbleId}", comId=self.comId)

    def activate_store_bubble(self, bubbleId: str):
        return self.request("POST", f"chat/chat-bubble/{bubbleId}/activate", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
        return self.request("GET", "store/items", params=dict(
            sectionGroupId="chat-bubble",
            start=start,
            size=size
        ), comId=self.comId)

    def get_store_stickers(self, start: int = 0, size: int = 25):
        return self.request("GET", "store/items", params=dict(
            sectionGroupId="sticker",
            start=start,
            size=size
        ), comId=self.comId)

    def purchase(self, objectId: str, objectType: int, autoRenew: bool = False, aminoPlus: bool = False):
        return self.request("POST", "store/purchase", data=dict(
            objectId=objectId,
            objectType=objectType,
            paymentContext=dict(
                discountStatus=int(aminoPlus),
                discountValue=1,  # ???
                isAutoRenew=autoRenew
            ),
            v=1,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_shared_file_info(self, fileId: str):
        return self.request("GET", f"shared-folder/files/{fileId}", comId=self.comId)

    def get_shared_file_comments(self, fileId: str, sorting: typing.Literal["newest", "oldest", "top", "vote"] = "newest", start: int = 0, size: int = 25):
        return self.request("GET", f"shared-folder/files/{fileId}/comment", params=dict(
            sort=sorting.replace("top", "vote"),
            start=start,
            size=size
        ), comId=self.comId)

    def get_shared_file_tipped_users(self, fileId: str, start: int = 0, size: int = 25):
        return self.request("GET", f"shared-folder/files/{fileId}/tipping/tipped-users-summary", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_shared_folder_info(self):
        return self.request("GET", "shared-folder/stats", comId=self.comId)

    def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):
        return self.request("GET", "shared-folder/files", params=dict(
            type=type,
            start=start,
            size=size
        ), comId=self.comId)

    def moderation_history(
        self,
        userId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        fileId: typing.Optional[str] = None,
        size: int = 25
    ):
        objectId = userId or blogId or wikiId or fileId
        objectType = 0 if userId else 1 if blogId else 2 if wikiId else 109 if fileId else None
        return self.request("GET", "admin/operation", params=dict(
            objectId=objectId,
            objectType=objectType,
            pagingType="t",
            size=size
        ), comId=self.comId)

    def get_disabled_posts(self, start: int = 0, size: int = 25):
        return self.request("GET", "feed/blog-disabled", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def check_exists_chat(self, userId: str):
        """Get the single chat if exists.

        Parameters
        ----------
        userId : str
            The user of chat

        Raises
        ------
        RequestedNoLongerExist
            If the chat not exists.

        Returns
        -------
        _type_
            _description_
        """
        return self.request("GET", "chat/thread", params=dict(type="exist-single", cv=1.2, q=userId), comId=self.comId)

    def review_quiz(self, blogId: str):
        return self.request("GET", f"blog/{blogId}", params=dict(action="review"), comId=self.comId)

    def update_quiz(self, blogId: str, bestQuiz: bool):
        return self.request("POST", f"blog/{blogId}/admin", data=dict(
            adminOpName=240 if bestQuiz else 241,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def change_blog_category_status(self, blogId: str, adminOpValue: typing.Dict[str, typing.Any]):
        return self.request("POST", f"blog/{blogId}/admin", data=dict(
            adminOpName=103,
            adminOpValue=adminOpValue,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def feature(
        self,
        duration: typing.Literal[1, 2, 3],
        userId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None
    ):
        fpath = f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}" if wikiId else f"chat/thread/{chatId}"
        return self.request("POST", f"{fpath}/admin", data=dict(
            adminOpName=114,
            adminOpValue=dict(
                featuredDuration=duration * (3600 if chatId else 86400),
                featuredType=4 if userId else 1 if blogId or wikiId else 5
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def unfeature(
        self,
        userId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None
    ):
        fpath = f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}" if wikiId else f"chat/thread/{chatId}"
        return self.request("POST", f"{fpath}/admin", data=dict(
            adminOpName=114,
            adminOpValue=dict(
                featuredType=0
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def hide(
        self,
        userId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        fileId: typing.Optional[str] = None,
        reason: typing.Optional[str] = None
    ):
        fpath = f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}" if wikiId else f"chat/thread/{chatId}" if chatId else f"shared-folder/files/{fileId}"
        return self.request("POST", f"{fpath}/admin", data=dict(
            adminOpName=18 if userId else 110,
            adminOpNote=dict(
                content=reason
            ),
            adminOpValue=9,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def unhide(
        self,
        userId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        blogId: typing.Optional[str] = None,
        wikiId: typing.Optional[str] = None,
        fileId: typing.Optional[str] = None,
        reason: typing.Optional[str] = None
    ):
        fpath = f"user-profile/{userId}" if userId else f"blog/{blogId}" if blogId else f"item/{wikiId}" if wikiId else f"chat/thread/{chatId}" if chatId else f"shared-folder/files/{fileId}"
        return self.request("POST", f"{fpath}/admin", data=dict(
            adminOpName=19 if userId else 110,
            adminOpNote=dict(
                content=reason
            ),
            adminOpValue=0,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def edit_titles(self, userId: str, titles: typing.List[str], colors: typing.List[typing.Optional[str]]):
        return self.request("POST", f"user-profile/{userId}/admin", data=dict(
            adminOpName=207,
            adminOpValue=dict(
                titles=[dict(
                    title=title,
                    color=color
                ) for title, color in zip(titles, colors)]
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def warn(self, userId: str, title: str = "Warning", reason: typing.Optional[str] = None):
        return self.request("POST", "notice", data=dict(
            uid=userId,
            title=title,
            content=reason,
            attachedObject=dict(
                objectId=userId,
                objectType=0
            ),
            penaltyType=0,
            adminOpNote=typing.cast("dict[str, typing.Any]", dict()),
            noticeType=7,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def strike(self, userId: str, duration: typing.Literal[1, 2, 3, 4, 5], title: str = "Strike", reason: typing.Optional[str] = None):
        penaltyValue = 3600 if duration == 1 else 10800 if duration == 2 else 21600 if duration == 3 else 43200 if duration == 4 else 86400
        return self.request("POST", "notice", data=dict(
            uid=userId,
            title=title,
            content=reason,
            attachedObject=dict(
                objectId=userId,
                objectType=0
            ),
            penaltyType=1,
            penaltyValue=penaltyValue,
            adminOpNote=typing.cast("dict[str, typing.Any]", dict()),
            noticeType=4,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def ban(self, userId: str, reason: str, banType: typing.Optional[int] = None):
        self.request("POST", f"user-profile/{userId}/ban", data=dict(
            reasonType=banType,
            note=dict(
                content=reason
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def unban(self, userId: str, reason: str):
        return self.request("POST", f"user-profile/{userId}/unban", data=dict(
            note=dict(
                content=reason
            ),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_featured_posts(self):
        return self.request("GET", "feed/featured", comId=self.comId)

    def reorder_featured_posts(self, objectIds: typing.Sequence[str]):
        return self.request("POST", "feed/featured/reorder", data=dict(
            objectIdList=list(objectIds)
        ), comId=self.comId)

    def get_featured_users(self, start: int = 0, size: int = 25):
        return self.request("GET", "user-profile", params=dict(
            type="featured",
            start=start,
            size=size
        ), comId=self.comId)

    def reorder_featured_users(self, userIds: typing.Sequence[str]):
        return self.request("POST", "user-profile/featured/reorder", data=dict(
            uidList=list(userIds),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_featured_chats(self, start: int = 0, size: int = 25):
        return self.request("GET", "chat/thread", params=dict(
            type="featured",
            start=start,
            size=size
        ), comId=self.comId)

    def get_hidden_blogs(self, start: int = 0, size: int = 25):
        return self.request("GET", "feed/blog-disabled", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def review_quiz_questions(self, quizId: str):
        return self.request("GET", f"blog/{quizId}", params=dict(action="review"), comId=self.comId)

    def get_recent_quiz(self, start: int = 0, size: int = 25):
        return self.request("GET", "blog", params=dict(
            type="quizzes-recent",
            start=start
            ,size=size
        ), comId=self.comId)

    def get_trending_quiz(self, start: int = 0, size: int = 25):
        return self.request("GET", f"feed/quiz-trending", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def get_best_quizzes(self, start: int = 0, size: int = 25):
        return self.request("GET", f"feed/quiz-best-quizzes", params=dict(
            start=start,
            size=size
        ), comId=self.comId)

    def apply_avatar_frame(self, frameId: str, applyToAll: bool = True):
        return self.request("POST", f"avatar-frame/apply", data=dict(
            frameId=frameId,
            applyToAll=int(applyToAll),
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False):
        return self.request("POST", f"chat/thread/apply-bubble", data=dict(
            applyToAll=int(applyToAll),
            bubbleId=bubbleId,
            threadId=chatId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def invite_to_vc(self, chatId: str, userId: str):
        return self.request("POST", f"chat/thread/{chatId}/vvchat-presenter/invite/", data=dict(
            uid=userId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def create_wiki_category(self, title: str, parentCategoryId: str, content: typing.Optional[str] = None):
        return self.request("POST", f"{self.api}/x{self.comId}/s/item-category", data=dict(
            content=content,
            icon=None,
            label=title,
            mediaList=None,
            parentCategoryId=parentCategoryId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def create_shared_folder(self,title: str):
        return self.request("POST", f"shared-folder/folders", data=dict(
            title=title,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def submit_wiki(self, wikiId: str, message: str):
        return self.request("POST", f"knowledge-base-request", data=dict(
            message=message,
            itemId=wikiId,
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def accept_wiki_request(self, requestId: str, destinationCategoryIdList: typing.List[str]):
        return self.request("POST", f"knowledge-base-request/{requestId}/approve", data=dict(
            destinationCategoryIdList=destinationCategoryIdList,
            actionType="create",
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def reject_wiki_request(self, requestId: str):
        return self.request("POST", f"knowledge-base-request/{requestId}/reject", data=dict(
            timestamp=currentTimeMillis()
        ), comId=self.comId)

    def get_wiki_submissions(self, start: int = 0, size: int = 25):
        return self.request("GET", f"knowledge-base-request", params=dict(
            type="all",
            start=start,
            size=size
        ), comId=self.comId)
