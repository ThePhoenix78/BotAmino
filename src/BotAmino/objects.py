from __future__ import annotations

import collections.abc
import typing
import typing_extensions

from .types import MediaType

__all__ = (
    "APIResponse",
    "Account",
    "AccountResponse",
    "AvatarFrame",
    "AvatarFrameList",
    "BasicProfile",
    "Channel",
    "Community",
    "CommunityList",
    "CommunityLite",
    "CommunityLiteList",
    "EventLogResponse",
    "LoginResponse",
    "ParticipatedExperiments",
    "RankingTable",
    "RankingTableList",
    "Thread",
    "ThreadList",
    "ThreadResponse",
    "UserProfile",
    "UserProfileList",
    "UserProfileLite",
    "UserProfileLiteList",
    "UserProfileResponse",
    "VisitSettings",
    "VisitSettingsResponse",
    "Wallet",
    "WalletResponse"
)

A = typing.TypeVar("A", bound="Array")
O = typing.TypeVar("O", bound="Object")


def nothing(data: typing.Any) -> typing.Any:
    return data


def safegetter(
    obj: typing.Any,
    *items: typing.Any,
    factory: collections.abc.Callable[[], typing.Any] | None = None
) -> typing.Any:
    try:
        for item in items:
            obj = obj[item]
    except (IndexError, KeyError, TypeError):
        obj = None
    if factory is None:
        return obj
    return obj or factory()


def safeitergetter(
    obj: typing.Any,
    *items: typing.Any,
    factory: collections.abc.Callable[[], typing.Any] | None = None
) -> list[typing.Any]:
    result: list[typing.Any] = []
    try:
        for subobj in obj:
            result.append(safegetter(subobj, *items, factory=factory))
    except TypeError:
        pass
    return result


def buildmapping(
    data: typing.Any,
    kconverter: collections.abc.Callable[[typing.Any], typing.Any] | None = None,
    vconverter: collections.abc.Callable[[typing.Any], typing.Any] | None = None
) -> dict[typing.Any, typing.Any]:
    kconverter = kconverter or nothing
    vconverter = vconverter or nothing
    return dict((kconverter(k), vconverter(v)) for k,v in dict(data).items())


def builditermapping(
    data: collections.abc.Iterable[typing.Any],
    kconverter: collections.abc.Callable[[typing.Any], typing.Any] | None = None,
    vconverter: collections.abc.Callable[[typing.Any], typing.Any] | None = None
) -> list[dict[typing.Any, typing.Any]]:
    result: list[dict[typing.Any, typing.Any]] = []
    try:
        for subdata in data:
            result.append(buildmapping(subdata, kconverter, vconverter))
    except TypeError:
        pass
    return result


class Array:
    __attr_names__: tuple[str, ...] = ()

    def __init__(self, data: collections.abc.MutableSequence[typing.Any]) -> None:
        self.json = data

    def __bool__(self) -> bool:
        return bool(self.json)

    def __iter__(self) -> collections.abc.Iterator[typing.Any]:
        return iter(self.json)

    def __len__(self) -> int:
        return len(self.__attr_names__)

    def __getstate__(self) -> list[typing.Any]:
        return self.to_json()

    def __setstate__(self, value: list[typing.Any]) -> None:
        type(self).__init__(self, value)

    def __getitem__(self, index: int | str) -> typing.Any:
        return getattr(self, self.to_attrname(index))

    def __setitem__(self, index: int | str, value: typing.Any) -> None:
        setattr(self, self.to_attrname(index), value)

    def to_attrname(self, index: int | str) -> str:
        if not isinstance(index, str):
            index = self.__attr_names__[index]
        return index

    def to_json(self, allowEmpty: bool = False) -> list[typing.Any]:
        data: list[typing.Any] = []
        for idx, name in enumerate(self.__attr_names__):
            value = getattr(self, name, None)
            if allowEmpty and not value:
                value = None
            if isinstance(value, (Array, ArrayList, Object, ObjectList)):
                value = value.to_json(allowEmpty=allowEmpty)
            data[idx] = value
        return data


class ArrayList(typing.Generic[A]):
    @property
    def __wrapped__(self) -> type[A]:
        args = typing.get_args(self)
        if not args:
            raise RuntimeError("Cannot determinate the wrapped object")
        wrapped, *_ = args
        return wrapped

    def __init__(self, data: collections.abc.Sequence[collections.abc.MutableSequence[typing.Any]]) -> None:
        self.json = data

    def __bool__(self) -> bool:
        return bool(self.json)

    def __iter__(self) -> collections.abc.Iterator[A]:
        return iter(map(self.__wrapped__, safeitergetter(self.json, factory=list)))

    def __len__(self) -> int:
        return len(self.json)

    def __getstate__(self) -> list[list[typing.Any]]:
        return self.to_json()

    def __setstate__(self, value: list[list[typing.Any]]) -> None:
        type(self).__init__(self, value)

    def to_json(self, allowEmpty: bool = False) -> list[list[typing.Any]]:
        return list(map(lambda obj: obj.to_json(allowEmpty=allowEmpty), self))


class Object:
    __attr_names__: typing.FrozenSet[tuple[str, str]] = frozenset({})

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        self.json = data

    def __bool__(self) -> bool:
        return bool(self.json)

    def __getstate__(self) -> dict[str, typing.Any]:
        return dict(self.to_json())

    def __setstate__(self, value: dict[str, typing.Any]) -> None:
        type(self).__init__(self, value)

    def __getitem__(self, key: str) -> typing.Any:
        for name, attrname in self.__attr_names__:
            if key in (name, attrname):
                return getattr(self, attrname)
        else:
            raise KeyError(key)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        for name, attrname in self.__attr_names__:
            if key in (name, attrname):
                setattr(self, attrname, value)
        else:
            raise KeyError(key)

    def to_json(self, allowEmpty: bool = False) -> dict[str, typing.Any]:
        data: dict[str, typing.Any] = {}
        for name, attrname in self.__attr_names__:
            value = getattr(self, attrname, None)
            if not allowEmpty and not value:
                continue
            if isinstance(value, dict):
                if typing.TYPE_CHECKING:
                    value = typing.cast(dict[str, typing.Any], value)
                for k, v in dict(value).items():
                    if isinstance(v, (Array, ArrayList, Object, ObjectList)):
                        value[k] = v.to_json(allowEmpty=allowEmpty) if value else None
            elif isinstance(value, (Array, ArrayList, Object, ObjectList)):
                value = value.to_json(allowEmpty=allowEmpty) if value else None
            data[name] = value
        return data


class ObjectList(typing.Generic[O]):
    @property
    def __wrapped__(self) -> type[O]:
        args = typing.get_args(self)
        if not args:
            raise RuntimeError("Cannot determinate the wrapped object")
        wrapped, *_ = args
        return wrapped

    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        self.json = data

    def __bool__(self) -> bool:
        return bool(self.json)

    def __iter__(self) -> collections.abc.Iterator[O]:
        return iter(map(self.__wrapped__, safeitergetter(self.json, factory=dict)))

    def __len__(self) -> int:
        return len(self.json)

    def __getstate__(self) -> list[dict[str, typing.Any]]:
        return self.to_json()

    def __setstate__(self, value: list[dict[str, typing.Any]]) -> None:
        type(self).__init__(self, value)

    def to_json(self, allowEmpty: bool = False) -> list[dict[str, typing.Any]]:
        return list(map(lambda obj: obj.to_json(allowEmpty=allowEmpty), self))


