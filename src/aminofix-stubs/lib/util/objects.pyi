from typing import Any, ClassVar
from typing_extensions import Self
from _typeshed import Incomplete

class Objects:
    class Users:
        team_amino: ClassVar[str]
        news_feed: ClassVar[str]

class UserProfile:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.fanClub: FanClubList
        self.accountMembershipStatus: int
        self.activation: Incomplete | None
        self.activePublicLiveThreadId: str | None
        self.age: int | None
        self.aminoId: str  # only global
        self.aminoIdEditable: bool | None
        self.appleId: str | None
        self.avatarFrame: dict[str, Any] | None
        self.avatarFrameId: str | None
        self.backgroundImage: str | None
        self.backgroundColor: str | None
        self.blogsCount: int
        self.commentsCount: int
        self.content: str | None
        self.coverAnimation: str
        self.createdTime: str
        self.customTitles: list[dict[str, str | None]] | None
        self.dateOfBirth: Incomplete | None
        self.defaultBubbleId: str | None
        self.disabledLevel: int | None
        self.disabledStatus: int | None
        self.disabledTime: str | None
        self.email: str | None
        self.extensions: dict[str, Any] | None
        self.facebookId: str | None
        self.fansCount: int | None
        self.followersCount: int
        self.followingCount: int
        self.followingStatus: int
        self.gender: int | None
        self.globalStrikeCount: int | None
        self.googleId: str | None
        self.icon: str | None
        self.influencerCreatedTime: str | None
        self.influencerInfo: dict[str, Any] | None
        self.influencerMonthlyFee: int | None
        self.influencerPinned: bool | None
        self.isGlobal: bool
        self.isMemberOfTeamAmino: bool
        self.isNicknameVerified: bool
        self.itemsCount: int
        self.lastStrikeTime: str | None
        self.lastWarningTime: str | None
        self.level: int
        self.mediaList: list[list[Incomplete]] | None
        self.membershipStatus: int
        self.modifiedTime: str | None
        self.mood: Incomplete | None
        self.moodSticker: dict[str, Any] | None
        self.nickname: str
        self.notificationSubscriptionStatus: int | None
        self.onlineStatus: int
        self.onlineStatus2: int | None
        self.phoneNumber: str | None
        self.postsCount: int
        self.privilegeOfChatInviteRequest: int
        self.privilegeOfCommentOnUserProfile: int
        self.pushEnabled: bool
        self.race: Incomplete | None
        self.reputation: int
        self.role: int
        self.securityLevel: int | None
        self.staffInfo: dict[str, Any] | None
        self.status: int
        self.storiesCount: int
        self.strikeCount: int | None
        self.tagList: Incomplete | None
        self.twitterId: str | None
        self.userId: str
        self.verified: bool
        self.visitPrivacy: int | None
        self.visitorsCount: int | None
        self.warningCount: int | None
        self.totalQuizHighestScore: int | None
        self.totalQuizPlayedTimes: int | None
        self.requestId: str | None
        self.message: Incomplete | None
        self.applicant: Incomplete | None
        self.avgDailySpendTimeIn7Days: Incomplete | None
        self.adminLogCountIn7Days: int | None
    def __bool__(self) -> bool: ...
    @property
    def UserProfile(self) -> Self: ...

class UserProfileList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.accountMembershipStatus: list[int]
        self.activation: list[Incomplete | None]
        self.activePublicLiveThreadId: list[str | None]
        self.age: list[int | None]
        self.aminoId: list[str]
        self.aminoIdEditable: list[bool | None]
        self.appleId: list[str | None]
        self.avatarFrame: list[dict[str, Any] | None]
        self.avatarFrameId: list[str | None]
        self.backgroundColor: list[str | None]
        self.backgroundImage: list[str | None]
        self.blogsCount: list[int]
        self.commentsCount: list[int]
        self.content: list[str | None]
        self.coverAnimation: list[str]
        self.createdTime: list[str]
        self.customTitles: list[list[dict[str, str | None]] | None]
        self.dateOfBirth: list[Incomplete | None]
        self.defaultBubbleId: list[str | None]
        self.disabledLevel: list[int | None]
        self.disabledStatus: list[int | None]
        self.disabledTime: list[str | None]
        self.email: list[str | None]
        self.extensions: list[dict[str, Any] | None]
        self.facebookId: list[str | None]
        self.fansCount: list[int | None]
        self.fanClub: list[FanClubList]
        self.followersCount: list[int]
        self.followingCount: list[int]
        self.followingStatus: list[int]
        self.gender: list[int | None]
        self.globalStrikeCount: list[int | None]
        self.googleId: list[str | None]
        self.icon: list[str | None]
        self.influencerCreatedTime: list[str | None]
        self.influencerInfo: list[dict[str, Any] | None]
        self.influencerMonthlyFee: list[int | None]
        self.influencerPinned: list[bool | None]
        self.isGlobal: list[bool]
        self.isMemberOfTeamAmino: list[bool]
        self.isNicknameVerified: list[bool]
        self.itemsCount: list[int]
        self.lastStrikeTime: list[str | None]
        self.lastWarningTime: list[str | None]
        self.level: list[int]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.membershipStatus: list[int | None]
        self.modifiedTime: list[str | None]
        self.mood: list[Incomplete | None]
        self.moodSticker: list[dict[str, Any] | None]
        self.nickname: list[str]
        self.notificationSubscriptionStatus: list[int | None]
        self.onlineStatus: list[int]
        self.onlineStatus2: list[int | None]
        self.phoneNumber: list[str | None]
        self.postsCount: list[int]
        self.privilegeOfChatInviteRequest: list[int | None]
        self.privilegeOfCommentOnUserProfile: list[int | None]
        self.pushEnabled: list[bool]
        self.race: list[Incomplete | None]
        self.reputation: list[int]
        self.role: list[int]
        self.securityLevel: list[int | None]
        self.staffInfo: list[dict[str, Any] | None]
        self.status: list[int]
        self.storiesCount: list[int]
        self.strikeCount: list[int]
        self.tagList: list[Incomplete | None]
        self.twitterId: list[str | None]
        self.userId: list[str]
        self.verified: list[bool]
        self.visitPrivacy: list[int | None]
        self.visitorsCount: list[int | None]
        self.warningCount: list[int | None]
        self.totalQuizPlayedTimes: list[int | None]
        self.totalQuizHighestScore: list[int | None]
        self.requestId: list[str | None]
        self.message: list[Incomplete | None]
        self.applicant: list[Incomplete | None]
        self.avgDailySpendTimeIn7Days: list[Incomplete | None]
        self.adminLogCountIn7Days: list[int | None]
    def __bool__(self) -> bool: ...
    @property
    def UserProfileList(self) -> Self: ...

