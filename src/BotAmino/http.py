from __future__ import annotations

import base64
import collections.abc
import locale
import time
import typing
import typing_extensions
import urllib.parse
import uuid
import json_minify  # type: ignore
import ujson
import requests

if typing.TYPE_CHECKING:
    from _typeshed import SupportsRead

from .errors import check_api_error, check_server_error
from .objects import (
    APIResponseLite,
    Account,
    AccountResponse,
    AffiliationsResponse,
    BasicProfile,
    BasicProfileResponse,
    CategoryList,
    ChatMemberResponse,
    CommunityInfoResponse,
    CommunityJoinResponse,
    CommunityList,
    CommunitySearchResponse,
    CommunityTrendingResponse,
    EventLogResponse,
    HumanReadable,
    JoinedCommunitiesResponse,
    LinkIdentifyResponse,
    LinkInfo,
    LinkInfoV2,
    LinkResolutionResponse,
    LinkedCommunityResponse,
    LoginResponse,
    ResultList,
    SearchAminoIdAndLinkResponse,
    SectionList,
    SoundCategoryResponse,
    SoundCountResponse,
    SoundSearchResponse,
    SoundSectionListResponse,
    Thread,
    ThreadList,
    ThreadListResponse,
    ThreadMemberResponse,
    ThreadResponse,
    UserProfile,
    UserProfileListResponse,
    UserProfileLiteList,
    UserProfileResponse,
    VisitSettings,
    VisitSettingsResponse,
    Wallet,
    WalletResponse,
)
from .types import (
    ContentType,
    MessageType,
    PaymentType,
    ValidationLevel,
    ValidationType,
)
from .typing import (
    BinaryFile,
    FileTypeInput,
    Proxies,
    SupportedAudioExt,
    SupportedImageExt,
    SupportedVideoExt,
)
from .utils import (
    build_device,
    build_uuid,
    currentTimeMillis,
    decode_sid,
    build_signature,
    read_file,
    update_device,
)

__all__ = ("HTTPClient",)

DEFAULT_AGENT = "Apple iPhone13 iOS v16.1.2 Main/3.13.1"
DEFAULT_LANGUAGE = "en"


