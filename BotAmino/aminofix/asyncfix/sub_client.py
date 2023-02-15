import json
import base64
import asyncio

from uuid import UUID
from os import urandom
from time import timezone
from binascii import hexlify
from typing import BinaryIO, Union
from time import time as timestamp
import requests

from . import client
from ..lib.util import exceptions, headers, objects, signature
from ..lib.util.helpers import gen_deviceId

class VCHeaders:
    def __init__(self, data = None):
        vc_headers = {
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "User-Agent": "Amino/45725 CFNetwork/1126 Darwin/19.5.0",  # Closest server (this one for me)
            "Host": "rt.applovin.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "Keep-Alive",
            "Accept": "*/*"
        }

        if data: vc_headers["Content-Length"] = str(len(data))
        self.vc_headers = vc_headers


class SubClient(client.Client):
    def __init__(self, comId: str = None, aminoId: str = None, *, profile: objects.UserProfile, deviceId: str = None):
        client.Client.__init__(self, deviceId=deviceId, sub=True)
        self.vc_connect = False
        self.comId = comId
        self.aminoId = aminoId
        self.profile: objects.UserProfile = profile
        self.community: objects.Community

    def __await__(self):
        return self._init().__await__()

    async def _init(self):
        if self.comId is not None:
            self.community: objects.Community = await self.get_community_info(self.comId)
        if self.aminoId is not None:
            self.comId = (await client.Client().search_community(self.aminoId)).comId[0]
            self.community: objects.Community = await client.Client().get_community_info(self.comId)
        if self.comId is None and self.aminoId is None: raise exceptions.NoCommunity()
        try: self.profile: objects.UserProfile = await self.get_user_info(userId=self.profile.userId)
        except AttributeError: raise exceptions.FailedLogin()
        except exceptions.UserUnavailable(): pass
        return self

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._close_session())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._close_session())

    async def _close_session(self):
        if not self.session.closed: await self.session.close()

    def parse_headers(self, data: str = None, type: str = None):
        return headers.ApisHeaders(deviceId=deviceId() if self.autoDevice else self.device_id, data=data, type=type).headers

    async def get_invite_codes(self, status: str = "normal", start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.InviteCodeList(json.loads(await response.text())["communityInvitationList"]).InviteCodeList

    async def generate_invite_code(self, duration: int = 0, force: bool = True):
        data = json.dumps({
            "duration": duration,
            "force": force,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/g/s-x{self.comId}/community/invitation", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.InviteCode(json.loads(await response.text())["communityInvitation"]).InviteCode

    async def delete_invite_code(self, inviteId: str):
        async with self.session.delete(f"{self.api}/g/s-x{self.comId}/community/invitation/{inviteId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def post_blog(self, title: str, content: str, imageList: list = None, captionList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None):
        mediaList = []

        if captionList is not None:
            for image, caption in zip(imageList, captionList):
                mediaList.append([100, self.upload_media(image, "image"), caption])

        else:
            if imageList is not None:
                for image in imageList:
                    print(self.upload_media(image, "image"))
                    mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "address": None,
            "content": content,
            "title": title,
            "mediaList": mediaList,
            "extensions": extensions,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def post_wiki(self, title: str, content: str, icon: str = None, imageList: list = None, keywords: str = None, backgroundColor: str = None, fansOnly: bool = False):
        mediaList = []

        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "label": title,
            "content": content,
            "mediaList": mediaList,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/item", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def edit_blog(self, blogId: str, title: str = None, content: str = None, imageList: list = None, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False):
        mediaList = []

        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])

        data = {
            "address": None,
            "mediaList": mediaList,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        }

        if title: data["title"] = title
        if content: data["content"] = content
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if categoriesList: data["taggedBlogCategoryIdList"] = categoriesList
        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_blog(self, blogId: str):
        async with self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_wiki(self, wikiId: str):
        async with self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None):
        if blogId is not None: refObjectId, refObjectType = blogId, 1
        elif wikiId is not None: refObjectId, refObjectType = wikiId, 2
        else: raise exceptions.SpecifyType()

        data = json.dumps({
            "content": content,
            "refObjectId": refObjectId,
            "refObjectType": refObjectType,
            "type": 2,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def check_in(self, tz: int = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/check-in", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def repair_check_in(self, method: int = 0):
        data = {"timestamp": int(timestamp() * 1000)}
        if method == 0: data["repairMethod"] = "1"  # Coins
        if method == 1: data["repairMethod"] = "2"  # Amino+

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/check-in/repair", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def edit_profile(self, nickname: str = None, content: str = None, icon: BinaryIO = None, chatRequestPrivilege: str = None, imageList: list = None, captionList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, colors: list = None, defaultBubbleId: str = None, fileType: str = "image"):
        mediaList = []

        data = {"timestamp": int(timestamp() * 1000)}

        if captionList is not None:
            for image, caption in zip(imageList, captionList):
                mediaList.append([100, self.upload_media(image, "image"), caption])

        else:
            if imageList is not None:
                for image in imageList:
                    mediaList.append([100, self.upload_media(image, "image"), None])

        if imageList is not None or captionList is not None:
            data["mediaList"] = mediaList

        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = self.upload_media(icon, fileType)
        if content: data["content"] = content

        if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
        if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        if titles or colors:
            tlt = []
            for titles, colors in zip(titles, colors):
                tlt.append({"title": titles, "color": colors})

            data["extensions"] = {"customTitles": tlt}

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def vote_poll(self, blogId: str, optionId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False):
        data = {
            "content": message,
            "stickerId": None,
            "type": 0,
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["respondTo"] = replyTo

        if isGuest: comType = "g-comment"
        else: comType = "comment"

        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/{comType}"

        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/{comType}"

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/{comType}"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId: url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}"
        elif blogId: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}"
        else: raise exceptions.SpecifyType()

        async with self.session.delete(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def like_blog(self, blogId: Union[str, list] = None, wikiId: str = None):
        """
        Like a Blog, Multiple Blogs or a Wiki.

        **Parameters**
            - **blogId** : ID of the Blog or List of IDs of the Blogs. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        data = {
            "value": 4,
            "timestamp": int(timestamp() * 1000)
        }

        if blogId:
            if isinstance(blogId, str):
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                url = f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?cv=1.2"

            elif isinstance(blogId, list):
                data["targetIdList"] = blogId
                data = json.dumps(data)
                url = f"{self.api}/x{self.comId}/s/feed/vote"

            else: raise exceptions.WrongType(type(blogId))

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            url = f"{self.api}/x{self. comId}/s/item/{wikiId}/vote?cv=1.2"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unlike_blog(self, blogId: str = None, wikiId: str = None):
        if blogId: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView"
        else: raise exceptions.SpecifyType()

        async with self.session.delete(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "value": 1,
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1"

        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1"

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId: url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
        elif blogId: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
        else: raise exceptions.SpecifyType()

        async with self.session.delete(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def upvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def downvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": -1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=-1", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unvote_comment(self, blogId: str, commentId: str):
        async with self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def reply_wall(self, userId: str, commentId: str, message: str):
        data = json.dumps({
            "content": message,
            "stackedId": None,
            "respondTo": commentId,
            "type": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def lottery(self, tz: int = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })
        async with self.session.post(f"{self.api}/x{self.comId}/s/check-in/lottery", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else:  return objects.LotteryLog(json.loads(await response.text())["lotteryLog"]).LotteryLog

    async def activity_status(self, status: str):
        if "on" in status.lower(): status = 1
        elif "off" in status.lower(): status = 2
        else: raise exceptions.WrongType(status)

        data = json.dumps({
            "onlineStatus": status,
            "duration": 86400,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def check_notifications(self):
        async with self.session.post(f"{self.api}/x{self.comId}/s/notification/checked", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_notification(self, notificationId: str):
        async with self.session.delete(f"{self.api}/x{self.comId}/s/notification/{notificationId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def clear_notifications(self):
        async with self.session.delete(f"{self.api}/x{self.comId}/s/notification", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def start_chat(self, userId: Union[str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise exceptions.WrongType(type(userId))

        data = {
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(timestamp() * 1000)
        }

        if isGlobal is True: data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"
        else: data["type"] = 0

        if publishToGlobal is True: data["publishToGlobal"] = 1
        else: data["publishToGlobal"] = 0

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def invite_to_chat(self, userId: Union[str, list], chatId: str):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise exceptions.WrongType(type(userId))

        data = json.dumps({
            "uids": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/invite", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def add_to_favorites(self, userId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/user-group/quick-access/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(timestamp() * 1000)
        }

        if blogId is not None: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping"
        elif chatId is not None: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping"
        elif objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.api}/x{self.comId}/s/tipping"

        else: raise exceptions.SpecifyType()

        data = json.dumps(data)

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def thank_tip(self, chatId: str, userId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def follow(self, userId: Union[str, list]):
        """
        Follow an User or Multiple Users.

        **Parameters**
            - **userId** : ID of the User or List of IDs of the Users.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        if isinstance(userId, str):
            async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member", headers=self.parse_headers()) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return response.status

        elif isinstance(userId, list):
            data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})

            async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined", headers=self.parse_headers(data=data), data=data) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return response.status

        else: raise exceptions.WrongType(type(userId))

    async def unfollow(self, userId: str):
        """
        Unfollow an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.delete(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def block(self, userId: str):
        """
        Block an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.post(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unblock(self, userId: str):
        """
        Unblock an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.delete(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def visit(self, userId: str):
        """
        Visit an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}?action=visit", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False):
        """
        Flag a User, Blog or Wiki.

        **Parameters**
            - **reason** : Reason of the Flag.
            - **flagType** : Type of the Flag.
            - **userId** : ID of the User.
            - **blogId** : ID of the Blog.
            - **wikiId** : ID of the Wiki.
            - *asGuest* : Execute as a Guest.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        if reason is None: raise exceptions.ReasonNeeded()
        if flagType is None: raise exceptions.FlagTypeNeeded()

        data = {
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["objectId"] = userId
            data["objectType"] = 0

        elif blogId:
            data["objectId"] = blogId
            data["objectType"] = 1

        elif wikiId:
            data["objectId"] = wikiId
            data["objectType"] = 2

        else: raise exceptions.SpecifyType()

        if asGuest: flg = "g-flag"
        else: flg = "flag"

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/{flg}", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None, linkSnippet: str = None, linkSnippetImage: BinaryIO = None):
        """
        Send a Message to a Chat.

        **Parameters**
            - **message** : Message to be sent
            - **chatId** : ID of the Chat.
            - **file** : File to be sent.
            - **fileType** : Type of the file.
                - ``audio``, ``image``, ``gif``
            - **messageType** : Type of the Message.
            - **mentionUserIds** : List of User IDS to mention. '@' needed in the Message.
            - **replyTo** : Message ID to reply to.
            - **stickerId** : Sticker ID to be sent.
            - **embedTitle** : Title of the Embed.
            - **embedContent** : Content of the Embed.
            - **embedLink** : Link of the Embed.
            - **embedImage** : Image of the Embed.
            - **embedId** : ID of the Embed.
            - **linkSnippet** : Link of the target snippet.
            - **linkSnippetImage** : Image target snippet.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """

        if message is not None and file is None:
            message = message.replace("<$", "‎‏").replace("$>", "‬‭")

        mentions = []
        if mentionUserIds:
            for mention_uid in mentionUserIds:
                mentions.append({"uid": mention_uid})

        if embedImage:
            embedImage = [[100, self.upload_media(embedImage, "image"), None]]

        if linkSnippetImage:
            linkSnippetImage = base64.b64encode(linkSnippetImage.read()).decode()

        data = {
            "type": messageType,
            "content": message,
            "clientRefId": int(timestamp() / 10 % 1000000000),
            "attachedObject": {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            },
            "extensions": {
                "mentionedArray": mentions,
                "linkSnippetList": [{
                    "link": linkSnippet,
                    "mediaType": 100,
                    "mediaUploadValue": linkSnippetImage,
                    "mediaUploadValueContentType": "image/png"
                }]
            },
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["replyMessageId"] = replyTo

        if stickerId:
            data["content"] = None
            data["stickerId"] = stickerId
            data["type"] = 3

        if file:
            data["content"] = None
            if fileType == "audio":
                data["type"] = 2
                data["mediaType"] = 110

            elif fileType == "image":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/jpg"
                data["mediaUhqEnabled"] = True

            elif fileType == "gif":
                data["mediaType"] = 100
                data["mediaUploadValueContentType"] = "image/gif"
                data["mediaUhqEnabled"] = True

            else: raise exceptions.SpecifyType(fileType)

            data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def full_embed(self, link: str, image: BinaryIO, message: str, chatId: str):
        data = {
        "type": 0,
        "content": message,
        "extensions": {
            "linkSnippetList": [{
                "link": link,
                "mediaType": 100,
                "mediaUploadValue": base64.b64encode(image.read()).decode(),
                "mediaUploadValueContentType": "image/png"
            }]
        },
            "clientRefId": int(timestamp() / 10 % 100000000),
            "timestamp": int(timestamp() * 1000),
            "attachedObject": None
        }
        
        data = json.dumps(data)
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):
        """
        Delete a Message from a Chat.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.
            - **asStaff** : If execute as a Staff member (Leader or Curator).
            - **reason** : Reason of the action to show on the Moderation History.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        data = {
            "adminOpName": 102,
            "adminOpNote": {"content": reason},
            "timestamp": int(timestamp() * 1000)
        }
        if asStaff and reason:
            data["adminOpNote"] = {"content": reason}

        data = json.dumps(data)
        if not asStaff:
            async with self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers()) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return response.status
        else:
            async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", headers=self.parse_headers(data=data), data=data) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return response.status

    async def mark_as_read(self, chatId: str, messageId: str):
        """
        Mark a Message from a Chat as Read.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        data = json.dumps({
            "messageId": messageId,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None, icon: str = None, backgroundImage: BinaryIO = None, content: str = None, announcement: str = None, coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None):
        """
        Send a Message to a Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - **title** : Title of the Chat.
            - **content** : Content of the Chat.
            - **icon** : Icon of the Chat.
            - **backgroundImage** : Background Image of the Chat.
            - **announcement** : Announcement of the Chat.
            - **pinAnnouncement** : If the Chat Announcement should Pinned or not.
            - **coHosts** : List of User IDS to be Co-Host.
            - **keywords** : List of Keywords of the Chat.
            - **viewOnly** : If the Chat should be on View Only or not.
            - **canTip** : If the Chat should be Tippable or not.
            - **canInvite** : If the Chat should be Invitable or not.
            - **fansOnly** : If the Chat should be Fans Only or not.
            - **publishToGlobal** : If the Chat should show on Public Chats or not.
            - **doNotDisturb** : If the Chat should Do Not Disturb or not.
            - **pinChat** : If the Chat should Pinned or not.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        data = {"timestamp": int(timestamp() * 1000)}

        if title: data["title"] = title
        if content: data["content"] = content
        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if announcement: data["extensions"] = {"announcement": announcement}
        if pinAnnouncement: data["extensions"] = {"pinAnnouncement": pinAnnouncement}
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}

        if publishToGlobal: data["publishToGlobal"] = 0
        if not publishToGlobal: data["publishToGlobal"] = 1

        res = []

        if doNotDisturb is not None:
            if doNotDisturb:
                data = json.dumps({"alertOption": 2, "timestamp": int(timestamp() * 1000)})
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(timestamp() * 1000)})
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

        if pinChat is not None:
            if pinChat:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/pin", headers=self.parse_headers()) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

            if not pinChat:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/unpin", headers=self.parse_headers()) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

        if backgroundImage is not None:
            data = json.dumps({"media": [100, self.upload_media(backgroundImage, "image"), None], "timestamp": int(timestamp() * 1000)})
            async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/background", headers=self.parse_headers(data=data), data=data) as response:
                if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                else: res.append(response.status)

        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(timestamp() * 1000)})
            async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/co-host", headers=self.parse_headers(data=data), data=data) as response:
                if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                else: res.append(response.status)

        if viewOnly is not None:
            if viewOnly:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/enable", headers=self.parse_headers(type="application/x-www-form-urlencoded")) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

            if not viewOnly:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/disable", headers=self.parse_headers(type="application/x-www-form-urlencoded")) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

        if canInvite is not None:
            if canInvite:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/enable", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

            if not canInvite:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/disable", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

        if canTip is not None:
            if canTip:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/enable", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

            if not canTip:
                async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/disable", headers=self.parse_headers(data=data), data=data) as response:
                    if response.status != 200: res.append(exceptions.CheckException(await response.text()))
                    else: res.append(response.status)

        data = json.dumps(data)
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: res.append(exceptions.CheckException(await response.text()))
            else: res.append(response.status)

        return res

    async def transfer_host(self, chatId: str, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def transfer_organizer(self, chatId: str, userIds: list):
        await self.transfer_host(chatId, userIds)

    async def accept_host(self, chatId: str, requestId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def accept_organizer(self, chatId: str, requestId: str):
        await self.accept_host(chatId, requestId)

    async def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        if allowRejoin: allowRejoin = 1
        if not allowRejoin: allowRejoin = 0

        async with self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def join_chat(self, chatId: str):
        """
        Join an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.parse_headers(type="application/x-www-form-urlencoded")) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def leave_chat(self, chatId: str):
        """
        Leave an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasynс.lib.util.exceptions>`
        """
        async with self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def send_active_obj(self, startTime: int = None, endTime: int = None, optInAdsFlags: int = 2147483647, tz: int = -timezone // 1000, timers: list = None, timestamp: int = int(timestamp() * 1000)): 
        data = {"userActiveTimeChunkList": [{"start": startTime, "end": endTime}], "timestamp": timestamp, "optInAdsFlags": optInAdsFlags, "timezone": tz} 
        if timers: data["userActiveTimeChunkList"] = timers 
        data = json_minify(json.dumps(data))  
        
        async with self.session.post(f"{self.api}/x{self.comId}/s/community/stats/user-active-time", headers=self.parse_headers(data=data), data=data) as response: 
          if response.status != 200: 
              return exceptions.CheckException(response.text) 
          else: return response.status
  
    async def delete_chat(self, chatId: str):
        """
        Delete a Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status
        
    async def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = json.dumps({
            "paymentContext": {
                "transactionId": transactionId,
                "isAutoRenew": autoRenew
            },
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}/subscribe", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def promotion(self, noticeId: str, type: str = "accept"):
        async with self.session.post(f"{self.api}/x{self.comId}/s/notice/{noticeId}/{type}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def play_quiz_raw(self, quizId: str, quizAnswerList: list, quizMode: int = 0):
        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0):
        quizAnswerList = []

        for question, answer in zip(questionIdsList, answerIdsList):
            part = json.dumps({
                "optIdList": [answer],
                "quizQuestionId": question,
                "timeSpent": 0.0
            })

            quizAnswerList.append(json.loads(part))

        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def vc_permission(self, chatId: str, permission: int):
        """Voice Chat Join Permissions
        1 - Open to Everyone
        2 - Approval Required
        3 - Invite Only
        """
        data = json.dumps({
            "vvChatJoinType": permission,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_vc_reputation_info(self, chatId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.VcReputation(json.loads(await response.text())).VcReputation

    async def claim_vc_reputation(self, chatId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.VcReputation(json.loads(await response.text())).VcReputation

    async def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent": url = f"{self.api}/x{self.comId}/s/user-profile?type=recent&start={start}&size={size}"
        elif type == "banned": url = f"{self.api}/x{self.comId}/s/user-profile?type=banned&start={start}&size={size}"
        elif type == "featured": url = f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}"
        elif type == "leaders": url = f"{self.api}/x{self.comId}/s/user-profile?type=leaders&start={start}&size={size}"
        elif type == "curators": url = f"{self.api}/x{self.comId}/s/user-profile?type=curators&start={start}&size={size}"
        else: raise exceptions.WrongType(type)

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileCountList(json.loads(await response.text())).UserProfileCountList

    async def get_online_users(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileCountList(json.loads(await response.text())).UserProfileCountList

    async def get_online_favorite_users(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileCountList(json.loads(await response.text())).UserProfileCountList

    async def get_user_info(self, userId: str):
        """
        Information of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`User Object <aminofixasync.lib.util.objects.UserProfile>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfile(json.loads(await response.text())["userProfile"]).UserProfile

    async def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that the User is Following.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <aminofixasync.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that are Following the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <aminofixasync.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that Visited the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Visitors List <aminofixasync.lib.util.objects.visitorsList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.VisitorsList(json.loads(await response.text())).VisitorsList

    async def get_user_checkins(self, userId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/check-in/stats/{userId}?timezone={-timezone // 1000}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserCheckIns(json.loads(await response.text())).UserCheckIns

    async def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.WikiList(json.loads(await response.text())["itemList"]).WikiList

    async def get_user_achievements(self, userId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserAchievements(json.loads(await response.text())["achievements"]).UserAchievements

    async def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.InfluencerFans(json.loads(await response.text())).InfluencerFans

    async def get_blocked_users(self, start: int = 0, size: int = 25):
        """
        List of Users that the User Blocked.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Users List <aminofixasync.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def get_blocker_users(self, start: int = 0, size: int = 25):
        """
        List of Users that are Blocking the User.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`List of User IDs <List>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return json.loads(await response.text())["blockerUidList"]

    async def search_users(self, nickname: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def get_saved_blogs(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/bookmark?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserSavedBlogs(json.loads(await response.text())["bookmarkList"]).UserSavedBlogs

    async def get_leaderboard_info(self, type: str, start: int = 0, size: int = 25):
        if "24" in type or "hour" in type: url = f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=1&start={start}&size={size}"
        elif "7" in type or "day" in type: url = f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=2&start={start}&size={size}"
        elif "rep" in type: url = f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=3&start={start}&size={size}"
        elif "check" in type: url = f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=4"
        elif "quiz" in type: url = f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=5&start={start}&size={size}"
        else: raise exceptions.WrongType(type)

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def get_wiki_info(self, wikiId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.GetWikiInfo(json.loads(await response.text())).GetWikiInfo

    async def get_recent_wiki_items(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.WikiList(json.loads(await response.text())["itemList"]).WikiList

    async def get_wiki_categories(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/item-category?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.WikiCategoryList(json.loads(await response.text())["itemCategoryList"]).WikiCategoryList

    async def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/item-category/{categoryId}?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.WikiCategory(json.loads(await response.text())).WikiCategory

    async def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping/tipped-users-summary?start={start}&size={size}"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary?start={start}&size={size}"
        elif chatId: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary?start={start}&size={size}"
        elif fileId: url = f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary?start={start}&size={size}"
        else: raise exceptions.SpecifyType()

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.TippedUsersSummary(json.loads(await response.text())).TippedUsersSummary

    async def get_chat_threads(self, start: int = 0, size: int = 25):
        """
        List of Chats the account is in.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <aminofixasync.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.ThreadList(json.loads(await response.text())["threadList"]).ThreadList

    async def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
        """
        List of Public Chats of the Community.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <aminofixasync.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.ThreadList(json.loads(await response.text())["threadList"]).ThreadList

    async def get_chat_thread(self, chatId: str):
        """
        Get the Chat Object from an Chat ID.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : :meth:`Chat Object <aminofixasync.lib.util.objects.Thread>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.Thread(json.loads(await response.text())["thread"]).Thread

    async def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):
        """
        List of Messages from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - *size* : Size of the list.
            - *pageToken* : Next Page Token.

        **Returns**
            - **Success** : :meth:`Message List <aminofixasync.lib.util.objects.MessageList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """

        if pageToken is not None: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.GetMessages(json.loads(await response.text())).GetMessages

    async def get_message_info(self, chatId: str, messageId: str):
        """
        Information of an Message from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - **message** : ID of the Message.

        **Returns**
            - **Success** : :meth:`Message Object <aminofixasync.lib.util.objects.Message>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.Message(json.loads(await response.text())["message"]).Message

    async def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
        if blogId or quizId:
            if quizId is not None: blogId = quizId

            async with self.session.get(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers()) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return objects.GetBlogInfo(json.loads(await response.text())).GetBlogInfo

        elif wikiId:
            async with self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers()) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return objects.GetWikiInfo(json.loads(await response.text())).GetWikiInfo

        elif fileId:
            async with self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}", headers=self.parse_headers()) as response:
                if response.status != 200: return exceptions.CheckException(await response.text())
                else: return objects.SharedFolderFile(json.loads(await response.text())["file"]).SharedFolderFile

        else: raise exceptions.SpecifyType()

    async def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"

        if blogId or quizId:
            if quizId is not None: blogId = quizId
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}"
        elif fileId: url = f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}"
        else: raise exceptions.SpecifyType()

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.CommentList(json.loads(await response.text())["commentList"]).CommentList

    async def get_blog_categories(self, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog-category?size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogCategoryList(json.loads(await response.text())["blogCategoryList"]).BlogCategoryList

    async def get_blogs_by_category(self, categoryId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.QuizRankings(json.loads(await response.text())).QuizRankings

    async def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):
        """
        List of Wall Comments of an User.

        **Parameters**
            - **userId** : ID of the User.
            - **sorting** : Order of the Comments.
                - ``newest``, ``oldest``, ``top``
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Comments List <aminofixasync.lib.util.objects.CommentList>`

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        else: raise exceptions.WrongType(sorting)

        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.CommentList(json.loads(await response.text())["commentList"]).CommentList

    async def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
        if pageToken is not None: url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}"

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.RecentBlogs(json.loads(await response.text())).RecentBlogs

    async def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["memberList"]).UserProfileList

    async def get_notifications(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.NotificationList(json.loads(await response.text())["notificationList"]).NotificationList

    # TODO : Get notice to finish this
    async def get_notices(self, start: int = 0, size: int = 25):
        """
        :param start: Start of the List (Start: 0)
        :param size: Amount of Notices to Show
        :return: Notices List
        """
        async with self.session.get(f"{self.api}/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.NoticeList(json.loads(await response.text())["noticeList"]).NoticeList

    async def get_sticker_pack_info(self, sticker_pack_id: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.StickerCollection(json.loads(await response.text())["stickerCollection"]).StickerCollection

    async def get_sticker_packs(self):
        async with self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.StickerCollection(json.loads(await response.text())["stickerCollection"]).StickerCollection

    # TODO : Finish this (Fineshed :D)
    async def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.apis}/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}", headers=self.parse_apis_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.ChatBubble(json.loads(await response.text())["storeItemList"]).ChatBubble

    async def get_store_avatar_frames(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.apis}/x{self.comId}/s/store/items?sectionGroupId=avatar-frame&start={start}&size={size}", headers=self.parse_apis_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.AvatarFrame(json.loads(await response.text())["storeItemList"]).AvatarFrame

    # TODO : Finish this (Fineshed :D)
    async def get_store_stickers(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.apis}/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}", headers=self.parse_apis_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.StoreStickers(json.loads(await response.text())["storeItemList"]).StoreStickers

    async def get_community_stickers(self):
        async with self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection?type=community-shared", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.CommunityStickerCollection(json.loads(await response.text())).CommunityStickerCollection

    async def get_sticker_collection(self, collectionId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.StickerCollection(json.loads(await response.text())["stickerCollection"]).StickerCollection

    async def get_shared_folder_info(self):
        async with self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/stats", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.GetSharedFolderInfo(json.loads(await response.text())["stats"]).GetSharedFolderInfo

    async def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.SharedFolderFileList(json.loads(await response.text())["fileList"]).SharedFolderFileList

    #
    # MODERATION MENU
    #

    async def moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, size: int = 25):
        if userId: url = f"{self.api}/x{self.comId}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}"
        elif blogId: url = f"{self.api}/x{self.comId}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&size={size}"
        elif quizId: url = f"{self.api}/x{self.comId}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&size={size}"
        elif wikiId: url = f"{self.api}/x{self.comId}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&size={size}"
        elif fileId: url = f"{self.api}/x{self.comId}/s/admin/operation?objectId={fileId}&objectType=109&pagingType=t&size={size}"
        else: url = f"{self.api}/x{self.comId}/s/admin/operation?pagingType=t&size={size}"

        async with self.session.get(url, headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.AdminLogList(json.loads(await response.text())["adminLogList"]).AdminLogList

    async def feature(self, time: int, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        if chatId:
            if time == 1: time = 3600
            if time == 1: time = 7200
            if time == 1: time = 10800

        else:
            if time == 1: time = 86400
            elif time == 2: time = 172800
            elif time == 3: time = 259200
            else: raise exceptions.WrongType(time)

        data = {
            "adminOpName": 114,
            "adminOpValue": {
                "featuredDuration": time
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpValue"] = {"featuredType": 4}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin"

        elif blogId:
            data["adminOpValue"] = {"featuredType": 1}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/admin"

        elif wikiId:
            data["adminOpValue"] = {"featuredType": 1}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/admin"

        elif chatId:
            data["adminOpValue"] = {"featuredType": 5}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unfeature(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "adminOpName": 114,
            "adminOpValue": {},
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin"

        elif blogId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/admin"

        elif wikiId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/admin"

        elif chatId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 18
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin"

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/admin"

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{quizId}/admin"

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/admin"

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin"

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 19
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin"

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/admin"

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/blog/{quizId}/admin"

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/item/{wikiId}/admin"

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin"

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            url = f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin"

        else: raise exceptions.SpecifyType()

        async with self.session.post(url, headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def edit_titles(self, userId: str, titles: list, colors: list):
        tlt = []
        for titles, colors in zip(titles, colors):
            tlt.append({"title": titles, "color": colors})

        data = json.dumps({
            "adminOpName": 207,
            "adminOpValue": {
                "titles": tlt
            },
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    # TODO : List all warning texts
    async def warn(self, userId: str, reason: str = None):
        data = json.dumps({
            "uid": userId,
            "title": "Custom",
            "content": reason,
            "attachedObject": {
                "objectId": userId,
                "objectType": 0
            },
            "penaltyType": 0,
            "adminOpNote": {},
            "noticeType": 7,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    # TODO : List all strike texts
    async def strike(self, userId: str, time: int, title: str = None, reason: str = None):
        if time == 1: time = 3600
        elif time == 2: time = 10800
        elif time == 3: time = 21600
        elif time == 4: time = 43200
        elif time == 5: time = 86400
        else: raise exceptions.WrongType(time)

        data = json.dumps({
            "uid": userId,
            "title": title,
            "content": reason,
            "attachedObject": {
                "objectId": userId,
                "objectType": 0
            },
            "penaltyType": 1,
            "penaltyValue": time,
            "adminOpNote": {},
            "noticeType": 4,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def ban(self, userId: str, reason: str, banType: int = None):
        data = json.dumps({
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/ban", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def unban(self, userId: str, reason: str):
        data = json.dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/unban", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def reorder_featured_users(self, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/featured/reorder", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_hidden_blogs(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def get_featured_users(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileCountList(json.loads(await response.text())).UserProfileCountList

    async def review_quiz_questions(self, quizId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}?action=review", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.QuizQuestionList(json.loads(await response.text())["blog"]["quizQuestionList"]).QuizQuestionList

    async def get_recent_quiz(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def get_trending_quiz(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def get_best_quiz(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BlogList(json.loads(await response.text())["blogList"]).BlogList

    async def send_action(self, actions: list, blogId: str = None, quizId: str = None, lastAction: bool = False):
        # Action List
        # Browsing

        if lastAction is True: t = 306
        else: t = 304

        data = {
            "o": {
                "actions": actions,
                "target": f"ndc://x{self.comId}/",
                "ndcId": int(self.comId),
                "params": {"topicIds": [45841, 17254, 26542, 42031, 22542, 16371, 6059, 41542, 15852]},
                "id": "831046"
            },
            "t": t
        }

        if blogId is not None or quizId is not None:
            data["target"] = f"ndc://x{self.comId}/blog/{blogId}"
            if blogId is not None: data["params"]["blogType"] = 0
            if quizId is not None: data["params"]["blogType"] = 6

        return await self.send(json.dumps(data))

    # Provided by "spectrum#4691"
    async def purchase(self, objectId: str, objectType: int, aminoPlus: bool = True, autoRenew: bool = False):
        data = {
            "objectId": objectId,
            "objectType": objectType,
            "v": 1,
            "timestamp": int(timestamp() * 1000)
        }

        if aminoPlus: data['paymentContext'] = {'discountStatus': 1, 'discountValue': 1, 'isAutoRenew': autoRenew}
        else: data['paymentContext'] = {'discountStatus': 0, 'discountValue': 1, 'isAutoRenew': autoRenew}

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/store/purchase", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    # Provided by "spectrum#4691"
    async def apply_avatar_frame(self, avatarId: str, applyToAll: bool = True):
        """
        Apply avatar frame.

        **Parameters**
            - **avatarId** : ID of the avatar frame.
            - **applyToAll** : Apply to all.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        data = {
            "frameId": avatarId,
            "applyToAll": 0,
            "timestamp": int(timestamp() * 1000)
        }

        if applyToAll: data["applyToAll"] = 1

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/avatar-frame/apply", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def invite_to_vc(self, chatId: str, userId: str):
        """
        Invite a User to a Voice Chat

        **Parameters**
            - **chatId** - ID of the Chat
            - **userId** - ID of the User

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofixasync.lib.util.exceptions>`
        """

        data = json.dumps({
            "uid": userId
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def add_poll_option(self, blogId: str, question: str):
        data = json.dumps({
            "mediaList": None,
            "title": question,
            "type": 0,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def create_wiki_category(self, title: str, parentCategoryId: str, content: str = None):
        data = json.dumps({
            "content": content,
            "icon": None,
            "label": title,
            "mediaList": None,
            "parentCategoryId": parentCategoryId,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/item-category", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def create_shared_folder(self, title: str):
        data = json.dumps({
            "title": title,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/folders", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def submit_to_wiki(self, wikiId: str, message: str):
        data = json.dumps({
            "message": message,
            "itemId": wikiId,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list):
        data = json.dumps({
            "destinationCategoryIdList": destinationCategoryIdList,
            "actionType": "create",
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/approve", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def reject_wiki_request(self, requestId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/reject", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_wiki_submissions(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.WikiRequestList(json.loads(await response.text())["knowledgeBaseRequestList"]).WikiRequestList

    async def get_live_layer(self):
        async with self.session.get(f"{self.api}/x{self.comId}/s/live-layer/homepage?v=2", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.LiveLayer(json.loads(await response.text())["liveLayerList"]).LiveLayer

    async def apply_bubble(self, bubbleId: str, chatId: str, applyToAll: bool = False):
        data = {
            "applyToAll": 0,
            "bubbleId": bubbleId,
            "threadId": chatId,
            "timestamp": int(timestamp() * 1000)
        }

        if applyToAll is True:
            data["applyToAll"] = 1

        data = json.dumps(data)

        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/apply-bubble", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_blog_users(self, blogId: str, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic%3Ax{self.comId}%3Ausers-browsing-blog-at%3A{blogId}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileCountList(json.loads(await response.text())).UserProfileCountList

    async def get_bubble_info(self, bubbleId: str):
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.Bubble(json.loads(await response.text())["chatBubble"]).Bubble

    async def get_bubble_template_list(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/x{self.comId}/s/chat/chat-bubble/templates?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.BubbleList(json.loads(await response.text())["templateList"]).BubbleList

    async def activate_bubble(self, bubbleId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}/activate", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def deactivate_bubble(self, bubbleId: str):
        async with self.session.post(f"{self.api}/x{self.comId}/s/chat/chat-bubble/{bubbleId}/deactivate", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status