class BlogList:
    def __init__(
        self,
        data: list[dict[str, Any]],
        nextPageToken: str | None = None,
        prevPageToken: str | None = None
    ) -> None:
        self.json: list[dict[str, Any]]
        self.nextPageToken: str | None
        self.prevPageToken: str | None
        self.author: UserProfileList
        self.quizQuestionList: list[QuizQuestionList]
        self.createdTime: list[str]
        self.globalVotesCount: list[int | None]
        self.globalVotedValue: list[int | None]
        self.keywords: list[str | None]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.style: list[dict[str, Any] | None]
        self.totalQuizPlayCount: list[int | None]
        self.title: list[str]
        self.tipInfo: list[dict[str, Any] | None]
        self.tippersCount: list[int | None]
        self.tippable: list[bool]
        self.tippedCoins: list[int | None]
        self.contentRating: list[Incomplete | None]
        self.needHidden: list[bool]
        self.guestVotesCount: list[int | None]
        self.type: list[int]
        self.status: list[int]
        self.globalCommentsCount: list[int | None]
        self.modifiedTime: list[str | None]
        self.widgetDisplayInterval: list[Incomplete | None]
        self.totalPollVoteCount: list[int | None]
        self.blogId: list[str]
        self.viewCount: list[int | None]
        self.fansOnly: list[bool | None]
        self.backgroundColor: list[str | None]
        self.votesCount: list[int | None]
        self.endTime: list[str | None]
        self.refObjectId: list[str | None]
        self.refObject: list[dict[str, Any] | None]
        self.votedValue: list[int | None]
        self.extensions: list[dict[str, Any] | None]
        self.commentsCount: list[int]
        self.content: list[str | None]
        self.featuredType: list[int | None]
        self.shareUrl: list[str]
        self.disabledTime: list[str | None]
        self.quizPlayedTimes: list[int | None]
        self.quizTotalQuestionCount: list[int | None]
        self.quizTrendingTimes: list[int | None]
        self.quizLastAddQuestionTime: list[str | None]
        self.isIntroPost: list[bool | None]
    def __bool__(self) -> bool: ...
    @property
    def BlogList(self) -> Self: ...

class RecentBlogs:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.nextPageToken: str | None
        self.prevPageToken: str | None
    def __bool__(self) -> bool: ...
    @property
    def RecentBlogs(self) -> BlogList: ...

class BlogCategoryList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.status: list[int]
        self.modifiedTime: list[str | None]
        self.icon: list[str | None]
        self.style: list[dict[str, Any]]
        self.title: list[str]
        self.content: list[str | None]
        self.createdTime: list[str]
        self.position: list[Incomplete]
        self.type: list[int]
        self.categoryId: list[str]
        self.blogsCount: list[int]
    def __bool__(self) -> bool: ...
    @property
    def BlogCategoryList(self) -> Self: ...

class Blog:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.quizQuestionList: QuizQuestionList
        self.createdTime: str
        self.globalVotesCount: int | None
        self.globalVotedValue: int | None
        self.keywords: str | None
        self.mediaList: list[list[Incomplete]] | None
        self.style: dict[str, Any] | None
        self.totalQuizPlayCount: int | None
        self.title: str
        self.tipInfo: dict[str, Any] | None
        self.tippersCount: int | None
        self.tippable: bool | None
        self.tippedCoins: int | None
        self.contentRating: Incomplete | None
        self.needHidden: bool
        self.guestVotesCount: int | None
        self.type: int
        self.status: int
        self.globalCommentsCount: int | None
        self.modifiedTime: str | None
        self.widgetDisplayInterval: Incomplete | None
        self.totalPollVoteCount: int | None
        self.blogId: str
        self.comId: int
        self.viewCount: int | None
        self.fansOnly: bool
        self.backgroundColor: str | None
        self.votesCount: int | None
        self.endTime: Incomplete | None
        self.refObjectId: str | None
        self.refObject: dict[str, Any] | None
        self.votedValue: int
        self.extensions: dict[str, Any] | None
        self.commentsCount: int
        self.content: str | None
        self.featuredType: int | None
        self.shareUrl: str
        self.disabledTime: str | None
        self.quizPlayedTimes: int | None
        self.quizTotalQuestionCount: int | None
        self.quizTrendingTimes: int | None
        self.quizLastAddQuestionTime: str | None
        self.isIntroPost: bool | None
    def __bool__(self) -> bool: ...
    @property
    def Blog(self) -> Self: ...

class Wiki:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.labels: WikiLabelList
        self.createdTime: str
        self.modifiedTime: str | None
        self.wikiId: str
        self.status: int
        self.style: dict[str, Any] | None
        self.globalCommentsCount: int | None
        self.votedValue: int | None
        self.globalVotesCount: int | None
        self.globalVotedValue: int | None
        self.contentRating: Incomplete | None
        self.title: str
        self.content: str | None
        self.keywords: str | None
        self.needHidden: bool
        self.guestVotesCount: int | None
        self.extensions: dict[str, Any] | None
        self.backgroundColor: str | None
        self.fansOnly: bool | None
        self.knowledgeBase: dict[str, Any] | None
        self.originalWikiId: str | None
        self.version: Incomplete | None
        self.contributors = Incomplete | None
        self.votesCount: int
        self.comId: int
        self.mediaList: list[list[Incomplete]] | None
        self.commentsCount: int
    def __bool__(self) -> bool: ...
    @property
    def Wiki(self) -> Self: ...

