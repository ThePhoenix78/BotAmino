from __future__ import annotations

import typing
import requests

from .objects import APIResponse

__all__ = ("APIError", "BotAminoError", "ServerError")


class BotAminoError(Exception): ...


class ServerError(BotAminoError):
    def __init__(self, response: requests.Response) -> None:
        super().__init__(response)
        self.status = response.status_code
        self.reason = response.reason
        self.response = response

    def __str__(self) -> str:
        if type(self) is ServerError:
            return super().__str__()
        return f"{self.status} - {self.reason}"


class APIError(BotAminoError, APIResponse):
    def __init__(self, data: dict[str, typing.Any]) -> None:
        super().__init__(data)
        super(APIResponse, self).__init__(data)

    def __str__(self) -> str:
        if type(self) is APIError:
            return super().__str__()
        return self.message


class WSError(BotAminoError):
    def __init__(self, data: dict[str, typing.Any]) -> None:
        super().__init__(data)
        self.code: int = data["code"]
        self.message: str = data["message"]


# server exceptions
class InternalServerError(ServerError): ...


class BadGateway(ServerError): ...


class ServiceUnavailable(ServerError): ...


# ws exceptions
class InternalWSError(WSError): ...


class ChannelNotAvailable(WSError): ...


class ChannelChatNotJoined(WSError): ...


class ChannelUserNotAvailable(WSError): ...


class TooManyPresenters(WSError): ...


class ChangeChannelTypeNotMatch(WSError): ...


class ChangeChannelTypeNoPermission(WSError): ...


class ChangeChannelJoinRoleNotMatch(WSError): ...


class ChannelNoPresenters(WSError): ...


class ChannelMembershipNoPermission(WSError): ...


class ChannelUserBusy(WSError): ...


class ChannelUserNotActive(WSError): ...


class InvalidLiveStreamTopic(WSError): ...


class InvalidLiveStreamAction(WSError): ...


class UpdatePlayListNoPermission(WSError): ...


class TooManyPresentersInScreeningRoom(WSError): ...


class ChannelClosed(WSError): ...


# api exceptions
class UnsupportedService(APIError): ...


class FileTooLarge(APIError): ...


class InvalidRequest(APIError): ...


class InvalidSession(APIError): ...


class AccessDenied(APIError): ...


class UnexistentData(APIError): ...


class ActionNotAllowed(APIError): ...


class MessageNeeded(APIError): ...


class InvalidAccountOrPassword(APIError): ...


class AccountDisabled(APIError): ...


class InvalidEmail(APIError): ...


class InvalidPassword(APIError): ...


class EmailAlreadyTaken(APIError): ...


class AccountDoesntExist(APIError): ...


class InvalidDevice(APIError): ...


class TooManyRequests(APIError): ...


class CantFollowYourself(APIError): ...


class UserUnavailable(APIError): ...


class YouAreBanned(APIError): ...


class UserNotMemberOfCommunity(APIError): ...


class RequestRejected(APIError): ...


class ActivateAccount(APIError): ...


class CantLeaveCommunity(APIError): ...


class ReachedTitleLength(APIError): ...


class EmailFlaggedAsSpam(APIError): ...


class AccountDeleted(APIError): ...


class API_ERR_EMAIL_NO_PASSWORD(APIError): ...


class API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY(APIError): ...


class ReachedMaxTitles(APIError): ...


class VerificationRequired(APIError):
    """Please verify your account before logging in on a new device."""


class API_ERR_INVALID_AUTH_NEW_DEVICE_LINK(APIError): ...


class MessageCooldown(APIError): ...


class UserBannedByTeamAmino(APIError): ...


class BadImage(APIError): ...


class InvalidThemepack(APIError): ...


class InvalidVoiceNote(APIError): ...


class RequestedNoLongerExist(APIError): ...


class FeatureNotUnlocked(APIError): ...


class PageRepostedTooRecently(APIError): ...


class InsufficientLevel(APIError): ...


class WallCommentingDisabled(APIError): ...


class CommunityNoLongerExists(APIError): ...


class InvalidCodeOrLink(APIError): ...


class CommunityNameAlreadyTaken(APIError): ...


class CommunityCreateLimitReached(APIError): ...


class CommunityDisabled(APIError): ...


class CommunityDeleted(APIError): ...


class ReachedMaxCategories(APIError): ...


class DuplicatePollOption(APIError): ...


class ReachedMaxPollOptions(APIError): ...


class TooManyChats(APIError): ...


class ChatFull(APIError): ...


class TooManyInviteUsers(APIError): ...


class ChatInvitesDisabled(APIError): ...


class RemovedFromChat(APIError): ...


class UserNotJoined(APIError): ...


class ScreenRoomNoMoreReputations(APIError): ...


class MemberKickedByOrganizer(APIError): ...


class LevelFiveRequiredToEnableProps(APIError): ...


class ChatViewOnly(APIError): ...


class ChatMessageTooBig(APIError): ...


class InviteCodeNotFound(APIError): ...


class AlreadyRequestedJoinCommunity(APIError): ...


class API_ERR_PUSH_SERVER_LIMITATION_APART(APIError): ...


class API_ERR_PUSH_SERVER_LIMITATION_COUNT(APIError): ...


class API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY(APIError): ...


class API_ERR_PUSH_SERVER_LIMITATION_TIME(APIError): ...


