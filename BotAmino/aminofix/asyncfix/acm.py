import json
import asyncio

from time import time as timestamp
from typing import BinaryIO

from . import client
from ..lib.util import exceptions, headers, objects

class ACM(client.Client):
    def __init__(self, profile: objects.UserProfile, comId: str = None):
        client.Client.__init__(self)
        self.profile = profile
        self.comId = comId

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._close_session())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._close_session())

    async def _close_session(self):
        if not self.session.closed: await self.session.close()

    # TODO : Finish the imaging sizing, might not work for every picture...
    async def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = 0, primaryLanguage: str = "en"):
        data = json.dumps({
            "icon": {
                "height": 512.0,
                "imageMatrix": [1.6875, 0.0, 108.0, 0.0, 1.6875, 497.0, 0.0, 0.0, 1.0],
                "path": self.upload_media(icon, "image"),
                "width": 512.0,
                "x": 0.0,
                "y": 0.0
            },
            "joinType": joinType,
            "name": name,
            "primaryLanguage": primaryLanguage,
            "tagline": tagline,
            "templateId": 9,
            "themeColor": themeColor,
            "timestamp": int(timestamp() * 1000)
        })

        async with self.session.post(f"{self.api}/g/s/community", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def delete_community(self, email: str, password: str, verificationCode: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "validationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email
            },
            "deviceID": self.device_id
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/g/s-x{self.comId}/community/delete-request", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def list_communities(self, start: int = 0, size: int = 25):
        async with self.session.get(f"{self.api}/g/s/community/managed?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.CommunityList(json.loads(await response.text())["communityList"]).CommunityList

    async def get_categories(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.get(f"{self.api}/x{self.comId}/s/blog-category?start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return json.loads(await response.text())

    async def change_sidepanel_color(self, color: str):
        data = json.dumps({
            "path": "appearance.leftSidePanel.style.iconColor",
            "value": color,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return json.loads(await response.text())

    async def upload_themepack_raw(self, file: BinaryIO):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/media/upload/target/community-theme-pack", headers=headers.Headers(data=file.read()).headers, data=file.read()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return json.loads(await response.text())

    async def promote(self, userId: str, rank: str):
        rank = rank.lower().replace("agent", "transfer-agent")

        if rank.lower() not in ["transfer-agent", "leader", "curator"]:
            raise exceptions.WrongType(rank)

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{rank}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_join_requests(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.get(f"{self.api}/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.JoinRequest(json.loads(await response.text())).JoinRequest

    async def accept_join_request(self, userId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/approve", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def reject_join_request(self, userId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/reject", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_community_stats(self):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.get(f"{self.api}/x{self.comId}/s/community/stats", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.CommunityStats(json.loads(await response.text())["communityStats"]).CommunityStats

    async def get_community_user_stats(self, type: str, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        if type.lower() == "leader": target = "leader"
        elif type.lower() == "curator": target = "curator"
        else: raise exceptions.WrongType(type)

        async with self.session.get(f"{self.api}/x{self.comId}/s/community/stats/moderation?type={target}&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.UserProfileList(json.loads(await response.text())["userProfileList"]).UserProfileList

    async def change_welcome_message(self, message: str, isEnabled: bool = True):
        data = json.dumps({
            "path": "general.welcomeMessage",
            "value": {
                "enabled": isEnabled,
                "text": message
            },
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def change_guidelines(self, message: str):
        data = json.dumps({
            "content": message,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/guideline", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def edit_community(self, name: str = None, description: str = None, aminoId: str = None, primaryLanguage: str = None, themePackUrl: str = None):
        data = {"timestamp": int(timestamp() * 1000)}

        if name is not None: data["name"] = name
        if description is not None: data["content"] = description
        if aminoId is not None: data["endpoint"] = aminoId
        if primaryLanguage is not None: data["primaryLanguage"] = primaryLanguage
        if themePackUrl is not None: data["themePackUrl"] = themePackUrl

        data = json.dumps(data)

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/settings", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def change_module(self, module: str, isEnabled: bool):
        if module.lower() == "chat": mod = "module.chat.enabled"
        elif module.lower() == "livechat": mod = "module.chat.avChat.videoEnabled"
        elif module.lower() == "screeningroom": mod = "module.chat.avChat.screeningRoomEnabled"
        elif module.lower() == "publicchats": mod = "module.chat.publicChat.enabled"
        elif module.lower() == "posts": mod = "module.post.enabled"
        elif module.lower() == "ranking": mod = "module.ranking.enabled"
        elif module.lower() == "leaderboards": mod = "module.ranking.leaderboardEnabled"
        elif module.lower() == "featured": mod = "module.featured.enabled"
        elif module.lower() == "featuredposts": mod = "module.featured.postEnabled"
        elif module.lower() == "featuredusers": mod = "module.featured.memberEnabled"
        elif module.lower() == "featuredchats": mod = "module.featured.publicChatRoomEnabled"
        elif module.lower() == "sharedfolder": mod = "module.sharedFolder.enabled"
        elif module.lower() == "influencer": mod = "module.influencer.enabled"
        elif module.lower() == "catalog": mod = "module.catalog.enabled"
        elif module.lower() == "externalcontent": mod = "module.externalContent.enabled"
        elif module.lower() == "topiccategories": mod = "module.topicCategories.enabled"
        else: raise exceptions.SpecifyType(module.lower())

        data = json.dumps({
            "path": mod,
            "value": isEnabled,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def add_influencer(self, userId: str, monthlyFee: int):
        data = json.dumps({
            "monthlyFee": monthlyFee,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.parse_headers(data=data), data=data) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def remove_influencer(self, userId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()
        async with self.session.delete(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status

    async def get_notice_list(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.get(f"{self.api}/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return objects.NoticeList(json.loads(await response.text())["noticeList"]).NoticeList

    async def delete_pending_role(self, noticeId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()

        async with self.session.delete(f"{self.api}/x{self.comId}/s/notice/{noticeId}", headers=self.parse_headers()) as response:
            if response.status != 200: return exceptions.CheckException(await response.text())
            else: return response.status