class WikiList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.labels: list[WikiLabelList]
        self.createdTime: list[str]
        self.modifiedTime: list[str | None]
        self.wikiId: list[str]
        self.status: list[int]
        self.style: list[dict[str, Any] | None]
        self.globalCommentsCount: list[int | None]
        self.votedValue: list[int | None]
        self.globalVotesCount: list[int | None]
        self.globalVotedValue: list[int | None]
        self.contentRating: list[Incomplete | None]
        self.title: list[str]
        self.content: list[str | None]
        self.keywords: list[str | None]
        self.needHidden: list[bool]
        self.guestVotesCount: list[int | None]
        self.extensions: list[dict[str, Any] | None]
        self.backgroundColor: list[str | None]
        self.fansOnly: list[bool | None]
        self.knowledgeBase: list[dict[str, Any] | None]
        self.originalWikiId: list[str | None]
        self.version: list[Incomplete | None]
        self.contributors: list[Incomplete | None]
        self.votesCount: list[int]
        self.comId: list[int]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.commentsCount: list[int]
    def __bool__(self) -> bool: ...
    @property
    def WikiList(self) -> Self: ...

class WikiLabelList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.title: list[str]
        self.content: list[str | None]
        self.type: list[int]
    def __bool__(self) -> bool: ...
    @property
    def WikiLabelList(self) -> Self: ...

class RankingTableList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.title: list[str]
        self.level: list[int]
        self.reputation: list[int]
        self.id: list[int]
    def __bool__(self) -> bool: ...
    @property
    def RankingTableList(self) -> Self: ...

class Community:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.agent: UserProfile
        self.rankingTable: RankingTableList
        self.usersCount: int
        self.createdTime: str
        self.aminoId: str
        self.icon: str
        self.link: str
        self.comId: int
        self.modifiedTime: str | None
        self.status: int
        self.joinType: int
        self.tagline: str
        self.primaryLanguage: str
        self.heat: float
        self.themePack: Incomplete
        self.probationStatus: int
        self.listedStatus: int
        self.userAddedTopicList: list[str] | None
        self.name: str
        self.isStandaloneAppDeprecated: bool | None
        self.searchable: bool
        self.influencerList: list[dict[str, Any]] | None
        self.keywords: str | None
        self.mediaList: list[list[Incomplete]] | None
        self.description: str | None
        self.isStandaloneAppMonetizationEnabled: bool | None
        self.advancedSettings: dict[str, Any] | None
        self.activeInfo: dict[str, Any] | None
        self.configuration: dict[str, Any] | None
        self.extensions: dict[str, Any] | None
        self.nameAliases: Incomplete | None
        self.templateId: int
        self.promotionalMediaList: list[list[Incomplete]] | None
        self.defaultRankingTypeInLeaderboard: int | None
        self.joinedBaselineCollectionIdList: list[str] | None
        self.newsfeedPages: Incomplete | None
        self.catalogEnabled: bool | None
        self.pollMinFullBarVoteCount: int | None
        self.leaderboardStyle: dict[str, Any] | None
        self.facebookAppIdList: list[str] | None
        self.welcomeMessage: str | None
        self.welcomeMessageEnabled: bool | None
        self.hasPendingReviewRequest: bool | None
        self.frontPageLayout: int | None
        self.themeColor: str
        self.themeHash: str
        self.themeVersion: int
        self.themeUrl: str
        self.themeHomePageAppearance: Incomplete | None
        self.themeLeftSidePanelTop: Incomplete | None
        self.themeLeftSidePanelBottom: Incomplete | None
        self.themeLeftSidePanelColor: str | None
        self.customList: Incomplete | None
    def __bool__(self) -> bool: ...
    @property
    def Community(self) -> Self: ...

class CommunityList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.agent: UserProfileList
        self.rankingTable: list[RankingTableList]
        self.usersCount: list[int]
        self.createdTime: list[str]
        self.aminoId: list[str]
        self.icon: list[str]
        self.link: list[str]
        self.comId: list[int]
        self.modifiedTime: list[str | None]
        self.status: list[int]
        self.joinType: list[int]
        self.tagline: list[str]
        self.primaryLanguage: list[str]
        self.heat: list[float]
        self.themePack: list[dict[str, Any]]
        self.probationStatus: list[int]
        self.listedStatus: list[int]
        self.userAddedTopicList: list[list[str] | None]
        self.name: list[str]
        self.isStandaloneAppDeprecated: list[bool | None]
        self.searchable: list[bool]
        self.influencerList: list[list[dict[str, Any]] | None]
        self.keywords: list[str | None]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.description: list[str | None]
        self.isStandaloneAppMonetizationEnabled: list[bool | None]
        self.advancedSettings: list[dict[str, Any] | None]
        self.activeInfo: list[dict[str, Any] | None]
        self.configuration: list[dict[str, Any] | None]
        self.extensions: list[dict[str, Any] | None]
        self.nameAliases: list[Incomplete | None]
        self.templateId: list[int]
        self.promotionalMediaList: list[list[list[Incomplete]] | None]
        self.defaultRankingTypeInLeaderboard: list[int | None]
        self.joinedBaselineCollectionIdList: list[list[str] | None]
        self.newsfeedPages: list[Incomplete | None]
        self.catalogEnabled: list[bool | None]
        self.pollMinFullBarVoteCount: list[int | None]
        self.leaderboardStyle: list[dict[str, Any] | None]
        self.facebookAppIdList: list[list[str] | None]
        self.welcomeMessage: list[str | None]
        self.welcomeMessageEnabled: list[bool | None]
        self.hasPendingReviewRequest: list[bool | None]
        self.frontPageLayout: list[int | None]
        self.themeColor: list[str]
        self.themeHash: list[str]
        self.themeVersion: list[int]
        self.themeUrl: list[str]
        self.themeHomePageAppearance: list[Incomplete | None]
        self.themeLeftSidePanelTop: list[Incomplete | None]
        self.themeLeftSidePanelBottom: list[Incomplete | None]
        self.themeLeftSidePanelColor: list[str | None]
        self.customList: list[Incomplete | None]
    def __bool__(self) -> bool: ...
    @property
    def CommunityList(self) -> Self: ...

