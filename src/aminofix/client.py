import base64
import json
import locale
import threading
import time
import uuid

import requests

from .lib.util import exceptions, headers, objects, helpers
from .socket import Callbacks, SocketHandler

__all__ = ("Client",)

#@dorthegra/IDörthe#8835 thanks for support!

class Client(Callbacks, SocketHandler):
    def __init__(
        self,
        deviceId=None,
        userAgent="Apple iPhone13,4 iOS v15.6.1 Main/3.12.9",
        proxies=None,
        certificatePath=None,
        socket_trace=False,
        socketDebugging=False,
        socket_enabled=True,
        autoDevice=False
    ):
        self.api = "https://service.aminoapps.com/api/v1"
        self.authenticated = False
        self.configured = False
        self.session = requests.Session()
        self.autoDevice = autoDevice
        self.device_id = deviceId or helpers.gen_deviceId()
        self.user_agent = userAgent
        self.socket_enabled = socket_enabled
        SocketHandler.__init__(self, socket_trace=socket_trace, debug=socketDebugging)
        Callbacks.__init__(self)
        self.proxies = proxies
        self.certificatePath = certificatePath
        self.sid = None
        self.userId = None
        self.account = objects.UserProfile({})
        self.profile = objects.UserProfile({})
        self.secret = None
        self.active_live_chats = set()

    def parse_headers(self, data=None, type=None):
        deviceId = helpers.gen_deviceId() if self.autoDevice else self.device_id
        return headers.ApisHeaders(deviceId=deviceId, user_agent=self.user_agent, auid=self.userId, sid=self.sid, data=data, type=type).headers

    def start_channel(self, comId, chatId, channelType):
        """Start a live chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.
        channelType : `int`
            The Type of the Channel

        """
        self.join_channel(comId, chatId, 1, channelType)
        self.send(json.dumps({
                "o": {
                    "ndcId": comId,
                    "threadId": chatId,
                    "joinRole": 1,
                    "channelType": channelType,
                    "id": "2154531"
                },
                "t": 108
            }))
        time.sleep(2)
        self.active_live_chats.add(chatId)

    def end_channel(self, comId, chatId):
        if chatId in self.active_live_chats:
            self.active_live_chats.remove(chatId)
        self.send(json.dumps({
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "channelType": 0,
                "id": "2154531"
            },
            "t": 108
        }))
        time.sleep(1)
        self.send(json.dumps({
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": 2,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }))
        time.sleep(1)

    def join_channel(self, comId, chatId, joinType, channelType):
        """Joins a Channel

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat
        joinType : `int`
            The Role of the join request
        channelType : `int`
            The Type of the Channel

        """
        self.send(json.dumps({
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "channelType": channelType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }))
        time.sleep(1)

    def start_voice_chat(self, comId, chatId):
        """Start a voice call/chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.start_channel(comId, chatId, 1)

    def end_voice_chat(self, comId, chatId):
        """End the voice call/chat

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.

        """
        self.end_channel(comId, chatId)

    def start_avatar_chat(self, comId, chatId):
        """Start an avatar call/chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.start_channel(comId, chatId, 3)

    def end_avatar_chat(self, comId, chatId):
        """End an avatar call/chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.end_channel(comId, chatId)

    def start_video_chat(self, comId, chatId):
        """Start a live stream in the chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.start_channel(comId, chatId, 4)

    def end_video_chat(self, comId, chatId):
        """End a video call/chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.end_channel(comId, chatId)

    def start_screen_room(self, comId, chatId):
        """Start a screening room in the chat

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.start_channel(comId, chatId, 5)

    def end_screen_room(self, comId, chatId):
        """End a screening room

        Parameters
        ----------
        comId : `int`
            The community ID of the chat.
        chatId : `str`
            The ID of the chat.

        """
        self.end_channel(comId, chatId)

    def join_voice_chat(self, comId, chatId):
        """Joins a Voice Chat

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat

        """
        self.join_channel(comId, chatId, 2, 1)

    def join_avatar_chat(self, comId, chatId):
        """Joins a Avatar Chat

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat

        """
        self.join_channel(comId, chatId, 2, 3)

    def join_video_chat(self, comId, chatId):
        """Joins a Video Chat

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat

        """
        self.join_channel(comId, chatId, 2, 4)

    def join_screen_room(self, comId, chatId):
        """Joins a Screening Room

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat

        """
        self.join_channel(comId, chatId, 2, 5)

    def fetch_channel(self, comId, chatId):
        """Request Channel Agora Token

        The response will be handled in the `on_fetch_channel` event.

        Parameters
        ----------
        comId : `int`
            The ID of the Community
        chatId : `str`
            The ID of the Chat

        """
        self.send(json.dumps({
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "id": "2154531"
            },
            "t": 200
        }))

    def login_sid(self, SID):
        """
        Login into an account with an SID

        **Parameters**
            - **SID** : SID of the account
        """
        uId = helpers.sid_to_uid(SID)
        self.authenticated = True
        self.sid = SID
        self.userId = uId
        self.account = self.get_account_info()
        self.profile = self.get_user_info(self.userId)
        if self.socket_enabled:
            self.run_amino_socket()

    def login(self, email, password):
        """
        Login into an account.

        **Parameters**
            - **email** : Email of the account.
            - **password** : Password of the account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/login", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            exceptions.CheckException(response.text)
        else:
            self.authenticated = True
            log = json.loads(response.text)
            self.sid = log["sid"]
            self.userId = log["auid"]
            self.account = objects.UserProfile(log["account"]).UserProfile
            self.profile = objects.UserProfile(log["userProfile"]).UserProfile
            self.secret = log["secret"]
            if self.socket_enabled:
                self.run_amino_socket()
            return log

    def login_phone(self, phoneNumber, password):
        """
        Login into an account.

        **Parameters**
            - **phoneNumber** : Phone number of the account.
            - **password** : Password of the account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "phoneNumber": phoneNumber,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/login", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        self.run_amino_socket()
        if response.status_code != 200:
            exceptions.CheckException(response.text)
        else:
            self.authenticated = True
            log = json.loads(response.text)
            self.sid = log["sid"]
            self.userId = log["auid"]
            self.account = objects.UserProfile(log["account"]).UserProfile
            self.profile = objects.UserProfile(log["userProfile"]).UserProfile
            self.secret = log["secret"]
            if self.socket_enabled:
                self.run_amino_socket()
            return log

    def login_secret(self, secret):
        """
        Login into an account.

        **Parameters**
            - **secret** : Secret of the account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "v": 2,
            "secret": secret,
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/login", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        self.run_amino_socket()
        if response.status_code != 200:
            exceptions.CheckException(response.text)
        else:
            self.authenticated = True
            log = json.loads(response.text)
            self.sid = log["sid"]
            self.userId = log["auid"]
            self.account = objects.UserProfile(log["account"]).UserProfile
            self.profile = objects.UserProfile(log["userProfile"]).UserProfile
            if self.socket_enabled:
                self.run_amino_socket()
            return log

    def register(self, nickname, email, password, verificationCode, deviceId=None):
        """
        Register an account.

        **Parameters**
            - **nickname** : Nickname of the account.
            - **email** : Email of the account.
            - **password** : Password of the account.
            - **verificationCode** : Verification code.
            - **deviceId** : The device id being registered to.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if deviceId == None:
            deviceId = self.device_id
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": deviceId,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "validationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email
            },
            "type": 1,
            "identity": email,
            "timestamp": int(time.time() * 1000)
        })        
        response = self.session.post(f"{self.api}/g/s/auth/register", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath, timeout=timeout)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def restore(self, email, password):
        """
        Restore a deleted account.

        **Parameters**
            - **email** : Email of the account.
            - **password** : Password of the account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "email": email,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/account/delete-request/cancel", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def logout(self):
        """
        Logout from an account.

        **Parameters**
            - No parameters required.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "deviceID": self.device_id,
            "clientType": 100,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/logout", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            self.authenticated = False
            self.sid = None
            self.userId = None
            self.account = objects.UserProfile({})
            self.profile = objects.UserProfile({})
            if self.socket_enabled:
                self.close()
            return response.status_code

    def configure(self, age, gender):
        """
        Configure the settings of an account.

        **Parameters**
            - **age** : Age of the account. Minimum is 13.
            - **gender** : Gender of the account.
                - ``Male``, ``Female`` or ``Non-Binary``

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if gender.lower() == "male":
            gender = 1
        elif gender.lower() == "female":
            gender = 2
        elif gender.lower() == "non-binary":
            gender = 255
        else:
            raise exceptions.SpecifyType()
        if age <= 12:
            raise exceptions.AgeTooLow()
        data = json.dumps({
            "age": age,
            "gender": gender,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/persona/profile/basic", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def verify(self, email, code):
        """
        Verify an account.

        **Parameters**
            - **email** : Email of the account.
            - **code** : Verification code.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "validationContext": {
                "type": 1,
                "identity": email,
                "data": {"code": code}},
            "deviceID": self.device_id,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/auth/check-security-validation", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def request_verify_code(self, email, resetPassword=False):
        """
        Request an verification code to the targeted email.

        **Parameters**
            - **email** : Email of the account.
            - **resetPassword** : If the code should be for Password Reset.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {
            "identity": email,
            "type": 1,
            "deviceID": self.device_id
        }
        if resetPassword is True:
            data["level"] = 2
            data["purpose"] = "reset-password"
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/auth/request-security-validation", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath, timeout=timeout)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def activate_account(self, email, code):
        """
        Activate an account.

        **Parameters**
            - **email** : Email of the account.
            - **code** : Verification code.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "type": 1,
            "identity": email,
            "data": {"code": code},
            "deviceID": self.device_id
        })
        response = self.session.post(f"{self.api}/g/s/auth/activate-email", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    # Provided by "𝑰 𝑵 𝑻 𝑬 𝑹 𝑳 𝑼 𝑫 𝑬#4082"
    def delete_account(self, password):
        """
        Delete an account.

        **Parameters**
            - **password** : Password of the account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "deviceID": self.device_id,
            "secret": f"0 {password}"
        })
        response = self.session.post(f"{self.api}/g/s/account/delete-request", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def change_password(self, email, password, code):
        """
        Change password of an account.

        **Parameters**
            - **email** : Email of the account.
            - **password** : Password of the account.
            - **code** : Verification code.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "updateSecret": f"0 {password}",
            "emailValidationContext": {
                "data": {
                    "code": code
                },
                "type": 1,
                "identity": email,
                "level": 2,
                "deviceID": self.device_id
            },
            "phoneNumberValidationContext": None,
            "deviceID": self.device_id
        })
        response = self.session.post(f"{self.api}/g/s/auth/reset-password", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def check_device(self, deviceId):
        """
        Check if the Device ID is valid.

        **Parameters**
            - **deviceId** : ID of the Device.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "deviceID": deviceId,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -time.timezone // 1000,
            "systemPushEnabled": True,
            "locale": locale.getdefaultlocale()[0],
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/device", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            self.configured = True
            return response.status_code

    def get_account_info(self):
        response = self.session.get(f"{self.api}/g/s/account", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfile(json.loads(response.text)["account"]).UserProfile

    def upload_media(self, file, fileType):
        """
        Upload file to the amino servers.

        **Parameters**
            - **file** : File to be uploaded.

        **Returns**
            - **Success** : Url of the file uploaded to the server.

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if fileType == "audio":
            type = "audio/aac"
        elif fileType == "image":
            type = "image/jpg"
        elif fileType == "gif":
            type = "image/gif"
        else:
            raise exceptions.SpecifyType(fileType)
        data = helpers.read_bytes(file)
        response = self.session.post(f"{self.api}/g/s/media/upload", data=data, headers=self.parse_headers(data, type), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200:
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["mediaValue"]

    def get_eventlog(self):
        response = self.session.get(f"{self.api}/g/s/eventlog/profile?language=en", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)

    def sub_clients(self, start=0, size=25):
        """
        List of Communities the account is in.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Community List <amino.lib.util.objects.CommunityList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if not self.authenticated:
            raise exceptions.NotLoggedIn()
        response = self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommunityList(json.loads(response.text)["communityList"]).CommunityList

    def sub_clients_profile(self, start=0, size=25):
        if not self.authenticated:
            raise exceptions.NotLoggedIn()
        response = self.session.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["userInfoInCommunities"]

    def get_user_info(self, userId):
        """
        Information of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`User Object <amino.lib.util.objects.UserProfile>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile

    def watch_ad(self):
        tapjoy = headers.Tapjoy(self.userId)
        data = json.dumps(tapjoy.data) 
        response = self.session.post("https://ads.tapdaq.com/v4/analytics/reward", data=data, headers=tapjoy.headers)
        if response.status_code != 204:
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

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
        response = self.session.get(f"{self.api}/g/s/chat/thread?type=joined-me&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Thread(json.loads(response.text)["thread"]).Thread

    def get_chat_users(self, chatId, start=0, size=25):
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["memberList"]).UserProfileList

    def join_chat(self, chatId):
        """
        Join an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.delete(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def start_chat(self, userId, message, title=None, content=None, isGlobal=False, publishToGlobal=False):
        """
        Start an Chat with an User or List of Users.

        **Parameters**
            - **userId** : ID of the User or List of User IDs.
            - **message** : Starting Message.
            - **title** : Title of Group Chat.
            - **content** : Content of Group Chat.
            - **isGlobal** : If Group Chat is Global.
            - **publishToGlobal** : If Group Chat should show in Global.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType()
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
        response = self.session.post(f"{self.api}/g/s/chat/thread", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Thread(json.loads(response.text)["thread"]).Thread

    def invite_to_chat(self, userId, chatId):
        """
        Invite a User or List of Users to a Chat.

        **Parameters**
            - **userId** : ID of the User or List of User IDs.
            - **chatId** : ID of the Chat.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if isinstance(userId, str):
            userIds = [userId]
        elif isinstance(userId, list):
            userIds = userId
        else:
            raise exceptions.WrongType
        data = json.dumps({
            "uids": userIds,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/invite", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def kick(self, userId, chatId, allowRejoin=True):
        if allowRejoin: allowRejoin = 1
        if not allowRejoin: allowRejoin = 0
        response = self.session.delete(f"{self.api}/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={allowRejoin}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_chat_messages(self, chatId, size=25, pageToken=None):
        """
        List of Messages from an Chat.

        **Parameters**
            - **chatId** : ID of the Chat.
            - *size* : Size of the list.
            - *size* : Size of the list.
            - *pageToken* : Next Page Token.

        **Returns**
            - **Success** : :meth:`Message List <amino.lib.util.objects.MessageList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if pageToken is not None:
            url = f"{self.api}/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&pageToken={pageToken}&size={size}"
        else:
            url = f"{self.api}/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"
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
            - **messageId** : ID of the Message.

        **Returns**
            - **Success** : :meth:`Message Object <amino.lib.util.objects.Message>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Message(json.loads(response.text)["message"]).Message

    def get_community_info(self, comId):
        """
        Information of an Community.

        **Parameters**
            - **comId** : ID of the Community.

        **Returns**
            - **Success** : :meth:`Community Object <amino.lib.util.objects.Community>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Community(json.loads(response.text)["community"]).Community

    def search_community(self, aminoId):
        """
        Search a Community byt its Amino ID.

        **Parameters**
            - **aminoId** : Amino ID of the Community.

        **Returns**
            - **Success** : :meth:`Community List <amino.lib.util.objects.CommunityList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/search/amino-id-and-link?q={aminoId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            response = json.loads(response.text)["resultList"]
            if len(response) == 0:
                raise exceptions.CommunityNotFound(aminoId)
            else:
                return objects.CommunityList([com["refObject"] for com in response]).CommunityList

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
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/joined?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/member?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
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
            - **Success** : :meth:`Visitors List <amino.lib.util.objects.VisitorsList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/visitors?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.VisitorsList(json.loads(response.text)).VisitorsList

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
        response = self.session.get(f"{self.api}/g/s/block?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileList(json.loads(response.text)["userProfileList"]).UserProfileList

    def get_blog_info(self, blogId=None, wikiId=None, quizId=None, fileId=None):
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            response = self.session.get(f"{self.api}/g/s/blog/{blogId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.GetBlogInfo(json.loads(response.text)).GetBlogInfo
        elif wikiId:
            response = self.session.get(f"{self.api}/g/s/item/{wikiId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.GetWikiInfo(json.loads(response.text)).GetWikiInfo
        elif fileId:
            response = self.session.get(f"{self.api}/g/s/shared-folder/files/{fileId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: 
                return exceptions.CheckException(response.text)
            else:
                return objects.SharedFolderFile(json.loads(response.text)["file"]).SharedFolderFile
        else:
            raise exceptions.SpecifyType()

    def get_blog_comments(self, blogId=None, wikiId=None, quizId=None, fileId=None, sorting="newest", start=0, size=25):
        if sorting == "newest":
            sorting = "newest"
        elif sorting == "oldest":
            sorting = "oldest"
        elif sorting == "top":
            sorting = "vote"
        else:
            raise exceptions.WrongType(sorting)
        if blogId or quizId:
            if quizId is not None:
                blogId = quizId
            response = self.session.get(f"{self.api}/g/s/blog/{blogId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.get(f"{self.api}/g/s/item/{wikiId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif fileId:
            response = self.session.get(f"{self.api}/g/s/shared-folder/files/{fileId}/comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

    def get_blocker_users(self, start=0, size=25):
        """
        List of Users that are Blocking the User.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`List of User IDs <None>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/block/full-list?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["blockerUidList"]

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
        if sorting.lower() == "newest": sorting = "newest"
        elif sorting.lower() == "oldest": sorting = "oldest"
        elif sorting.lower() == "top": sorting = "vote"
        else:
            raise exceptions.WrongType(sorting)
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommentList(json.loads(response.text)["commentList"]).CommentList

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
            raise exceptions.ReasonNeeded
        if flagType is None:
            raise exceptions.FlagTypeNeeded
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
            raise exceptions.SpecifyType
        if asGuest:
            flg = "g-flag"
        else:
            flg = "flag"
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/{flg}", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
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
        if mentions:
            extensions["mentionedArray"] = mentions
        if embedId or embedType or embedLink or embedTitle or embedContent or embedImage:
            data["attachedObject"] = {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent,
                "mediaList": embedImage
            }
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
                raise exceptions.SpecifyType()
            data["mediaUploadValue"] = base64.b64encode(helpers.read_bytes(file)).decode()
        if extensions:
            data["extensions"] = extensions
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/message", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
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
            "adminOpNote": {"content": reason},
            "timestamp": int(time.time() * 1000)
        }
        data = json.dumps(data)
        if not asStaff: response = self.session.delete(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else: response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}/admin", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/mark-as-read", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def edit_chat(self, chatId, doNotDisturb=None, pinChat=None, title=None, icon=None, backgroundImage=None, content=None, announcement=None, coHosts=None, keywords=None, pinAnnouncement=None, publishToGlobal=None, canTip=None, viewOnly=None, canInvite=None, fansOnly=None):
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
        data = {"timestamp": int(time.time() * 1000)}
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
                data = json.dumps({"alertOption": 2, "timestamp": int(time.time() * 1000)})
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
            if not doNotDisturb:
                data = json.dumps({"alertOption": 1, "timestamp": int(time.time() * 1000)})
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/alert", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
        if pinChat is not None:
            if pinChat:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/pin", data=data, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
            if not pinChat:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/unpin", data=data, headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
        if backgroundImage is not None:
            data = json.dumps({"media": [100, backgroundImage, None], "timestamp": int(time.time() * 1000)})
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.userId}/background", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: res.append(exceptions.CheckException(response.text))
            else: res.append(response.status_code)
        if coHosts is not None:
            data = json.dumps({"uidList": coHosts, "timestamp": int(time.time() * 1000)})
            response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/co-host", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
            if response.status_code != 200: res.append(exceptions.CheckException(response.text))
            else: res.append(response.status_code)
        if viewOnly is not None:
            if viewOnly:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/view-only/enable", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
            if not viewOnly:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/view-only/disable", headers=self.parse_headers(type="application/x-www-form-urlencoded"), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
        if canInvite is not None:
            if canInvite:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/members-can-invite/enable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
            if not canInvite:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/members-can-invite/disable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
        if canTip is not None:
            if canTip:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/tipping-perm-status/enable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
            if not canTip:
                response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/tipping-perm-status/disable", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
                if response.status_code != 200: res.append(exceptions.CheckException(response.text))
                else: res.append(response.status_code)
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: res.append(exceptions.CheckException(response.text))
        else: res.append(response.status_code)
        return res

    def visit(self, userId):
        """
        Visit an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}?action=visit", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def send_coins(self, coins: int, blogId= None, chatId= None, objectId= None, transactionId= None):
        url = None
        if transactionId is None:
            transactionId = str(uuid.uuid4())
        data = {
            "coins": coins,
            "tippingContext": {"transactionId": transactionId},
            "timestamp": int(time.time() * 1000)
        }
        if blogId is not None:
            url = f"{self.api}/g/s/blog/{blogId}/tipping"
        if chatId is not None:
            url = f"{self.api}/g/s/chat/thread/{chatId}/tipping"
        if objectId is not None:
            data["objectId"] = objectId
            data["objectType"] = 2
            url = f"{self.api}/g/s/tipping"
        if url is None:
            raise exceptions.SpecifyType()
        data = json.dumps(data)
        response = self.session.post(url, headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
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
            response = self.session.post(f"{self.api}/g/s/user-profile/{userId}/member", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif isinstance(userId, list):
            data = json.dumps({"targetUidList": userId, "timestamp": int(time.time() * 1000)})
            response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/joined", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.WrongType
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
        response = self.session.delete(f"{self.api}/g/s/user-profile/{userId}/member/{self.userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.post(f"{self.api}/g/s/block/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
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
        response = self.session.delete(f"{self.api}/g/s/block/{userId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def join_community(self, comId, invitationId=None):
        """
        Join a Community.

        **Parameters**
            - **comId** : ID of the Community.
            - **invitationId** : ID of the Invitation Code.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {"timestamp": int(time.time() * 1000)}
        if invitationId: data["invitationId"] = invitationId
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/x{comId}/s/community/join", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def request_join_community(self, comId, message=None):
        """
        Request to join a Community.

        **Parameters**
            - **comId** : ID of the Community.
            - **message** : Message to be sent.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({"message": message, "timestamp": int(time.time() * 1000)})
        response = self.session.post(f"{self.api}/x{comId}/s/community/membership-request", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def leave_community(self, comId):
        """
        Leave a Community.

        **Parameters**
            - **comId** : ID of the Community.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/x{comId}/s/community/leave", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def flag_community(self, comId, reason, flagType, isGuest=False):
        """
        Flag a Community.

        **Parameters**
            - **comId** : ID of the Community.
            - **reason** : Reason of the Flag.
            - **flagType** : Type of Flag.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if reason is None: raise exceptions.ReasonNeeded
        if flagType is None: raise exceptions.FlagTypeNeeded
        data = json.dumps({
            "objectId": comId,
            "objectType": 16,
            "flagType": flagType,
            "message": reason,
            "timestamp": int(time.time() * 1000)
        })
        if isGuest: flg = "g-flag"
        else: flg = "flag"
        response = self.session.post(f"{self.api}/x{comId}/s/{flg}", data=data, headers=self.parse_headers(data=data), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def edit_profile(self, nickname=None, content=None, icon=None, backgroundColor=None, backgroundImage=None, defaultBubbleId=None):
        """
        Edit account's Profile.

        **Parameters**
            - **nickname** : Nickname of the Profile.
            - **content** : Biography of the Profile.
            - **icon** : Icon of the Profile.
            - **backgroundImage** : Url of the Background Picture of the Profile.
            - **backgroundColor** : Hexadecimal Background Color of the Profile.
            - **defaultBubbleId** : Chat bubble ID.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {
            "address": None,
            "latitude": 0,
            "longitude": 0,
            "mediaList": None,
            "eventSource": "UserProfileView",
            "timestamp": int(time.time() * 1000)
        }
        if nickname: data["nickname"] = nickname
        if icon: data["icon"] = self.upload_media(icon, "image")
        if content: data["content"] = content
        if backgroundColor: data["extensions"] = {"style": {"backgroundColor": backgroundColor}}
        if backgroundImage: data["extensions"] = {"style": {"backgroundMediaList": [[100, backgroundImage, None, None, None]]}}
        if defaultBubbleId: data["extensions"] = {"defaultBubbleId": defaultBubbleId}
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            self.profile = objects.UserProfile(json.loads(response.text)["userProfile"]).UserProfile
            return response.status_code

    def set_privacy_status(self, isAnonymous=False, getNotifications=False):
        """
        Edit account's Privacy Status.

        **Parameters**
            - **isAnonymous** : If visibility should be Anonymous or not.
            - **getNotifications** : If account should get new Visitors Notifications.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {"timestamp": int(time.time() * 1000)}
        if not isAnonymous: data["privacyMode"] = 1
        if isAnonymous: data["privacyMode"] = 2
        if not getNotifications: data["notificationStatus"] = 2
        if getNotifications: data["privacyMode"] = 1
        data = json.dumps(data)
        response = self.session.post(f"{self.api}/g/s/account/visit-settings", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def set_amino_id(self, aminoId):
        """
        Edit account's Amino ID.

        **Parameters**
            - **aminoId** : Amino ID of the Account.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({"aminoId": aminoId, "timestamp": int(time.time() * 1000)})
        response = self.session.post(f"{self.api}/g/s/account/change-amino-id", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_linked_communities(self, userId):
        """
        Get a List of Linked Communities of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`Community List <amino.lib.util.objects.CommunityList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/linked-community", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommunityList(json.loads(response.text)["linkedCommunityList"]).CommunityList

    def get_unlinked_communities(self, userId):
        """
        Get a List of Unlinked Communities of an User.

        **Parameters**
            - **userId** : ID of the User.

        **Returns**
            - **Success** : :meth:`Community List <amino.lib.util.objects.CommunityList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile/{userId}/linked-community", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommunityList(json.loads(response.text)["unlinkedCommunityList"]).CommunityList

    def reorder_linked_communities(self, comIds):
        """
        Reorder List of Linked Communities.

        **Parameters**
            - **comIds** : IDS of the Communities.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({"ndcIds": comIds, "timestamp": int(time.time() * 1000)})
        response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/reorder", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def add_linked_community(self, comId):
        """
        Add a Linked Community on your profile.

        **Parameters**
            - **comId** : ID of the Community.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/{comId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def remove_linked_community(self, comId):
        """
        Remove a Linked Community on your profile.

        **Parameters**
            - **comId** : ID of the Community.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.delete(f"{self.api}/g/s/user-profile/{self.userId}/linked-community/{comId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def comment(self, message, userId=None, blogId=None, wikiId=None, replyTo=None):
        """
        Comment on a User's Wall, Blog or Wiki.

        **Parameters**
            - **message** : Message to be sent.
            - **userId** : ID of the User. (for Walls)
            - **blogId** : ID of the Blog. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)
            - **replyTo** : ID of the Comment to Reply to.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if message is None:
            raise exceptions.MessageNeeded
        data = {
            "content": message,
            "stickerId": None,
            "type": 0,
            "timestamp": int(time.time() * 1000)
        }
        if replyTo: data["respondTo"] = replyTo
        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/user-profile/{userId}/g-comment", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/blog/{blogId}/g-comment", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/item/{wikiId}/g-comment", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else: raise exceptions.SpecifyType
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def delete_comment(self, commentId, userId=None, blogId=None, wikiId=None):
        """
        Delete a Comment on a User's Wall, Blog or Wiki.

        **Parameters**
            - **commentId** : ID of the Comment.
            - **userId** : ID of the User. (for Walls)
            - **blogId** : ID of the Blog. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if userId:
            response = self.session.delete(f"{self.api}/g/s/user-profile/{userId}/g-comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            response = self.session.delete(f"{self.api}/g/s/blog/{blogId}/g-comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/g/s/item/{wikiId}/g-comment/{commentId}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType
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
                response = self.session.post(f"{self.api}/g/s/blog/{blogId}/g-vote?cv=1.2", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
            elif isinstance(blogId, list):
                data["targetIdList"] = blogId
                data = json.dumps(data)
                response = self.session.post(f"{self.api}/g/s/feed/g-vote", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
            else: raise exceptions.WrongType(type(blogId))
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/item/{wikiId}/g-vote?cv=1.2", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType()
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unlike_blog(self, blogId=None, wikiId=None):
        """
        Remove a like from a Blog or Wiki.

        **Parameters**
            - **blogId** : ID of the Blog. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if blogId:
            response = self.session.delete(f"{self.api}/g/s/blog/{blogId}/g-vote?eventSource=UserProfileView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/g/s/item/{wikiId}/g-vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def like_comment(self, commentId: str, userId= None, blogId= None, wikiId= None):
        """
        Like a Comment on a User's Wall, Blog or Wiki.

        **Parameters**
            - **commentId** : ID of the Comment.
            - **userId** : ID of the User. (for Walls)
            - **blogId** : ID of the Blog. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = {
            "value": 4,
            "timestamp": int(time.time() * 1000)
        }
        if userId:
            data["eventSource"] = "UserProfileView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            data["eventSource"] = "PostDetailView"
            data = json.dumps(data)
            response = self.session.post(f"{self.api}/g/s/item/{wikiId}/comment/{commentId}/g-vote?cv=1.2&value=1", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def unlike_comment(self, commentId, userId=None, blogId=None, wikiId=None):
        """
        Remove a like from a Comment on a User's Wall, Blog or Wiki.

        **Parameters**
            - **commentId** : ID of the Comment.
            - **userId** : ID of the User. (for Walls)
            - **blogId** : ID of the Blog. (for Blogs)
            - **wikiId** : ID of the Wiki. (for Wikis)

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if userId:
            response = self.session.delete(f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif blogId:
            response = self.session.delete(f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        elif wikiId:
            response = self.session.delete(f"{self.api}/g/s/item/{wikiId}/comment/{commentId}/g-vote?eventSource=PostDetailView", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        else:
            raise exceptions.SpecifyType

        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_membership_info(self):
        """
        Get Information about your Amino+ Membership.

        **Parameters**
            - No parameters required.

        **Returns**
            - **Success** : :meth:`Membership Object <amino.lib.util.objects.Membership>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/membership?force=true", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.Membership(json.loads(response.text)).Membership

    def get_ta_announcements(self, language="en", start=0, size=25):
        """
        Get the list of Team Amino's Announcement Blogs.

        **Parameters**
            - **language** : Language of the Blogs.
                - ``en``, ``es``, ``pt``, ``ar``, ``ru``, ``fr``, ``de``
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Blogs List <amino.lib.util.objects.BlogList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        if language not in self.get_supported_languages():
            raise exceptions.UnsupportedLanguage(language)
        response = self.session.get(f"{self.api}/g/s/announcement?language={language}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.BlogList(json.loads(response.text)["blogList"]).BlogList

    def get_wallet_info(self):
        """
        Get Information about the account's Wallet.

        **Parameters**
            - No parameters required.

        **Returns**
            - **Success** : :meth:`Wallet Object <amino.lib.util.objects.WalletInfo>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/wallet", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WalletInfo(json.loads(response.text)["wallet"]).WalletInfo

    def get_wallet_history(self, start=0, size=25):
        """
        Get the Wallet's History Information.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`Wallet Object <amino.lib.util.objects.WalletInfo>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.WalletHistory(json.loads(response.text)["coinHistoryList"]).WalletHistory

    def get_from_deviceid(self, deviceId):
        """
        Get the User ID from an Device ID.

        **Parameters**
            - **deviceID** : ID of the Device.

        **Returns**
            - **Success** : :meth:`User ID <amino.lib.util.objects.UserProfile.userId>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/auid?deviceId={deviceId}")
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["auid"]

    def get_from_code(self, code):
        """
        Get the Object Information from the Amino URL Code.

        **Parameters**
            - **code** : Code from the Amino URL.
                - ``http://aminoapps.com/p/EXAMPLE``, the ``code`` is 'EXAMPLE'.

        **Returns**
            - **Success** : :meth:`From Code Object <amino.lib.util.objects.FromCode>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/link-resolution?q={code}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.FromCode(json.loads(response.text)["linkInfoV2"]).FromCode

    def get_from_id(self, objectId, objectType, comId=None):
        """
        Get the Object Information from the Object ID and Type.

        **Parameters**
            - **objectID** : ID of the Object. User ID, Blog ID, etc.
            - **objectType** : Type of the Object.
            - *comId* : ID of the Community. Use if the Object is in a Community.

        **Returns**
            - **Success** : :meth:`From Code Object <amino.lib.util.objects.FromCode>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "objectId": objectId,
            "targetCode": 1,
            "objectType": objectType,
            "timestamp": int(time.time() * 1000)
        })
        if comId:
            response = self.session.post(f"{self.api}/g/s-x{comId}/link-resolution", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        else:
            response = self.session.post(f"{self.api}/g/s/link-resolution", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.FromCode(json.loads(response.text)["linkInfoV2"]).FromCode

    def get_supported_languages(self):
        """
        Get the List of Supported Languages by Amino.

        **Parameters**
            - No parameters required.

        **Returns**
            - **Success** : :meth:`List of Supported Languages <List>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/community-collection/supported-languages?start=0&size=100", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["supportedLanguages"]

    def claim_new_user_coupon(self):
        """
        Claim the New User Coupon available when a new account is created.

        **Parameters**
            - No parameters required.

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.post(f"{self.api}/g/s/coupon/new-user-coupon/claim", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def get_subscriptions(self, start=0, size=25):
        """
        Get Information about the account's Subscriptions.

        **Parameters**
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`List <List>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/store/subscription?objectType=122&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return json.loads(response.text)["storeSubscriptionItemList"]

    def get_all_users(self, type="recent", start=0, size=25):
        """
        Get list of users of Amino.

        **Parameters**
            - *type* : The users type.
            - *start* : Where to start the list.
            - *size* : Size of the list.

        **Returns**
            - **Success** : :meth:`User Profile Count List Object <amino.lib.util.objects.UserProfileCountList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = self.session.get(f"{self.api}/g/s/user-profile?type={type}&start={start}&size={size}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.UserProfileCountList(json.loads(response.text)).UserProfileCountList

    def accept_host(self, chatId, requestId):
        data = json.dumps({})
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def accept_organizer(self, chatId, requestId):
        self.accept_host(chatId, requestId)

    # Contributed by 'https://github.com/LynxN1'
    def link_identify(self, code):
        response = self.session.get(f"{self.api}/g/s/community/link-identify?q=http%3A%2F%2Faminoapps.com%2Finvite%2F{code}", headers=self.parse_headers(), proxies=self.proxies, verify=self.certificatePath)
        return json.loads(response.text)

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
        response = self.session.post(f"{self.api}/g/s/chat/thread/{chatId}/vvchat-presenter/invite", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def wallet_config(self, level):
        """
        Changes ads config

        **Parameters**
            - **level** - Level of the ads.
                - ``1``, ``2``

        **Returns**
            - **Success** : 200 (int)

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        data = json.dumps({
            "adsLevel": level,
            "timestamp": int(time.time() * 1000)
        })
        response = self.session.post(f"{self.api}/g/s/wallet/ads/config", headers=self.parse_headers(data=data), data=data, proxies=self.proxies, verify=self.certificatePath)
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return response.status_code

    def purchase(self, objectId, objectType, autoRenew=False):
        data = json.dumps({
            "objectId": objectId,
            "objectType": objectType,
            "v": 1,
            "paymentContext":
            {
                "discountStatus": 0,
                "isAutoRenew": autoRenew
            },
            "timestamp": time.time()
        })
        response = self.session.post(f"{self.api}/g/s/store/purchase", headers=self.parse_headers(data=data), data=data)
        if response.status_code != 200:
            return exceptions.CheckException(json.loads(response.text()))
        else:
            return response.status_code

    def get_public_communities(self, language="en", size=25):
        """
        Get public communites

        **Parameters**
            - **language** - Set up language

        **Returns**
            - **Success** : :meth:`Community List <amino.lib.util.objects.CommunityList>`

            - **Fail** : :meth:`Exceptions <aminofix.lib.util.exceptions>`
        """
        response = requests.get(f"{self.api}/g/s/topic/0/feed/community?language={language}&type=web-explore&categoryKey=recommendation&size={size}&pagingType=t", headers=self.parse_headers())
        if response.status_code != 200: 
            return exceptions.CheckException(response.text)
        else:
            return objects.CommunityList(json.loads(response.text)["communityList"]).CommunityList
