import requests
import json
from time import time as timestamp
from typing import BinaryIO

from . import client
from .lib.util import exceptions, headers, device, objects

device = device.DeviceGenerator()
headers.sid = client.Client().sid

class ACM(client.Client):
    def __init__(self, profile: objects.UserProfile, comId: str = None):
        client.Client.__init__(self)

        self.profile = profile
        self.comId = comId

    # TODO : Finish the imaging sizing, might not work for every picture...
    def create_community(self, name: str, tagline: str, icon: BinaryIO, themeColor: str, joinType: int = 0, primaryLanguage: str = "en"):
        data = json.dumps({
            "icon": {
                "height": 512.0,
                "imageMatrix": [1.6875, 0.0, 108.0, 0.0, 1.6875, 497.0, 0.0, 0.0, 1.0],
                "path": self.upload_media(icon),
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

        response = requests.post(f"{self.api}/g/s/community", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def delete_community(self, email: str, password: str, verificationCode: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "validationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email
            },
            "deviceID": device.device_id
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/g/s-x{self.comId}/community/delete-request", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def list_communities(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/g/s/community/managed?start={start}&size={size}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommunityList(json.loads(response.text)["communityList"]).CommunityList

    def get_categories(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.get(f"{self.api}/x{self.comId}/s/blog-category?start={start}&size={size}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def change_sidepanel_color(self, color: str):
        data = json.dumps({
            "path": "appearance.leftSidePanel.style.iconColor",
            "value": color,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code == 200: return response.status_code
        else: return json.loads(response.text)

    def upload_themepack_raw(self, file: BinaryIO):
        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/media/upload/target/community-theme-pack", data=file.read(), headers=headers.Headers(data=file.read()).headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return json.loads(response.text)

    def promote(self, userId: str, rank: str):
        rank = rank.lower().replace("agent", "transfer-agent")

        if rank.lower() not in ["transfer-agent", "leader", "curator"]:
            raise exceptions.WrongType(rank)

        data = json.dumps({})

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{rank}", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_join_requests(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        response = requests.get(f"{self.api}/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.JoinRequest(json.loads(response.text)).JoinRequest

    def accept_join_request(self, userId: str):
        data = json.dumps({})

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/accept", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def reject_join_request(self, userId: str):
        data = json.dumps({})

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/reject", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_community_stats(self):
        if self.comId is None: raise exceptions.CommunityNeeded()

        response = requests.get(f"{self.api}/x{self.comId}/s/community/stats", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.CommunityStats(json.loads(response.text)["communityStats"]).CommunityStats

    def get_community_user_stats(self, type: str, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()

        if type.lower() == "leader": target = "leader"
        elif type.lower() == "curator": target = "curator"
        else: raise exceptions.WrongType(type)

        response = requests.get(f"{self.api}/x{self.comId}/s/community/stats/moderation?type={target}&start={start}&size={size}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def change_welcome_message(self, message: str, isEnabled: bool = True):
        data = json.dumps({
            "path": "general.welcomeMessage",
            "value": {
                "enabled": isEnabled,
                "text": message
            },
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def change_guidelines(self, message: str):
        data = json.dumps({
            "content": message,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/guideline", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def edit_community(self, name: str = None, description: str = None, aminoId: str = None, primaryLanguage: str = None, themePackUrl: str = None):
        data = {"timestamp": int(timestamp() * 1000)}

        if name is not None: data["name"] = name
        if description is not None: data["content"] = description
        if aminoId is not None: data["endpoint"] = aminoId
        if primaryLanguage is not None: data["primaryLanguage"] = primaryLanguage
        if themePackUrl is not None: data["themePackUrl"] = themePackUrl

        data = json.dumps(data)

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/settings", data=data, headers=headers.Headers(data=data).headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def change_module(self, module: str, isEnabled: bool):
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
        else: raise exceptions.SpecifyType()

        data = json.dumps({
            "path": mod,
            "value": isEnabled,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def add_influencer(self, userId: str, monthlyFee: int):
        data = json.dumps({
            "monthlyFee": monthlyFee,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.post(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def remove_influencer(self, userId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.delete(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code

    def get_notice_list(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.get(f"{self.api}/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return objects.NoticeList(json.loads(response.text)["noticeList"]).NoticeList

    def delete_pending_role(self, noticeId: str):
        if self.comId is None: raise exceptions.CommunityNeeded()
        response = requests.delete(f"{self.api}/x{self.comId}/s/notice/{noticeId}", headers=headers.Headers().headers)
        if response.status_code != 200: return exceptions.CheckException(json.loads(response.text))
        else: return response.status_code