class VisitorsList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.profile: UserProfileList
        self.visitors: list[dict[str, Any]]
        self.lastCheckTime: str
        self.visitorsCapacity: Incomplete
        self.visitorsCount: int
        self.ownerPrivacyMode: list[Incomplete]
        self.visitorPrivacyMode: list[Incomplete]
        self.visitTime: list[Incomplete]
    def __bool__(self) -> bool: ...
    @property
    def VisitorsList(self) -> None: ...

class CommentList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.votesSum: list[int]
        self.votedValue: list[int]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.parentComId: list[int]
        self.parentId: list[str]
        self.parentType: list[int]
        self.content: list[str | None]
        self.extensions: list[dict[str, Any] | None]
        self.comId: list[int]
        self.modifiedTime: list[str | None]
        self.createdTime: list[str]
        self.commentId: list[str]
        self.subcommentsCount: list[int]
        self.type: list[int]
    def __bool__(self) -> bool: ...
    @property
    def CommentList(self) -> Self: ...

class Membership:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.premiumFeature: bool
        self.hasAnyAndroidSubscription: bool
        self.hasAnyAppleSubscription: bool
        self.accountMembership: bool
        self.paymentType: int
        self.membershipStatus: int
        self.isAutoRenew: bool
        self.createdTime: str
        self.modifiedTime: str | None
        self.renewedTime: str | None
        self.expiredTime: str | None
    def __bool__(self) -> bool: ...
    @property
    def Membership(self) -> Self: ...

class FromCode:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.community: Community
        self.path: str
        self.objectType: int
        self.shortCode: str
        self.fullPath: str
        self.targetCode: int
        self.objectId: str
        self.shortUrl: str
        self.fullUrl: str
        self.comId: int
        self.comIdPost: int
    def __bool__(self) -> bool: ...
    @property
    def FromCode(self) -> Self: ...

class UserProfileCountList:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.profile: UserProfileList
        self.userProfileCount: int
    def __bool__(self) -> bool: ...
    @property
    def UserProfileCountList(self) -> Self: ...

class UserCheckIns:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.hasAnyCheckIn: bool
        self.brokenStreaks: Incomplete | None
        self.consecutiveCheckInDays: int
    def __bool__(self) -> bool: ...
    @property
    def UserCheckIns(self) -> Self: ...

class WalletInfo:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.totalCoinsFloat: float
        self.adsEnabled: bool
        self.adsVideoStats: dict[str, Any] | None
        self.adsFlags: int
        self.totalCoins: int
        self.businessCoinsEnabled: bool
        self.totalBusinessCoins: int | None
        self.totalBusinessCoinsFloat: float | None
    def __bool__(self) -> bool: ...
    @property
    def WalletInfo(self) -> Self: ...

class WalletHistory:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.bonusCoins: list[int]
        self.bonusCoinsFloat: list[float]
        self.taxCoins: list[int]
        self.taxCoinsFloat: list[float]
        self.isPositive: list[bool]
        self.transanctionId: list[str]
        self.changedCoins: list[int]
        self.totalCoinsFloat: list[float]
        self.changedCoinsFloat: list[float]
        self.sourceType: list[int]
        self.createdTime: list[str]
        self.totalCoins: list[int]
        self.originCoinsFloat: list[float]
        self.originCoins: list[int]
        self.extData: list[dict[str, Any]]
        self.title: list[str]
        self.description: list[str | None]
        self.icon: list[str | None]
        self.objectDeeplinkUrl: list[str | None]
        self.sourceIp: list[Incomplete | None]
    def __bool__(self) -> bool: ...
    @property
    def WalletHistory(self) -> Self: ...

class UserAchievements:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.secondsSpentOfLast24Hours: int
        self.secondsSpentOfLast7Days: int
        self.numberOfFollowersCount: int
        self.numberOfPostsCreated: int
    def __bool__(self) -> bool: ...
    @property
    def UserAchievements(self) -> Self: ...

class UserSavedBlogs:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.object: list[Blog | Wiki | dict[str, Any]]
        self.objectType: list[int]
        self.bookmarkedTime: list[str]
        self.objectId: list[str]
        self.objectJson: list[dict[str, Any]]
    def __bool__(self) -> bool: ...
    @property
    def UserSavedBlogs(self) -> Self: ...

class GetWikiInfo:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.wiki: Wiki
        self.inMyFavorites: bool
        self.isBookmarked: bool
    def __bool__(self) -> bool: ...
    @property
    def GetWikiInfo(self) -> Self: ...

class GetBlogInfo:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.blog: Blog
        self.isBookmarked: bool
    def __bool__(self) -> bool: ...
    @property
    def GetBlogInfo(self) -> Self: ...

class GetSharedFolderInfo:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.folderCount: int
        self.fileCount: int
    def __bool__(self) -> bool: ...
    @property
    def GetSharedFolderInfo(self) -> Self: ...

class WikiCategoryList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.itemsCount: list[int]
        self.parentCategoryId: list[str]
        self.categoryId: list[str]
        #self.content: list[str | None]
        self.extensions: list[dict[str, Any] | None]
        self.createdTime: list[str]
        #self.subcategoriesCount: list[int]
        self.title: list[str]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.icon: list[str]
    def __bool__(self) -> bool: ...
    @property
    def WikiCategoryList(self) -> Self: ...

class WikiCategory:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.subCategory: WikiCategoryList
        self.itemsCount: int
        self.parentCategoryId: str
        self.parentType: int
        self.categoryId: str
        #self.content: str | None
        self.extensions: dict[str, Any] | None
        self.createdTime: str
        #self.subcategoriesCount = None
        self.title: str
        self.mediaList: list[list[Incomplete]] | None
        self.icon: str
    def __bool__(self) -> bool: ...
    @property
    def WikiCategory(self) -> Self: ...

class TippedUsersSummary:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfileList
        self.tipSummary: dict[str, Any]
        self.totalCoins: int
        self.tippersCount: int
        self.globalTipSummary: dict[str, Any] | None
        self.globalTippersCount: int | None
        self.globalTotalCoins: int | None
        self.lastTippedTime: list[str | None]
        self.totalTippedCoins: list[int]
        self.lastThankedTime: list[str | None]
    def __bool__(self) -> bool: ...
    @property
    def TippedUsersSummary(self) -> Self: ...

