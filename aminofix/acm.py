import json
import time

from .client import Client
from .lib.util import (
    CommunityList,
    CommunityNeeded,
    CommunityStats,
    JoinRequest,
    NoticeList,
    SpecifyType,
    UserProfileList,
    WrongType,
    CheckException
)

__all__ = ("ACM",)

class ACM(Client):
    def __init__(self, profile, comId):
        super().__init__()
        self.profile = profile
        self.comId = comId

    # TODO : Finish the imaging sizing, might not work for every picture...
    def create_community(self, name, tagline, icon, themeColor, joinType=0, primaryLanguage="en"):
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
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/community", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def delete_community(self, email, password, verificationCode):
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
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/g/s-x{self.comId}/community/delete-request", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def list_communities(self, start=0, size=25):
        response = self.session.get(f"{self.api}/g/s/community/managed?start={start}&size={size}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return CommunityList(json.loads(response.text)["communityList"]).CommunityList

    def get_categories(self, start=0, size=25):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/blog-category?start={start}&size={size}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return json.loads(response.text)

    def change_sidepanel_color(self, color):
        data = json.dumps({
            "path": "appearance.leftSidePanel.style.iconColor",
            "value": color,
            "timestamp": int(time.time() * 1000)
        })
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return response.status_code
        else:
            return json.loads(response.text)

    def upload_themepack_raw(self, file):
        if self.comId is None:
            raise CommunityNeeded()
        data = file.read()
        response = self.session.post(f"{self.api}/x{self.comId}/s/media/upload/target/community-theme-pack", data=data, headers=self.parse_headers(data=data))
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return json.loads(response.text)

    def promote(self, userId, rank):
        rank = rank.lower().replace("agent", "transfer-agent")
        if rank.lower() not in ["transfer-agent", "leader", "curator"]:
            raise WrongType(rank)
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/user-profile/{userId}/{rank}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def get_join_requests(self, start=0, size=25):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/community/membership-request?status=pending&start={start}&size={size}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return JoinRequest(json.loads(response.text)).JoinRequest

    def accept_join_request(self, userId):
        data = json.dumps({})
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/accept", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def reject_join_request(self, userId):
        data = json.dumps({})
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/membership-request/{userId}/reject", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def get_community_stats(self):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/community/stats", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return CommunityStats(json.loads(response.text)["communityStats"]).CommunityStats

    def get_community_user_stats(self, type, start=0, size=25):
        if self.comId is None:
            raise CommunityNeeded()
        if type.lower() not in ("curator", "leader"):
            raise WrongType(type)
        response = self.session.get(f"{self.api}/x{self.comId}/s/community/stats/moderation?type={type}&start={start}&size={size}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def change_welcome_message(self, message, isEnabled=True):
        data = json.dumps({
            "path": "general.welcomeMessage",
            "value": {
                "enabled": isEnabled,
                "text": message
            },
            "timestamp": int(time.time() * 1000)
        })
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def change_guidelines(self, message):
        data = json.dumps({
            "content": message,
            "timestamp": int(time.time() * 1000)
        })
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/guideline", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def edit_community(self, name=None, description=None, aminoId=None, primaryLanguage=None, themePackUrl=None):
        data = {"timestamp": int(time.time() * 1000)}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["content"] = description
        if aminoId is not None:
            data["endpoint"] = aminoId
        if primaryLanguage is not None:
            data["primaryLanguage"] = primaryLanguage
        if themePackUrl is not None:
            data["themePackUrl"] = themePackUrl
        data = json.dumps(data)
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/settings", data=data, headers=self.parse_headers(data=data))
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def change_module(self, module, isEnabled):
        mod = {
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
            "topiccategories": "module.topicCategories.enabled"
        }.get(module)
        if not mod:
            raise SpecifyType()
        data = json.dumps({
            "path": mod,
            "value": isEnabled,
            "timestamp": int(time.time() * 1000)
        })
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def add_influencer(self, userId, monthlyFee):
        data = json.dumps({
            "monthlyFee": monthlyFee,
            "timestamp": int(time.time() * 1000)
        })
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.post(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def remove_influencer(self, userId):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.delete(f"{self.api}/x{self.comId}/s/influencer/{userId}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code

    def get_notice_list(self, start=0, size=25):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.get(f"{self.api}/x{self.comId}/s/notice?type=management&status=1&start={start}&size={size}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return NoticeList(json.loads(response.text)["noticeList"]).NoticeList

    def delete_pending_role(self, noticeId):
        if self.comId is None:
            raise CommunityNeeded()
        response = self.session.delete(f"{self.api}/x{self.comId}/s/notice/{noticeId}", headers=self.parse_headers())
        if response.status_code != 200:
            return CheckException(response.text)
        else:
            return response.status_code