class AlreadyCheckedIn(APIError): ...


class AlreadyUsedMonthlyRepair(APIError): ...


class AccountAlreadyRestored(APIError): ...


class IncorrectVerificationCode(APIError): ...


class NotOwnerOfChatBubble(APIError): ...


class NotEnoughCoins(APIError): ...


class AlreadyPlayedLottery(APIError): ...


class CannotSendCoins(APIError): ...


class AminoIDAlreadyChanged(APIError): ...


class InvalidAminoID(APIError): ...


class InvalidName(APIError): ...


SERVER_ERRORS: dict[int, type[ServerError]] = {
    500: InternalServerError,
    502: BadGateway,
    503: ServiceUnavailable,
}

WS_ERRORS: dict[int, type[WSError]] = {
    1: InternalWSError,
    101: ChannelNotAvailable,
    102: ChannelChatNotJoined,
    103: ChannelUserNotAvailable,
    105: TooManyPresenters,
    106: ChangeChannelTypeNotMatch,
    107: ChangeChannelTypeNoPermission,
    108: ChangeChannelJoinRoleNotMatch,
    109: ChannelNoPresenters,
    110: ChannelMembershipNoPermission,
    111: ChannelUserBusy,
    112: ChannelUserNotActive,
    113: InvalidLiveStreamTopic,
    114: InvalidLiveStreamAction,
    115: UpdatePlayListNoPermission,
    116: TooManyPresentersInScreeningRoom,
    117: ChannelClosed,
}

API_ERRORS: dict[int, type[APIError]] = {
    100: UnsupportedService,
    102: FileTooLarge,
    103: InvalidRequest,
    104: InvalidRequest,
    105: InvalidSession,
    106: AccessDenied,
    107: UnexistentData,
    110: ActionNotAllowed,
    113: MessageNeeded,
    200: InvalidAccountOrPassword,
    201: AccountDisabled,
    210: AccountDisabled,
    213: InvalidEmail,
    214: InvalidPassword,
    215: EmailAlreadyTaken,
    216: AccountDoesntExist,
    218: InvalidDevice,
    219: TooManyRequests,
    221: CantFollowYourself,
    225: UserUnavailable,
    229: YouAreBanned,
    230: UserNotMemberOfCommunity,
    235: RequestRejected,
    238: ActivateAccount,
    239: CantLeaveCommunity,
    240: ReachedTitleLength,
    241: EmailFlaggedAsSpam,
    246: AccountDeleted,
    251: API_ERR_EMAIL_NO_PASSWORD,
    257: API_ERR_COMMUNITY_USER_CREATED_COMMUNITIES_VERIFY,
    262: ReachedMaxTitles,
    270: VerificationRequired,
    271: API_ERR_INVALID_AUTH_NEW_DEVICE_LINK,
    291: MessageCooldown,
    293: UserBannedByTeamAmino,
    300: BadImage,
    313: InvalidThemepack,
    314: InvalidVoiceNote,
    500: RequestedNoLongerExist,
    579: FeatureNotUnlocked,
    700: RequestedNoLongerExist,
    503: PageRepostedTooRecently,
    551: InsufficientLevel,
    702: WallCommentingDisabled,
    801: CommunityNoLongerExists,
    802: InvalidCodeOrLink,
    805: CommunityNameAlreadyTaken,
    806: CommunityCreateLimitReached,
    814: CommunityDisabled,
    833: CommunityDeleted,
    1002: ReachedMaxCategories,
    1501: DuplicatePollOption,
    1507: ReachedMaxPollOptions,
    1600: RequestedNoLongerExist,
    1602: TooManyChats,
    1605: ChatFull,
    1606: TooManyInviteUsers,
    1611: ChatInvitesDisabled,
    1612: RemovedFromChat,
    1613: UserNotJoined,
    1627: ScreenRoomNoMoreReputations,
    1637: MemberKickedByOrganizer,
    1661: LevelFiveRequiredToEnableProps,
    1663: ChatViewOnly,
    1664: ChatMessageTooBig,
    1900: InviteCodeNotFound,
    2001: AlreadyRequestedJoinCommunity,
    2501: API_ERR_PUSH_SERVER_LIMITATION_APART,
    2502: API_ERR_PUSH_SERVER_LIMITATION_COUNT,
    2503: API_ERR_PUSH_SERVER_LINK_NOT_IN_COMMUNITY,
    2504: API_ERR_PUSH_SERVER_LIMITATION_TIME,
    2601: AlreadyCheckedIn,
    2611: AlreadyUsedMonthlyRepair,
    2800: AccountAlreadyRestored,
    3102: IncorrectVerificationCode,
    3905: NotOwnerOfChatBubble,
    4300: NotEnoughCoins,
    4400: AlreadyPlayedLottery,
    4500: CannotSendCoins,
    4501: CannotSendCoins,
    6001: AminoIDAlreadyChanged,
    6002: InvalidAminoID,
    9901: InvalidName,
}


def check_server_error(response: requests.Response) -> ServerError:
    return SERVER_ERRORS.get(response.status_code, ServerError)(response)


def check_api_error(data: dict[str, typing.Any]) -> APIError:
    return API_ERRORS.get(data.get("api:statuscode", -1), APIError)(data)


def check_ws_error(data: dict[str, typing.Any]) -> WSError:
    return WS_ERRORS.get(data.get("code", -1), WSError)(data)