class Thread:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.membersSummary: UserProfileList
        self.userAddedTopicList: list[str] | None
        self.membersQuota: int
        self.chatId: str
        self.keywords: str | None
        self.membersCount: int
        self.isPinned: bool
        self.title: str | None
        self.membershipStatus: int
        self.content: str | None
        self.needHidden: bool
        self.alertOption: Incomplete
        self.lastReadTime: str | None
        self.type: int
        self.status: int
        self.publishToGlobal: bool
        self.modifiedTime: str | None
        self.condition: int
        self.icon: str | None
        self.latestActivityTime: str | None
        self.extensions: dict[str, Any] | None
        self.viewOnly: bool
        self.coHosts: list[str] | None
        self.membersCanInvite: bool
        self.announcement: str | None
        self.language: str | None
        self.lastMembersSummaryUpdateTime: str | None
        self.backgroundImage: str
        self.channelType: int
        self.comId: int
        self.createdTime: str
        self.creatorId: str
        self.bannedUsers: list[str] | None
        self.tippingPermStatus: int
        self.visibility: int
        self.fansOnly: bool | None
        self.pinAnnouncement: bool
        self.vvChatJoinType: int | None
        self.screeningRoomHostId: str | None
        self.screeningRoomPermission: Incomplete | None
        self.disabledTime: str | None
        self.organizerTransferCreatedTime: str | None
        self.organizerTransferId: str | None
    def __bool__(self) -> bool: ...
    @property
    def Thread(self) -> Self: ...

class ThreadList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.membersSummary: list[UserProfileList]
        self.userAddedTopicList: list[list[str] | None]
        self.membersQuota: list[int]
        self.chatId: list[str]
        self.keywords: list[str | None]
        self.membersCount: list[int]
        self.isPinned: list[bool]
        self.title: list[str | None]
        self.membershipStatus: list[int]
        self.content: list[str | None]
        self.needHidden: list[bool]
        self.alertOption: list[Incomplete]
        self.lastReadTime: list[str | None]
        self.type: list[int]
        self.status: list[str]
        self.publishToGlobal: list[bool]
        self.modifiedTime: list[str | None]
        self.condition: list[int]
        self.icon: list[str | None]
        self.latestActivityTime: list[str | None]
        self.extensions: list[dict[str, Any] | None]
        self.viewOnly: list[bool]
        self.coHosts: list[list[str] | None]
        self.membersCanInvite: list[bool]
        self.announcement: list[str | None]
        self.language: list[str | None]
        self.lastMembersSummaryUpdateTime: list[str | None]
        self.backgroundImage: list[str]
        self.channelType: list[int]
        self.comId: list[int]
        self.createdTime: list[str]
        self.creatorId: list[str]
        self.bannedUsers: list[list[str] | None]
        self.tippingPermStatus: list[int]
        self.visibility: list[int]
        self.fansOnly: list[bool | None]
        self.pinAnnouncement: list[bool]
        self.vvChatJoinType: list[int | None]
        self.screeningRoomHostId: list[str | None]
        self.screeningRoomPermission: list[Incomplete | None]
        self.disabledTime: list[str | None]
        self.organizerTransferCreatedTime: list[str | None]
        self.organizerTransferId: list[str | None]
    def __bool__(self) -> bool: ...
    @property
    def ThreadList(self) -> Self: ...

class Sticker:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.collection: StickerCollection
        self.status: int
        self.icon: str
        self.iconV2: str
        self.name: str
        self.stickerId: str
        self.smallIcon: str
        self.smallIconV2: str
        self.stickerCollectionId: str | None
        self.mediumIcon: str
        self.mediumIconV2: str
        self.extensions: dict[str, Any] | None
        self.usedCount: int
        self.createdTime: str
    def __bool__(self) -> bool: ...
    @property
    def Sticker(self) -> Self: ...

class StickerList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.collection: StickerCollectionList
        self.status: list[int]
        self.icon: list[str]
        self.iconV2: list[str]
        self.name: list[str]
        self.stickerId: list[str]
        self.smallIcon: list[str]
        self.smallIconV2: list[str]
        self.stickerCollectionId: list[str]
        self.mediumIcon: list[str]
        self.mediumIconV2: list[str]
        self.extensions: list[dict[str, Any] | None]
        self.usedCount: list[int]
        self.createdTime: list[str]
    def __bool__(self) -> bool: ...
    @property
    def StickerList(self) -> Self: ...

class StickerCollection:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.originalAuthor: UserProfile
        self.originalCommunity: Community
        self.status: int
        self.collectionType: int
        self.modifiedTime: str | None
        self.bannerUrl: str
        self.smallIcon: str
        self.stickersCount: int
        self.usedCount: int
        self.icon: str
        self.title: str
        self.collectionId: str
        self.extensions: dict[str, Any] | None
        self.isActivated: bool
        self.ownershipStatus: int
        self.isNew: bool | None
        self.availableComIds: list[int] | None
        self.description: str | None
        self.iconSourceStickerId: str
        self.restrictionInfo: dict[str, Any] | None
        self.discountValue: int
        self.discountStatus: int
        self.ownerId: str
        self.ownerType: int
        self.restrictType: int
        self.restrictValue: int
        self.availableDuration: Incomplete | None
    def __bool__(self) -> bool: ...
    @property
    def StickerCollection(self) -> Self: ...

class StickerCollectionList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.originalAuthor: UserProfileList
        self.originalCommunity: CommunityList
        self.status: list[int]
        self.collectionType: list[int]
        self.modifiedTime: list[str | None]
        self.bannerUrl: list[str]
        self.smallIcon: list[str]
        self.stickersCount: list[int]
        self.usedCount: list[int]
        self.icon: list[str]
        self.name: list[str]
        self.collectionId: list[str]
        self.extensions: list[dict[str, Any] | None]
        self.isActivated: list[bool]
        self.ownershipStatus: list[int]
        self.isNew: list[bool | None]
        self.availableComIds: list[list[int] | None]
        self.description: list[str | None]
        self.iconSourceStickerId: list[str]
        self.restrictionInfo: list[dict[str, Any] | None]
        self.discountValue: list[int]
        self.discountStatus: list[int]
        self.ownerId: list[str]
        self.ownerType: list[int]
        self.restrictType: list[int]
        self.restrictValue: list[int]
        self.availableDuration: list[Incomplete | None]
    def __bool__(self) -> bool: ...
    @property
    def StickerCollectionList(self) -> Self: ...