class APIResponseLite(Object):
    __attr_names__ = frozenset({
        ("api:debuginfo", "debuginfo"),
        ("api:duration", "duration"),
        ("api:message", "message"),
        ("api:statuscode", "statuscode"),
        ("api:timestamp", "timestamp")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.debuginfo: str | None = safegetter(data, "api:debuginfo")
        self.duration: str = safegetter(data, "api:duration")
        self.message: str = safegetter(data, "api:message")
        self.statuscode: int = safegetter(data, "api:statuscode")
        self.timestamp: str = safegetter(data, "api:timestamp")


class APIResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("deeplink", "deeplink"),
        ("cancelButtonText", "cancelButtonText"),
        ("noCancelButton", "noCancelButton"),
        ("okButtonText", "okButtonText"),
        ("title", "title"),
        ("url", "url")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.deeplink: str | None = safegetter(data, "deeplink")
        self.cancelButtonText: str | None = safegetter(data, "cancelButtonText")
        self.noCancelButton: bool | None = safegetter(data, "noCancelButton")
        self.okButtonText: str | None = safegetter(data, "okButtonText")
        self.title: str | None = safegetter(data, "title")
        self.url: str | None = safegetter(data, "url")


class AccountResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("account", "account")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.account: Account = Account(safegetter(data, "account", factory=dict))


class AffiliationsResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("affiliations", "affiliations")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.affiliations: list[int] = safegetter(data, "affiliations", factory=list)


class BasicProfileResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("basicProfile", "profile")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.profile: BasicProfile = BasicProfile(safegetter(data, "basicProfile", factory=dict))


class ChatMemberResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("memberList", "members")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.members: UserProfileLiteList = UserProfileLiteList(safegetter(data, "memberList", factory=list))


class CommunityInfoResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("community", "community"),
        ("currentUserInfo", "currentUserInfo"),
        ("isCurrentUserJoined", "isCurrentUserJoined")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.community: Community = Community(safegetter(data, "community", factory=dict))
        self.currentUserInfo: CurrentUserInfo = CurrentUserInfo(safegetter(data, "currentUserInfo", factory=dict))
        self.isCurrentUserJoined: bool = safegetter(data, "isCurrentUserJoined", factory=bool)


class CommunityJoinResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("newUserProfile", "newProfile"),
        ("notificationsCount", "notificationsCount"),
        ("userProfile", "profile")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.newProfile: bool = safegetter(data, "newUserProfile", factory=bool)
        self.notificationsCount: int = safegetter(data, "notificationsCount")
        self.profile: UserProfile = UserProfile(safegetter(data, "userProfile"))


class CommunitySearchResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("communityList", "communities"),
        ("userInfoInJoinedCommunities", "profiles"),
        ("userJoinedCommunityList", "joinedCommunities")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.communities: CommunityList = CommunityList(safegetter(data, "communityList", factory=list))
        self.joinedCommunities: CommunityList = CommunityList(safegetter(data, "userJoinedCommunityList", factory=list))
        self.profiles: dict[int, UserProfile] = buildmapping(safegetter(data, "userInfoInJoinedCommunities", factory=dict), int, UserProfile)


class CommunityTrendingResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("communityList", "communities")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.communities: CommunityList = safegetter(data, "communityList")


class DeviceResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("devOptions", "devOptions"),
        ("detailLogging", "detailLogging")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.devOptions: DevOptions = DevOptions(safegetter(data, "devOptions", factory=dict))
        self.detailLogging: DetailLogging = DetailLogging(safegetter(data, "detailLogging", factory=dict))


class EventLogResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("auid", "auid"),
        ("contentLanguage", "contentLanguage"),
        ("globalStrategyInfo", "globalStrategyInfo"),
        ("interestPickerStyle", "interestPickerStyle"),
        ("landingOption", "landingOption"),
        ("needTriggerInterestPicker", "needTriggerInterestPicker"),
        ("needsBirthDateUpdate", "needsBirthDateUpdate"),
        ("participatedExperiments", "participatedExperiments"),
        ("showStoreBadge", "showStoreBadge"),
        ("signUpStrategy", "signUpStrategy"),
        ("uid", "userId")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.auid: str = safegetter(data, "auid")
        self.contentLanguage: str = safegetter(data, "contentLanguage")
        self.globalStrategyInfo: str = safegetter(data, "globalStrategyInfo", factory=lambda: "{}")
        self.interestPickerStyle: int = safegetter(data, "interestPickerStyle", factory=int)
        self.landingOption: int = safegetter(data, "landingOption", factory=int)
        self.needTriggerInterestPicker: bool = safegetter(data, "needTriggerInterestPicker", factory=bool)
        self.needsBirthDateUpdate: bool = safegetter(data, "needsBirthDateUpdate", factory=bool)
        self.participatedExperiments: ParticipatedExperiments = ParticipatedExperiments(safegetter(data, "participatedExperiments", factory=dict))
        self.showStoreBadge: bool = safegetter(data, "showStoreBadge", factory=bool)
        self.signUpStrategy: int = safegetter(data, "signUpStrategy", factory=int)
        self.userId: str = safegetter(data, "uid")


class HumanReadable(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("threadCheckResultInCommunities", "chatsInCommunities"),
        ("treatedNdcIds", "comIds")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.comIds: list[int] = safegetter(data, "treatedNdcIds", factory=list)
        self.chatsInCommunities: dict[int, ThreadCheckResultInCommunity] = buildmapping(safegetter(data, "threadCheckResultInCommunities", factory=dict), int, ThreadCheckResultInCommunity)


class JoinedCommunitiesResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("communityList", "communities"),
        ("showStoreBadge", "showStoreBadge"),
        ("userInfoInCommunities", "communityProfiles")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.communities: CommunityList = CommunityList(safegetter(data, "communityList", factory=list))
        self.showStoreBadge: bool = safegetter(data, "showStoreBadge", factory=bool)
        self.communityProfiles: collections.abc.Mapping[int, UserProfileLite] = buildmapping(safegetter(data, "userInfoInCommunities", factory=dict), int, UserProfileLite)


class LinkIdentifyResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("community", "community"),
        ("currentUserInfo", "currentUserInfo"),
        ("isCurrentUserJoined", "isCurrentUserJoined"),
        ("path", "path")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.community: Community = Community(safegetter(data, "community", factory=dict))
        self.currentUserInfo: CurrentUserInfo = CurrentUserInfo(safegetter(data, "currentUserInfo", factory=dict))
        self.isCurrentUserJoined: bool = safegetter(data, "isCurrentUserJoined", factory=bool)
        self.path: str = safegetter(data, "path")


class LinkResolutionResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("linkInfoV2", "linkInfoV2")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.linkInfoV2: LinkInfoV2 = LinkInfoV2(safegetter(data, "linkInfoV2", factory=dict))


class LinkedCommunityResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("linkedCommunityList", "linkedCommunities"),
        ("unlinkedCommunityList", "unlinkedCommunities")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.linkedCommunities: CommunityLiteList = CommunityLiteList(safegetter(data, "linkedCommunityList", factory=list))
        self.unlinkedCommunities: CommunityLiteList = CommunityLiteList(safegetter(data, "unlinkedCommunityList", factory=list))


class LoginResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("account", "account"),
        ("auid", "auid"),
        ("userProfile", "profile"),
        ("secret", "secret"),
        ("sid", "sid")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.account: Account = Account(safegetter(data, "account", factory=dict))
        self.auid: str = safegetter(data, "auid")
        self.profile: UserProfile = UserProfile(safegetter(data, "userProfile", factory=dict))
        self.secret: str | None = safegetter(data, "secret")
        self.sid: str = safegetter(data, "sid")


class SearchAminoIdAndLinkResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("resultList", "results")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.results: ResultList = ResultList(safegetter(data, "resultList", factory=list))


class SoundCategoryResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("categoryList", "categories"),
        ("paging", "paging")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.categories: CategoryList = CategoryList(safegetter(data, "categoryList", factory=list))
        self.paging: Paging = Paging(safegetter(data, "paging", factory=dict))


class SoundCountResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("paging", "paging"),
        ("total", "total")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.paging: Paging = Paging(safegetter(data, "paging", factory=dict))
        self.total: int = safegetter(data, "total", factory=int)


class SoundSearchResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("paging", "paging"),
        ("seed", "seed"),
        ("total", "total")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.assetList: AssetList = AssetList(safegetter(data, "assetList", factory=list))
        self.paging: Paging = Paging(safegetter(data, "paging", factory=dict))
        self.seed: str = safegetter(data, "seed")
        self.total: int = safegetter(data, "total", factory=int)


class SoundSectionListResponse(APIResponseLite):
    __attr_names__ = frozenset({
        *APIResponseLite.__attr_names__,
        ("sectionList", "sections")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.sections: SectionList = SectionList(safegetter(data, "sectionList", factory=list))


class ThreadMemberResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("membershipStatus", "membershipStatus")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.membershipStatus: typing.Literal[0, 1] = safegetter(data, "membershipStatus", factory=int)
        # alias references
        self.joined = self.membershipStatus


class ThreadResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("thread", "chat")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.chat: Thread = Thread(safegetter(data, "thread", factory=dict))


class ThreadListResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("threadList", "chats"),
        ("playlistInThreadList", "playlists"),
        ("userInfoInThread", "userInfoInChat")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.chats: ThreadList = ThreadList(safegetter(data, "threadList", factory=list))
        self.playlists: collections.abc.Mapping[str, PlayList] = buildmapping(safegetter(data, "playlistInThreadList", factory=dict), str, PlayList)
        self.userInfoInChat: collections.abc.Mapping[str, UserInfoInThread] = buildmapping(safegetter(data, "userInfoInThread", factory=dict), str, UserInfoInThread)


class UserInfoInThread(Object):
    __attr_names__ = frozenset((
        ("userProfileCount", "profileCount"),
        ("userProfileList", "profile")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.profileCount: int = safegetter(data, "userProfileCount", factory=int)
        self.profile: UserProfileList = UserProfileList(safegetter(data, "userProfileList", factory=list))


class UserProfileResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("userProfile", "profile"),
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.profile: UserProfile = UserProfile(safegetter(data, "userProfile", factory=dict))


class UserProfileListResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("userProfileCount", "profileCount"),
        ("userProfileList", "profile")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.profile: UserProfileList = UserProfileList(safegetter(data, "userProfileList", factory=list))
        self.profileCount: int = safegetter(data, "userProfileCount", factory=int)

    def __iter__(self) -> collections.abc.Iterator["UserProfile"]:
        return iter(self.profile)


class VisitSettingsResponse(APIResponseLite):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.visitSettings: VisitSettings = VisitSettings(safegetter(data, "visitSettings", factory=dict))


class WalletResponse(APIResponseLite):
    __attr_names__ = frozenset((
        *APIResponseLite.__attr_names__,
        ("wallet", "wallet")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.wallet: Wallet = Wallet(safegetter(data, "wallet", factory=dict))


class StoreItemBase(Object):
    __attr_names__ = frozenset((
        ("availableNdcIds", "availableComIds"),
        ("isActivated", "isActivated"),
        ("isNew", "isNew"),
        ("ownershipInfo", "ownershipInfo"),
        ("restrictionInfo", "restrictionInfo")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.additionalBenefits: AdditionalBenefits = AdditionalBenefits(safegetter(data, "additionalBenefits", factory=dict))
        self.availableComIds: list[int] = safegetter(data, "availableNdcIds", factory=list)
        self.isActivated: bool = safegetter(data, "isActivated", factory=bool)
        self.isNew: bool = safegetter(data, "isNew", factory=bool)
        self.ownershipInfo: OwnershipInfo = OwnershipInfo(safegetter(data, "ownershipInfo", factory=dict))
        self.restrictionInfo: RestrictionInfo = RestrictionInfo(safegetter(data, "restrictionInfo", factory=dict))


class Account(Object):
    __attr_names__ = frozenset((
        ("activation", "activation"),
        ("advancedSettings", "advancedSettings"),
        ("aminoId", "aminoId"),
        ("aminoIdEditable", "aminoIdEditable"),
        ("appleID", "appleId"),
        ("createdTime", "createdTime"),
        ("deviceID", "deviceId"),
        ("email", "email"),
        ("emailActivation", "emailActivation"),
        ("extensions", "extensions"),
        ("facebookID", "facebookId"),
        ("googleID", "googleId"),
        ("icon", "icon"),
        ("mediaList", "mediaList"),
        ("membership", "membership"),
        ("modifiedTime", "modifiedTime"),
        ("nickname", "nickname"),
        ("phoneNumber", "phoneNumber"),
        ("phoneNumberActivation", "phoneNumberActivation"),
        ("securityLevel", "securityLevel"),
        ("status", "status"),
        ("twitterID", "twitterId"),
        ("username", "username")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.activation: bool = safegetter(data, "activation", factory=bool)
        self.adsEnabled: bool = safegetter(data, "extensions", "adsEnabled", factory=bool)
        self.adsFlags: int = safegetter(data, "extensions", "adsFlags", factory=int)
        self.adsLevel: int | None = safegetter(data, "extensions", "adsLevel")
        self.advancedSettings: dict[str, typing.Any] = safegetter(data, "advancedSettings", factory=dict)
        self.aminoId: str = safegetter(data, "aminoId")
        self.aminoIdEditable: bool = safegetter(data, "aminoIdEditable", factory=bool)
        self.analyticsEnabled: bool = safegetter(data, "advancedSettings", "analyticsEnabled", factory=bool)
        self.appleId: str | None = safegetter(data, "appleID")
        self.avatarFrame: AvatarFrame = AvatarFrame(safegetter(data, "avatarFrame", factory=dict))
        self.avatarFrameId: str | None = safegetter(data, "extensions", "avatarFrameId")
        self.contentLanguage: str = safegetter(data, "extensions", "contentLanguage", factory=lambda: "en")
        self.createdTime: str = safegetter(data, "createdTime")
        self.deviceId: str | None = safegetter(data, "deviceID")
        self.deviceInfo: dict[str, typing.Any] = safegetter(data, "extensions", "deviceInfo", factory=dict)
        self.email: str | None = safegetter(data, "email")
        self.emailActivation: bool = safegetter(data, "emailActivation", factory=bool)
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.facebookId: str | None = safegetter(data, "facebookID")
        self.googleId: str | None = safegetter(data, "googleID")
        self.icon: str | None = safegetter(data, "icon")
        self.lastPopupTime: str | None = safegetter(data, "extensions", "popupConfig", "ads", "lastPopupTime")
        self.mediaLabAdsMigrationAugust2020: bool = safegetter(data, "extensions", "mediaLabAdsMigrationAugust2020", factory=bool)
        self.mediaList: list[list[typing.Any]] = safegetter(data, "mediaList", factory=list)
        self.membership: typing.Any | None = safegetter(data, "membership")
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.nickname: str = safegetter(data, "nickname")
        self.phoneNumber: str | None = safegetter(data, "phoneNumber")
        self.phoneNumberActivation: bool = safegetter(data, "phoneNumberActivation", factory=bool)
        self.popupConfig: dict[str, typing.Any] = safegetter(data, "extensions", "popupConfig", factory=dict)
        self.securityLevel: int = safegetter(data, "securityLevel")
        self.status: int = safegetter(data, "status", factory=int)
        self.twitterId: str | None = safegetter(data, "twitterID")
        self.username: str | None = safegetter(data, "username")


class AdditionalBenefits(Object):
    __attr_names__ = frozenset((
        ("firstMonthFreeAminoPlusMembership", "firstMonthFreeAminoPlusMembership"),
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.firstMonthFreeAminoPlusMembership: bool = safegetter(data, "firstMonthFreeAminoPlusMembership", factory=bool)


class AdsVideoStats(Object):
    __attr_names__ = frozenset((
        ("canEarnedCoins", "canEarnedCoins"),
        ("canNotWatchVideoReason", "canNotWatchReason"),
        ("canWatchVideo", "canWatch"),
        ("nextWatchVideoInterval", "nextWatchInterval"),
        ("watchVideoMaxCount", "watchMaxCount"),
        ("watchedVideoCount", "watchedCount")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.canEarnedCoins: typing.Literal[0, 1] = safegetter(data, "canEarnedCoins", factory=int)
        self.canNotWatchReason: int | None = safegetter(data, "canNotWatchVideoReason")
        self.canWatch: bool = safegetter(data, "canWatchVideo", factory=bool)
        self.nextWatchInterval: int = safegetter(data, "nextWatchVideoInterval", factory=int)
        self.watchedCount: int = safegetter(data, "watchedVideoCount", factory=int)
        self.watchMaxCount: int = safegetter(data, "watchVideoMaxCount", factory=int)


class AvatarFrame(Object):
    __attr_names__ = frozenset((
        ("icon", "icon"),
        ("frameId", "frameId"),
        ("frameType", "frameType"),
        ("name", "name"),
        ("ownershipStatus", "ownershipStatus"),
        ("resourceUrl", "url"),
        ("status", "status"),
        ("version", "version")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.icon: str = safegetter(data, "icon")
        self.frameId: str = safegetter(data, "frameId")
        self.frameType: int = safegetter(data, "frameType")
        self.name: str = safegetter(data, "name")
        self.ownershipStatus: int | None = safegetter(data, "ownershipStatus")
        self.status: int = safegetter(data, "status")
        self.url: str = safegetter(data, "resourceUrl")
        self.version: int = safegetter(data, "version")


class AvatarFrameList(ObjectList[AvatarFrame]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.icon: list[str] = safeitergetter(data, "icon")
        self.frameId: list[str] = safeitergetter(data, "frameId")
        self.frameType: list[int] = safeitergetter(data, "frameType")
        self.name: list[str] = safeitergetter(data, "name")
        self.ownershipStatus: list[int | None] = safeitergetter(data, "ownershipStatus")
        self.status: list[int] = safeitergetter(data, "status")
        self.url: list[str] = safeitergetter(data, "resourceUrl")
        self.version: list[int] = safeitergetter(data, "version")


class BasicProfile(Object):
    __attr_names__ = frozenset((
        ("age", "age"),
        ("auid", "auid"),
        ("country_code", "country_code"),
        ("dateOfBirth", "dateOfBirth"),
        ("gender", "gender")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.age: int = safegetter(data, "age", factory=int)
        self.auid: str = safegetter(data, "auid")
        self.country_code: str = safegetter(data, "country_code")
        self.dateOfBirth: int = safegetter(data, "dateOfBirth")
        self.gender: int = safegetter(data, "gender")


class CategoryLite(Object):
    __attr_names__ = frozenset({
        ("assetType", "assetType"),
        ("children", "childrenIds"),
        ("createdTime", "createdTime"),
        ("id", "categoryId"),
        ("status", "status"),
        ("style", "style"),
        ("title", "title"),
        ("totalCount", "totalCount")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.assetType: int = safegetter(data, "assetType", factory=int)
        self.categoryId: str = safegetter(data, "id")
        self.childrenIds: list[str] = safegetter(data, "children", factory=list)
        self.createdTime: str = safegetter(data, "createdTime")
        self.status: int = safegetter(data, "status", factory=int)
        self.style: Style = Style(safegetter(data, "style", factory=dict))
        self.title: str = safegetter(data, "title")
        self.totalCount: int = safegetter(data, "totalCount", factory=int)


class CategoryLiteList(ObjectList[CategoryLite]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.assetType: list[int] = safeitergetter(data, "assetType", factory=int)
        self.categoryId: list[str] = safeitergetter(data, "id")
        self.childrenIds: list[list[str]] = safeitergetter(data, "children", factory=list)
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.status: list[int] = safeitergetter(data, "status", factory=int)
        self.style: StyleList = StyleList(safeitergetter(data, "style", factory=dict))
        self.title: list[str] = safeitergetter(data, "title")
        self.totalCount: list[int] = safeitergetter(data, "totalCount", factory=int)


class Category(CategoryLite):
    __attr_names__ = frozenset({
        *CategoryLite.__attr_names__,
        ("categoryType", "categoryType"),
        ("computedTags", "computedTags"),
        ("Level", "level"),
        ("parents", "parents"),
        ("sectionList", "sectionList"),
        ("tags", "tags")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.categoryType: str = safegetter(data, "categoryType")
        self.computedTags: list[str] = safegetter(data, "computedTags", factory=list)
        self.level: int = safegetter(data, "Level", factory=int)
        self.parents = safegetter(data, "parents", factory=list)  # unknown
        self.sectionList = safegetter(data, "sectionList")  # unknown
        self.tags: list[str] = safegetter(data, "tags", factory=list)


class CategoryList(CategoryLiteList):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.categoryType: list[str] = safeitergetter(data, "categoryType")
        self.computedTags: list[list[str]] = safeitergetter(data, "computedTags", factory=list)
        self.level: list[int] = safeitergetter(data, "Level", factory=int)
        self.parents = safeitergetter(data, "parents", factory=list)  # unknown
        self.sectionList = safeitergetter(data, "sectionList")  # unknown
        self.tags: list[list[str]] = safeitergetter(data, "tags", factory=list)

    @property
    def __wrapped__(self) -> typing.Type[Category]:
        return Category

    def __iter__(self) -> collections.abc.Iterator[Category]:
        return iter(map(self.__wrapped__, safeitergetter(self.json, factory=dict)))


class Channel(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.name: str = safegetter(data, "channelName")
        self.key: str = safegetter(data, "channelKey")
        self.uid: int = safegetter(data, "channelUid")
        self.expiredTime: int = safegetter(data, "expiredTime")
        self.comId: int = safegetter(data, "ndcId")
        self.chatId: str = safegetter(data, "threadId")


class ChannelUserInfo(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.joinRole: int = safegetter(data, "joinRole")
        self.comId: int = safegetter(data, "ndcId")
        self.chatId: str = safegetter(data, "threadId")
        self.userId: str = safegetter(data, "uid")


class CommunityLite(Object):
    __attr_names__ = frozenset((
        ("agent", "agent"),
        ("activeInfo", "activeInfo"),
        ("endpoint", "aminoId"),
        ("createdTime", "createdTime"),
        ("communityHeat", "heat"),
        ("icon", "icon"),
        ("joinType", "joinType"),
        ("link", "link"),
        ("listedStatus", "listedStatus"),
        ("membersCount", "usersCount"),
        ("modifiedTime", "modifiedTime"),
        ("name", "name"),
        ("ndcId", "comId"),
        ("primaryLanguage", "primaryLanguage"),
        ("probationStatus", "probationStatus"),
        ("promotionalMediaList", "promotionalMediaList"),
        ("status", "status"),
        ("tagline", "tagline"),
        ("templateId", "templateId"),
        ("themePack", "themePack"),
        ("updatedTime", "updatedTime"),
        ("userAddedTopicList", "userAddedTopicList")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.agent: UserProfileLite = UserProfileLite(safegetter(data, "agent", factory=dict))
        self.activeInfo: dict[str, typing.Any] = safegetter(data, "activeInfo", factory=dict)
        self.aminoId: str = safegetter(data, "endpoint")
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.createdTime: str = safegetter(data, "createdTime")
        self.heat: float = safegetter(data, "communityHeat", factory=float)
        self.icon: str = safegetter(data, "icon")
        self.joinType: int = safegetter(data, "joinType", factory=lambda: 1)
        self.link: str = safegetter(data, "link")
        self.listedStatus: int = safegetter(data, "listedStatus", factory=int)
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.name: str = safegetter(data, "name")
        self.primaryLanguage: str = safegetter(data, "primaryLanguage", factory=lambda: "en")
        self.probationStatus: int = safegetter(data, "probationStatus", factory=int)
        self.promotionalMediaList: list[list[typing.Any]] = safegetter(data, "promotionalMediaList", factory=list)
        self.status: int = safegetter(data, "status", factory=int)
        self.tagline: str = safegetter(data, "tagline")
        self.templateId: int = safegetter(data, "templateId", factory=int)
        self.themeColor: str = safegetter(data, "themePack", "themeColor")
        self.themeHash: str = safegetter(data, "themePack", "themePackHash")
        self.themePack: dict[str, typing.Any] = safegetter(data, "themePack", factory=dict)
        self.themeUrl: str = safegetter(data, "themePack", "themePackUrl")
        self.themeVersion: int = safegetter(data, "themePack", "themePackRevision")
        self.updatedTime: str | None = safegetter(data, "updatedTime")
        self.userAddedTopicList: list[typing.Any] = safegetter(data, "userAddedTopicList", factory=list)
        self.usersCount: int = safegetter(data, "membersCount", factory=int)


class Community(CommunityLite):
    __attr_names__ = frozenset((
        *CommunityLite.__attr_names__,
        ("advancedSettings", "advancedSettings"),
        ("configuration", "configuration"),
        ("content", "description"),
        ("extensions", "extensions"),
        ("influencerList", "influencerList"),
        ("isStandaloneAppDeprecated", "isStandaloneAppDeprecated"),
        ("isStandaloneAppMonetizationEnabled", "isStandaloneAppMonetizationEnabled"),
        ("keywords", "keywords"),
        ("mediaList", "mediaList"),
        ("searchable", "searchable")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.advancedSettings: dict[str, typing.Any] = safegetter(data, "advancedSettings", factory=dict)
        self.catalogEnabled: bool = safegetter(data, "advancedSettings", "catalogEnabled", factory=bool)
        self.configuration: dict[str, typing.Any] = safegetter(data, "configuration", factory=dict)
        self.customList: list[dict[str, typing.Any]] = safegetter(data, "configuration", "page", "customList", factory=list)
        self.defaultRankingTypeInLeaderboard: int = safegetter(data, "advancedSettings", "defaultRankingTypeInLeaderboard", factory=lambda: 1)
        self.description: str | None = safegetter(data, "content")
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.facebookAppIdList: list[str] = safegetter(data, "advancedSettings", "facebookAppIdList", factory=list)
        self.frontPageLayout: int = safegetter(data, "advancedSettings", "frontPageLayout", factory=lambda: 1)
        self.hasPendingReviewRequest: bool = safegetter(data, "advancedSettings", "hasPendingReviewRequest", factory=bool)
        self.influencerList: UserProfileLiteList = UserProfileLiteList(safegetter(data, "influencerList", factory=list))  # userprofilelite
        self.isStandaloneAppDeprecated: bool = safegetter(data, "isStandaloneAppDeprecated", factory=bool)
        self.isStandaloneAppMonetizationEnabled: bool = safegetter(data, "isStandaloneAppMonetizationEnabled", factory=bool)
        self.joinedBaselineCollectionIdList: list[str] = safegetter(data, "advancedSettings", "joinedBaselineCollectionIdList", factory=list)
        self.keywords: str | None = safegetter(data, "keywords")
        self.leaderboardStyle: dict[str, typing.Any] = safegetter(data, "advancedSettings", "leaderboardStyle", factory=dict)
        self.mediaList: list[list[typing.Any]] = safegetter(data, "mediaList", factory=list)
        self.nameAliases: str | None = safegetter(data, "extensions", "communityNameAliases")
        self.newsfeedPages: list[dict[str, typing.Any]] = safegetter(data, "advancedSettings", "newsfeedPages", factory=list)
        self.pollMinFullBarVoteCount: int = safegetter(data, "advancedSettings", "pollMinFullBarVoteCount", factory=int)
        self.rankingTable: RankingTableList = RankingTableList(safegetter(data, "advancedSettings", "rankingTable", factory=list))
        self.searchable: bool = safegetter(data, "searchable", factory=bool)
        self.themeHomePageAppearance: list[dict[str, typing.Any]] = safegetter(data, "configuration", "appearance", "homePage", "navigation", factory=list)
        self.themeLeftSidePanelBottom: list[dict[str, typing.Any]] = safegetter(data, "configuration", "appearance", "leftSidePanel", "navigation", "level2", factory=list)
        self.themeLeftSidePanelColor: str | None = safegetter(data, "configuration", "appearance", "leftSidePanel", "style", "iconColor")
        self.themeLeftSidePanelTop: list[dict[str, typing.Any]] = safegetter(data, "configuration", "appearance", "leftSidePanel", "navigation", "level1", factory=list)
        self.welcomeMessage: str | None = safegetter(data, "advancedSettings", "welcomeMessageText")
        self.welcomeMessageEnabled: bool = safegetter(data, "advancedSettings", "welcomeMessageEnabled", factory=bool)
        # alias references
        self.wikiEnabled = self.catalogEnabled


class CommunityLiteList(ObjectList[CommunityLite]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.agent: UserProfileLiteList = UserProfileLiteList(safeitergetter(data, "agent", factory=list))
        self.activeInfo: list[dict[str, typing.Any]] = safeitergetter(data, "activeInfo", factory=dict)
        self.aminoId: list[str] = safeitergetter(data, "endpoint")
        self.comId: list[int] = safeitergetter(data, "ndcId", factory=int)
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.heat: list[float] = safeitergetter(data, "communityHeat", factory=float)
        self.icon: list[str] = safeitergetter(data, "icon")
        self.joinType: list[int] = safeitergetter(data, "joinType", factory=lambda: 1)
        self.link: list[str] = safeitergetter(data, "link")
        self.listedStatus: list[int] = safeitergetter(data, "listedStatus", factory=int)
        self.modifiedTime: list[str | None] = safeitergetter(data, "modifiedTime")
        self.name: list[str] = safeitergetter(data, "name")
        self.primaryLanguage: list[str] = safeitergetter(data, "primaryLanguage", factory=lambda: "en")
        self.probationStatus: list[int] = safeitergetter(data, "probationStatus", factory=int)
        self.promotionalMediaList: list[list[list[typing.Any]]] = safeitergetter(data, "promotionalMediaList", factory=list)
        self.status: list[int] = safeitergetter(data, "status", factory=int)
        self.tagline: list[str] = safeitergetter(data, "tagline")
        self.templateId: list[int] = safeitergetter(data, "templateId", factory=int)
        self.themeColor: list[str] = safeitergetter(data, "themePack", "themeColor")
        self.themeHash: list[str] = safeitergetter(data, "themePack", "themePackHash")
        self.themePack: list[dict[str, typing.Any]] = safeitergetter(data, "themePack", factory=dict)
        self.themeUrl: list[str] = safeitergetter(data, "themePack", "themePackUrl")
        self.themeVersion: list[int] = safeitergetter(data, "themePack", "themePackRevision")
        self.updatedTime: list[str | None] = safeitergetter(data, "updatedTime")
        self.userAddedTopicList: list[list[typing.Any]] = safeitergetter(data, "userAddedTopicList", factory=list)
        self.usersCount: list[int] = safeitergetter(data, "membersCount", factory=int)


class CommunityList(CommunityLiteList):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.advancedSettings: list[dict[str, typing.Any]] = safeitergetter(data, "advancedSettings", factory=dict)
        self.catalogEnabled: list[bool] = safeitergetter(data, "advancedSettings", "catalogEnabled", factory=bool)
        self.configuration: list[dict[str, typing.Any]] = safeitergetter(data, "configuration", factory=dict)
        self.customList: list[list[dict[str, typing.Any]]] = safeitergetter(data, "configuration", "page", "customList", factory=list)
        self.defaultRankingTypeInLeaderboard: list[int] = safeitergetter(data, "advancedSettings", "defaultRankingTypeInLeaderboard", factory=lambda: 1)
        self.description: list[str | None] = safeitergetter(data, "content")
        self.extensions: list[dict[str, typing.Any]] = safeitergetter(data, "extensions", factory=dict)
        self.facebookAppIdList: list[list[str]] = safeitergetter(data, "advancedSettings", "facebookAppIdList", factory=list)
        self.frontPageLayout: list[int] = safeitergetter(data, "advancedSettings", "frontPageLayout", factory=lambda: 1)
        self.hasPendingReviewRequest: list[bool] = safeitergetter(data, "advancedSettings", "hasPendingReviewRequest", factory=bool)
        self.influencerList: list[UserProfileLiteList] = list(map(UserProfileLiteList, safeitergetter(data, "influencerList", factory=list)))
        self.isStandaloneAppDeprecated: list[bool] = safeitergetter(data, "isStandaloneAppDeprecated", factory=bool)
        self.isStandaloneAppMonetizationEnabled: list[bool] = safeitergetter(data, "isStandaloneAppMonetizationEnabled", factory=bool)
        self.joinedBaselineCollectionIdList: list[list[str]] = safeitergetter(data, "advancedSettings", "joinedBaselineCollectionIdList", factory=list)
        self.keywords: list[str | None] = safeitergetter(data, "keywords")
        self.leaderboardStyle: list[dict[str, typing.Any]] = safeitergetter(data, "advancedSettings", "leaderboardStyle", factory=dict)
        self.mediaList: list[list[list[typing.Any]]] = safeitergetter(data, "mediaList", factory=list)
        self.nameAliases: list[str | None] = safeitergetter(data, "extensions", "communityNameAliases")
        self.newsfeedPages: list[list[dict[str, typing.Any]]] = safeitergetter(data, "advancedSettings", "newsfeedPages", factory=list)
        self.pollMinFullBarVoteCount: list[int] = safeitergetter(data, "advancedSettings", "pollMinFullBarVoteCount", factory=int)
        self.rankingTable: list[RankingTableList] = list(map(RankingTableList, safeitergetter(data, "advancedSettings", "rankingTable", factory=list)))
        self.searchable: list[bool] = safeitergetter(data, "searchable", factory=bool)
        self.themeHomePageAppearance: list[list[dict[str, typing.Any]]] = safeitergetter(data, "configuration", "appearance", "homePage", "navigation", factory=list)
        self.themeLeftSidePanelBottom: list[list[dict[str, typing.Any]]] = safeitergetter(data, "configuration", "appearance", "leftSidePanel", "navigation", "level2", factory=list)
        self.themeLeftSidePanelColor: list[str | None] = safeitergetter(data, "configuration", "appearance", "leftSidePanel", "style", "iconColor")
        self.themeLeftSidePanelTop: list[list[dict[str, typing.Any]]] = safeitergetter(data, "configuration", "appearance", "leftSidePanel", "navigation", "level1", factory=list)
        self.welcomeMessage: list[str | None] = safeitergetter(data, "advancedSettings", "welcomeMessageText")
        self.welcomeMessageEnabled: list[bool] = safeitergetter(data, "advancedSettings", "welcomeMessageEnabled", factory=bool)
        # alias references
        self.wikiEnabled = self.catalogEnabled

    @property
    def __wrapped__(self) -> type[Community]:
        return Community

    def __iter__(self) -> collections.abc.Iterator[Community]:
        return iter(map(self.__wrapped__, safeitergetter(self.json, factory=dict)))


class CurrentUserInfo(Object):
    __attr_names__ = frozenset((
        ("notificationsCount", "notificationsCount"),
        ("userProfile", "profile")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.notificationsCount: int = safegetter(data, "notificationsCount", factory=int)
        self.profile: UserProfile = UserProfile(safegetter(data, "userProfile", factory=dict))


class DetailLogging(Object):
    __attr_names__ = frozenset((
        ("enabled", "enabled"),
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.enabled: bool = safegetter(data, "enabled", factory=bool)


class DevOptions(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)


class FanClub(Object): ...


class FanClubList(ObjectList[FanClub]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)


class Invitation(Object):
    __attr_names__ = frozenset((
        ("author", "author"),
        ("createdTime", "createdTime"),
        ("duration", "duration"),
        ("invitationId", "invId"),
        ("inviteCode", "inviteCode"),
        ("link", "link"),
        ("modifiedTime", "modifiedTime"),
        ("ndcId", "comId"),
        ("status", "status")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.author: UserProfileLite = UserProfileLite(safegetter(data, "author", factory=dict))
        self.comId: int = safegetter(data, "ndcId")
        self.createdTime: str | None = safegetter(data, "createdTime")
        self.duration: int = safegetter(data, "duration", factory=int)
        self.invId: str = safegetter(data, "invitationId")
        self.inviteCode: str = safegetter(data, "inviteCode")
        self.link: str = safegetter(data, "link")
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.status: int = safegetter(data, "status")


class JamendoExt(Object):
    __attr_names__ = frozenset({
        ("date", "date"),
        ("jid", "id"),
        ("sha2", "sha2"),
        ("tags", "tags"),
        ("url", "url")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.url: str = safegetter(data, "url")
        self.date: str = safegetter(data, "date")
        self.id: int = safegetter(data, "jid", factory=int)
        self.sha2: str = safegetter(data, "sha2")
        self.tags: str = safegetter(data, "tags")


class JamendoExtList(ObjectList[JamendoExt]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.url: list[str] = safeitergetter(data, "url")
        self.date: list[str] = safeitergetter(data, "date")
        self.id: list[int] = safeitergetter(data, "jid", factory=int)
        self.sha2: list[str] = safeitergetter(data, "sha2")
        self.tags: list[str] = safeitergetter(data, "tags")


class LinkInfo(Object):
    __attr_names__ = frozenset((
        ("fullPath", "fullPath"),
        ("ndcId", "comId"),
        ("objectId", "objectId"),
        ("objectType", "objectType"),
        ("shortCode", "shortCode"),
        ("shareURLFullPath", "shareURLFullPath"),
        ("shareURLShortCode", "shareURLShortCode"),
        ("targetCode", "targetCode")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.fullPath: str = safegetter(data, "fullPath")
        self.objectId: str = safegetter(data, "objectId")
        self.objectType: int = safegetter(data, "objectType")
        # shortCode: the final component of the shareURLShortCode
        self.shortCode: str = safegetter(data, "shortCode")
        # shareURLFullPath: like http://aminoapps.com/web/x0/chat-thread/da629b3b-149b-4a57-af4e-efd18be2c5ed
        self.shareURLFullPath: str = safegetter(data, "shareURLFullPath")
        # shareURLShortCode: like http://aminoapps.com/p/{shortCode}
        self.shareURLShortCode: str = safegetter(data, "shareURLShortCode")
        self.targetCode: int = safegetter(data, "targetCode")
        # alias references (amino.fix)
        self.fullUrl = self.shareURLFullPath
        self.shortUrl = self.shareURLShortCode


class LinkInfoV2(Object):
    __attr_names__ = frozenset((
        ("extensions", "extensions"),
        ("path", "path")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.path: str = safegetter(data, "path")
        self.community: Community = Community(safegetter(data, "extensions", "community"))
        self.currentUserInfo: CurrentUserInfo = CurrentUserInfo(safegetter(data, "extensions", "currentUserInfo", factory=dict))
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.invitation: Invitation = Invitation(safegetter(data, "extensions", "invitation"))
        self.invId: str | None = safegetter(data, "extensions", "invitationId")
        self.isCurrentUserJoined: bool = safegetter(data, "extensions", "isCurrentUserJoined", factory=bool)
        self.linkInfo: LinkInfo = LinkInfo(safegetter(data, "extensions", "linkInfo", factory=dict))
        # shorcuts
        self.comId = self.community.comId or self.linkInfo.comId
        self.objectId = self.linkInfo.objectId
        self.objectType = self.linkInfo.objectType
        self.shareURLShortCode = self.linkInfo.shareURLShortCode


class LiveLayerEvent(Object):
    __attr_names__ = frozenset((
        ("ndcId", "comId"),
        ("topic", "topic"),
        ("userProfileCount", "profileCount"),
        ("userProfileList", "profile")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.comId: int = safegetter(data, "ndcId")
        self.profile: UserProfileLiteList = UserProfileLiteList(safegetter(data, "userProfileList", factory=list))
        self.profileCount: int = safegetter(data, "userProfileCount")
        self.topic: str = safegetter(data, "topic")


class MediaMetadata(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.coverImage: str = safegetter(data, "coverImage")
        self.duration: float = (safegetter(data, "duration") or 0.0) * 1000
        self.width: int = safegetter(data, "width")
        self.height: int = safegetter(data, "height")
        self.author: str = safegetter(data, "author")
        self.fileName: str = safegetter(data, "fileName")

    @classmethod
    def new(
        cls,
        coverImage: str,
        duration: float,
        width: int,
        height: int,
        author: str,
        fileName: str
    ):
        return cls(dict(
            coverImage=coverImage,
            duration=duration/1000,
            width=width,
            height=height,
            author=author,
            fileName=fileName
        ))
            

class Media(Array):
    __attr_names__ = (
        "type",
        "url",
        "caption",
        "refId",
        "null",
        "metadata"
    )

    def __init__(self, data: collections.abc.MutableSequence[typing.Any]) -> None:
        super().__init__(data)
        self.type: int = safegetter(data, 0)
        self.url: str = safegetter(data, 1)
        self.caption: str | None = safegetter(data, 2)
        self.refId: str | None = safegetter(data, 3)
        self.null: typing.Any | None = safegetter(data, 4)
        self.metadata: dict[str, str] = safegetter(data, 5, factory=dict)

    @classmethod
    def new(
        cls,
        type: typing.Union[MediaType, int],
        url: str,
        caption: str | None = None,
        refId: str | None = None,
        metadata: MediaMetadata | None = None
    ):
        return cls([type, url, caption, refId, None, metadata.json if metadata else None])


class MediaList(ArrayList[Media]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.MutableSequence[typing.Any]]) -> None:
        super().__init__(data)
        self.type: int = safegetter(data, 0)
        self.url: str = safegetter(data, 1)
        self.caption: str | None = safegetter(data, 2)
        self.refId: str | None = safegetter(data, 3)
        self.null: typing.Any | None = safegetter(data, 4)
        self.metadata: dict[str, str] = safegetter(data, 5, factory=dict)

    def add(self, *medias: Media) -> None:
        data = self.to_json()
        data.extend(map(lambda media: list(media.json), medias))
        type(self).__init__(self, data)


class Notification(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.aps: PushAPS = PushAPS(safegetter(data, "aps", factory=dict))
        self.community: Community = Community(safegetter(data, "community", factory=dict))
        self.expireTime: int = safegetter(data, "exp")
        self.ext: dict[str, typing.Any] = safegetter(data, "ext", factory=dict)
        self.fromUser: UserProfile = safegetter(data, "userProfile")
        self.messageId: str = safegetter(data, "id")
        self.messageType: int = safegetter(data, "msgType")
        self.minPayloadVersion = safegetter(data, "cv")
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.nickname: str = safegetter(data, "nickname")
        self.picType: int = safegetter(data, "picType", factory=int)
        self.picUrl: str = safegetter(data, "picUrl")
        self.chatId: str = safegetter(data, "tid")
        self.chatType: int  = safegetter(data, "ttype", lambda: -1)
        self.createdTime: str = safegetter(data, "ts")
        self.trackId: str = safegetter(data, "t")
        self.type: int = safegetter(data, "notifType")
        self.userId: str = safegetter(data, "uid")
        self.url: str = safegetter(data, "u")


class OwnershipInfo(Object):
    __attr_names__ = frozenset((
        ("createdTime", "createdTime"),
        ("expiredTime", "expiredTime"),
        ("isAutoRenew", "isAutoRenew"),
        ("ownershipStatus", "ownershipStatus")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.createdTime: str = safegetter(data, "createdTime")
        self.expiredTime: str | None = safegetter(data, "expiredTime")
        self.isAutoRenew: bool = safegetter(data, "isAutoRenew", factory=bool)
        self.ownershipStatus: int = safegetter(data, "ownershipStatus", factory=int)


class Paging(Object):
    __attr_names__ = frozenset({
        ("count", "count")
    })
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.count: int = safegetter(data, "count", factory=int)


class PushAPS(Object):
    __attr_names__ = frozenset((
        ("alert", "alert"),
        ("badge", "badge"),
        ("sound", "sound"),
        ("message", "message"),
        ("title", "title")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.alert: str | dict[str, typing.Any] | None = safegetter(data, "alert")
        self.badge: int = safegetter(data, "badge") or 0
        self.sound: str | None = safegetter(data, "sound")
        self.message: str = self.alert if isinstance(self.alert, str) else (safegetter(self.alert, "body") or safegetter(data, "message"))
        self.title: str | None = safegetter(self.alert, "title") or safegetter(data, "title")


class ParticipatedExperiments(Object):
    __attr_names__ = frozenset((
        ("chatMembersCommonChannel", "chatMembersCommonChannel"),
        ("communityMembersCommonChannel", "communityMembersCommonChannel"),
        ("communityTabExp", "communityTabExp"),
        ("couponPush", "couponPush"),
        ("landingOptionExp", "landingOptionExp"),
        ("retentionSrPush", "retentionSrPush"),
        ("userVectorCommunitySimilarityChannel", "userVectorCommunitySimilarityChannel")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.chatMembersCommonChannel: int = safegetter(data, "chatMembersCommonChannel")
        self.communityMembersCommonChannel: int = safegetter(data, "communityMembersCommonChannel")
        self.communityTabExp: int = safegetter(data, "communityTabExp")
        self.couponPush: int = safegetter(data, "couponPush")
        self.landingOptionExp: int = safegetter(data, "landingOptionExp")
        self.retentionSrPush: int = safegetter(data, "retentionSrPush")
        self.userVectorCommunitySimilarityChannel: int = safegetter(data, "userVectorCommunitySimilarityChannel")


class PlayList(Object):
    __attr_names__ = frozenset((
        ("currentItemIndex", "currentItemIndex"),
        ("currentItemStatus", "currentItemStatus"),
        ("items", "items")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.currentItemIndex: int = safegetter(data, "currentItemIndex", factory=int)
        self.currentItemStatus: int = safegetter(data, "currentItemStatus", factory=int)
        self.items: PlayListItemList = PlayListItemList(safegetter(data, "items", factory=list))

    def __len__(self) -> int:
        return len(self.items)

    def add(self, *items: PlayListItem) -> None:
        data = self.to_json()
        data["items"] = [*self.items.json, *map(lambda item: item.json, items)]
        type(self).__init__(self, data)

    @classmethod
    def new(cls, *items: PlayListItem) -> typing_extensions.Self:
        return cls({
            "currentItemIndex": 0,
            "currentItemStatus": 0,
            "items": [item.json for item in items]
        })


class PlayListItem(Object):
    __attr_names__ = frozenset((
        ("duration", "duration"),
        ("isDone", "isDone"),
        ("mediaList", "mediaList"),
        ("title", "title"),
        ("type", "type"),
        ("url", "url")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.duration: float | None = safegetter(data, "duration")
        self.isDone: bool = safegetter(data, "isDone", factory=bool)
        self.mediaList: list[list[typing.Any]] = safegetter(data, "mediaList", factory=list)
        self.title: str = safegetter(data, "title")
        self.type: int = safegetter(data, "type")
        self.url: str = safegetter(data, "url")

    def mark_as_played(self) -> None:
        data = self.to_json(allowEmpty=True)
        data["isDone"] = True
        type(self).__init__(self, data)

    @classmethod
    def new(
        cls,
        type: int,
        url: str,
        title: str,
        backgroundImage: str | None = None,
        duration: float | None = None
    ) -> typing_extensions.Self:
        return cls({
            "duration": duration,
            "isDone": False,
            "mediaList": [100, backgroundImage, None] if backgroundImage else None,
            "title": title,
            "type": type,
            "url": url
        })


class PlayListItemList(ObjectList[PlayListItem]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        self.json = data
        self.duration: list[float | None] = safeitergetter(data, "duration")
        self.isDone: list[bool] = safeitergetter(data, "isDone", factory=bool)
        self.mediaList: list[list[list[typing.Any]]] = safeitergetter(data, "mediaList", factory=list)
        self.title: list[str] = safeitergetter(data, "title")
        self.type: list[int] = safeitergetter(data, "type")
        self.url: list[str] = safeitergetter(data, "url")


class RankingTable(Object):
    __attr_names__ = frozenset((
        ("id", "id"),
        ("level", "level"),
        ("reputation", "reputation"),
        ("title", "title")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.id: str = safegetter(data, "id")
        self.level: int = safegetter(data, "level")
        self.reputation: int = safegetter(data, "reputation")
        self.title: str = safegetter(data, "title")


class RankingTableList(ObjectList[RankingTable]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.id: list[str] = safeitergetter(data, "id", factory=str)
        self.level: list[int] = safeitergetter(data, "level", factory=int)
        self.reputation: list[int] = safeitergetter(data, "reputation", factory=int)
        self.title: list[str] = safeitergetter(data, "title", factory=str)


class RestrictionInfo(Object):
    __attr_names__ = frozenset((
        ("availableDuration", "availableDuration"),
        ("discountStatus", "discountStatus"),
        ("discountValue", "discountValue"),
        ("ownerType", "ownerType"),
        ("ownerUid", "ownerId"),
        ("restrictType", "restrictType"),
        ("restrictValue", "restrictValue")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.availableDuration: int | None = safegetter(data, "availableDuration")
        self.discountStatus: int = safegetter(data, "discountStatus", factory=int)
        self.discountValue: int | None = safegetter(data, "discountValue", factory=int)
        self.ownerId: str | None = safegetter(data, "ownerUid")
        self.ownerType: int | None = safegetter(data, "ownerType")
        self.restrictType: int = safegetter(data, "restrictType", factory=int)
        self.restrictValue: int | None = safegetter(data, "restrictValue")


class Result(Object):
    __attr_names__ = frozenset((
        ("aminoId", "aminoId"),
        ("ndcId", "comId"),
        ("objectId", "objectId"),
        ("objectType", "objectType"),
        ("refObject", "refObject")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.aminoId: str = safegetter(data, "aminoId")
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.objectId: str = safegetter(data, "objectId")
        self.objectType: int = safegetter(data, "objectType", factory=int)
        self.refObject: dict[str, typing.Any] = safegetter(data, "refObject", factory=dict)


class ResultList(ObjectList[Result]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.aminoId: list[str] = safeitergetter(data, "aminoId")
        self.comId: list[int] = safeitergetter(data, "ndcId", factory=int)
        self.objectId: list[str] = safeitergetter(data, "objectId")
        self.objectType: list[int] = safeitergetter(data, "objectType", factory=int)
        self.refObject: list[dict[str, typing.Any]] = safeitergetter(data, "refObject", factory=dict)


class Asset(Object):
    __attr_names__ = frozenset({
        ("assetType", "assetType"),
        ("categoryList", "categoryList"),
        ("createdTime", "createdTime"),
        ("id", "id"),
        ("objectId", "objectId"),
        ("objectType", "objectType"),
        ("refObject", "refObject"),
        ("searchKeywordList", "searchKeywordList"),
        ("status", "status")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.assetType: int = safegetter(data, "assetType", factory=int)
        self.categoryList = safegetter(data, "categoryList")  # unknown
        self.createdTime: str = safegetter(data, "createdTime")
        self.id: str = safegetter(data, "id")
        #self.isNone: bool = safegetter(data, "isNone", factory=bool)
        self.objectId: str = safegetter(data, "objectId")
        self.objectType: int = safegetter(data, "objectType", factory=int)
        self.refObject = safegetter(data, "refObject", factory=dict)
        self.searchKeywordList = safegetter(data, "searchKeywordList")  # unknown
        self.status: int = safegetter(data, "status")
        #self.thumbnailUrl: str = safegetter(data, "thumbnailUrl")
        #self.url: str = safegetter(data, "url")
        # 
        #self.categoryList: AssetCategoryList = AssetCategoryList(safegetter(data, "categoryList", factory=list))
        #self.refObject: typing.Union[Asset, Sound] = Sound(refObject) if self.objectType == 101 else Asset(refObject)


class AssetList(ObjectList[Asset]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.assetType: list[int] = safeitergetter(data, "assetType", factory=int)
        self.categoryList = safeitergetter(data, "categoryList")  # unknown
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.id: list[str] = safeitergetter(data, "id")
        self.objectId: list[str] = safeitergetter(data, "objectId")
        self.objectType: list[int] = safeitergetter(data, "objectType", factory=int)
        self.refObject: SoundList = SoundList(safeitergetter(data, "refObject", factory=dict))
        self.searchKeywordList = safeitergetter(data, "searchKeywordList")  # unknown
        self.status: list[int] = safeitergetter(data, "status", factory=int)


class Section(Object):
    __attr_names__ = frozenset({
        ("name", "name"),
        ("title", "title")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.name: str = safegetter(data, "name")
        self.title: str = safegetter(data, "title")


class SectionList(ObjectList[Section]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.name: list[str] = safeitergetter(data, "name")
        self.title: list[str] = safeitergetter(data, "title")


class Sound(Object):
    __attr_names__ = frozenset({
        ("album", "album"),
        ("artist", "artist"),
        ("createdTime", "createdTime"),
        ("duration", "duration"),
        ("fileSizeInByte", "fileSizeInByte"),
        ("fileType", "fileType"),
        ("genre", "genre"),
        ("id", "id"),
        ("jamendoExt", "jamendo"),
        ("mediaType", "mediaType"),
        ("mediaUrl", "mediaUrl"),
        ("source", "source"),
        ("status", "status"),
        ("thumbnailUrl", "thumbnailUrl"),
        ("title", "title"),
        ("type", "type")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.album: str = safegetter(data, "album")
        self.artist: str = safegetter(data, "artist")
        self.createdTime: str = safegetter(data, "createdTime")
        self.duration: int = safegetter(data, "duration", factory=int)
        self.jamendo: JamendoExt = JamendoExt(safegetter(data, "jamendoExt", factory=dict))
        self.fileSizeInByte: int = safegetter(data, "fileSizeInByte", factory=int)
        self.fileType: str = safegetter(data, "fileType")
        self.genre: str = safegetter(data, "genre")
        self.id: str = safegetter(data, "id")
        self.mediaType: int = safegetter(data, "mediaType", factory=int)
        self.mediaUrl: str = safegetter(data, "mediaUrl")
        self.source: str = safegetter(data, "source")  # {Jamendo,}
        self.status: int = safegetter(data, "status", factory=int)
        self.tags: list[str] = safegetter(data, "tags", factory=list)
        self.thumbnailUrl: str = safegetter(data, "thumbnailUrl")
        self.title: str = safegetter(data, "title")
        self.type: int = safegetter(data, "type", factory=int)


class SoundList(ObjectList[Sound]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.album: list[str] = safeitergetter(data, "album")
        self.artist: list[str] = safeitergetter(data, "artist")
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.duration: list[int] = safeitergetter(data, "duration", factory=int)
        self.jamendo: JamendoExtList = JamendoExtList(safeitergetter(data, "jamendoExt", factory=dict))
        self.fileSizeInByte: list[int] = safeitergetter(data, "fileSizeInByte", factory=int)
        self.fileType: list[str] = safeitergetter(data, "fileType")
        self.genre: list[str] = safeitergetter(data, "genre")
        self.id: list[str] = safeitergetter(data, "id")
        self.mediaType: list[int] = safeitergetter(data, "mediaType", factory=int)
        self.mediaUrl: list[str] = safeitergetter(data, "mediaUrl")
        self.source: list[str] = safeitergetter(data, "source")
        self.status: list[int] = safeitergetter(data, "status", factory=int)
        self.tags: list[list[str]] = safeitergetter(data, "tags", factory=list)
        self.thumbnailUrl: list[str] = safeitergetter(data, "thumbnailUrl")
        self.title: list[str] = safeitergetter(data, "title")
        self.type: list[int] = safeitergetter(data, "type", factory=int)


class Sticker(Object):
    __attr_names__ = frozenset((
        ("createdTime", "createdTime"),
        ("icon", "icon"),
        ("iconV2", "iconV2"),
        ("mediumIcon", "mediumIcon"),
        ("mediumIconV2", "mediumIconV2"),
        ("name", "name"),
        ("smallIcon", "smallIcon"),
        ("smallIconV2", "smallIconV2"),
        ("status", "status"),
        ("stickerCollectionId", "collectionId"),
        ("stickerCollectionSummary", "collection"),
        ("stickerId", "stickerId"),
        ("usedCount", "usedCount")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.collection: StickerCollection = StickerCollection(safegetter(data, "stickerCollectionSummary", factory=dict))
        self.collectionId: str = safegetter(data, "stickerCollectionId")
        self.createdTime: str = safegetter(data, "createdTime")
        self.icon: str = safegetter(data, "icon")
        self.iconV2: str = safegetter(data, "iconV2")
        self.mediumIcon: str = safegetter(data, "mediumIcon")
        self.mediumIconV2: str = safegetter(data, "mediumIconV2")
        self.name: str = safegetter(data, "name")
        self.smallIcon: str = safegetter(data, "smallIcon")
        self.smallIconV2: str = safegetter(data, "smallIconV2")
        self.status: int = safegetter(data, "status", factory=int)
        self.stickerId: str = safegetter(data, "stickerId")
        self.usedCount: int = safegetter(data, "usedCount", factory=int)


class StickerCollection(Object):
    __attr_names__ = frozenset((
        ("bannerUrl", "bannerUrl"),
        ("collectionId", "collectionId"),
        ("collectionType", "collectionType"),
        ("createdTime", "createdTime"),
        ("description", "description"),
        ("extensions", "extensions"),
        ("icon", "icon"),
        ("modifiedTime", "modifiedTime"),
        ("name", "name"),
        ("ownershipStatus", "ownershipStatus"),
        ("smallIcon", "smallIcon"),
        ("status", "status"),
        ("stickersCount", "stickersCount"),
        ("uid", "authorId"),
        ("usedCount", "usedCount")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.authorId: str = safegetter(data, "uid")
        self.bannerUrl: str = safegetter(data, "bannerUrl")
        self.collectionId: str = safegetter(data, "collectionId")
        self.collectionType: int = safegetter(data, "collectionType", factory=int)
        self.createdTime: str = safegetter(data, "createdTime")
        self.description: str | None = safegetter(data, "description")
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.icon: str = safegetter(data, "icon")
        self.iconSourceStickerId: str | None = safegetter(data, "extensions", "iconSourceStickerId")
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.name: str = safegetter(data, "name")
        self.ownershipStatus: int = safegetter(data, "ownershipStatus", factory=int)
        self.smallIcon: str = safegetter(data, "smallIcon")
        self.status: int = safegetter(data, "status")
        self.stickersCount: int = safegetter(data, "stickersCount", factory=int)
        self.usedCount: int = safegetter(data, "usedCount")


class Style(Object):
    __attr_names__ = frozenset({
        ("backgroundColor", "backgroundColor"),
        ("coverMediaList", "coverMediaList")
    })

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.coverMediaList: list[Media] = list(map(Media, safegetter(data, "coverMediaList", factory=list)))
        self.backgroundColor: str | None = safegetter(data, "backgroundColor")
        self.iconColor: str | None = safegetter(data, "iconColor")


class StyleList(ObjectList[Style]):
    def __init__(self, data: collections.abc.Sequence[collections.abc.Mapping[str, typing.Any]]) -> None:
        super().__init__(data)
        self.backgroundColor: list[str | None] = safeitergetter(data, "backgroundColor")


class Thread(Object):
    __attr_names__ = frozenset((
        ("alertOption", "alertOption"),
        ("author", "author"),
        ("condition", "condition"),
        ("content", "content"),
        ("createdTime", "createdTime"),
        ("extensions", "extensions"),
        ("icon", "icon"),
        ("isPinned", "isPinned"),
        ("keywords", "keywords"),
        ("lastReadTime", "lastReadTime"),
        ("latestActivityTime", "latestActivityTime"),
        ("membersCount", "membersCount"),
        ("membersQuota", "membersQuota"),
        ("membersSummary", "membersSummary"),
        ("membershipStatus", "membershipStatus"),
        ("modifiedTime", "modifiedTime"),
        ("needHidden", "needHidden"),
        ("threadId", "chatId"),
        ("ndcId", "comId"),
        ("publishToGlobal", "publishToGlobal"),
        ("status", "status"),
        ("strategyInfo", "strategyInfo"),
        ("title", "title"),
        ("type", "type"),
        ("userAddedTopicList", "userAddedTopicList")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.alertOption: typing.Literal[0, 1] = safegetter(data, "alertOption", factory=int)
        self.announcement: str | None = safegetter(data, "extensions", "announcement")
        self.author: UserProfileLite = UserProfileLite(safegetter(data, "author", factory=dict))
        self.avchatId: str | None = safegetter(data, "extensions", "avchatId")
        self.avchatMembers: list[str] = safegetter(data, "extensions", "avchatMemberUidList", factory=list)
        self.backgroundImage: str | None = safegetter(data, "extensions", "bm", 1)
        self.bannedUsers: list[str] = safegetter(data, "extensions", "bannedMemberUidList", factory=list)
        self.channelType: int = safegetter(data, "extensions", "channelType", factory=int)
        self.channelTypeLastCreatedTime: int | None = safegetter(data, "extensions", "channelTypeLastCreatedTime")
        self.chatId: str = safegetter(data, "threadId")
        self.coHosts: list[str] = safegetter(data, "extensions", "coHost", factory=list)
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.condition: typing.Literal[0, 1] = safegetter(data, "condition", factory=int)
        self.content: str | None = safegetter(data, "content")
        self.creatorId: str = safegetter(data, "extensions", "creatorUid")
        self.createdTime: str = safegetter(data, "createdTime")
        self.disabledTime: list[str | None] = safegetter(data, "extensions", "__disabledTime__")
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.fansOnly: bool = safegetter(data, "extensions", "fansOnly", factory=bool)
        self.icon: str = safegetter(data, "icon")
        self.isPinned: bool = safegetter(data, "isPinned", factory=bool)
        self.keywords: str | None = safegetter(data, "keywords")
        self.language: str = safegetter(data, "extensions", "language", factory=lambda: "en")
        self.lastMembersSummaryUpdateTime: int | None = safegetter(data, "extensions", "lastMembersSummaryUpdateTime")
        self.lastReadTime: str | None = safegetter(data, "lastReadTime")
        self.latestActivityTime: str | None = safegetter(data, "latestActivityTime")
        self.membersCanInvite: bool = safegetter(data, "extensions", "membersCanInvite", factory=bool)
        self.membersCount: int = safegetter(data, "membersCount", factory=int)
        self.membersQuota: int = safegetter(data, "membersQuota")
        self.membersSummary: UserProfileLiteList = UserProfileLiteList(safegetter(data, "membersSummary", factory=list))
        self.membershipStatus: typing.Literal[0, 1] = safegetter(data, "membershipStatus", factory=int)
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.needHidden: bool = safegetter(data, "needHidden", factory=bool)
        self.organizerTransferCreatedTime: str | None = safegetter(data, "extensions", "organizerTransferRequest", "createdTime")
        self.organizerTransferId: str | None = safegetter(data, "extensions", "organizerTransferRequest", "requestId")
        self.pinAnnouncement: bool = safegetter(data, "extensions", "pinAnnouncement", factory=bool)
        self.publishToGlobal: typing.Literal[0, 1] = safegetter(data, "publishToGlobal", factory=int)
        self.screeningRoomHostId: str | None = safegetter(data, "extensions", "screeningRoomHostUid")
        self.screeningRoomAction: int | None = safegetter(data, "extensions", "screeningRoomPermission", "action")
        self.screeningRoomUsers: list[str] = safegetter(data, "extensions", "screeningRoomPermission", "uidList", factory=list)
        self.screeningRoomPermission: dict[str, typing.Any] = safegetter(data, "extensions", "screeningRoomPermission", factory=dict)
        self.status: int = safegetter(data, "status", factory=int)
        self.strategyInfo: str = safegetter(data, "strategyInfo") or "{}"
        self.tippingPermStatus: int = safegetter(data, "extensions", "tippingPermStatus", factory=int)
        self.title: str = safegetter(data, "title")
        self.type: int = safegetter(data, "type", factory=int)
        self.userAddedTopicList: list[typing.Any] = safegetter(data, "userAddedTopicList", factory=list)
        self.viewOnly: bool = safegetter(data, "extensions", "viewOnly", factory=bool)
        self.visibility: int = safegetter(data, "extensions", "visibility", factory=int)
        self.vvChatJoinType: int = safegetter(data, "extensions", "vvChatJoinType", factory=lambda: 1)
        # alias references
        self.host = self.author
        self.joined = self.membershipStatus
        self.muted = self.alertOption
        self.unread = self.condition


class ThreadCheckResultInCommunity(Object):
    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.alertOption: int = safegetter(data, "alertOption", factory=int)
        self.chatId: str = safegetter(data, "threadId")
        self.lastReadTime: str = safegetter(data, "lastReadTime")
        self.latestActivityTime: str = safegetter(data, "latestActivityTime")


class ThreadList(ObjectList[Thread]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.alertOption: list[typing.Literal[0, 1]] = safeitergetter(data, "alertOption", factory=int)
        self.announcement: list[str | None] = safeitergetter(data, "extensions", "announcement")
        self.author = UserProfileList(safeitergetter(data, "author", factory=dict))
        self.avchatId: list[str | None] = safeitergetter(data, "extensions", "avchatId")
        self.avchatMembers: list[list[str]] = safeitergetter(data, "extensions", "avchatMemberUidList", factory=list)
        self.backgroundImage: list[str | None] = safeitergetter(data, "extensions", "bm", 1)
        self.bannedUsers: list[list[str]] = safeitergetter(data, "extensions", "bannedMemberUidList")
        self.channelType: list[int] = safeitergetter(data, "extensions", "channelType", factory=int)
        self.channelTypeLastCreatedTime: list[int | None] = safeitergetter(data, "extensions", "channelTypeLastCreatedTime")
        self.chatId: list[str] = safeitergetter(data, "threadId")
        self.coHosts: list[list[str]] = safeitergetter(data, "extensions", "coHost", factory=list)
        self.comId: list[int] = safeitergetter(data, "ndcId", factory=int)
        self.condition: list[typing.Literal[0, 1]] = safeitergetter(data, "condition", factory=int)
        self.content: list[str | None] = safeitergetter(data, "content")
        self.creatorId: list[str] = safeitergetter(data, "extensions", "creatorUid")
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.disabledTime: list[str | None] = safeitergetter(data, "extensions", "__disabledTime__")
        self.extensions: list[dict[str, typing.Any]] = safeitergetter(data, "extensions", factory=dict)
        self.fansOnly: list[bool] = safeitergetter(data, "extensions", "fansOnly", factory=bool)
        self.icon: list[str] = safeitergetter(data, "icon")
        self.isPinned: list[bool] = safeitergetter(data, "isPinned", factory=bool)
        self.keywords: list[str | None] = safeitergetter(data, "keywords")
        self.language: list[str] = safeitergetter(data, "extensions", "language", factory=lambda: "en")
        self.lastMembersSummaryUpdateTime: list[int | None] = safeitergetter(data, "extensions", "lastMembersSummaryUpdateTime")
        self.lastReadTime: list[str | None] = safeitergetter(data, "lastReadTime")
        self.latestActivityTime: list[str | None] = safeitergetter(data, "latestActivityTime")
        self.membersCanInvite: list[bool] = safeitergetter(data, "extensions", "membersCanInvite", factory=bool)
        self.membersCount: list[int] = safeitergetter(data, "membersCount", factory=int)
        self.membersQuota: list[int] = safeitergetter(data, "membersQuota")
        self.membersSummary = list(map(UserProfileList, safeitergetter(data, "membersSummary", factory=list)))
        self.membershipStatus: list[typing.Literal[0, 1]] = safeitergetter(data, "membershipStatus", factory=int)
        self.modifiedTime: list[str | None] = safeitergetter(data, "modifiedTime")
        self.needHidden: list[bool] = safeitergetter(data, "needHidden", factory=bool)
        self.organizerTransferCreatedTime: list[str | None] = safeitergetter(data, "extensions", "organizerTransferRequest", "createdTime")
        self.organizerTransferId: list[str | None] = safeitergetter(data, "extensions", "organizerTransferRequest", "requestId")
        self.pinAnnouncement: list[bool] = safeitergetter(data, "extensions", "pinAnnouncement", factory=bool)
        self.publishToGlobal: list[typing.Literal[0, 1]] = safeitergetter(data, "publishToGlobal", factory=int)
        self.screeningRoomHostId: list[str | None] = safeitergetter(data, "extensions", "screeningRoomHostUid")
        self.screeningRoomAction: list[int | None] = safeitergetter(data, "extensions", "screeningRoomPermission", "action")
        self.screeningRoomUsers: list[list[str]] = safeitergetter(data, "extensions", "screeningRoomPermission", "uidList", factory=list)
        self.screeningRoomPermission: list[dict[str, typing.Any]] = safeitergetter(data, "extensions", "screeningRoomPermission", factory=dict)
        self.status: list[int] = safeitergetter(data, "status", factory=int)
        self.strategyInfo: list[str] = safeitergetter(data, "strategyInfo", factory=lambda: "{}")
        self.tippingPermStatus: list[int] = safeitergetter(data, "extensions", "tippingPermStatus", factory=int)
        self.title: list[str] = safeitergetter(data, "title")
        self.type: list[int] = safeitergetter(data, "type", factory=int)
        self.userAddedTopicList: list[list[typing.Any]] = safeitergetter(data, "userAddedTopicList", factory=list)
        self.viewOnly: list[bool] = safeitergetter(data, "extensions", "viewOnly", factory=bool)
        self.visibility: list[int] = safeitergetter(data, "extensions", "visibility", factory=int)
        self.vvChatJoinType: list[int] = safeitergetter(data, "extensions", "vvChatJoinType", factory=lambda: 1)
        # alias references
        self.host = self.author
        self.joined = self.membershipStatus
        self.muted = self.alertOption
        self.unread = self.condition


class UserProfileLite(Object):
    __attr_names__ = frozenset((
        ("accountMembershipStatus", "accountMembershipStatus"),
        ("avatarFrame", "avatarFrame"),
        ("avatarFrameId", "avatarFrameId"),
        ("followingStatus", "followingStatus"),
        ("icon", "icon"),
        ("influencerInfo", "influencerInfo"),
        ("isNicknameVerified", "isNicknameVerified"),
        ("level", "level"),
        ("membersCount", "followersCount"),
        ("membershipStatus", "membershipStatus"),
        ("nickname", "nickname"),
        ("ndcId", "comId"),
        ("reputation", "reputation"),
        ("role", "role"),
        ("status", "status"),
        ("uid", "userId")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.accountMembershipStatus: int = safegetter(data, "accountMembershipStatus", factory=int)
        self.avatarFrame: AvatarFrame = AvatarFrame(safegetter(data, "avatarFrame", factory=dict))
        self.avatarFrameId: str | None = safegetter(data, "avatarFrameId")
        self.comId: int = safegetter(data, "ndcId", factory=int)
        self.fansCount: int = safegetter(data, "influencerInfo", "fansCount", factory=int)
        self.followersCount: int = safegetter(data, "membersCount", factory=int)
        self.followingStatus: int = safegetter(data, "followingStatus", factory=int)
        self.icon: str | None = safegetter(data, "icon")
        self.isNicknameVerified: bool = safegetter(data, "isNicknameVerified", factory=bool)
        self.level: int = safegetter(data, "level") or 0
        self.membershipStatus: int = safegetter(data, "membershipStatus") or 0
        self.nickname: str = safegetter(data, "nickname")
        self.reputation: int = safegetter(data, "reputation") or 0
        self.role: int = safegetter(data, "role", factory=int)
        self.status: int = safegetter(data, "status", factory=int)
        self.influencerCreatedTime: str | None = safegetter(data, "influencerInfo", "createdTime")
        self.influencerInfo: dict[str, typing.Any] | None = safegetter(data, "influencerInfo")
        self.influencerMonthlyFee: int | None = safegetter(data, "influencerInfo", "monthlyFee")
        self.influencerPinned: bool | None = safegetter(data, "influencerInfo", "pinned")
        self.userId: str = safegetter(data, "uid")


class UserProfile(UserProfileLite):
    __attr_names__ = frozenset((
        *UserProfileLite.__attr_names__,
        ("activation", "activation"),
        ("activePublicLiveThreadId", "activePublicLiveThreadId"),
        ("adminInfo", "staffInfo"),
        ("adminLogCountIn7Days", "adminLogCountIn7Days"),
        ("age", "age"),
        ("aminoId", "aminoId"),
        ("aminoIdEditable", "aminoIdEditable"),
        ("appleID", "appleId"),
        ("applicant", "applicant"),
        ("avgDailySpendTimeIn7Days", "avgDailySpendTimeIn7Days"),
        ("blogsCount", "blogsCount"),
        ("commentsCount", "commentsCount"),
        ("consecutiveCheckInDays", "consecutiveCheckInDays"),
        ("content", "content"),
        ("createdTime", "createdTime"),
        ("dateOfBirth", "dateOfBirth"),
        ("extensions", "extensions"),
        ("email", "email"),
        ("fanClubList", "fanClub"),
        ("facebookID", "facebookId"),
        ("isGlobal", "isGlobal"),
        ("itemsCount", "itemsCount"),
        ("joinedCount", "followingCount"),
        ("gender", "gender"),
        ("googleID", "googleId"),
        ("mediaList", "mediaList"),
        ("message", "message"),
        ("modifiedTime", "modifiedTime"),
        ("mood", "mood"),
        ("moodSticker", "moodSticker"),
        ("notificationSubscriptionStatus", "notificationSubscriptionStatus"),
        ("onlineStatus", "onlineStatus"),
        ("phoneNumber", "phoneNumber"),
        ("postsCount", "postsCount"),
        ("pushEnabled", "pushEnabled"),
        ("race", "race"),
        ("requestId", "requestId"),
        ("securityLevel", "securityLevel"),
        ("settings", "settings"),
        ("storiesCount", "storiesCount"),
        ("tagList", "tagList"),
        ("totalQuizHighestScore", "totalQuizHighestScore"),
        ("totalQuizPlayedTimes", "totalQuizPlayedTimes"),
        ("twitterID", "twitterId"),
        ("verified", "verified"),
        ("visitPrivacy", "visitPrivacy"),
        ("visitorsCount", "visitorsCount")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.activation: None = safegetter(data, "activation")
        self.activePublicLiveThreadId: str | None = safegetter(data, "activePublicLiveThreadId")
        self.adminLogCountIn7Days: int = safegetter(data, "adminLogCountIn7Days", factory=int)
        self.age: int | None = safegetter(data, "age")
        self.aminoId: str | None = safegetter(data, "aminoId")
        self.aminoIdEditable: None = safegetter(data, "aminoIdEditable")
        self.appleId: None = safegetter(data, "appleID")
        self.applicant: typing.Any | None = safegetter(data, "applicant")
        self.avgDailySpendTimeIn7Days: int = safegetter(data, "avgDailySpendTimeIn7Days", factory=int)
        self.backgroundColor: str | None = safegetter(data, "extensions", "style", "backgroundColor")
        self.backgroundImage: str | None = safegetter(data, "extensions", "style", "backgroundMediaList", 1)
        self.blogsCount: int = safegetter(data, "blogsCount", factory=int)
        self.commentsCount: int = safegetter(data, "commentsCount", factory=int)
        self.consecutiveCheckInDays: int = safegetter(data, "consecutiveCheckInDays") or 0
        self.content: str | None = safegetter(data, "content")
        self.coverAnimation: str = safegetter(data, "extensions", "coverAnimation", factory=lambda: "none")
        self.createdTime: str = safegetter(data, "createdTime")
        self.customTitles: list[dict[str, str | None]] = safegetter(data, "extensions", "customTitles", factory=list)
        self.dateOfBirth: str | None = safegetter(data, "dateOfBirth")
        self.defaultBubbleId: str | None = safegetter(data, "extensions", "defaultBubbleId")
        self.disabledLevel: int = safegetter(data, "extensions", "__disabledLevel__", factory=int)
        self.disabledStatus: int = safegetter(data, "extensions", "__disabledStatus__", factory=int)
        self.disabledTime: str | None = safegetter(data, "extensions", "__disabledTime__")
        self.email: None = safegetter(data, "email")
        self.extensions: dict[str, typing.Any] = safegetter(data, "extensions", factory=dict)
        self.fanClub = FanClubList(safegetter(data, "fanClubList", factory=list))
        self.facebookId: None = safegetter(data, "facebookID")
        self.followingCount: int = safegetter(data, "joinedCount", factory=int)
        self.gender: typing.Any | None = safegetter(data, "gender")
        self.globalStrikeCount: int = safegetter(data, "adminInfo", "globalStrikeCount", factory=int)
        self.googleId: None = safegetter(data, "googleID")
        self.isGlobal: bool = safegetter(data, "isGlobal", factory=bool)
        self.isMemberOfTeamAmino: bool = safegetter(data, "extensions", "isMemberOfTeamAmino", factory=bool)
        self.itemsCount: int = safegetter(data, "itemsCount", factory=int)
        self.lastStrikeTime: str | None = safegetter(data, "adminInfo", "lastStrikeTime")
        self.lastWarningTime: str | None = safegetter(data, "adminInfo", "lastWarningTime")
        self.mediaList: list[list[typing.Any]] = safegetter(data, "mediaList", factory=list)
        self.message: str | None = safegetter(data, "message")
        self.modifiedTime: str | None = safegetter(data, "modifiedTime")
        self.mood: typing.Any | None = safegetter(data, "mood")
        self.moodSticker: typing.Any | None = safegetter(data, "moodSticker")
        self.notificationSubscriptionStatus: int = safegetter(data, "notificationSubscriptionStatus", factory=int)
        self.onlineStatus: int = safegetter(data, "onlineStatus", factory=lambda: 1)
        self.onlineStatus2: int | None = safegetter(data, "settings", "onlineStatus")
        self.phoneNumber: None = safegetter(data, "phoneNumber")
        self.postsCount: int = safegetter(data, "postsCount") or 0
        self.privilegeOfChatInviteRequest: int = safegetter(data, "extensions", "privilegeOfChatInviteRequest", factory=lambda: 1)
        self.privilegeOfCommentOnUserProfile: int = safegetter(data, "extensions", "privilegeOfCommentOnUserProfile", factory=lambda: 1)
        self.pushEnabled: bool = safegetter(data, "pushEnabled", factory=bool)
        self.race: typing.Any | None = safegetter(data, "race")
        self.requestId: str | None = safegetter(data, "requestId")
        self.securityLevel: None = safegetter(data, "securityLevel")
        self.settings: dict[str, typing.Any] = safegetter(data, "settings", factory=dict)
        self.staffInfo: dict[str, typing.Any] | None = safegetter(data, "adminInfo")
        self.storiesCount: int = safegetter(data, "storiesCount", factory=int)
        self.strikeCount: int = safegetter(data, "adminInfo", "strikeCount", factory=int)
        self.tagList: typing.Any | None = safegetter(data, "tagList")
        self.totalQuizHighestScore: int = safegetter(data, "totalQuizHighestScore", factory=int)
        self.totalQuizPlayedTimes: int = safegetter(data, "totalQuizPlayedTimes", factory=int)
        self.twitterId: None = safegetter(data, "twitterID")
        self.verified: typing.Literal[0, 1] = safegetter(data, "verified")
        self.visitPrivacy: int = safegetter(data, "visitPrivacy", factory=int)
        self.visitorsCount: int = safegetter(data, "visitorsCount", factory=int)
        self.warningCount: int = safegetter(data, "adminInfo", "warningCount", factory=int)
        # alias references
        self.bio = self.content
        self.chatRequestPrivilege = self.privilegeOfChatInviteRequest
        self.settingOnlineStatus = self.onlineStatus2
        self.wallCommentPrivilege = self.privilegeOfCommentOnUserProfile
        self.wikisCount = self.itemsCount


class UserProfileLiteList(ObjectList[UserProfileLite]):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.accountMembershipStatus: list[int] = safeitergetter(data, "accountMembershipStatus", factory=int)
        self.avatarFrame: AvatarFrameList = AvatarFrameList(safeitergetter(data, "avatarFrame", factory=dict))
        self.avatarFrameId: list[str | None] = safeitergetter(data, "avatarFrameId")
        self.comId: list[int] = safeitergetter(data, "ndcId", factory=int)
        self.followersCount: list[int] = safeitergetter(data, "membersCount", factory=int)
        self.followingStatus: list[int] = safeitergetter(data, "followingStatus", factory=int)
        self.icon: list[str | None] = safeitergetter(data, "icon")
        self.isNicknameVerified: list[bool] = safeitergetter(data, "isNicknameVerified", factory=bool)
        self.level: list[int] = safeitergetter(data, "level", factory=int)
        self.membershipStatus: list[int] = safeitergetter(data, "membershipStatus", factory=int)
        self.nickname: list[str] = safeitergetter(data, "nickname")
        self.reputation: list[int] = safeitergetter(data, "reputation", factory=int)
        self.role: list[int] = safeitergetter(data, "role", factory=int)
        self.status: list[int] = safeitergetter(data, "status", factory=int)
        self.influencerCreatedTime: list[str | None] = safeitergetter(data, "influencerInfo", "createdTime")
        self.influencerInfo: list[dict[str, typing.Any] | None] = safeitergetter(data, "influencerInfo")
        self.influencerMonthlyFee: list[int | None] = safeitergetter(data, "influencerInfo", "monthlyFee")
        self.influencerPinned: list[bool | None] = safeitergetter(data, "influencerInfo", "pinned")
        self.userId: list[str] = safeitergetter(data, "uid")


class UserProfileList(UserProfileLiteList):
    def __init__(self, data: collections.abc.Sequence[dict[str, typing.Any]]) -> None:
        super().__init__(data)
        self.activation: list[None] = safeitergetter(data, "activation")
        self.activePublicLiveThreadId: list[str | None] = safeitergetter(data, "activePublicLiveThreadId")
        self.adminLogCountIn7Days: list[int] = safeitergetter(data, "adminLogCountIn7Days", factory=int)
        self.age: list[int | None] = safeitergetter(data, "age")
        self.aminoId: list[str | None] = safeitergetter(data, "aminoId")
        self.aminoIdEditable: list[None] = safeitergetter(data, "aminoIdEditable")
        self.appleId: list[None] = safeitergetter(data, "appleID")
        self.applicant: list[typing.Any | None] = safeitergetter(data, "applicant")
        self.avgDailySpendTimeIn7Days: list[int] = safeitergetter(data, "avgDailySpendTimeIn7Days", factory=int)
        self.backgroundColor: list[str | None] = safeitergetter(data, "extensions", "style", "backgroundColor")
        self.backgroundImage: list[str | None] = safeitergetter(data, "extensions", "style", "backgroundMediaList", 1)
        self.blogsCount: list[int] = safeitergetter(data, "blogsCount", factory=int)
        self.commentsCount: list[int] = safeitergetter(data, "commentsCount", factory=int)
        self.consecutiveCheckInDays: list[int] = safeitergetter(data, "consecutiveCheckInDays", factory=int)
        self.content: list[str | None] = safeitergetter(data, "content")
        self.coverAnimation: list[str] = safeitergetter(data, "extensions", "coverAnimation", factory=lambda: "none")
        self.createdTime: list[str] = safeitergetter(data, "createdTime")
        self.customTitles: list[dict[str, str | None]] = safeitergetter(data, "extensions", "customTitles", factory=list)
        self.dateOfBirth: list[str | None] = safeitergetter(data, "dateOfBirth")
        self.defaultBubbleId: list[str | None] = safeitergetter(data, "extensions", "defaultBubbleId")
        self.disabledLevel: list[int] = safeitergetter(data, "extensions", "__disabledLevel__", factory=int)
        self.disabledStatus: list[int] = safeitergetter(data, "extensions", "__disabledStatus__", factory=int)
        self.disabledTime: list[str | None] = safeitergetter(data, "extensions", "__disabledTime__")
        self.email: list[None] = safeitergetter(data, "email")
        self.extensions: list[dict[str, typing.Any]] = safeitergetter(data, "extensions", factory=dict)
        self.fanClub: list[FanClubList] = list(map(FanClubList, safeitergetter(data, "fanClubList", factory=list)))
        self.facebookId: list[None] = safeitergetter(data, "facebookID")
        self.fansCount: list[int] = safeitergetter(data, "influencerInfo", "fansCount", factory=int)
        self.followingCount: list[int] = safeitergetter(data, "joinedCount", factory=int)
        self.gender: list[typing.Any | None] = safeitergetter(data, "gender")
        self.globalStrikeCount: list[int] = safeitergetter(data, "adminInfo", "globalStrikeCount", factory=int)
        self.googleId: list[None] = safeitergetter(data, "googleID")
        self.isGlobal: list[bool] = safeitergetter(data, "isGlobal", factory=bool)
        self.isMemberOfTeamAmino: list[bool] = safeitergetter(data, "extensions", "isMemberOfTeamAmino", factory=bool)
        self.itemsCount: list[int] = safeitergetter(data, "itemsCount", factory=int)
        self.lastStrikeTime: list[str | None] = safeitergetter(data, "adminInfo", "lastStrikeTime")
        self.lastWarningTime: list[str | None] = safeitergetter(data, "adminInfo", "lastWarningTime")
        self.mediaList: list[list[list[typing.Any]]] = safeitergetter(data, "mediaList", factory=list)
        self.message: list[str | None] = safeitergetter(data, "message")
        self.modifiedTime: list[str | None] = safeitergetter(data, "modifiedTime")
        self.mood: list[typing.Any | None] = safeitergetter(data, "mood")
        self.moodSticker: list[typing.Any | None] = safeitergetter(data, "moodSticker")
        self.notificationSubscriptionStatus: list[int] = safeitergetter(data, "notificationSubscriptionStatus", factory=int)
        self.onlineStatus: list[int] = safeitergetter(data, "onlineStatus", factory=lambda: 1)
        self.onlineStatus2: list[int | None] = safeitergetter(data, "settings", "onlineStatus")
        self.phoneNumber: list[None] = safeitergetter(data, "phoneNumber")
        self.postsCount: list[int] = safeitergetter(data, "postsCount", factory=int)
        self.privilegeOfChatInviteRequest: list[int] = safeitergetter(data, "extensions", "privilegeOfChatInviteRequest", factory=lambda: 1)
        self.privilegeOfCommentOnUserProfile: list[int] = safeitergetter(data, "extensions", "privilegeOfCommentOnUserProfile", factory=lambda: 1)
        self.pushEnabled: list[bool] = safeitergetter(data, "pushEnabled", factory=bool)
        self.race: list[typing.Any | None] = safeitergetter(data, "race")
        self.requestId: list[str | None] = safeitergetter(data, "requestId")
        self.securityLevel: list[None] = safeitergetter(data, "securityLevel")
        self.settings: list[dict[str, typing.Any]] = safeitergetter(data, "settings", factory=dict)
        self.staffInfo: list[dict[str, typing.Any] | None] = safeitergetter(data, "adminInfo")
        self.storiesCount: list[int] = safeitergetter(data, "storiesCount", factory=int)
        self.strikeCount: list[int] = safeitergetter(data, "adminInfo", "strikeCount", factory=int)
        self.tagList: list[typing.Any | None] = safeitergetter(data, "tagList")
        self.totalQuizHighestScore: list[int] = safeitergetter(data, "totalQuizHighestScore", factory=int)
        self.totalQuizPlayedTimes: list[int] = safeitergetter(data, "totalQuizPlayedTimes", factory=int)
        self.twitterId: list[None] = safeitergetter(data, "twitterID")
        self.verified: list[typing.Literal[0, 1]] = safeitergetter(data, "verified", factory=int)
        self.visitPrivacy: list[int] = safeitergetter(data, "visitPrivacy", factory=int)
        self.visitorsCount: list[int] = safeitergetter(data, "visitorsCount", factory=int)
        self.warningCount: list[int] = safeitergetter(data, "adminInfo", "warningCount", factory=int)
        # alias references
        self.bio = self.content
        self.settingOnlineStatus = self.onlineStatus2
        self.wikisCount = self.itemsCount

    @property
    def __wrapped__(self) -> typing.Type[UserProfile]:
        return UserProfile

    def __iter__(self) -> collections.abc.Iterator[UserProfile]:
        return iter(map(self.__wrapped__, safeitergetter(self.json, factory=dict)))


class VisitSettings(Object):
    __attr_names__ = frozenset((
        ("notificationStatus", "notificationStatus"),
        ("privacyMode", "privacyMode")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.notificationStatus: int = safegetter(data, "notificationStatus", factory=int)
        self.privacyMode: int = safegetter(data, "privacyMode", factory=int)


class Wallet(Object):
    __attr_names__ = frozenset((
        ("adsEnabled", "adsEnabled"),
        ("adsFlags", "adsFlags"),
        ("adsVideoStats", "adsVideoStats"),
        ("businessCoinsEnabled", "businessCoinsEnabled"),
        ("totalBusinessCoins", "totalBusinessCoins"),
        ("totalBusinessCoinsFloat", "totalBusinessCoinsFloat"),
        ("totalCoins", "totalCoins"),
        ("totalCoinsFloat", "totalCoinsFloat")
    ))

    def __init__(self, data: collections.abc.Mapping[str, typing.Any]) -> None:
        super().__init__(data)
        self.adsEnabled: bool = safegetter(data, "adsEnabled", factory=bool)
        self.adsFlags: int = safegetter(data, "adsFlags", factory=int)
        self.adsVideoStats: AdsVideoStats = AdsVideoStats(safegetter(data, "adsVideoStats", factory=dict))
        self.businessCoinsEnabled: bool = safegetter(data, "businessCoinsEnabled", factory=bool)
        self.totalBusinessCoins: int = safegetter(data, "totalBusinessCoins", factory=int)
        self.totalBusinessCoinsFloat: float = float(safegetter(data, "totalBusinessCoinsFloat", factory=float))
        self.totalCoins: int = int(safegetter(data, "totalCoins", factory=int))
        self.totalCoinsFloat: float = safegetter(data, "totalCoinsFloat")