class HTTPClient:
    @property
    def agent(self) -> str:
        return getattr(self, "_agent")

    @agent.setter
    def agent(self, value: str) -> None:
        setattr(self, "_agent", value)

    @property
    def auid(self) -> str | None:
        return getattr(self, "_auid")

    @auid.setter
    def auid(self, value: str | None) -> None:
        setattr(self, "_auid", value)

    @property
    def certificatePath(self) -> str | None:
        return getattr(self, "_certificatePath")

    @certificatePath.setter
    def certificatePath(self, value: str | None) -> None:
        setattr(self, "_certificatePath", value)

    @property
    def deviceId(self) -> str:
        return getattr(self, "_deviceId")

    @deviceId.setter
    def deviceId(self, value: str) -> None:
        setattr(self, "_deviceId", update_device(value))

    @property
    def language(self) -> str:
        return getattr(self, "_language")

    @language.setter
    def language(self, value: str) -> None:
        setattr(self, "_language", value)

    @property
    def proxies(self) -> Proxies | None:
        return getattr(self, "_proxies")

    @proxies.setter
    def proxies(self, value: Proxies | None) -> None:
        setattr(self, "_proxies", value)

    @property
    def secret(self) -> str | None:
        return getattr(self, "_secret")

    @secret.setter
    def secret(self, value: str | None) -> None:
        setattr(self, "_secret", value)

    @property
    def sid(self) -> str | None:
        return getattr(self, "_sid")

    @sid.setter
    def sid(self, value: str | None) -> None:
        setattr(self, "_sid", value)

    @property
    def smdeviceId(self) -> str:
        return getattr(self, "_smdeviceId")

    @smdeviceId.setter
    def smdeviceId(self, value: str) -> None:
        setattr(self, "_smdeviceId", value)

    @property
    def timeout(self) -> float | None:
        return getattr(self, "_timeout")

    @timeout.setter
    def timeout(self, value: float | None) -> None:
        setattr(self, "_timeout", value)

    @property
    def timezone(self) -> int:
        return getattr(self, "_timezone")

    @timezone.setter
    def timezone(self, value: int) -> None:
        setattr(self, "_timezone", value)

    @property
    def userId(self) -> str | None:
        return self.auid

    @userId.setter
    def userId(self, value: str | None) -> None:
        self.auid = value

    @property
    def account(self) -> Account:
        return getattr(self, "_account")

    @account.setter
    def account(self, value: Account) -> None:
        setattr(self, "_account", value)

    @property
    def profile(self) -> UserProfile:
        return getattr(self, "_profile")

    @profile.setter
    def profile(self, value: UserProfile) -> None:
        setattr(self, "_profile", value)

    @property
    def api(self) -> str:
        return "https://service.aminoapps.com/api/v1/"

    @property
    def authenticated(self) -> bool:
        return bool(self.sid)

    def __init__(
        self,
        deviceId: str | None = None,
        smdeviceId: str | None = None,
        proxies: Proxies | None = None,
        certificatePath: str | None = None,
        agent: str | None = None,
        language: str | None = None,
        timeout: float | None = None,
        timezone: int | None = None,
    ) -> None:
        self.agent = agent or DEFAULT_AGENT
        self.certificatePath = certificatePath
        self.deviceId = deviceId or build_device()
        self.language = language or DEFAULT_LANGUAGE
        self.proxies = proxies
        self.smdeviceId = smdeviceId or build_uuid()
        self.timeout = timeout
        self.timezone = timezone or 0
        self.auid = None
        self.secret = None
        self.sid = None
        self.account = Account({})
        self.profile = UserProfile({})

    def headers(
        self,
        data: bytes | str | None = None,
        content_type: ContentType | str | None = None,
    ) -> dict[str, str]:
        headers = {
            "SMDEVICEID": self.smdeviceId,
            "AUID": self.smdeviceId,
            "NDCDEVICEID": self.deviceId,
            "NDCLANG": self.language,
            "Accept-Language": "en-US",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.agent,
            "Host": "service.aminoapps.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
        }
        if data:
            headers["NDC-MSG-SIG"] = build_signature(data)
            headers["Content-Lenght"] = str(len(data))
            headers["Content-Type"] = "application/json; charset=utf-8"
        if content_type:
            if content_type.startswith(ContentType.MULTIPART):
                if "boundary" not in content_type:
                    content_type += f";boundary=" + str(uuid.uuid4())
            headers["Content-Type"] = content_type
        if self.auid:
            headers["AUID"] = self.auid
        if self.sid:
            headers["NDCAUTH"] = f"sid={self.sid}"
        return headers

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, typing.Any] | None = None,
        data: dict[str, typing.Any] | str | bytes | None = None,
        files: (
            collections.abc.Mapping[str, SupportsRead[str | bytes] | str | bytes] | None
        ) = None,
        content_type: ContentType | str | None = None,
        custom_headers: typing.Mapping[str, str] | None = None,
        comId: int = 0,
        scope: bool = False,
        minify: bool = False,
        errors: bool = True,
    ) -> dict[str, typing.Any]:
        ndcpath = (f"g/s-x{comId}/" if scope else f"x{comId}/s/") if comId else "g/s/"
        url = urllib.parse.urljoin(
            self.api, urllib.parse.urljoin(ndcpath, path.removeprefix("/"))
        )
        if isinstance(data, dict):
            data = ujson.dumps(data)
        if minify and isinstance(data, str):
            data = typing.cast(str, json_minify.json_minify(data))  # type: ignore
        if files:
            if content_type is None:
                content_type = ContentType.MULTIPART
        headers = self.headers(data, content_type)
        if custom_headers:
            headers.update(custom_headers)
        with requests.Session() as session:
            try:
                response = session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    files=files,
                    headers=headers,
                    timeout=self.timeout,
                    proxies=self.proxies,
                )
            except requests.ConnectionError as exc:
                raise ConnectionError(*exc.args) from None
            try:
                payload = typing.cast(dict[str, typing.Any], ujson.loads(response.text))
            except ujson.JSONDecodeError:
                raise check_server_error(response) from None
            if errors and payload.get("api:statuscode") != 0:
                raise check_api_error(payload) from None
        return payload

    def get_account_affiliations(self, affiliationType: str = "active") -> list[int]:
        return AffiliationsResponse(
            self.request(
                "GET", "account/affiliations", params=dict(type=affiliationType)
            )
        ).affiliations

    def get_trending_communities(self, language: str | None = None) -> CommunityList:
        return CommunityTrendingResponse(
            self.request(
                "GET",
                "community/trending",
                params=dict(language=language or self.language),
            )
        ).communities

    def search_community(
        self, q: str, language: str | None = None, completeKeyword: bool = True
    ) -> CommunitySearchResponse:
        return CommunitySearchResponse(
            self.request(
                "GET",
                "community/search",
                params=dict(
                    q=q,
                    timezone=self.timezone,
                    language=language or self.language,
                    completeKeyword=int(completeKeyword),
                ),
            )
        )

    def search_from_aminoId(self, aminoId: str) -> ResultList:
        return SearchAminoIdAndLinkResponse(
            self.request("GET", "search/amino-id-and-link", params=dict(q=aminoId))
        ).results

    def get_sound_sections(self) -> SectionList:
        return SoundSectionListResponse(
            self.request("GET", "asset/sound/section")
        ).sections

    def count_sound_category(
        self, q: str, categoryId: collections.abc.Sequence[str] | str
    ) -> SoundCountResponse:
        filterIds = None if isinstance(categoryId, str) else ",".join(categoryId)
        return SoundCountResponse(
            self.request(
                "GET",
                "asset/sound/count",
                params=dict(
                    q=q,
                    categoryId=None if filterIds else categoryId,
                    filterIds=filterIds,
                ),
            )
        )

    def get_sound_categories(
        self, sectionName: str | None = None, start: int = 0, size: int = 25
    ) -> CategoryList:
        # name: SFX, Music
        return SoundCategoryResponse(
            self.request(
                "GET",
                "asset/sound/category2",
                params=dict(section=sectionName, start=start, size=size),
            )
        ).categories

    def get_children_sound_categories(self, categoryId: str) -> CategoryList:
        return SoundCategoryResponse(
            self.request(
                "GET",
                "asset/sound/category2/children",
                params=dict(categoryId=categoryId),
            )
        ).categories

    def search_sounds(
        self,
        categoryId: collections.abc.Sequence[str] | str,
        sort: typing.Literal["default", "relevance", "shortest", "longest"] = "default",
        seed: str | None = None,
        start: int = 0,
        size: int = 25,
    ) -> SoundSearchResponse:
        filterIds = None if isinstance(categoryId, str) else ",".join(categoryId)
        return SoundSearchResponse(
            self.request(
                "GET",
                "asset/sound/search2",
                params=dict(
                    categoryId=None if filterIds else categoryId,
                    filterIds=filterIds,
                    sortBy=sort,
                    seed=seed,
                    start=start,
                    size=size,
                ),
            )
        )

    def check_push_notification(self):
        return self.request(
            "GET",
            "push/check",
            params=dict(timezone=self.timezone, language=self.language),
        )

    def report_push_track(
        self,
        trackId: str,
        trackType: typing.Literal["open", "receive"],
        notificationsEnabled: typing.Literal["off", "on"],
        broadcast: typing.Literal["off", "on"] | None = None,
        chat: typing.Literal["off", "on"] | None = None,
        alert: typing.Literal["off", "on"] | None = None,
        acm: typing.Literal["off", "on"] | None = None,
        scenario: typing.Literal["background", "foreground"] = "background",
        shown: bool = False,
    ):
        systemPushCategory: dict[str, str] = {
            "broadcast": notificationsEnabled,
            "chat": notificationsEnabled,
            "alert": notificationsEnabled,
            "community-management": notificationsEnabled,
        }
        if broadcast:
            systemPushCategory.update(broadcast=broadcast)
        if chat:
            systemPushCategory.update(chat=chat)
        if alert:
            systemPushCategory.update(alert=alert)
        if acm:
            systemPushCategory.update({"community-management": acm})
        systemPushCategory["community-management"] = notificationsEnabled
        return self.request(
            "POST",
            "push/track",
            data=dict(
                trackId=trackId,
                trackType=trackType,
                scenario=scenario,
                systemPushStatus=notificationsEnabled,
                systemPushCategory=systemPushCategory,
                shown=shown,
            ),
        )

    def get_unread_chats(
        self, comIds: collections.abc.Iterable[int] = [0]
    ) -> HumanReadable:
        return HumanReadable(
            self.request(
                "GET",
                "chat/thread-check/human-readable",
                params=dict(ndcIds=",".join(map(str, set(comIds)))),
            )
        )

    def search_chat_member(self, chatId: str, q: str) -> UserProfileLiteList:
        return ChatMemberResponse(
            self.request(
                "GET", f"chat/thread/{chatId}/member", params=dict(q=q, type="at")
            )
        ).members

    def get_user_from_ids(
        self, userIds: collections.abc.Sequence[str] | str
    ) -> UserProfileListResponse:
        userIds = [userIds] if isinstance(userIds, str) else userIds
        return UserProfileListResponse(
            self.request(
                "GET", "user-profile", params=dict(type="uid", q=",".join(userIds))
            )
        )

    def get_device_options(self):
        return self.request("GET", "device/dev-options")

    def get_latest_payment(self):
        return self.request("GET", "membership/latest-payment-context")

    def update_membership(self, autoRenew: bool):
        return self.request(
            "POST",
            "membership/config",
            data=dict(
                paymentContext=dict(isAutoRenew=autoRenew),
                paymentType=1,
                timestamp=currentTimeMillis(),
            ),
        )

    def redeem_aminoplus(self, autoRenew: bool = True, couponId: str | None = None):
        return self.request(
            "POST",
            "membership/product/subscribe",
            data=dict(
                sku="",
                packageName="com.narvii.amino.master",
                paymentType=PaymentType.COIN,
                paymentContext=dict(
                    transactionId=build_uuid(),
                    isAutoRenew=autoRenew,
                    couponMappingIdList=[couponId] if couponId else None,
                ),
                timestamp=currentTimeMillis(),
            ),
        )

    def redeem_aminoplus_v2(self):
        return self.request(
            "POST",
            "membership/product/v2",
            data=dict(
                packageName="com.narvii.amino.master",
                paymentType=PaymentType.COIN,
                timestamp=currentTimeMillis(),
            ),
        )

    def subscribe_product_v2(
        self, aminoPlusPricingVersion: int, paymentType: PaymentType
    ):
        return self.request(
            "POST",
            "membership/product/v2",
            data=dict(
                paymentType=paymentType,
                packageName="com.narvii.amino.master",
                packageVersion=aminoPlusPricingVersion,
                timestamp=currentTimeMillis(),
            ),
        )

    def subscribe_product(
        self,
        productSku: str,
        paymentType: PaymentType,
        autoRenew: bool = True,
        couponId: str | None = None,
    ):
        return self.request(
            "POST",
            "membership/product/subscribe",
            data=dict(
                sku=productSku,
                packageName="com.narvii.amino.master",
                paymentType=paymentType,
                transactionId=build_uuid(),
                paymentContext=dict(
                    isAutoRenew=autoRenew,
                    couponMappingIdList=[couponId] if couponId else None,
                ),
                timestamp=currentTimeMillis(),
            ),
        )

    def get_from_id(
        self, objectId: str, objectType: int, comId: int | None = None
    ) -> LinkInfoV2:
        """Get object data from a link.

        Parameters
        ----------
        objectId : `str`
            The object ID. User ID, Blog ID, etc.
        objectType : `int`
            The type of the object.
        comId : `int`, `optional`
            The community ID, if the object is in the community. Default is `None`.

        Returns
        -------
        LinkResolutionResponse
            The amino api response.

        """
        return LinkResolutionResponse(
            self.request(
                "POST",
                "link-resolution",
                data=dict(
                    objectId=objectId,
                    objectType=objectType,
                    targetCode=1,
                    timestamp=currentTimeMillis(),
                ),
                comId=comId or 0,
                scope=isinstance(comId, int),
            )
        ).linkInfoV2

    def get_from_link(self, link: str) -> LinkInfoV2:
        """Get object data from a link.

        Parameters
        ----------
        link : `str`
            The link to get data.

        Returns
        -------
        LinkResolutionResponse
            The link data object.

        """
        return LinkResolutionResponse(
            self.request("GET", "link-resolution", params=dict(q=link))
        ).linkInfoV2

    @typing_extensions.deprecated("use get_from_link instead")
    def get_from_code(self, link: str) -> LinkInfo:
        return self.get_from_link(link).linkInfo

    def get_link_info(self, link: str) -> LinkIdentifyResponse:
        return LinkIdentifyResponse(
            self.request("GET", "community/link-identify", params=dict(q=link))
        )

    def upload_media(
        self,
        file: BinaryFile,
        fileType: FileTypeInput,
        ext: SupportedAudioExt | SupportedImageExt | SupportedVideoExt | None = None,
    ) -> str:
        """Upload file to the amino server

        Parameters
        ----------
        file : `BinaryIO`, `Path`, `str`
            A file opened in rb mode or path.
        fileType : str
            The file type (audio, image, video).
        ext : str, optional
            The file extension name. If not provided the is extracted from the file name.

        Returns
        -------
        str
            The url of the uploaded media.

        See Also
        --------
        - `BotAmino.types.FileTypeInput`
        - `BotAmino.types.SupportedAudioExt`
        - `BotAmino.types.SupportedImageExt`
        - `BotAmino.types.SupportedVideoExt`

        """
        if fileType not in typing.get_args(FileTypeInput):
            fts = ", ".join(map(repr, typing.get_args(FileTypeInput)))
            raise ValueError(f"fileType must be %s not %r." % (fts, fileType))
        data = read_file(file)
        if not ext:
            if isinstance(file, typing.BinaryIO) and file.name:
                _, ext = typing.cast(
                    list[
                        typing.Union[
                            SupportedAudioExt, SupportedImageExt, SupportedVideoExt
                        ]
                    ],
                    file.name.rsplit(".", 1),
                )
            ext = (
                "acc"
                if fileType == "audio"
                else (
                    "mp4"
                    if fileType == "video"
                    else "jpeg" if fileType == "image" else "gif"
                )
            )
        content_type = f"{fileType}/{ext}".lower()
        return self.request(
            "POST", "media/upload", data=data, content_type=content_type
        )["mediaValue"]

    def get_user_info(self, userId: str | None = None) -> UserProfile:
        """Get user profile.

        Parameters
        ----------
        userId : `str`, optional
            The user ID to get information. If not provided the account userId is used.

        Returns
        -------
        UserProfile
            The user profile object.

        """
        userId = userId or self.userId
        return UserProfileResponse(
            self.request(
                "GET", f"user-profile/{userId}", params=dict(withAvatarFrame=1)
            )
        ).profile

    def edit_profile(
        self,
        nickname: str | None = None,
        content: str | None = None,
        icon: typing.BinaryIO | str | None = None,
        backgroundColor: str | None = None,
        backgroundImage: typing.BinaryIO | str | None = None,
        defaultBubbleId: str | None = None,
    ) -> UserProfile:
        extensions: dict[str, typing.Any] = {}
        data: dict[str, typing.Any] = dict(
            address=None,
            latitude=0,
            longitude=0,
            mediaList=None,
            eventSource="UserProfileView",
            timestamp=currentTimeMillis(),
        )
        if nickname:
            data.update(nickname=nickname)
        if icon:
            if not isinstance(icon, str):
                icon = self.upload_media(icon, "image")
            data.update(icon=icon)
        if content:
            data.update(content=content)
        if backgroundColor:
            extensions.update(style=dict(backgroundColor=backgroundColor))
        if backgroundImage:
            if not isinstance(backgroundImage, str):
                backgroundImage = self.upload_media(backgroundImage, fileType="image")
            extensions.update(
                style=dict(
                    backgroundMediaList=[[100, backgroundImage, None, None, None]]
                )
            )
        if defaultBubbleId:
            extensions.update(defaultBubbleId=defaultBubbleId)
        if extensions:
            data.update(extensions=extensions)
        response = UserProfileResponse(
            self.request("POST", f"user-profile/{self.userId}", data=data)
        )
        self.profile = response.profile
        return response.profile

    def get_visit_settings(self) -> VisitSettings:
        return VisitSettingsResponse(
            self.request("GET", "account/visit-settings")
        ).visitSettings

    def edit_visit_settings(
        self, isAnonymous: bool = False, getNotifications: bool = False
    ) -> VisitSettings:
        data = dict(privacyMode=int(isAnonymous) + 1, timestamp=currentTimeMillis())
        if not getNotifications:
            data["notificationStatus"] = 2
        if getNotifications:
            data["privacyMode"] = 1
        return VisitSettingsResponse(
            self.request("POST", "account/visit-settings", data=data)
        ).visitSettings

    def register_check(self, email: str) -> APIResponseLite:
        """Check if the email is already registered.

        Parameters
        ----------
        email : `str`
            The email to check

        Raises
        ------
        EmailAlreadyTaken
            If the email is already registered

        Returns
        -------
        APIResponseLite
            The JSON response

        """
        return APIResponseLite(
            self.request(
                "POST",
                "auth/register-check",
                data=dict(email=email, deviceID=self.deviceId),
            )
        )

    def login(self, email: str, password: str) -> LoginResponse:
        """Login via email.

        Parameters
        ----------
        email : `str`
            The account email.
        password : `str`
            The account password.

        Returns
        -------
        LoginResponse
            The login object.

        """
        response = LoginResponse(
            self.request(
                "POST",
                "auth/login",
                data=dict(
                    action="normal",
                    # bundleID="com.narvii.master",
                    # clientCallbackURL="narviiapp://default",
                    clientType=100,
                    deviceID=self.deviceId,
                    email=email,
                    # locale="en_US",
                    secret=f"0 {password}",
                    # systemPushEnabled=0,
                    timestamp=currentTimeMillis(),
                    # timezone=self.timezone,
                    v=2,
                ),
            )
        )
        self.auid = response.auid
        self.sid = response.sid
        self.secret = response.secret
        self.account = response.account
        self.profile = response.profile
        return response

    def login_phone(self, phone: str, password: str) -> LoginResponse:
        """Login via phone.

        Parameters
        ----------
        phone : `str`
            The account phone number.
        password : `str`
            The account password.

        Returns
        -------
        LoginResponse
            The login object.

        """
        response = LoginResponse(
            self.request(
                "POST",
                "auth/login",
                data=dict(
                    action="normal",
                    clientType=100,
                    deviceID=self.deviceId,
                    phoneNumber=phone,
                    secret=f"0 {password}",
                    timestamp=currentTimeMillis(),
                    v=2,
                ),
            )
        )
        self.auid = response.auid
        self.sid = response.sid
        self.secret = response.secret
        self.account = response.account
        self.profile = response.profile
        return response

    def login_secret(self, secret: str) -> LoginResponse:
        """Login via secret.

        Parameters
        ----------
        secret : `str`
            The account secret password.

        Returns
        -------
        LoginResponse
            The login object.

        """
        response = LoginResponse(
            self.request(
                "POST",
                "auth/login",
                data=dict(
                    action="normal",
                    clientType=100,
                    deviceID=self.deviceId,
                    secret=secret,
                    timestamp=currentTimeMillis(),
                    v=2,
                ),
            )
        )
        self.auid = response.auid
        self.sid = response.sid
        self.secret = secret
        self.account = response.account
        self.profile = response.profile
        return response

    def login_sid(self, sid: str) -> None:
        """Login via session ID.

        Parameters
        ----------
        sid : `str`
            The last session ID

        Raises
        ------
        ValueError
            If the sid has expired

        """
        sid_info = decode_sid(sid)
        if sid_info.expired:
            raise ValueError("sid has expired")
        self.auid = sid_info.objectId
        self.sid = sid
        self.account = self.get_account_info()
        self.profile = self.get_user_info(self.auid)

    def logout(self) -> APIResponseLite:
        """Logout from the account.

        Returns
        -------
        APIResponseLite
            The logout response.

        """
        response = APIResponseLite(
            self.request(
                "POST",
                "auth/logout",
                data=dict(
                    clientType=100,
                    deviceID=self.deviceId,
                    timestamp=currentTimeMillis(),
                ),
            )
        )
        self.auid = self.userId = self.sid = self.secret = None
        self.account, self.profile = Account({}), UserProfile({})
        return response

    def get_account_info(self) -> Account:
        """Get account information.

        Returns
        -------
        Account
            The user account object.

        """
        return AccountResponse(self.request("GET", "account")).account

    def verify(self, email: str, code: str, resetPassword: bool = False):
        """Confirm if the verification code is correct.

        Parameters
        ----------
        email : str
            The account email.
        code : str
            The verification code.
        resetPassword : bool, optional
            The action is to reset the password. Default is `False`.

        Returns
        -------
        APIResponseLite

        """
        return self.request(
            "POST",
            "auth/check-security-validation",
            data=dict(
                validationContext=dict(
                    data=dict(code=code),
                    level=(
                        ValidationLevel.SECRET
                        if resetPassword
                        else ValidationLevel.IDENTITY
                    ),
                    identity=email,
                    type=ValidationType.EMAIL,
                ),
                deviceID=self.deviceId,
                timestamp=currentTimeMillis(),
            ),
        )

    def verify_account(self, email: str, key: str, code: str):
        """Confirm that an email is yours

        Normally, you need to confirm when logging in on other devices for amino to allow you to log in.

        Parameters
        ----------
        email : `str`
            The account email to verify.
        key : `str`
            The verification token received in the mailbox (verifyInfoKey).
        code : `str`
            The verification code received in the mailbox.

        Raises
        ------
        InvalidAuthNewDeviceLink
            If the token does not exist or is already used.

        Returns
        -------

        """
        return self.request(
            "POST",
            "auth/verify-account",
            data=dict(
                validationContext=dict(
                    level=ValidationLevel.IDENTITY,
                    identity=email,
                    type=ValidationType.EMAIL,
                    data=dict(code=code),
                ),
                verifyInfoKey=key,
                deviceID=self.deviceId,
                timestamp=currentTimeMillis(),
            ),
        )

    def request_verify_code(
        self, email: str, resetPassword: bool = False, key: str | None = None
    ):
        """Request an verification code to the targeted email.

        Parameters
        ----------
        email : `str`
            Email of the account.
        resetPassword : `bool`
            If the code should be for Password Reset.
        key : `str`, `optional`
            The verification token to use.

        Returns
        -------

        """
        data = dict(
            deviceID=self.deviceId,
            identity=email,
            level=ValidationLevel.IDENTITY,
            type=ValidationType.EMAIL,
            verifyInfoKey=key,
        )
        if resetPassword is True:
            data.update(level=ValidationLevel.SECRET, purpose="reset-password")
        return self.request("POST", "auth/request-security-validation", data=data)

    def activate_account(self, email: str, code: str):
        """Activate an account.

        Parameters
        ----------
        email : str
            Email of the account.
        code : str
            The verification code.

        Returns

        """
        return self.request(
            "POST",
            "auth/activate-email",
            data=dict(
                data=dict(code=code),
                deviceID=self.deviceId,
                type=ValidationType.EMAIL,
                identity=email,
            ),
        )

    def get_account_eventlog(self, language: str = "en") -> EventLogResponse:
        return EventLogResponse(
            self.request("GET", "eventlog/profile", params=dict(language=language))
        )

    def check_device(
        self, deviceId: str, gcmToken: str | None = None
    ) -> APIResponseLite:
        """Check if the Device ID is valid.

        Parameters
        ----------
        deviceId : str
            The ID of the device.

        Returns
        -------

        """
        local_lang, _ = locale.getlocale()
        return APIResponseLite(
            self.request(
                "POST",
                "device",
                data=dict(
                    bundleID="com.narvii.amino.master",
                    clientType=100,
                    deviceID=deviceId,
                    locale=local_lang,
                    systemPushEnabled=True,
                    timestamp=currentTimeMillis(),
                    timezone=self.timezone,
                    deviceToken=gcmToken,
                    deviceTokenType=1 if gcmToken else None,
                ),
            )
        )

    def get_basic_profile(self) -> BasicProfile:
        return BasicProfileResponse(
            self.request("GET", "persona/profile/basic")
        ).profile

    def configure_basic_profile(
        self, age: int, gender: typing.Literal["male", "female", "non-binary"]
    ):
        """Configure the settings of an account.

        Parameters
        ----------
        age : int
            The user age. Minimum is 13.
        gender : {male, female, non-binary}
            Gender of the account.

        Returns
        -------
        APIResponseLite

        Raises
        ------
        ValueError
            If the age is less than 13

        """
        value = 1 if gender == "male" else 2 if gender == "female" else 255
        if age < 13:
            raise ValueError("The age has to be greater than 12")
        return self.request(
            "POST",
            "persona/profile/basic",
            data=dict(age=age, gender=value, timestamp=currentTimeMillis()),
        )

    def joined_communities(
        self, start: int = 0, size: int = 25
    ) -> JoinedCommunitiesResponse:
        """Get a list of the user's joined communities.

        Parameters
        ----------
        start : `int`, `optional`
            The start index. Default is `0`.
        size : `int`, `optional`
            The size of the list. Default is `25` (max is 250).

        Returns
        -------
        CommunityList
            The joined community list object.

        """
        return JoinedCommunitiesResponse(
            self.request(
                "GET", "community/joined", params=dict(start=start, size=size, v=1)
            )
        )

    @typing_extensions.deprecated("use joined_communities instead")
    def sub_clients(self, start: int = 0, size: int = 25) -> CommunityList:
        return self.joined_communities(start=start, size=size).communities

    def get_linked_communities(
        self, userId: str | None = None
    ) -> LinkedCommunityResponse:
        userId = userId or self.userId
        return LinkedCommunityResponse(
            self.request("GET", f"user-profile/{userId}/linked-community")
        )

    def reorder_linked_communities(self, comIds: list[int]) -> APIResponseLite:
        return APIResponseLite(
            self.request(
                "POST",
                f"user-profile/{self.userId}/linked-community/reorder",
                data=dict(ndcIds=comIds, timestamp=currentTimeMillis()),
            )
        )

    def add_linked_community(self, comId: int) -> APIResponseLite:
        return APIResponseLite(
            self.request("POST", f"user-profile/{self.userId}/linked-community/{comId}")
        )

    def remove_linked_community(self, comId: int) -> APIResponseLite:
        return APIResponseLite(
            self.request(
                "DELETE", f"user-profile/{self.userId}/linked-community/{comId}"
            )
        )

    def joined_chats(self, start: int = 0, size: int = 25) -> ThreadListResponse:
        """Get a list of the user's joined global chats.

        Parameters
        ----------
        start : `int`, `optional`
            The start index. Default is 0.
        size : `int`, `optional`
            The size of the list. Default is `25` (max is 250).

        Returns
        -------
        ThreadListResponse
            The joined chat response object.

        """
        return ThreadListResponse(
            self.request(
                "GET",
                "chat/thread",
                params=dict(type="joined-me", start=start, size=size),
            )
        )

    @typing_extensions.deprecated("use joined_chats instead")
    def get_chat_threads(self, start: int = 0, size: int = 25) -> ThreadList:
        return self.joined_chats(start=start, size=size).chats

    def invite_to_vc(self, chatId: str, userId: str):
        return self.request(
            "POST",
            f"chat/thread/{chatId}/vvchat-presenter/invite",
            data=dict(uid=userId, timestamp=currentTimeMillis()),
        )

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
        return ThreadResponse(self.request("GET", f"chat/thread/{chatId}")).chat

    @typing_extensions.deprecated("use get_chat_info instead")
    def get_chat_thread(self, chatId: str) -> Thread:
        return self.get_chat_info(chatId)

    def accept_host(self, chatId: str, requestId: str):
        return self.request(
            "POST",
            f"chat/thread/{chatId}/transfer-organizer/{requestId}/accept",
            data=dict(timestamp=currentTimeMillis()),
        )

    def decline_host(self, chatId: str, requestId: str):
        return self.request(
            "POST",
            f"chat/thread/{chatId}/transfer-organizer/{requestId}/decline",
            data=dict(timestamp=currentTimeMillis()),
        )

    def get_chat_messages(
        self, chatId: str, start: int = 0, size: int = 25, pageToken: str | None = None
    ):
        return self.request(
            "GET",
            f"chat/thread/{chatId}/message",
            params=dict(
                pageToken=pageToken, pagingType="t", start=start, size=size, v=2
            ),
        )

    def get_message_info(self, chatId: str, messageId: str):
        return self.request("GET", f"chat/thread/{chatId}/message/{messageId}")

    def get_chat_users(self, chatId: str, start: int = 0, size: int = 25):
        """Get chat member profile list

        Parameters
        ----------
        chatId : `str`
            The chat ID to fetch members.
        start : `int`, `optional`
            The start of the list index. Default is `0`.
        size : `int`, `optional`
            The size of the member list request, max is 250. Default is `25`.

        Returns
        -------
        """
        return self.request(
            "GET",
            f"chat/thread/{chatId}/member",
            params=dict(start=start, size=size, type="default", cv=1.2),
        )

    def invite_to_chat(self, userId: list[str] | str, chatId: str):
        return self.request(
            "POST",
            f"chat/thread/{chatId}/member/invite",
            data=dict(
                uids=[userId] if isinstance(userId, str) else userId,
                timestamp=currentTimeMillis(),
            ),
        )

    def kick(self, userId: str, chatId: str, allowRejoin: bool = True):
        return self.request(
            "DELETE",
            f"chat/thread/{chatId}/member/{userId}",
            params=dict(allowRejoin=int(allowRejoin)),
        )

    def leave_chat(self, chatId: str) -> APIResponseLite:
        """Leave a chat.

        Parameters
        ----------
        chatId : `str`
            The chat ID to leave.

        Returns
        -------
        APIResponseLite
            The amino api response.

        """
        return APIResponseLite(
            self.request("DELETE", f"chat/thread/{chatId}/member/{self.userId}")
        )

    def join_chat(self, chatId: str) -> ThreadMemberResponse:
        """Join a chat.

        Parameters
        ----------
        chatId : `str`
            The chat ID to join.

        Returns
        -------
        Json
            The JSON response.

        """
        return ThreadMemberResponse(
            self.request("POST", f"chat/thread/{chatId}/member/{self.userId}")
        )

    def start_chat(
        self,
        userId: collections.abc.Iterable[str] | str | None = None,
        message: str | None = None,
        title: str | None = None,
        content: str | None = None,
        chatType: int = 0,
    ):
        """Start a chat.

        Parameters
        ----------
        userId : `Iterable[str]`, `str`
            The user ID to chat or list of user IDs to chat.
        title : `str`, `optional`
            The chat title. Default is `None`.
        message : `str`, `optional`
            The initial message. Default is `None`.
        content : `str`, `optional`
            The chat description. Default is `None`.
        chatType : `int`, `optional`
            The chat type. Default is `0`.
                0: DM
                1: Private
                2: Public

        Returns
        -------
        Thread
            The new chat object.

        """
        inviteUids = (
            [userId]
            if isinstance(userId, str)
            else None if userId is None else list(userId)
        )
        return self.request(
            "POST",
            "chat/thread",
            data=dict(
                content=content,
                initialMessageContent=message,
                inviteeUids=inviteUids,
                title=title,
                type=chatType,
                timestamp=currentTimeMillis(),
            ),
            custom_headers={"ndc-submit-token": str(uuid.uuid4())},
        )

    def get_wallet_info(self) -> Wallet:
        return WalletResponse(self.request("GET", "wallet")).wallet

    def get_business_wallet_stats(self):
        return self.request(
            "GET", "wallet/business-coin/stats", params=dict(timezone=self.timezone)
        )

    def get_wallet_history(self, start: int = 0, size: int = 25):
        return self.request(
            "GET", "wallet/coin/history", params=dict(start=start, size=size)
        )

    def wallet_config(self, level: int):
        return self.request(
            "POST",
            "wallet/ads/config",
            data=dict(adsLevel=level, timestamp=currentTimeMillis()),
        )

    def get_from_deviceid(self, deviceId: str):
        return self.request("GET", "auid", params=dict(deviceId=deviceId))

    def get_community_lite(self, comId: int):
        return self.request("GET", "community/min-info", comId=comId, scope=True)

    def get_community_info(self, comId: int) -> CommunityInfoResponse:
        return CommunityInfoResponse(
            self.request(
                "GET",
                "community/info",
                params=dict(
                    withInfluencerList=1,
                    withTopicList="true",
                    influencerListOrderStrategy="fansCount",
                ),
                comId=comId,
                scope=True,
            )
        )

    def get_trending_topics(self, language: str = "en"):
        return self.request("GET", "topic/trending", params=dict(language=language))

    def get_public_communities(self, language: str = "en", size: int = 25):
        return self.request(
            "GET",
            "topic/0/feed/community",
            params=dict(
                language=language,
                type="web-explore",
                categoryKey="recommendation",
                size=size,
                pagingType="t",
            ),
        )

    def get_global_chats(self):
        return self.request("GET", "topic/0/feed/chat")

    def discover_topics(self, topicId: int, sectionKey: str, language: str = "en"):
        return self.request(
            "GET",
            f"topic/{topicId}/feed/story/{sectionKey}",
            params=dict(type="topic-list", v="2.0.0", language=language),
        )

    def get_interests(self, language: str = "en"):
        return self.request(
            "GET", "persona/onboarding-interests", params=dict(language=language)
        )

    def get_interest_topic(self, interestId: str):
        return self.request("GET", f"interest/{interestId}/topics")

    def get_topic_content(self, topicId: int):
        return self.request("GET", f"topic/{topicId}/content-modules")

    def get_bookmarks(self):
        return self.request("GET", "persona/bookmarked-topics")

    def reorder_bookmark(self, topicIds: collections.abc.Iterable[int]):
        return self.request(
            "POST",
            "persona/bookmarked-topics/reorder",
            data=dict(topicIds=list(topicIds), timestamp=int(time.time())),
        )

    def get_topic_bookmark(self, topicId: int):
        return self.request(
            "POST",
            f"persona/bookmarked-topics/{topicId}/bookmark",
            params=dict(v=2),
            data=dict(timestamp=currentTimeMillis()),
        )

    def unbookmark(self, topicId: int):
        return self.request(
            "POST",
            f"persona/bookmarked-topics/{topicId}/unbookmark",
            params=dict(v=2),
            data=dict(timestamp=currentTimeMillis()),
        )

    def get_supported_languages(self):
        return self.request(
            "GET",
            "community-collection/supported-languages",
            params=dict(start=0, size=100),
        )

    def get_all_users(
        self, type: typing.Literal["online", "recent"], start: int = 0, size: int = 25
    ) -> UserProfileListResponse:
        return UserProfileListResponse(
            self.request(
                "GET", "user-profile", params=dict(start=start, size=size, type=type)
            )
        )

    def get_user_following(self, userId: str, start: int = 0, size: int = 25):
        return self.request(
            "GET", f"user-profile/{userId}/joined", params=dict(start=start, size=size)
        )

    def get_user_followers(self, userId: str, start: int = 0, size: int = 25):
        return self.request(
            "GET", f"user-profile/{userId}/member", params=dict(start=start, size=size)
        )

    def get_user_visitors(self, userId: str, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            f"user-profile/{userId}/visitors",
            params=dict(start=start, size=size),
        )

    def get_blocked_users(self, start: int = 0, size: int = 25):
        return self.request("GET", f"block", params=dict(start=start, size=size))

    def get_blocker_users(self, start: int = 0, size: int = 25):
        return self.request(
            "GET", f"block/full-list", params=dict(start=start, size=size)
        )

    def get_wall_comments(
        self,
        userId: str,
        sorting: typing.Literal["newest", "oldest", "top"],
        start: int = 0,
        size: int = 25,
    ):
        return self.request(
            "GET",
            f"user-profile/{userId}/g-comment",
            params=dict(sort=sorting.replace("top", "vote"), start=start, size=size),
        )

    def send_text(
        self,
        chatId: str,
        message: str,
        messageType: int = 0,
        replyTo: str | None = None,
        mentionUserIds: collections.abc.Iterable[str] | None = None,
    ):
        return self.send_message(
            chatId=chatId,
            message=message,
            messageType=messageType,
            replyTo=replyTo,
            mentionUserIds=mentionUserIds,
        )

    def send_embed(
        self,
        chatId: str,
        objectId: str,
        objectType: int,
        link: str,
        title: str,
        content: str,
        image: collections.abc.Iterable[typing.BinaryIO] | typing.BinaryIO,
        parentId: str | None = None,
        parentType: str | None = None,
    ):
        return self.send_message(
            chatId,
            embedId=objectId,
            embedType=objectType,
            embedLink=link,
            embedTitle=title,
            embedContent=content,
            embedImage=image,
            embedParentId=parentId,
            embedParentType=parentType,
        )

    def send_audio(self, chatId: str, file: typing.BinaryIO):
        return self.send_message(chatId, file=file, fileType="audio")

    def send_image(self, chatId: str, file: typing.BinaryIO):
        return self.send_message(chatId, file=file, fileType="image")

    def send_gif(self, chatId: str, file: typing.BinaryIO):
        return self.send_message(chatId, file=file, fileType="gif")

    def send_sticker(self, chatId: str, stickerId: str):
        return self.send_message(chatId, stickerId=stickerId)

    def send_video(
        self,
        chatId: str,
        video: typing.BinaryIO,
        coverImage: typing.BinaryIO | None = None,
    ):
        return self.send_message(
            chatId, file=video, fileType="video", coverImage=coverImage
        )

    def send_message(
        self,
        chatId: str,
        message: str | None = None,
        messageType: MessageType | int = 0,
        file: typing.BinaryIO | None = None,
        fileType: FileTypeInput | None = None,
        coverImage: typing.BinaryIO | None = None,
        replyTo: str | None = None,
        mentionUserIds: collections.abc.Iterable[str] | None = None,
        stickerId: str | None = None,
        embedId: str | None = None,
        embedType: int | None = None,
        embedLink: str | None = None,
        embedTitle: str | None = None,
        embedContent: str | None = None,
        embedImage: (
            collections.abc.Iterable[typing.BinaryIO] | typing.BinaryIO | None
        ) = None,
        embedParentId: str | None = None,
        embedParentType: str | None = None,
    ):
        mentions: list[dict[str, str]] | None = None
        embedMediaList: list[list[typing.Any]] | None = None
        files: dict[str, typing.BinaryIO] | None = None
        content_type: str | None = None
        if message is not None and file is None:
            message = message.replace("<$", "\u200e\u200f").replace(
                "$>", "\u202c\u202d"
            )
        if mentionUserIds:
            mentions = [{"uid": userId} for userId in mentionUserIds]
        data: dict[str, typing.Any] = dict(
            attachedObject=None,
            content=message,
            clientRefId=int(time.time() / 10 % 1000000000),
            extensions=dict(mentionedArray=mentions),
            timestamp=currentTimeMillis(),
            type=messageType,
        )
        if any((embedId, embedType, embedLink, embedTitle, embedContent, embedImage)):
            if embedImage:
                embedMediaList = [
                    [100, self.upload_media(img, "image"), None]
                    for img in (
                        [embedImage]
                        if isinstance(embedImage, typing.BinaryIO)
                        else embedImage
                    )
                ]
            data.update(
                attachedObject=dict(
                    content=embedContent,
                    link=embedLink,
                    mediaList=embedMediaList,
                    objectId=embedId,
                    objectType=embedType,
                    title=embedTitle,
                    parentId=embedParentId,
                    parentType=embedParentType,
                )
            )
        if replyTo:
            data.update(replyMessageId=replyTo)
        if stickerId:
            data.update(content=None, stickerId=stickerId, type=3)
        if file:
            data.update(content=None)
            if fileType == "audio":
                data.update(type=2, mediaType=110)
            elif fileType == "image":
                data.update(
                    mediaType=100,
                    mediaUploadValueContentType="image/jpeg",
                    mediaUhqEnabled=True,
                )
            elif fileType == "gif":
                data.update(
                    mediaType=100,
                    mediaUploadValueContentType="image/gif",
                    mediaUhqEnabled=True,
                )
            elif fileType == "video":
                files = {"video.mp4": file}
                videoUpload = dict(contentType="video/mp4", video="video.mp4")
                if coverImage:
                    videoUpload.update(cover="cover.jpg")
                    files["cover.jpg"] = coverImage
                data.update(videoUpload=videoUpload)
                content_type = ContentType.MULTIPART
            else:
                raise ValueError(f"Unsupported fileType: {fileType}")
            data.update(mediaUploadValue=base64.b64encode(file.read()).decode())
        return self.request(
            "POST",
            f"chat/thread/{chatId}/message",
            data=data,
            files=files,
            content_type=content_type,
        )

    def edit_chat(
        self,
        chatId: str,
        doNotDisturb: bool | None = None,
        pinChat: bool | None = None,
        title: str | None = None,
        icon: typing.BinaryIO | str | None = None,
        backgroundImage: typing.BinaryIO | str | None = None,
        content: str | None = None,
        announcement: str | None = None,
        coHosts: collections.abc.Iterable[str] | None = None,
        keywords: collections.abc.Iterable[str] | None = None,
        pinAnnouncement: bool | None = None,
        publishToGlobal: bool | None = None,
        canTip: bool | None = None,
        viewOnly: bool | None = None,
        canInvite: bool | None = None,
        fansOnly: bool | None = None,
    ):
        extensions: dict[str, typing.Any] = {}
        data: dict[str, typing.Any] = dict(timestamp=currentTimeMillis())
        if title:
            data.update(title=title)
        if content:
            data.update(content=content)
        if icon:
            if not isinstance(icon, str):
                icon = self.upload_media(icon, fileType="image")
            data.update(icon=icon)
        if keywords:
            data.update(keywords=list(keywords))
        if isinstance(publishToGlobal, bool):
            data.update(publishToGlobal=int(publishToGlobal))
        if announcement:
            extensions.update(announcement=announcement)
        if isinstance(pinAnnouncement, bool):
            extensions.update(pinAnnouncement=pinAnnouncement)
        if isinstance(fansOnly, bool):
            extensions.update(fansOnly=fansOnly)
        res: list[dict[str, typing.Any]] = []
        if doNotDisturb is not None:
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/member/{self.userId}/alert",
                data=dict(
                    alertOption=int(doNotDisturb) + 1, timestamp=currentTimeMillis()
                ),
            )
            res.append(response)
        if pinChat is not None:
            fpath = "pin" if pinChat else "unpin"
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/{fpath}",
                data=dict(timestamp=currentTimeMillis()),
            )
            res.append(response)
        if backgroundImage is not None:
            if not isinstance(backgroundImage, str):
                backgroundImage = self.upload_media(backgroundImage, fileType="image")
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/member/{self.userId}/background",
                data=dict(
                    media=[100, backgroundImage, None], timestamp=currentTimeMillis()
                ),
            )
            res.append(response)
        if coHosts is not None:
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/co-host",
                data=dict(uidList=list(coHosts), timestamp=currentTimeMillis()),
            )
            res.append(response)
        if viewOnly is not None:
            fpath = "enable" if viewOnly else "disable"
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/view-only/{fpath}",
                data=dict(timestamp=currentTimeMillis()),
                content_type="application/x-www-form-urlencoded",
            )
            res.append(response)
        if canInvite is not None:
            fpath = "enable" if canInvite else "disable"
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/members-can-invite/{fpath}",
                data=dict(timestamp=currentTimeMillis()),
            )
            res.append(response)
        if canTip is not None:
            fpath = "enable" if canTip else "disable"
            response = self.request(
                "POST",
                f"chat/thread/{chatId}/tipping-perm-status/{fpath}",
                data=dict(timestamp=currentTimeMillis()),
            )
            res.append(response)
        response = self.request("POST", f"chat/thread/{chatId}", data=data)
        res.append(response)
        return res

    def delete_message(
        self,
        chatId: str,
        messageId: str,
        asStaff: bool = False,
        reason: str | None = None,
    ):
        method, url = "DELETE", f"chat/thread/{chatId}/message/{messageId}"
        if asStaff:
            url += "/admin"
            method = "POST"
        return self.request(
            method,
            url,
            data=dict(
                adminOpName=102,
                adminOpNote=dict(content=reason),
                timestamp=currentTimeMillis(),
            ),
        )

    def mark_as_read(self, chatId: str, messageId: str):
        return self.request(
            "POST",
            f"chat/thread/{chatId}/mark-as-read",
            data=dict(messageId=messageId, timestamp=currentTimeMillis()),
        )

    def visit(self, userId: str):
        return self.request(
            "GET", f"user-profile/{userId}", params=dict(action="visit")
        )

    def follow_users(self, userIds: collections.abc.Iterable[str]):
        return self.request(
            "POST",
            f"user-profile/{self.userId}/joined",
            data=dict(targetUidList=list(userIds), timestamp=currentTimeMillis()),
        )

    def follow(self, userId: str):
        return self.request("POST", f"user-profile/{userId}/member")

    def unfollow(self, userId: str):
        return self.request("DELETE", f"user-profile/{userId}/member/{self.userId}")

    def block(self, userId: str):
        return self.request("POST", f"block/{userId}")

    def unblock(self, userId: str):
        return self.request("DELETE", f"block/{userId}")

    def join_community(
        self, comId: int, invId: str | None = None
    ) -> CommunityJoinResponse:
        data: dict[str, typing.Any] = dict(timestamp=currentTimeMillis())
        if invId:
            data["invitationId"] = invId
        return CommunityJoinResponse(
            self.request("POST", f"community/join", data=data, comId=comId)
        )

    def request_join_community(self, comId: int, message: str | None = None):
        return self.request(
            "POST",
            "community/membership-request",
            data=dict(message=message, timestamp=currentTimeMillis()),
            comId=comId,
        )

    def leave_community(self, comId: int):
        return self.request("POST", "community/leave", comId=comId)

    def flag_community(
        self, comId: int, reason: str, flagType: int, isGuest: bool = False
    ):
        return self.request(
            "POST",
            "g-flag" if isGuest else "flag",
            data=dict(
                objectId=comId,
                objectType=16,
                flagType=flagType,
                message=reason,
                timestamp=currentTimeMillis(),
            ),
            comId=comId,
        )

    def get_membership_info(self):
        return self.request("GET", "membership", params=dict(force="true"))

    def get_ta_announcements(
        self, language: str = "en", start: int = 0, size: int = 25
    ):
        return self.request(
            "GET",
            "announcement",
            params=dict(language=language, start=start, size=size),
        )

    def get_bubble_info(self, bubbleId: str):
        return self.request("GET", f"chat/chat-bubble/{bubbleId}")

    def activate_store_bubble(self, bubbleId: str):
        return self.request(
            "POST",
            f"chat/chat-bubble/{bubbleId}/activate",
            data=dict(timestamp=currentTimeMillis()),
        )

    def get_store_chat_bubbles(self, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            "store/items",
            params=dict(sectionGroupId="chat-bubble", start=start, size=size),
        )

    def purchase(
        self,
        objectId: str,
        objectType: int,
        autoRenew: bool = False,
        aminoPlus: bool = False,
    ):
        return self.request(
            "POST",
            "store/purchase",
            data=dict(
                objectId=objectId,
                objectType=objectType,
                v=1,
                paymentContext=dict(
                    discountStatus=int(aminoPlus),
                    discountValue=1,  # ???
                    isAutoRenew=autoRenew,
                ),
                timestamp=currentTimeMillis(),
            ),
        )

    def get_product_subscriptions(self, start: int = 0, size: int = 25):
        return self.request(
            "GET",
            "store/subscription",
            params=dict(objectType=122, start=start, size=size),
        )

    def config_product_subscription(
        self, objectId: str, objectType: int, autoRenew: bool
    ):
        return self.request(
            "POST",
            "store/subscription/config",
            data=dict(
                paymentContext=dict(isAutoRenew=autoRenew),
                objectType=objectType,
                objectId=objectId,
                timestamp=currentTimeMillis(),
            ),
        )