class Message:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.sticker: Sticker
        self.content: str | None
        self.includedInSummary: bool
        self.isHidden: bool
        self.messageType: int
        self.messageId: str
        self.mediaType: int
        self.mediaValue: str | None
        self.chatBubbleId: str | None
        self.clientRefId: int
        self.chatId: str
        self.createdTime: str
        self.chatBubbleVersion: int | None
        self.type: int
        self.replyMessage: dict[str, Any] | None
        self.extensions: dict[str, Any] | None
        self.duration: float | None
        self.originalStickerId: str | None
        self.videoDuration: float | None
        self.videoExtensions: dict[str, Any] | None
        self.videoHeight: int | None
        self.videoCoverImage: str | None
        self.videoWidth: int | None
        self.mentionUserIds: list[str] | None
        self.tippingCoins: Incomplete | None
    def __bool__(self) -> bool: ...
    @property
    def Message(self) -> Self: ...

class MessageList:
    def __init__(self, data: list[dict[str, Any]], nextPageToken: str | None = None, prevPageToken: str | None = None) -> None:
        self.json: list[dict[str, Any]]
        self.nextPageToken: str | None
        self.prevPageToken: str | None
        self.author: UserProfileList
        self.sticker: StickerList
        self.content: list[str | None]
        self.includedInSummary: list[bool]
        self.isHidden: list[bool]
        self.messageType: list[int]
        self.messageId: list[str]
        self.mediaType: list[int]
        self.mediaValue: list[str | None]
        self.chatBubbleId: list[str | None]
        self.clientRefId: list[int]
        self.chatId: list[str]
        self.createdTime: list[str]
        self.chatBubbleVersion: list[int | None]
        self.type: list[int]
        self.extensions: list[dict[str, Any] | None]
        self.mentionUserIds: list[list[str] | None]
        self.duration: list[float | None]
        self.originalStickerId: list[str | None]
        self.videoExtensions: list[dict[str, Any] | None]
        self.videoDuration: list[float | None]
        self.videoHeight: list[int | None]
        self.videoWidth: list[int | None]
        self.videoCoverImage: list[str | None]
        self.tippingCoins: list[Incomplete | None]
    def __bool__(self) -> bool: ...
    @property
    def MessageList(self) -> Self: ...

class GetMessages:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.messageList: list[dict[str, Any]]
        self.nextPageToken: str | None
        self.prevPageToken: str | None
    def __bool__(self) -> bool: ...
    @property
    def GetMessages(self) -> MessageList: ...

class CommunityStickerCollection:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.sticker: StickerCollectionList
        self.stickerCollectionCount: int
    def __bool__(self) -> bool: ...
    @property
    def CommunityStickerCollection(self) -> Self: ...

class NotificationList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.contextComId: list[int]
        self.objectText: list[str]
        self.objectType: list[int]
        self.contextValue: list[Incomplete | None]
        self.comId: list[int]
        self.notificationId: list[str]
        self.objectSubtype: list[int]
        self.parentType: list[int]
        self.createdTime: list[str]
        self.parentId: list[str]
        self.type: list[int]
        self.contextText: list[str]
        self.objectId: list[str]
        self.parentText: list[str]
    def __bool__(self) -> bool: ...
    @property
    def NotificationList(self) -> Self: ...

class AdminLogList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.createdTime: list[str]
        self.objectType: list[int]
        self.operationName: list[str]
        self.comId: list[int]
        self.referTicketId: list[str]
        self.extData: list[dict[str, Any]]
        self.operationDetail: list[Incomplete | None]
        self.operationLevel: list[int]
        self.moderationLevel: list[int]
        self.operation: list[int]
        self.objectId: list[str]
        self.logId: list[str]
        self.objectUrl: list[str]
        self.content: list[str | None]
        self.value: list[Incomplete]
    def __bool__(self) -> bool: ...
    @property
    def AdminLogList(self) -> Self: ...

class LotteryLog:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.awardValue: int
        self.parentId: str
        self.parentType: int
        self.objectId: str
        self.objectType: int
        self.createdTime: str
        self.awardType: int
        self.refObject: dict[str, Any]
    def __bool__(self) -> bool: ...
    @property
    def LotteryLog(self) -> Self: ...

class VcReputation:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.availableReputation: int
        self.maxReputation: int
        self.reputation: int
        self.participantCount: int
        self.totalReputation: int
        self.duration: int
    def __bool__(self) -> bool: ...
    @property
    def VcReputation(self) -> Self: ...

class FanClubList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.profile: UserProfileList
        self.targetUserProfile: UserProfileList
        self.userId: list[str]
        self.lastThankedTime: list[str | None]
        self.expiredTime: list[str | None]
        self.createdTime: list[str]
        self.status: list[int]
        self.targetUserId: list[str]
    def __bool__(self) -> bool: ...
    @property
    def FanClubList(self) -> Self: ...

class InfluencerFans:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.influencerProfile: UserProfile
        self.fanClubList: FanClubList
        self.myFanClub: Incomplete
    def __bool__(self) -> bool: ...
    @property
    def InfluencerFans(self) -> Self: ...

class QuizQuestionList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.status: list[int]
        self.parentType: list[int]
        self.title: list[str]
        self.createdTime: list[str]
        self.questionId: list[str]
        self.parentId: list[str]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.extensions: list[dict[str, Any] | None]
        self.style: list[dict[str, Any] | None]
        self.backgroundImage: list[str | None]
        self.backgroundColor: list[str | None]
        self.answerExplanation: list[str | None]
        self.answersList: list[QuizAnswers]
    def __bool__(self) -> bool: ...
    @property
    def QuizQuestionList(self) -> Self: ...

