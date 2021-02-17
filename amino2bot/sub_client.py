import json
import base64
import requests

from uuid import UUID
from os import urandom
from time import timezone
from typing import BinaryIO
from binascii import hexlify
from time import time as timestamp

from . import client
from .lib.util import exceptions, headers, device, objects

device = device.DeviceGenerator()
headers.sid = client.Client().sid

class SubClient(client.Client):
    def __init__(self, comId: str, profile: objects.UserProfile):
        client.Client.__init__(self)

        if not comId: raise exceptions.NoCommunity()

        self.comId = comId
        try: self.profile: objects.UserProfile = self.get_user_info(userId=profile.userId)
        except AttributeError: raise exceptions.FailedLogin()

    def post_blog(self, title: str, content: str, categoriesList: list = None, backgroundColor: str = None, fansOnly: bool = False, extensions: dict = None):
        data = {
            "address": None,
            "content": content,
            "title": title,
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
        response = requests.post(f"{self.api}/x{self.comId}/s/blog", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def post_wiki(self, title: str, content: str, icon: str = None, keywords: str = None, backgroundColor: str = None, images: list = None, fansOnly: bool = False):
        if images:
            images_list = []
            for item in images:
                content = content.replace(item.replace_key, f"[IMG={item.replace_key}]")
                images_list.append(item.media_list_item)

        data = {
            "label": title,
            "content": content,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(timestamp() * 1000)
        }

        if icon: data["icon"] = icon
        if keywords: data["keywords"] = keywords
        if fansOnly: data["extensions"] = {"fansOnly": fansOnly}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        data = json.dumps(data)
        response = requests.post(f"{self.api}/x{self.comId}/s/item", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_blog(self, blogId: str, title: str = None, content: str = None, categoriesList: list = None, backgroundColor: str = None, images: list = None, fansOnly: bool = False):
        if images:
            images_list = []
            for item in images:
                content = content.replace(item.replace_key, f"[IMG={item.replace_key}]")
                images_list.append(item.media_list_item)

        else: images_list = None

        data = {
            "address": None,
            "mediaList": images_list,
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
        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_blog(self, blogId: str):
        response = requests.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def repost_blog(self, content: str = None, blogId: str = None, wikiId: str = None):
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

        response = requests.post(f"{self.api}/x{self.comId}/s/blog", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def check_in(self, tz: str = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/check-in", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def repair_check_in(self, method: int = 0):
        data = {"timestamp": int(timestamp() * 1000)}
        if method == 0: data["repairMethod"] = "1"  # Coins
        if method == 1: data["repairMethod"] = "2"  # Amino+

        data = json.dumps(data)
        response = requests.post(f"{self.api}/x{self.comId}/s/check-in/repair", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def lottery(self, tz: str = -timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/check-in/lottery", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.LotteryLog(json.loads(response.text)["lotteryLog"]).LotteryLog

    def edit_profile(self, nickname: str = None, content: str = None, icon: str = None, chatRequestPrivilege: str = None, mediaList: list = None, backgroundImage: str = None, backgroundColor: str = None, titles: list = None, defaultBubbleId: str = None):
        data = {"timestamp": int(timestamp() * 1000)}

        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = icon
        if content: data["content"] = content
        if mediaList: data["mediaList"] = mediaList
        if chatRequestPrivilege: data["extensions"] = {"privilegeOfChatInviteRequest": chatRequestPrivilege}
        if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if titles: data["extensions"] = {"customTitles": titles}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}

        data = json.dumps(data)
        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def vote_poll(self, blogId: str, optionId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def comment(self, message: str, userId: str = None, blogId: str = None, wikiId: str = None, replyTo: str = None, isGuest: bool = False):
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
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{comType}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/{comType}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/{comType}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId: response = requests.delete(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif blogId: response = requests.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def like_blog(self, blogId: [str, list] = None, wikiId: str = None):
        """
        Like a Blog, Multiple Blogs or a Wiki.

        **Parameters**
            - **blogId** : ID of the Blog or List of IDs of the Blogs. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        data = {
            "value": 4,
            "timestamp": int(timestamp() * 1000)
        }

        if blogId:
            if isinstance(blogId, str):
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?cv=1.2", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

            elif isinstance(blogId, list):
                data["targetIdList"] = blogId
                data = json.dumps(data)
                response = requests.post(f"{self.api}/x{self.comId}/s/feed/vote", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

            else: raise exceptions.WrongType

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self. comId}/s/item/{wikiId}/vote?cv=1.2", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unlike_blog(self, blogId: str = None, wikiId: str = None):
        if blogId: response = requests.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "value": 1,
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unlike_comment(self, commentId: str, userId: str = None, blogId: str = None, wikiId: str = None):
        if userId: response = requests.delete(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif blogId: response = requests.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def upvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def downvote_comment(self, blogId: str, commentId: str):
        data = json.dumps({
            "value": -1,
            "eventSource": "PostDetailView",
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=-1", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unvote_comment(self, blogId: str, commentId: str):
        response = requests.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def reply_wall(self, userId: str, commentId: str, message: str):
        data = json.dumps({
            "content": message,
            "stackedId": None,
            "respondTo": commentId,
            "type": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    # TODO : Fix stay online object, returning Invalid Request
    def send_active_obj(self):
        data = json.dumps({
            "userActiveTimeChunkList": [{
                "start": int(timestamp()),
                "end": int(timestamp()) + int(30)
            }],
            "optInAdsFlags": 2147483647,
            "timezone": -timezone // 1000
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/community/stats/user-active-time", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def activity_status(self, status: str):
        if "on" in status.lower(): status = 1
        elif "off" in status.lower(): status = 2
        else: raise exceptions.WrongType(status)

        data = json.dumps({
            "onlineStatus": status,
            "duration": 86400,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    # TODO : Finish this
    def watch_ad(self):
        response = requests.post(f"{self.api}/g/s/wallet/ads/video/start", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def check_notifications(self):
        response = requests.post(f"{self.api}/x{self.comId}/s/notification/checked", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_notification(self, notificationId: str):
        response = requests.delete(f"{self.api}/x{self.comId}/s/notification/{notificationId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def clear_notifications(self):
        response = requests.delete(f"{self.api}/x{self.comId}/s/notification", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def start_chat(self, userId: [str, list], message: str, title: str = None, content: str = None, isGlobal: bool = False, publishToGlobal: bool = False):
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

        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def invite_to_chat(self, userId: [str, list], chatId: str):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise exceptions.WrongType(type(userId))

        data = json.dumps({
            "uids": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/invite", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def add_to_favorites(self, userId: str):
        response = requests.post(f"{self.api}/x{self.comId}/s/user-group/quick-access/{userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def send_coins(self, coins: int, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
        url = None
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(timestamp() * 1000)
        }

        if blogId is not None: url = f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping"
        if chatId is not None: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping"
        if objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.api}/x{self.comId}/s/tipping"

        if url is None: raise exceptions.SpecifyType()

        data = json.dumps(data)
        response = requests.post(url, headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def thank_tip(self, chatId: str, userId: str):
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def follow(self, userId: [str, list]):
        """
        Follow an User or Multiple Users.

        **Parameters**
            - **userId** : ID of the User or List of IDs of the Users.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        if isinstance(userId, str):
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)

        elif isinstance(userId, list):
            data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.WrongType(type(userId))

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unfollow(self, userId: str):
        """
        Unfollow an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.delete(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def block(self, userId: str):
        """
        Block an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.post(f"{self.api}/x{self.comId}/s/block/{userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def unblock(self, userId: str):
        """
        Unblock an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.delete(f"{self.api}/x{self.comId}/s/block/{userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def visit(self, userId: str):
        """
        Visit an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}?action=visit", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def flag(self, reason: str, flagType: int, userId: str = None, blogId: str = None, wikiId: str = None, asGuest: bool = False):
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

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
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
        response = requests.post(f"{self.api}/x{self.comId}/s/{flg}", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def send_message(self, chatId: str, message: str = None, messageType: int = 0, file: BinaryIO = None, fileType: str = None, replyTo: str = None, mentionUserIds: list = None, stickerId: str = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None, embedImage: BinaryIO = None):
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

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """

        if message is not None and file is None:
            message = message.replace("<$", "‎‏").replace("$>", "‬‭")

        mentions = []
        if mentionUserIds:
            for mention_uid in mentionUserIds:
                mentions.append({"uid": mention_uid})

        if embedImage:
            embedImage = [[100, self.upload_media(embedImage), None]]

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
            "extensions": {"mentionedArray": mentions},
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

            else: raise exceptions.SpecifyType()

            data["mediaUploadValue"] = base64.b64encode(file.read()).decode()

        data = json.dumps(data)
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_message(self, chatId: str, messageId: str, asStaff: bool = False, reason: str = None):
        """
        Delete a Message from a Chat.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.
            - **asStaff** : If execute as a Staff member (Leader or Curator).
            - **reason** : Reason of the action to show on the Moderation History.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        data = {
            "adminOpName": 102,
            "adminOpNote": {"content": reason},
            "timestamp": int(timestamp() * 1000)
        }

        data = json.dumps(data)
        if not asStaff: response = requests.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def mark_as_read(self, chatId: str, messageId: str):
        """
        Mark a Message from a Chat as Read.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        data = json.dumps({
            "messageId": messageId,
            "timestamp": int(timestamp() * 1000)
        })
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", headers=headers.Headers().headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_chat(self, chatId: str, doNotDisturb: bool = None, pinChat: bool = None, title: str = None, icon: str = None, backgroundImage: str = None, content: str = None, announcement: str = None, coHosts: list = None, keywords: list = None, pinAnnouncement: bool = None, publishToGlobal: bool = None, canTip: bool = None, viewOnly: bool = None, canInvite: bool = None, fansOnly: bool = None):
        """
        Send a Message to a Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - **title** : Title of the Chat.
            - **content** : Content of the Chat.
            - **icon** : Icon of the Chat.
            - **backgroundImage** : Url of the Background Image of the Chat.
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

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
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
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(timestamp() * 1000)})
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

        if pinChat is not None:
            if pinChat:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/pin", data=data, headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

            if not pinChat:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/unpin", data=data, headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

        if backgroundImage is not None:
            data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(timestamp() * 1000)})
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/background", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
            else: res.append(response.status_code)

        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(timestamp() * 1000)})
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/co-host", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
            else: res.append(response.status_code)

        if viewOnly is not None:
            if viewOnly:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/enable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

            if not viewOnly:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/disable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

        if canInvite is not None:
            if canInvite:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/enable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

            if not canInvite:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/disable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

        if canTip is not None:
            if canTip:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/enable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

            if not canTip:
                response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/disable", data=data, headers=headers.Headers(data=data).headers, proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
                else: res.append(response.status_code)

        data = json.dumps(data)
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: res.append(exceptions.CheckException(json.loads(response.text)))
        else: res.append(response.status_code)

        return res

    def transfer_host(self, chatId: str, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def transfer_organizer(self, chatId: str, userIds: list):
        self.transfer_host(chatId, userIds)

    def accept_host(self, chatId: str, requestId: str):
        data = json.dumps({"timestamp": int(timestamp() * 1000)})

        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def accept_organizer(self, chatId: str):
        """
        Accept a chat transfer organizer request.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """

        chat_thread = self.get_chat_thread(chatId).json
        transferRequest = chat_thread['extensions'].get('organizerTransferRequest')
        if(not transferRequest):
            raise exceptions.TransferRequestNeeded
        return self.accept_host(chatId, transferRequest["requestId"])

    def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        if allowRejoin: allowRejoin = 1
        if not allowRejoin: allowRejoin = 0
        response = requests.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def join_chat(self, chatId: str):
        """
        Join an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def leave_chat(self, chatId: str):
        """
        Leave an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def subscribe(self, userId: str, autoRenew: str = False, transactionId: str = None):
        if transactionId is None: transactionId = str(UUID(hexlify(urandom(16)).decode('ascii')))

        data = json.dumps({
            "paymentContext": {
                "transactionId": transactionId,
                "isAutoRenew": autoRenew
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/influencer/{userId}/subscribe", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def promotion(self, noticeId: str, type: str = "accept"):
        response = requests.post(f"{self.api}/x{self.comId}/s/notice/{noticeId}/{type}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def play_quiz_xd(self, quizId: str, quizAnswerList, quizMode: int = 0):
        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def play_quiz(self, quizId: str, questionIdsList: list, answerIdsList: list, quizMode: int = 0):
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

        response = requests.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def vc_permission(self, chatId: str, permission: int):
        """Voice Chat Join Permissions
        1 - Open to Everyone
        2 - Approval Required
        3 - Invite Only
        """
        data = json.dumps({
            "vvChatJoinType": permission,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_vc_reputation_info(self, chatId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.VcReputation(json.loads(response.text)).VcReputation

    def claim_vc_reputation(self, chatId: str):
        response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.VcReputation(json.loads(response.text)).VcReputation

    def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent": response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=recent&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif type == "banned": response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=banned&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif type == "featured": response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif type == "leaders": response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=leaders&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif type == "curators": response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=curators&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.WrongType(type)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_online_users(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_online_favorite_users(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_user_info(self, userId: str):
        """
        Information of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`User Object <amino.lib.util.objects.UserProfile>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile

    def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that the User is Following.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that are Following the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        """
        List of Users that Visited the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Visitors List <amino.lib.util.objects.visitorsList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.VisitorsList(json.loads(response.text)).VisitorsList

    def get_user_checkins(self, userId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/check-in/stats/{userId}?timezone={-timezone // 1000}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserCheckIns(json.loads(response.text)).UserCheckIns

    def get_user_blogs(self, userId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_user_wikis(self, userId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    def get_user_achievements(self, userId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/achievements", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserAchievements(json.loads(response.text)["achievements"]).UserAchievements

    def get_influencer_fans(self, userId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.InfluencerFans(json.loads(response.text)).InfluencerFans

    def get_blocked_users(self, start: int = 0, size: int = 25):
        """
        List of Users that the User Blocked.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Users List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/{self.comId}/s/block?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_blocker_users(self, start: int = 0, size: int = 25):
        """
        List of Users that are Blocking the User.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`List of User IDs <List>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/block/full-list?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["blockerUidList"]

    def search_users(self, nickname: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_saved_blogs(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/bookmark?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserSavedBlogs(json.loads(response.text)["bookmarkList"]).UserSavedBlogs

    def get_leaderboard_info(self, type: str, start: int = 0, size: int = 25):
        if "24" in type or "hour" in type: response = requests.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=1&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif "7" in type or "day" in type: response = requests.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=2&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif "rep" in type: response = requests.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=3&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif "check" in type: response = requests.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=4", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif "quiz" in type: response = requests.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=5&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.WrongType(type)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_wiki_info(self, wikiId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo

    def get_recent_wiki_items(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    def get_wiki_categories(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/item-category?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.WikiCategoryList(json.loads(response.text)["itemCategoryList"]).WikiCategoryList

    def get_wiki_category(self, categoryId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/item-category/{categoryId}?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.WikiCategory(json.loads(response.text)).WikiCategory

    def get_tipped_users(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, chatId: str = None, start: int = 0, size: int = 25):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = requests.get(f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping/tipped-users-summary?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.get(f"{self.api}/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif chatId: response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif fileId: response = requests.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.TippedUsersSummary(json.loads(response.text)).TippedUsersSummary

    def get_chat_threads(self, start: int = 0, size: int = 25):
        """
        List of Chats the account is in.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <amino.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    def get_public_chat_threads(self, type: str = "recommended", start: int = 0, size: int = 25):
        """
        List of Public Chats of the Community.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <amino.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    def get_chat_thread(self, chatId: str):
        """
        Get the Chat Object from an Chat ID.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : :meth:`Chat Object <amino.lib.util.objects.Thread>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Thread(json.loads(response.text)["thread"]).Thread

    def get_chat_messages(self, chatId: str, size: int = 25, pageToken: str = None):
        """
        List of Messages from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - *size* : Size of the list.
            - *pageToken* : Next Page Token.

        **Returns**
            - **Success** : :meth:`Message List <amino.lib.util.objects.MessageList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """

        if pageToken is not None: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"

        response = requests.get(url, headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetMessages(json.loads(response.text)).GetMessages

    def get_message_info(self, chatId: str, messageId: str):
        """
        Information of an Message from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - **message** : ID of the Message.

        **Returns**
            - **Success** : :meth:`Message Object <amino.lib.util.objects.Message>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.Message(json.loads(response.text)["message"]).Message

    def get_blog_info(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None):
        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = requests.get(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.GetBlogInfo(json.loads(response.text)).GetBlogInfo

        elif wikiId:
            response = requests.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo

        elif fileId:
            response = requests.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
            else: return objects.SharedFolderFile(json.loads(response.text)["file"]).SharedFolderFile

        else: raise exceptions.SpecifyType()

    def get_blog_comments(self, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, sorting: str = "newest", start: int = 0, size: int = 25):
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"

        if blogId or quizId:
            if quizId is not None: blogId = quizId
            response = requests.get(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.get(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif fileId: response = requests.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()

        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    def get_blog_categories(self, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/blog-category?size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogCategoryList(json.loads(response.text)["blogCategoryList"]).BlogCategoryList

    def get_quiz_rankings(self, quizId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.QuizRankings(json.loads(response.text)).QuizRankings

    def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):
        """
        List of Wall Comments of an User.

        **Parameters**
            - **userId** : ID of the User.
            - **sorting** : Order of the Comments.
                - ``newest``, ``oldest``, ``top``
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Comments List <amino.lib.util.objects.CommentList>`

            - **Fail** : :meth:`Exceptions <amino.lib.util.exceptions>`
        """
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        else: raise exceptions.WrongType(sorting)

        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    def get_recent_blogs(self, pageToken: str = None, start: int = 0, size: int = 25):
        if pageToken is not None: url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&pageToken={pageToken}&size={size}"
        else: url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}"

        response = requests.get(url, headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.RecentBlogs(json.loads(response.text)).RecentBlogs

    def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["memberList"]).UserProfileList

    def get_notifications(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.NotificationList(json.loads(response.text)["notificationList"]).NotificationList

    # TODO : Get notice to finish this
    def get_notices(self, start: int = 0, size: int = 25):
        """
        :param start: Start of the List (Start: 0)
        :param size: Amount of Notices to Show
        :return: Notices List
        """
        response = requests.get(f"{self.api}/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)["noticeList"]

    def get_sticker_pack_info(self, sticker_pack_id: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    # TODO : Finish this
    def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else:
            response = json.loads(response.text)
            del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
            return response

    # TODO : Finish this
    def get_store_stickers(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else:
            response = json.loads(response.text)
            del response["api:message"], response["api:statuscode"], response["api:duration"], response["api:timestamp"]
            return response

    def get_community_stickers(self):
        response = requests.get(f"{self.api}/x{self.comId}/s/sticker-collection?type=community-shared", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommunityStickerCollection(json.loads(response.text)).CommunityStickerCollection

    def get_sticker_collection(self, collectionId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    def get_shared_folder_info(self):
        response = requests.get(f"{self.api}/x{self.comId}/s/shared-folder/stats", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.GetSharedFolderInfo(json.loads(response.text)["stats"]).GetSharedFolderInfo

    def get_shared_folder_files(self, type: str = "latest", start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.SharedFolderFileList(json.loads(response.text)["fileList"]).SharedFolderFileList

    #
    # MODERATION MENU
    #

    def moderation_history(self, userId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, size: int = 25):
        if userId: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif blogId: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif quizId: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        elif fileId: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={fileId}&objectType=109&pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        else: response = requests.get(f"{self.api}/x{self.comId}/s/admin/operation?pagingType=t&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.AdminLogList(json.loads(response.text)["adminLogList"]).AdminLogList

    def feature(self, time: int, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        if chatId:
            if time == 1: time = 3600
            if time == 2: time = 7200
            if time == 3: time = 10800

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
            data["adminOpValue"].update({"featuredType": 4})
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["adminOpValue"].update({"featuredType": 1})
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["adminOpValue"].update({"featuredType": 1})
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif chatId:
            data["adminOpValue"].update({"featuredType": 5})
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def unfeature(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        data = {
            "adminOpName": 114,
            "adminOpValue": {},
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif chatId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def hide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 18
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def unhide(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None, quizId: str = None, fileId: str = None, reason: str = None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        }

        if userId:
            data["adminOpName"] = 19
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = requests.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)

        else: raise exceptions.SpecifyType()
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def edit_titles(self, userId: str, titles: list, colors: list):
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

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    # TODO : List all warning texts
    def warn(self, userId: str, reason: str = None):
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

        response = requests.post(f"{self.api}/x{self.comId}/s/notice", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    # TODO : List all strike texts
    def strike(self, userId: str, time: int, title: str = None, reason: str = None):
        if time == 1: time = 86400
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

        response = requests.post(f"{self.api}/x{self.comId}/s/notice", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def ban(self, userId: str, reason: str, banType: int = None):
        data = json.dumps({
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/ban", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def unban(self, userId: str, reason: str):
        data = json.dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/unban", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def reorder_featured_users(self, userIds: list):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(timestamp() * 1000)
        })

        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/featured/reorder", headers=headers.Headers(data=data).headers, data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def get_hidden_blogs(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_featured_users(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def review_quiz_questions(self, quizId: str):
        response = requests.get(f"{self.api}/x{self.comId}/s/blog/{quizId}?action=review", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.QuizQuestionList(json.loads(response.text)["blog"]["quizQuestionList"]).QuizQuestionList

    def get_recent_quiz(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_trending_quiz(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_best_quiz(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}", headers=headers.Headers().headers, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def send_action(self, actions: list, blogId: str = None, quizId: str = None, lastAction: bool = False):
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

        return self.socket.send(json.dumps(data))
