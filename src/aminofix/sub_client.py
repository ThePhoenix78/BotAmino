import base64
import json
import os
import time
import uuid

import json_minify

from .client import Client
from .socket import Callbacks, SocketHandler
from .lib.util import exceptions, helpers, objects

__all__ = ("SubClient",)

class VCHeaders:
    def __init__(self, data=None):
        vc_headers = {
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "User-Agent": "Amino/45725 CFNetwork/1126 Darwin/19.5.0",  # Closest server (this one for me)
            "Host": "rt.applovin.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "Keep-Alive",
            "Accept": "*/*"
        }
        if data:
            vc_headers["Content-Length"] = str(len(data))
        self.vc_headers = vc_headers

class SubClient(Client):
    def __init__(
        self,
        comId=None,
        aminoId=None,
        *,
        client,
        deviceId=None,
        autoDevice=False,
        proxies=None,
        certificatePath=None
    ):
        self.client = client
        Client.__init__(
            self=self,
            deviceId=deviceId or client.device_id,
            userAgent=client.user_agent,
            autoDevice=autoDevice,
            proxies=proxies,
            certificatePath=certificatePath
        )
        self.sid = client.sid
        self.userId = client.userId
        self.account = client.account
        self.secret = client.secret
        self.socket = client.socket
        self.vc_connect = False
        if comId:
            self.comId = comId
            self.community = self.get_community_info(comId)
        elif aminoId:
            link = "http://aminoapps.com/c/" + aminoId
            self.comId = self.get_from_code(link).comId
            self.community = self.get_community_info(self.comId)
        else:
            raise exceptions.NoCommunity()
        try:
            self.profile = self.get_user_info(userId=client.profile.userId)
        except AttributeError:
            raise exceptions.FailedLogin()
        except exceptions.UserUnavailable:
            pass

    def __getattribute__(self, name):
        if hasattr(Callbacks, name) or hasattr(SocketHandler, name):
            return getattr(self.client, name)
        return object.__getattribute__(self, name)

    def get_invite_codes(self, status="normal", start=0, size=25):
        response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/invitation?status={status}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.InviteCodeList(json.loads(response.text)["communityInvitationList"]).InviteCodeList

    def generate_invite_code(self, duration=0, force=True):
        data = json.dumps({
            "duration": duration,
            "force": force,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s-x{self.comId}/community/invitation", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.InviteCode(json.loads(response.text)["communityInvitation"]).InviteCode

    def get_vip_users(self, start=0, size=25):
        response = self.session.get(f"{self.api}/{self.comId}/s/influencer?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def delete_invite_code(self, inviteId):
        response = self.session.delete(f"{self.api}/g/s-x{self.comId}/community/invitation/{inviteId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def post_blog(self, title, content, imageList=None, captionList=None, categoriesList=None, backgroundColor=None, fansOnly=False, extensions=None):
        mediaList = []
        if extensions is None:
            extensions = {}
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
            "latitude": 0,
            "longitude": 0,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(time.time() * 1000)
        }
        if fansOnly:
            extensions["fansOnly"] = fansOnly
        if backgroundColor:
            extensions["style"] = {"backgroundColor": backgroundColor}
        if categoriesList:
            data["taggedBlogCategoryIdList"] = categoriesList
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def post_wiki(self, title, content, icon=None, imageList=None, keywords=None, backgroundColor=None, fansOnly=False):
        mediaList, extensions = [], {}
        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])
        data = {
            "label": title,
            "content": content,
            "mediaList": mediaList,
            "eventSource": "GlobalComposeMenu",
            "timestamp": int(time.time() * 1000)
        }
        if icon:
            data["icon"] = icon
        if keywords:
            data["keywords"] = keywords
        if fansOnly:
            extensions["fansOnly"] = fansOnly
        if backgroundColor:
            extensions["style"] = {"backgroundColor": backgroundColor}
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/item", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def edit_blog(self, blogId, title=None, content=None, imageList=None, categoriesList=None, backgroundColor=None, fansOnly=False):
        mediaList, extensions = [], {}
        for image in imageList:
            mediaList.append([100, self.upload_media(image, "image"), None])
        data = {
            "address": None,
            "mediaList": mediaList,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "PostDetailView",
            "timestamp": int(time.time() * 1000)
        }
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if fansOnly:
            extensions["fansOnly"] = fansOnly
        if backgroundColor:
            extensions["style"] = {"backgroundColor": backgroundColor}
        if categoriesList:
            data["taggedBlogCategoryIdList"] = categoriesList
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_blog(self, blogId):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_wiki(self, wikiId):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def repost_blog(self, content=None, blogId=None, wikiId=None):
        if blogId is not None:
            refObjectId, refObjectType = blogId, 1
        elif wikiId is not None:
            refObjectId, refObjectType = wikiId, 2
        else:
            raise exceptions.SpecifyType()
        data = json.dumps({
            "content": content,
            "refObjectId": refObjectId,
            "refObjectType": refObjectType,
            "type": 2,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def check_in(self, tz=-time.timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def repair_check_in(self, method=0):
        data = {"timestamp": int(time.time() * 1000)}
        if method == 0:
            data["repairMethod"] = "1"  # Coins
        elif method == 1:
            data["repairMethod"] = "2"  # Amino+
        else:
            raise ValueError(f"Invalid method. Expected 0 or 1. Got {method!r}")
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in/repair", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def lottery(self, tz=-time.timezone // 1000):
        data = json.dumps({
            "timezone": tz,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/check-in/lottery", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.LotteryLog(json.loads(response.text)["lotteryLog"]).LotteryLog

    def edit_profile(
        self,
        nickname=None,
        content=None,
        icon=None,
        backgroundColor=None,
        backgroundImage=None,
        defaultBubbleId=None,
        chatRequestPrivilege=None,
        imageList=None,
        captionList=None,
        titles=None,
        colors=None
    ):
        mediaList, extensions = [], {}
        data = {"timestamp": int(time.time() * 1000)}
        if captionList is not None:
            for image, caption in zip(imageList, captionList):
                mediaList.append([100, self.upload_media(image, "image"), caption])
        else:
            if imageList is not None:
                for image in imageList:
                    mediaList.append([100, self.upload_media(image, "image"), None])
        if mediaList:
            data["mediaList"] = mediaList
        if nickname:
            data["nickname"] = nickname
        if icon:
            data["icon"] = self.upload_media(icon, "image")
        if content:
            data["content"] = content
        if chatRequestPrivilege:
            extensions["privilegeOfChatInviteRequest"] = chatRequestPrivilege
        if backgroundImage:
            extensions["style"] = {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}
        if backgroundColor:
            extensions["style"] = {"backgroundColor": backgroundColor}
        if defaultBubbleId:
            extensions["defaultBubbleId"] = defaultBubbleId
        if titles:
            customTitles = []
            if not colors:
                colors = [None] * len(titles)
            for title, color in zip(titles, colors):
                customTitles.append({"title": title, "color": color})
            extensions["customTitles"] = customTitles
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            self.profile = objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile
            return response.status_code

    def vote_poll(self, blogId, optionId):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option/{optionId}/vote", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def comment(self, message, userId=None, blogId=None, wikiId=None, replyTo=None, isGuest=False):
        data = {
            "content": message,
            "stickerId": None,
            "type": 0,
            "timestamp": int(time.time() * 1000)
        }
        if replyTo:
            data["respondTo"] = replyTo
        if isGuest:
            comType = "g-comment"
        else:
            comType = "comment"
        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{comType}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/{comType}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/{comType}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200:
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_comment(self, commentId, userId=None, blogId=None, wikiId=None):
        if userId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def like_blog(self, blogId=None, wikiId=None):
        """
        Like a Blog, Multiple Blogs or a Wiki.

        **Parameters**
            - **blogId** : ID of the Blog or List of IDs of the Blogs. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {
            "value": 4,
            "timestamp": int(time.time() * 1000)
        }
        if blogId:
            if isinstance(blogId, str):
                data["eventSource"] = "UserProfileView"
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?cv=1.2", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
            elif isinstance(blogId, list):
                data["targetIdList"] = blogId
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/x{self.comId}/s/feed/vote", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
            else:
                raise exceptions.WrongType()
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self. comId}/s/item/{wikiId}/vote?cv=1.2", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unlike_blog(self, blogId=None, wikiId=None):
        if blogId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/vote?eventSource=UserProfileView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def like_comment(self, commentId, userId=None, blogId=None, wikiId=None):
        data = {
            "value": 1,
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unlike_comment(self, commentId, userId=None, blogId=None, wikiId=None):
        if userId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def upvote_comment(self, blogId, commentId):
        data = json.dumps({
            "value": 1,
            "eventSource": "PostDetailView",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def downvote_comment(self, blogId, commentId):
        data = json.dumps({
            "value": -1,
            "eventSource": "PostDetailView",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?cv=1.2&value=-1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unvote_comment(self, blogId, commentId):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment/{commentId}/vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def reply_wall(self, userId, commentId, message):
        data = json.dumps({
            "content": message,
            "stackedId": None,
            "respondTo": commentId,
            "type": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def send_active_obj(self, startTime=None, endTime=None, optInAdsFlags=2147483647, tz=-time.timezone // 1000, timers= None, timestamp=None):
        if not timestamp:
            timestamp = int(time.time() * 1000)
        data = {"userActiveTimeChunkList": [{"start": startTime, "end": endTime}], "timestamp": timestamp, "optInAdsFlags": optInAdsFlags, "timezone": tz} 
        if timers:
            data["userActiveTimeChunkList"] = timers
        data = json_minify.json_minify(json.dumps(data))
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/stats/user-active-time", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath) 
        if response.status_code != 200: 
            return exceptions.CheckException(response.text) 
        else:
            return response.status_code

    def activity_status(self, status):
        if "on" in status.lower(): status = 1
        elif "off" in status.lower(): status = 2
        else:
            raise exceptions.WrongType(status)
        data = json.dumps({
            "onlineStatus": status,
            "duration": 86400,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/online-status", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    # TODO : Finish this
    def watch_ad(self):
        response = self.session.post(f"{self.api}/g/s/wallet/ads/video/start", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def check_notifications(self):
        response = self.session.post(f"{self.api}/x{self.comId}/s/notification/checked", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_notification(self, notificationId):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/notification/{notificationId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def clear_notifications(self):
        response = self.session.delete(f"{self.api}/x{self.comId}/s/notification", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def start_chat(self, userId, message, title=None, content=None, isGlobal=False, publishToGlobal=False):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType(type(userId))
        data = {
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(time.time() * 1000)
        }
        if isGlobal is True:
            data["type"] = 2
            data["eventSource"] = "GlobalComposeMenu"
        else:
            data["type"] = 0
        if publishToGlobal is True:
            data["publishToGlobal"] = 1
        else:
            data["publishToGlobal"] = 0
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Thread(json.loads(response.text)["thread"]).Thread

    def invite_to_chat(self, userId, chatId):
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType(type(userId))
        data = json.dumps({
            "uids": userIds,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/invite", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def add_to_favorites(self, userId):
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-group/quick-access/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def send_coins(self, coins, blogId=None, chatId=None, objectId=None, transactionId=None):
        url = None
        if transactionId is None:
            transactionId = str(uuid.uuid4())
        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(time.time() * 1000)
        }
        if blogId is not None:
            url = f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping"
        if chatId is not None:
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping"
        if objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.api}/x{self.comId}/s/tipping"
        if url is None:
            raise exceptions.SpecifyType()
        data = json.dumps(data)
        response = self.session.post(url, headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def thank_tip(self, chatId, userId):
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users/{userId}/thank", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def follow(self, userId):
        """
        Follow an User or Multiple Users.

        **Parameters**
            - **userId** : ID of the User or List of IDs of the Users.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if isinstance(userId, str):
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif isinstance(userId, list):
            data = json.dumps({"targetUidList": userId, "timestamp": int(time.time() * 1000)})

            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.WrongType(type(userId))
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unfollow(self, userId):
        """
        Unfollow an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.delete(f"{self.api}/x{self.comId}/s/user-profile/{self.profile.userId}/joined/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def block(self, userId):
        """
        Block an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unblock(self, userId):
        """
        Unblock an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.delete(f"{self.api}/x{self.comId}/s/block/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def visit(self, userId):
        """
        Visit an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}?action=visit", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def flag(self, reason, flagType, userId=None, blogId=None, wikiId=None, asGuest=False):
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

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if reason is None:
            raise exceptions.ReasonNeeded()
        if flagType is None:
            raise exceptions.FlagTypeNeeded()
        data = {
            "flagType": flagType,
            "message": reason,
            "timestamp": int(time.time() * 1000)
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
        else:
            raise exceptions.SpecifyType()
        if asGuest:
            flg = "g-flag"
        else:
            flg = "flag"
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/{flg}", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def send_message(
        self,
        chatId,
        message=None,
        messageType=0,
        file=None,
        fileType=None,
        replyTo=None,
        mentionUserIds=None,
        stickerId=None,
        embedId=None,
        embedType=None,
        embedLink=None,
        embedTitle=None,
        embedContent=None,
        embedImage=None
    ):
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

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        mentions, extensions = [], {}
        if message is not None and file is None:
            message = message.replace("<$", "\u200e\u200f").replace("$>", "\u202c\u202d")
        if mentionUserIds:
            for mention_uid in mentionUserIds:
                mentions.append({"uid": mention_uid})
        if embedImage:
            embedImage = [[100, self.upload_media(embedImage, "image"), None]]
        data = {
            "type": messageType,
            "content": message,
            "clientRefId": int(time.time() / 10 % 1000000000),
            "timestamp": int(time.time() * 1000)
        }
        if embedId or embedType or embedLink or embedTitle or embedContent or embedImage:
            data["attachedObject"] = {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            }
        if mentions:
            extensions["mentionedArray"] = mentions
        if replyTo:
            data["replyMessageId"] = replyTo
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
            else:
                raise exceptions.SpecifyType(fileType)
            data["mediaUploadValue"] = base64.b64encode(helpers.read_bytes(file)).decode()
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def full_embed(self, link, image, message, chatId):
        data = {
            "type": 0,
            "content": message,
            "extensions": {
                "linkSnippetList": [{
                    "link": link,
                    "mediaType": 100,
                    "mediaUploadValue": base64.b64encode(helpers.read_bytes(image)).decode(),
                    "mediaUploadValueContentType": "image/png"
                }]
            },
            "clientRefId": int(time.time() / 10 % 100000000),
            "timestamp": int(time.time() * 1000),
            "attachedObject": None
        }
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_message(self, chatId, messageId, asStaff=False, reason=None):
        """
        Delete a Message from a Chat.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.
            - **asStaff** : If execute as a Staff member (Leader or Curator).
            - **reason** : Reason of the action to show on the Moderation History.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {
            "adminOpName": 102,
            "timestamp": int(time.time() * 1000)
        }
        if asStaff and reason:
            data["adminOpNote"] = {"content": reason}
        data = json.dumps(data)
        if not asStaff:
            response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def mark_as_read(self, chatId, messageId):
        """
        Mark a Message from a Chat as Read.

        **Parameters**
            - **messageId** : ID of the Message.
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "messageId": messageId,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/mark-as-read", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def edit_chat(
        self,
        chatId,
        doNotDisturb=None,
        pinChat=None,
        title=None,
        icon=None,
        backgroundImage=None,
        content=None,
        announcement=None,
        coHosts=None,
        keywords=None,
        pinAnnouncement=None,
        publishToGlobal=None,
        canTip=None,
        viewOnly=None,
        canInvite=None,
        fansOnly=None
    ):
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

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        extensions = {}
        data = {"timestamp": int(time.time() * 1000)}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if icon:
            data["icon"] = icon
        if keywords:
            data["keywords"] = keywords
        if announcement:
            extensions["announcement"] = announcement
        if pinAnnouncement:
            extensions["pinAnnouncement"] = pinAnnouncement
        if fansOnly:
            extensions["fansOnly"] = fansOnly
        if publishToGlobal:
            data["publishToGlobal"] = 0
        if not publishToGlobal:
            data["publishToGlobal"] = 1
        if extensions:
            data["extensions"] = extensions
        res = []
        if doNotDisturb is not None:
            if doNotDisturb:
                data = json.dumps({"alertOption": 2, "timestamp": int(time.time() * 1000)})
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(time.time() * 1000)})
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/alert", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
        if pinChat is not None:
            if pinChat:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/pin", data=data, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
            if not pinChat:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/unpin", data=data, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
        if backgroundImage is not None:
            data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(time.time() * 1000)})
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}/background", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200:
                res.append(exceptions.CheckException(response.text))
            else:
                res.append(response.status_code)
        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(time.time() * 1000)})
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/co-host", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200:
                res.append(exceptions.CheckException(response.text))
            else:
                res.append(response.status_code)
        if viewOnly is not None:
            if viewOnly:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/enable", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
            if not viewOnly:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/view-only/disable", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
        if canInvite is not None:
            if canInvite:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/enable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
            if not canInvite:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/members-can-invite/disable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
        if canTip is not None:
            if canTip:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/enable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
            if not canTip:
                response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping-perm-status/disable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200:
                    res.append(exceptions.CheckException(response.text))
                else:
                    res.append(response.status_code)
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            res.append(exceptions.CheckException(response.text))
        else:
            res.append(response.status_code)
        return res

    def transfer_host(self, chatId, userIds):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def transfer_organizer(self, chatId, userIds):
        self.transfer_host(chatId, userIds)

    def accept_host(self, chatId, requestId):
        data = json.dumps({})
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def accept_organizer(self, chatId, requestId):
        self.accept_host(chatId, requestId)

    def kick(self, userId, chatId, allowRejoin=True):
        if allowRejoin:
            allowRejoin = 1
        if not allowRejoin:
            allowRejoin = 0
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def join_chat(self, chatId):
        """
        Join an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def leave_chat(self, chatId):
        """
        Leave an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member/{self.profile.userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_chat(self, chatId):
        """
        Delete a Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.delete(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def subscribe(self, userId, autoRenew=False, transactionId=None):
        if transactionId is None:
            transactionId = str(uuid.uuid4())
        data = json.dumps({
            "paymentContext": {
                "transactionId": transactionId,
                "isAutoRenew": autoRenew
            },
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}/subscribe", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def promotion(self, noticeId: str, type: str = "accept"):
        response = self.session.post(f"{self.api}/x{self.comId}/s/notice/{noticeId}/{type}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def play_quiz_raw(self, quizId, quizAnswerList, quizMode=0):
        data = json.dumps({
            "mode": quizMode,
            "quizAnswerList": quizAnswerList,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def play_quiz(self, quizId, questionIdsList, answerIdsList, quizMode=0):
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
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def vc_permission(self, chatId, permission):
        """Voice Chat Join Permissions
        1 - Open to Everyone
        2 - Approval Required
        3 - Invite Only
        """
        if permission not in (1, 2, 3):
            raise ValueError(f"Invalid permission type. Expected 1, 2 or 3. Got {permission!r}")
        data = json.dumps({
            "vvChatJoinType": permission,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-permission", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_vc_reputation_info(self, chatId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.VcReputation(json.loads(response.text)).VcReputation

    def claim_vc_reputation(self, chatId):
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/avchat-reputation", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.VcReputation(json.loads(response.text)).VcReputation

    def get_all_users(self, type="recent", start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_online_users(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/live-layer?topic=ndtopic:x{self.comId}:online-members&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_online_favorite_users(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-group/quick-access?type=online&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def get_user_info(self, userId):
        """
        Information of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`User Object <amino.lib.util.objects.UserProfile>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile

    def get_user_following(self, userId, start=0, size=25):
        """
        List of Users that the User is Following.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_user_followers(self, userId, start=0, size=25):
        """
        List of Users that are Following the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_user_visitors(self, userId, start=0, size=25):
        """
        List of Users that Visited the User.

        **Parameters**
            - **userId** : ID of the User.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Visitors List <amino.lib.util.objects.visitorsList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.VisitorsList(json.loads(response.text)).VisitorsList

    def get_user_checkins(self, userId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/check-in/stats/{userId}?timezone={-time.timezone // 1000}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserCheckIns(json.loads(response.text)).UserCheckIns

    def get_user_blogs(self, userId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog?type=user&q={userId}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_user_wikis(self, userId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item?type=user-all&start={start}&size={size}&cv=1.2&uid={userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    def get_user_achievements(self, userId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/achievements", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserAchievements(json.loads(response.text)["achievements"]).UserAchievements

    def get_influencer_fans(self, userId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/influencer/{userId}/fans?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.InfluencerFans(json.loads(response.text)).InfluencerFans

    def get_blocked_users(self, start=0, size=25):
        """
        List of Users that the User Blocked.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Users List <amino.lib.util.objects.UserProfileList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_blocker_users(self, start=0, size=25):
        """
        List of Users that are Blocking the User.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`List of User IDs <List>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/block?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["blockerUidList"]

    def search_users(self, nickname, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_saved_blogs(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/bookmark?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserSavedBlogs(json.loads(response.text)["bookmarkList"]).UserSavedBlogs

    def get_leaderboard_info(self, type, start=0, size=25):
        if "24" in type or "hour" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=1&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif "7" in type or "day" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=2&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif "rep" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=3&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif "check" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=4", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif "quiz" in type: response = self.session.get(f"{self.api}/g/s-x{self.comId}/community/leaderboard?rankingType=5&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.WrongType(type)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_wiki_info(self, wikiId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo

    def get_recent_wiki_items(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item?type=catalog-all&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WikiList(json.loads(response.text)["itemList"]).WikiList

    def get_wiki_categories(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item-category?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WikiCategoryList(json.loads(response.text)["itemCategoryList"]).WikiCategoryList

    def get_wiki_category(self, categoryId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/item-category/{categoryId}?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else: return objects.WikiCategory(json.loads(response.text)).WikiCategory

    def get_tipped_users(self, blogId=None, wikiId=None, quizId=None, fileId=None, chatId=None, start=0, size=25):
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{blogId}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif chatId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/tipping/tipped-users-summary?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.TippedUsersSummary(json.loads(response.text)).TippedUsersSummary

    def get_chat_threads(self, start=0, size=25):
        """
        List of Chats the account is in.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <amino.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    def get_public_chat_threads(self, type="recommended", start=0, size=25):
        """
        List of Public Chats of the Community.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Chat List <amino.lib.util.objects.ThreadList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread?type=public-all&filterType={type}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.ThreadList(json.loads(response.text)["threadList"]).ThreadList

    def get_chat_thread(self, chatId):
        """
        Get the Chat Object from an Chat ID.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : :meth:`Chat Object <amino.lib.util.objects.Thread>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Thread(json.loads(response.text)["thread"]).Thread

    def get_chat_messages(self, chatId, size=25, pageToken=None):
        """
        List of Messages from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - *size* : Size of the list.
            - *pageToken* : Next Page Token.

        **Returns**
            - **Success** : :meth:`Message List <amino.lib.util.objects.MessageList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if pageToken is not None:
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"
        response = self.session.get(url, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.GetMessages(json.loads(response.text)).GetMessages

    def get_message_info(self, chatId, messageId):
        """
        Information of an Message from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - **message** : ID of the Message.

        **Returns**
            - **Success** : :meth:`Message Object <amino.lib.util.objects.Message>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Message(json.loads(response.text)["message"]).Message

    def get_blog_info(self, blogId=None, wikiId=None, quizId=None, fileId=None):
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{blogId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.GetBlogInfo(json.loads(response.text)).GetBlogInfo
        elif wikiId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo
        elif fileId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.SharedFolderFile(json.loads(response.text)["file"]).SharedFolderFile
        else:
            raise exceptions.SpecifyType()

    def get_blog_comments(self, blogId=None, wikiId=None, quizId=None, fileId=None, sorting="newest", start=0, size=25):
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    def get_blog_categories(self, size: int = 25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog-category?size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogCategoryList(json.loads(response.text)["blogCategoryList"]).BlogCategoryList

    def get_blogs_by_category(self, categoryId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog-category/{categoryId}/blog-list?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_quiz_rankings(self, quizId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}/quiz/result?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.QuizRankings(json.loads(response.text)).QuizRankings

    def get_wall_comments(self, userId, sorting, start=0, size=25):
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

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        else:
            raise exceptions.WrongType(sorting)
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile/{userId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    def get_recent_blogs(self, pageToken=None, start=0, size=25):
        if pageToken is not None:
            url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/x{self.comId}/s/feed/blog-all?pagingType=t&start={start}&size={size}"
        response = self.session.get(url, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.RecentBlogs(json.loads(response.text)).RecentBlogs

    def get_chat_users(self, chatId, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["memberList"]).UserProfileList

    def get_notifications(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/notification?pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.NotificationList(json.loads(response.text)["notificationList"]).NotificationList

    def get_notices(self, start=0, size=25):
        """
        :param start: Start of the List (Start: 0)
        :param size: Amount of Notices to Show
        :return: Notices List
        """
        response = self.session.get(f"{self.api}/x{self.comId}/s/notice?type=usersV2&status=1&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.NoticeList(json.loads(response.text)["noticeList"]).NoticeList

    def get_sticker_pack_info(self, sticker_pack_id):
        response = self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection/{sticker_pack_id}?includeStickers=true", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    def get_sticker_packs(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection?includeStickers=false&type=my-active-collection&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    # TODO : Finish this
    def get_store_chat_bubbles(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=chat-bubble&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            response = json.loads(response.text)
            return response

    # TODO : Finish this
    def get_store_stickers(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/store/items?sectionGroupId=sticker&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            response = json.loads(response.text)
            return response

    def get_community_stickers(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection?type=community-shared&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommunityStickerCollection(json.loads(response.text)).CommunityStickerCollection

    def get_sticker_collection(self, collectionId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/sticker-collection/{collectionId}?includeStickers=true", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.StickerCollection(json.loads(response.text)["stickerCollection"]).StickerCollection

    def get_shared_folder_info(self):
        response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/stats", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.GetSharedFolderInfo(json.loads(response.text)["stats"]).GetSharedFolderInfo

    def get_shared_folder_files(self, type="latest", start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/shared-folder/files?type={type}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.SharedFolderFileList(json.loads(response.text)["fileList"]).SharedFolderFileList

    # MODERATION MENU
    def moderation_history(self, userId=None, blogId=None, wikiId=None, quizId=None, fileId=None, start=0, size=25):
        if userId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={userId}&objectType=0&pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={blogId}&objectType=1&pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif quizId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={quizId}&objectType=1&pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={wikiId}&objectType=2&pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?objectId={fileId}&objectType=109&pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            response = self.session.get(f"{self.api}/x{self.comId}/s/admin/operation?pagingType=t&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.AdminLogList(json.loads(response.text)["adminLogList"]).AdminLogList

    def feature(self, time, userId=None, chatId=None, blogId=None, wikiId=None):
        if chatId:
            if time == 1: time = 3600
            elif time == 2: time = 7200
            else: time = 10800
        else:
            if time == 1: time = 86400
            elif time == 2: time = 172800
            else: time = 259200
        data = {
            "adminOpName": 114,
            "adminOpValue": {
                "featuredDuration": time
            },
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["adminOpValue"] = {"featuredType": 4}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["adminOpValue"] = {"featuredType": 1}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["adminOpValue"] = {"featuredType": 1}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif chatId:
            data["adminOpValue"] = {"featuredType": 5}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def unfeature(self, userId=None, chatId=None, blogId=None, wikiId=None):
        data = {
            "adminOpName": 114,
            "adminOpValue": {},
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif chatId:
            data["adminOpValue"] = {"featuredType": 0}
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def hide(self, userId=None, chatId=None, blogId=None, wikiId=None, quizId=None, fileId=None, reason=None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["adminOpName"] = 18
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 9
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def unhide(self, userId=None, chatId=None, blogId=None, wikiId=None, quizId=None, fileId=None, reason=None):
        data = {
            "adminOpNote": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["adminOpName"] = 19
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif quizId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{quizId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/item/{wikiId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif chatId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            data["adminOpName"] = 110
            data["adminOpValue"] = 0
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/files/{fileId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def edit_titles(self, userId, titles, colors):
        tlt = []
        for titles, colors in zip(titles, colors):
            tlt.append({"title": titles, "color": colors})
        data = json.dumps({
            "adminOpName": 207,
            "adminOpValue": {
                "titles": tlt
            },
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    # TODO : List all warning texts
    def warn(self, userId, reason=None):
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
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    # TODO : List all strike texts
    def strike(self, userId, duration, title=None, reason=None):
        if duration == 1: duration = 86400
        elif duration == 2: duration = 10800
        elif duration == 3: duration = 21600
        elif duration == 4: duration = 43200
        elif duration == 5: duration = 86400
        else:
            raise exceptions.WrongType(time)
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
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/notice", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def ban(self, userId, reason, banType=None):
        data = json.dumps({
            "reasonType": banType,
            "note": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/ban", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def unban(self, userId, reason):
        data = json.dumps({
            "note": {
                "content": reason
            },
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/unban", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def reorder_featured_users(self, userIds):
        data = json.dumps({
            "uidList": userIds,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/featured/reorder", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def get_hidden_blogs(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/blog-disabled?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_featured_users(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/user-profile?type=featured&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def review_quiz_questions(self, quizId):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog/{quizId}?action=review", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.QuizQuestionList(json.loads(response.text)["blog"]["quizQuestionList"]).QuizQuestionList

    def get_recent_quiz(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog?type=quizzes-recent&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_trending_quiz(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-trending?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_best_quiz(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/feed/quiz-best-quizzes?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def send_action(self, actions, blogId=None, quizId=None, lastAction=False):
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
        return self.send(json.dumps(data))

    # Provided by "spectrum#4691"
    def purchase(self, objectId, objectType, autoRenew=False, aminoPlus=True):
        data = {
            "paymentContext": {
                "discountStatus": int(aminoPlus),
                "discountValue": 1,
                "isAutoRenew": autoRenew
            },
            "objectId": objectId,
            "objectType": objectType,
            "v": 1,
            "timestamp": int(time.time() * 1000)
        }
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/store/purchase", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    # Provided by "spectrum#4691"
    def apply_avatar_frame(self, avatarId, applyToAll=True):
        """
        Apply avatar frame.

        **Parameters**
            - **avatarId** : ID of the avatar frame.
            - **applyToAll** : Apply to all.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`

        """

        data = {"frameId": avatarId,
                "applyToAll": 0,
                "timestamp": int(time.time() * 1000)}
        if applyToAll: data["applyToAll"] = 1
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/avatar-frame/apply", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def invite_to_vc(self, chatId, userId):
        """
        Invite a User to a Voice Chat

        **Parameters**
            - **chatId** - ID of the Chat
            - **userId** - ID of the User

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "uid": userId
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/{chatId}/vvchat-presenter/invite/", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def add_poll_option(self, blogId, question):
        data = json.dumps({
            "mediaList": None,
            "title": question,
            "type": 0,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/blog/{blogId}/poll/option", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def create_wiki_category(self, title, parentCategoryId, content=None):
        data = json.dumps({
            "content": content,
            "icon": None,
            "label": title,
            "mediaList": None,
            "parentCategoryId": parentCategoryId,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/item-category", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def create_shared_folder(self, title: str):
        data = json.dumps({
            "title":title,
            "timestamp":int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/shared-folder/folders", headers=self.parse_headers(data=data),data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def submit_to_wiki(self, wikiId, message):
        data = json.dumps({
            "message": message,
            "itemId": wikiId,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def accept_wiki_request(self, requestId, destinationCategoryIdList):
        data = json.dumps({
            "destinationCategoryIdList": destinationCategoryIdList,
            "actionType": "create",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/approve", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def reject_wiki_request(self, requestId):
        data = json.dumps({})
        response = self.session.post(f"{self.api}/x{self.comId}/s/knowledge-base-request/{requestId}/reject", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_wiki_submissions(self, start=0, size=25):
        response = self.session.get(f"{self.api}/x{self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WikiRequestList(json.loads(response.text)["knowledgeBaseRequestList"]).WikiRequestList

    def get_live_layer(self):
        response = self.session.get(f"{self.api}/x{self.comId}/s/live-layer/homepage?v=2", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.LiveLayer(json.loads(response.text)["liveLayerList"]).LiveLayer

    def apply_bubble(self, bubbleId, chatId, applyToAll=False):
        data = {
            "applyToAll": 0,
            "bubbleId": bubbleId,
            "threadId": chatId,
            "timestamp": int(time.time() * 1000)
        }
        if applyToAll is True:
            data["applyToAll"] = 1
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{self.comId}/s/chat/thread/apply-bubble", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code