class QuizAnswers:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.answerId: list[str]
        self.isCorrect: list[bool]
        self.mediaList: list[list[list[Incomplete]] | None]
        self.title: list[str]
        self.qhash: list[Incomplete]
    def __bool__(self) -> bool: ...
    @property
    def QuizAnswers(self) -> Self: ...

class QuizRankings:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.rankingList: list[QuizRanking]
        self.quizPlayedTimes: int
        self.quizInBestQuizzes: bool
        self.profile: QuizRanking
    def __bool__(self) -> bool: ...
    @property
    def QuizRankings(self) -> Self: ...

class QuizRanking:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.highestMode: int
        self.modifiedTime: str | None
        self.isFinished: bool
        self.hellIsFinished: bool
        self.highestScore: int
        self.beatRate: int
        self.lastBeatRate: int
        self.totalTimes: int
        self.latestScore: int
        self.latestMode: int
        self.createdTime: str
    def __bool__(self) -> bool: ...
    @property
    def QuizRanking(self) -> Self: ...

class QuizRankingList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.highestMode: list[int]
        self.modifiedTime: list[str | None]
        self.isFinished: list[bool]
        self.hellIsFinished: list[bool]
        self.highestScore: list[int]
        self.beatRate: list[int]
        self.lastBeatRate: list[int]
        self.totalTimes: list[int]
        self.latestScore: list[int]
        self.latestMode: list[int]
        self.createdTime: list[str]
    def __bool__(self) -> bool: ...
    @property
    def QuizRankingList(self) -> Self: ...

class SharedFolderFile:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.votesCount: int
        self.createdTime: str
        self.modifiedTime: str | None
        self.extensions: dict[str, Any] | None
        self.title: str
        self.media: str
        self.width: int
        self.height: int
        self.commentsCount: int
        self.fileType: int
        self.votedValue: int
        self.fileId: str
        self.comId: int
        self.status: int
        self.fileUrl: str
        self.mediaType: int
    def __bool__(self) -> bool: ...
    @property
    def SharedFolderFile(self) -> Self: ...

class SharedFolderFileList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.votesCount: list[int]
        self.createdTime: list[str]
        self.modifiedTime: list[str | None]
        self.extensions: list[dict[str, Any] | None]
        self.title: list[str]
        self.media: list[str]
        self.width: list[int]
        self.height: list[int]
        self.commentsCount: list[int]
        self.fileType: list[int]
        self.votedValue: list[int]
        self.fileId: list[str]
        self.comId: list[int]
        self.status: list[int]
        self.fileUrl: list[str]
        self.mediaType: list[int]
    def __bool__(self) -> bool: ...
    @property
    def SharedFolderFileList(self) -> Self: ...

class Event:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.comId: int
        self.alertOption: Incomplete | None
        self.membershipStatus: int
        self.actions: list[str] | None
        self.target: str | None
        self.params: dict[str, Any] | None
        self.threadType: int | None
        self.id: str | None
        self.duration: float | None
        self.message: Message
    def __bool__(self) -> bool: ...
    @property
    def Event(self) -> Self: ...

class JoinRequest:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfileList
        self.communityMembershipRequestCount: int
    def __bool__(self) -> bool: ...
    @property
    def JoinRequest(self) -> Self: ...

class CommunityStats:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.dailyActiveMembers: int
        self.monthlyActiveMembers: int
        self.totalTimeSpent: int
        self.totalPostsCreated: int
        self.newMembersToday: int
        self.totalMembers: int
    def __bool__(self) -> bool: ...
    @property
    def CommunityStats(self) -> Self: ...

class InviteCode:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.author: UserProfile
        self.status: int
        self.duration: Incomplete
        self.invitationId: str
        self.link: str
        self.modifiedTime: str | None
        self.comId: int
        self.createdTime: str
        self.inviteCode: str
    def __bool__(self) -> bool: ...
    @property
    def InviteCode(self) -> Self: ...

class InviteCodeList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.status: list[int]
        self.duration: list[Incomplete | None]
        self.invitationId: list[str]
        self.link: list[str]
        self.modifiedTime: list[str | None]
        self.comId: list[int]
        self.createdTime: list[str]
        self.inviteCode: list[str]
    def __bool__(self) -> bool: ...
    @property
    def InviteCodeList(self) -> Self: ...

class WikiRequestList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.wiki: WikiList
        self.originalWiki: WikiList
        self.authorId: list[str]
        self.status: list[int]
        self.modifiedTime: list[str | None]
        self.message: list[str | None]
        self.wikiId: list[str]
        self.requestId: list[str]
        self.destinationItemId: list[str]
        self.createdTime: list[str]
        self.responseMessage: list[str | None]
    def __bool__(self) -> bool: ...
    @property
    def WikiRequestList(self) -> Self: ...

class LiveLayer:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.userProfileCount: list[int]
        self.topic: list[str]
        self.userProfileList: list[UserProfileList]
        self.mediaList: list[list[list[Incomplete]] | None]
    def __bool__(self) -> bool: ...
    @property
    def LiveLayer(self) -> Self: ...

class AvatarFrameList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.author: UserProfileList
        self.targetUser: UserProfileList
        self.isGloballyAvailable: list[bool]
        self.extensions: list[dict[str, Any]]
        self.frameType: list[int]
        self.resourceUrl: list[str]
        self.md5: list[Incomplete | None]
        self.icon: list[str]
        self.createdTime: list[str]
        self.config: list[dict[str, Any] | None]
        self.moodColor: list[str]
        self.configName: list[str | None]
        self.configVersion: list[int]
        self.userIconBorderColor: list[str]
        self.avatarFramePath: list[str]
        self.avatarId: list[str]
        self.ownershipStatus: list[int]
        self.frameUrl: list[str]
        self.additionalBenefits: list[dict[str, Any] | None]
        self.firstMonthFreeAminoPlusMembership: list[Incomplete | None]
        self.restrictionInfo: list[dict[str, Any] | None]
        self.ownerType: list[int]
        self.restrictType: list[int]
        self.restrictValue: list[int]
        self.availableDuration: list[Incomplete | None]
        self.discountValue: list[int]
        self.discountStatus: list[int]
        self.ownerId: list[str]
        self.ownershipInfo: list[dict[str, Any] | None]
        self.isAutoRenew: list[bool]
        self.modifiedTime: list[str | None]
        self.name: list[str]
        self.frameId: list[str]
        self.version: list[int]
        self.isNew: list[bool | None]
        self.availableComIds: list[int]
        self.status: list[int]
    def __bool__(self) -> bool: ...
    @property
    def AvatarFrameList(self) -> Self: ...

