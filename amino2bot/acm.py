import requests
import json
from time import time as timestamp
from typing import BinaryIO

from . import client
from .lib.util import exceptions, headers, device

device = device.DeviceGenerator()
headers.sid = client.Client().sid

class ACM(client.Client):
    def __init__(self, profile: str, comId: str = None):
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
        if response.status_code != 200:
            response = json.loads(response.text)
            if response["api:statuscode"] == 805: raise exceptions.CommunityNameAlreadyTaken
            if response["api:statuscode"] == 2800: raise exceptions.AccountAlreadyRestored
            else: return response

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

        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.post(f"{self.api}/g/s-x{self.comId}/community/delete-request", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code != 200:
            response = json.loads(response.text)
            if response["api:statuscode"] == 200: raise exceptions.InvalidAccountOrPassword
            if response["api:statuscode"] == 213: raise exceptions.InvalidEmail
            if response["api:statuscode"] == 214: raise exceptions.InvalidPassword
            if response["api:statuscode"] == 270: raise exceptions.VerificationRequired
            if response["api:statuscode"] == 833: raise exceptions.CommunityDeleted
            else: return response

        else: return response.status_code

    def list_communities(self, start: int = 0, size: int = 25):
        response = requests.get(f"{self.api}/g/s/community/managed?start={start}&size={size}", headers=headers.Headers().headers)
        return json.loads(response.text)

    def edit_modules(self, module: str, value):
        """
        Modules:
          chat: module.chat.enabled
          posts: module.post.enabled
          wiki: module.catalog.enabled
          | curation : module.catalog.curationEnabled
          categories: module.topicCategories.enabled
        """
        data = json.dumps({
            "path": f"module.{module}.enabled",
            "value": value,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=headers.Headers(data=data).headers, data=data)
        return json.loads(response.text)

    def get_categories(self, start: int = 0, size: int = 25):
        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.get(f"{self.api}/x{self.comId}/s/blog-category?start={start}&size={size}", headers=headers.Headers().headers)
        return json.loads(response.text)

    def change_sidepanel_color(self, color: str):
        data = json.dumps({
            "path": "appearance.leftSidePanel.style.iconColor",
            "value": color,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.post(f"{self.api}/x{self.comId}/s/community/configuration", headers=headers.Headers(data=data).headers, data=data)
        if response.status_code == 200: return response.status_code
        else: return json.loads(response.text)

    def upload_themepack_raw(self, file: BinaryIO):
        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.post(f"{self.api}/x{self.comId}/s/media/upload/target/community-theme-pack", data=file.read(), headers=headers.Headers(data=file.read()).headers)
        if response.status_code == 200: return json.loads(response.text)["mediaValue"]
        else: return json.loads(response.text)

    def upload_theme(self, themePackUrl: str):
        data = json.dumps({
            "themePackUrl": themePackUrl,
            "timestamp": int(timestamp() * 1000)
        })

        if self.comId is None: raise exceptions.CommunityNeeded
        response = requests.post(f"{self.api}/x{self.comId}/s/community/settings", data=data, headers=headers.Headers(data=data).headers)
        if response.status_code == 200: return response.status_code
        else: return json.loads(response.text)