class BubbleConfig:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.status: int
        self.allowedSlots: Incomplete | None
        self.name: str
        self.vertexInset: Incomplete | None
        self.zoomPoint: Incomplete | None
        self.coverImage: str
        self.bubbleType: int
        self.contentInsets: Incomplete | None
        self.version: int
        self.linkColor: str
        self.backgroundPath: str
        self.id: str
        self.previewBackgroundUrl: str
    def __bool__(self) -> bool: ...
    @property
    def BubbleConfig(self) -> Self: ...

class Bubble:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.config: BubbleConfig
        self.uid: str
        self.isActivated: bool
        self.isNew: bool | None
        self.bubbleId: str
        self.resourceUrl: str
        self.version: int
        self.backgroundImage: str
        self.status: int
        self.modifiedTime: str | None
        self.ownershipInfo: dict[str, Any] | None
        self.expiredTime: str | None
        self.isAutoRenew: bool
        self.ownershipStatus: int
        self.bannerImage: int
        self.md5: Incomplete | None
        self.name: str
        self.coverImage: str
        self.bubbleType: int
        self.extensions: dict[str, Any] | None
        self.templateId: int
        self.createdTime: str
        self.deletable: bool
        self.backgroundMedia: Incomplete | None
        self.description: str | None
        self.materialUrl: str
        self.comId: int
        self.restrictionInfo: dict[str, Any] | None
        self.discountValue: int
        self.discountStatus: int
        self.ownerId: str
        self.ownerType: int
        self.restrictType: int
        self.restrictValue: int
        self.availableDuration: Incomplete | None
    def __bool__(self) -> bool: ...
    @property
    def Bubble(self) -> Self: ...

class BubbleConfigList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.status: list[int]
        self.allowedSlots: list[Incomplete | None]
        self.name: list[str | None]
        self.vertexInset: list[Incomplete | None]
        self.zoomPoint: list[Incomplete | None]
        self.coverImage: list[str | None]
        self.bubbleType: list[int]
        self.contentInsets: list[Incomplete | None]
        self.version: list[int]
        self.linkColor: list[str]
        self.backgroundPath: list[str]
        self.id: list[str]
        self.previewBackgroundUrl: list[str]
    def __bool__(self) -> bool: ...
    @property
    def BubbleConfigList(self) -> None: ...

class BubbleList:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.config: BubbleConfigList
        self.uid: list[str]
        self.isActivated: list[bool]
        self.isNew: list[bool | None]
        self.bubbleId: list[str]
        self.resourceUrl: list[str]
        self.version: list[int]
        self.backgroundImage: list[str]
        self.status: list[int]
        self.modifiedTime: list[str | None]
        self.ownershipInfo: list[dict[str, Any] | None]
        self.expiredTime: list[str | None]
        self.isAutoRenew: list[bool]
        self.ownershipStatus: list[int]
        self.bannerImage: list[str]
        self.md5: list[Incomplete | None]
        self.name: list[str]
        self.coverImage: list[str]
        self.bubbleType: list[int]
        self.extensions: list[dict[str, Any] | None]
        self.templateId: list[int]
        self.createdTime: list[str]
        self.deletable: list[bool | None]
        self.backgroundMedia: list[Incomplete]
        self.description: list[str | None]
        self.materialUrl: list[str]
        self.comId: list[int]
        self.restrictionInfo: list[dict[str, Any] | None]
        self.discountValue: list[int]
        self.discountStatus: list[int]
        self.ownerId: list[str]
        self.ownerType: list[int]
        self.restrictType: list[int]
        self.restrictValue: list[int]
        self.availableDuration: list[Incomplete | None]
    def __bool__(self) -> bool: ...
    @property
    def BubbleList(self) -> Self: ...

class AvatarFrame:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.name: list[str]
        self.id: list[str]
        self.resourceUrl: list[str]
        self.icon: list[str]
        self.frameUrl: list[str]
        self.value: list[int]
    def __bool__(self) -> bool: ...
    @property
    def AvatarFrame(self) -> Self: ...

class ChatBubble:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.name: list[str]
        self.bubbleId: list[str]
        self.bannerImage: list[str]
        self.backgroundImage: list[str]
        self.resourceUrl: list[str]
        self.value: list[int]
    def __bool__(self) -> bool: ...
    @property
    def ChatBubble(self) -> Self: ...

class StoreStickers:
    def __init__(self, data: list[dict[str, Any]]) -> None:
        self.json: list[dict[str, Any]]
        self.id: list[str]
        self.name: list[str]
        self.icon: list[str]
        self.value: list[int]
        self.smallIcon: list[str]
    def __bool__(self) -> bool: ...
    @property
    def StoreStickers(self) -> Self: ...

class NoticeList:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.notificationId: list[str]
        self.noticeId: list[str]
        self.ndcId: list[int]
        self.title: list[str]
        self.targetNickname: list[str]
        self.targetLevel: list[int]
        self.targetReputation: list[int]
        self.targetUid: list[str]
        self.operatorNickname: list[str]
        self.operatorLevel: list[int]
        self.operatorReputation: list[int]
        self.operatorUid: list[str]
        self.operatorRole: list[int]
    def __bool__(self) -> bool: ...
    @property
    def NoticeList(self) -> Self: ...

class WSException:
    def __init__(self, data: dict[str, Any]) -> None:
        self.json: dict[str, Any]
        self.code: int
        self.message: str
    def __bool__(self) -> bool: ...
    @property
    def WSException(self) -> Self: ...

class Channel:
    def __init__(self, data) -> None:
        self.json: dict[str, Any]
        self.exception: WSException
        self.name: str
        self.key: str
        self.uid: int
        self.expiredTime: int
        self.comId: int
        self.chatId: str
    def __bool__(self) -> bool: ...
    @property
    def Channel(self) -> Self: ...
