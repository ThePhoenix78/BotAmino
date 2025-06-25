import enum


class EnumBase(enum.Enum):
    def __str__(self) -> str:
        return str(self.value)


class ActionReqType(str, enum.Enum):
    NEW = "new"
    DELETE = "delete"
    UPDATE = "update"
    EDIT = "edit"


class AdminOperation(int, enum.Enum):
    HIDE_USER = 18
    UNHIDE_USER = 19
    OBJECT_FEATURED = 114
    OBJECT_REMOVE_FEATURED = 116
    OBJECT_STATUS = 110
    SET_USER_MEMBERSHIP_TITLE = 207
    ADD_TO_BEST_QUIZZES = 240
    REMOVE_FROM_BEST_QUIZZES = 241


class BubbleType(int, enum.Enum):
    CUSTOM = 1
    OFFICIAL = 2


class BrowsePath(str, enum.Enum):
    COMMUNITY = "default"
    MEMBERS = "all-members"
    JOINED_CHATS = "my-chats"


class ChatMembership(int, enum.Enum):
    # NOT_JOINED = 0
    # JOINED = 1
    JOINED = 0
    UN_JOINED = 1
    JOIN_DISABLED = 2


class ChatType(int, enum.Enum):
    SINGLE = 0
    GROUP = 1
    PUBLIC = 2


class ChatMemberReqType(str, enum.Enum):
    HOST_CANDIDATES = "organizer-transfer-candidates"


class ChatReqType(str, enum.Enum):
    DISABLED = "public-disabled"
    KEYWORD = "public-keyword"  # params: q=''
    JOINED = "joined-me"
    PUBLIC = "public-all"
    EXIST_SINGLE = "exist-single"  # params: q=''


class ChatFilter(str, enum.Enum):
    RECOMMENDED = "recommended"
    POPULAR = "popular"
    LATEST = "latest"


class BlogCategoryType(int, enum.Enum):
    NORMAL = 0
    SECTIONHEADER = 1
    FEATURED = 2
    BEST_QUIZZES = 3


class BlogType(int, enum.Enum):
    NORMAL = 0
    CROSSPOST = 1
    REPOST = 2
    QUESTION = 3
    POLL = 4
    LINK = 5
    QUIZ = 6
    IMAGE = 7
    EXTERNAL_POST = 8
    STORY = 9
    STORY_CROSSPOST = 10


class LiveLayerAction(str, enum.Enum):
    BROWSING = "Browsing"
    CHATTING = "Chatting"
    COMMENTING = "Commenting"
    PLAYING = "Playing"
    POLLING = "Polling"
    RECORDING = "Recording"
    TYPING = "Typing"
    VOTING = "Voting"


class ChannelJoinRole(int, enum.Enum):
    GUEST = 0
    PRESENTER = 1
    AUDIENCE = 2
    GUEST_AUDIENCE = 3


class ChannelType(int, enum.Enum):
    NONE = 0
    AUDIO = 1
    AVATAR = 3
    VIDEO = 4
    SCREEN_ROOM = 5


class ClientType(int, enum.Enum):
    MASTER = 100
    STANDALONE = 101
    ACM = 200
    STORY_EDITOR = 201


class CommunityListedStatus(int, enum.Enum):
    NONE = 0
    UNLISTED = 1
    LISTED = 2


class CommunityProbationStatus(int, enum.Enum):
    OFF = 0
    ON = 1


class CommentPermission(int, enum.Enum):
    EVERYONE = 1
    FOLLOWINGS = 2
    ONLY_USER = 3


class CommentSort(int, enum.Enum):
    NEWEST = 0
    OLDEST = 1
    TOP = 2


class ContentType(str, enum.Enum):
    BINARY = "application/octet-stream"
    JSON = "application/json charset=utf-8"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain charset=utf-8"
    URL_FORM = "application/x-www-form-urlencoded charset=utf-8"


class Presence(int, enum.Enum):
    NONE = 0
    ONLINE = 1
    OFFLINE = 2


class DisabledLevel(int, enum.Enum):
    NONE = 0
    CURATOR = 1
    LEADER = 2
    IMOD = 3


class ExternalSourceType(int, enum.Enum):
    YOUTUBE = 1
    REDDIT = 2


class FeatureType(int, enum.Enum):
    TOP_IMAGE = 0
    TOP_TEXT = 1
    NORMAL_IMAGE = 2
    NORMAL_TEXT = 3
    PIN = 4
    MIDDLE_IMAGE = 5
    MIDDLE_TEXT = 6
    FULLSCREEN_IMAGE = 8
    FULLSCREEN_TEXT = 9
    TOP_SEPARATE_IMAGE = 10


class FeaturedType(int, enum.Enum):
    NONE = 0
    NORMAL = 1
    PINNED = 2
    MEMBER = 4


class FlagType(int, enum.Enum):
    BULLYING = 0
    INAPPROPRIATE_CONTENT = 1
    SPAM = 2
    ART_THEFT = 3
    OFF_TOPIC = 4
    TROLLING = 5
    SEXUALLY_EXPLICIT = 100
    VIOLENT_CONTENT = 101
    SEXUALLY_PROFILE = 102
    USER_IN_AUDIO_CHAT = 104
    USER_IN_VIDEO_CHAT = 105
    VIOLENCE_OR_DANGEROUS_ACTIVITY = 106
    HATE_SPEECH_AND_BIGOTRY = 107
    SELF_INJURY_AND_SUICIDE = 108
    HARASSMENT_AND_TROLLING = 109
    NUDITY_AND_PORNOGRAPHY = 110
    OTHERS = 200
    OTHERS_LIVE_MODE = 201


class Gender(int, enum.Enum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2
    NON_BINARY = 255


class APILiveLayerTopic(str, enum.Enum):
    HOMEPAGE = "homepage"
    ONLINE = "online-members"
    PLAYING_QUIZZES = "quizzes"
    WATCHING_VIDEOS = "public-watching-videos"  # screen room
    VOTING_BLOGS = "voting-blogs"
    POLLING_POLLS = "polls"
    READING_POSTS = "blogs"
    BROWSING = "pages"
    CHANNEL_CHATTING = "public-vv-chats"
    # CHANNEL_CHATTING_PRIVATE = ""
    CHATTING = "public-chats"
    # CHATTING_PRIVATE = ""
    COMMENTING_BLOGS = "commenting-blogs"
    LIVE_CHATTING = "public-live-chats"


class LiveLayerTopic(str, enum.Enum):
    # HOMEPAGE = "homepage"
    # ONLINE = "online-members"
    # CHATS = "public-chats"
    # CHANNELS = "public-vv-chats"
    PLAYING_QUIZZES = "users-playing-quizzes"
    WATCHING_VIDEOS = "users-watching-videos"  # screen room
    WATCHING_VIDEOS_PRIVATE = "users-watching-videos-private"
    VOTING_BLOGS = "users-voting-blogs"
    POLLING_POLLS = "users-polling-polls"
    READING_POSTS = "users-browsing-blogs"
    BROWSING = "users-browsing-pages"
    CHANNEL_CHATTING = "users-vv-chatting"
    CHANNEL_CHATTING_PRIVATE = "users-vv-chatting-private"
    CHATTING = "users-chatting"
    CHATTING_PRIVATE = "users-chatting-private"
    COMMENTING_BLOGS = "users-commenting-blogs"
    LIVE_CHATTING = "users-live-chatting"

    BROWSING_BLOG = "users-browsing-blog-at"
    TYPING_START = "users-start-typing-at"
    TYPING_END = "users-end-typing-at"
    CHAT_RECORDING_START = "users-start-recording-at"
    CHAT_RECORDING_END = "users-end-recording-at"


class PlaylistItemType(int, enum.Enum):
    LOCAL_VIDEO = 1
    YOUTUBE = 2
    LOCAL_AUDIO = 3


class JoinType(int, enum.Enum):
    OPEN = 1
    APPROVAL_REQUIRED = 2
    INVITE_ONLY = 3


class MessageType(int, enum.Enum):
    TEXT = 0
    STRIKE = 1
    VOICE = 2
    STICKER = 3
    VIDEO = 4
    SHARE_EXURL = 50
    SHARE_USER = 51
    VOICE_CALL_NO_ANSWERED = 52
    VOICE_CALL_CANCELLED = 53
    VOICE_CALL_DECLINED = 54
    VIDEO_CALL_NO_ANSWERED = 55
    VIDEO_CALL_CANCELLED = 56
    VIDEO_CALL_DECLINED = 57
    AVATAR_CALL_NO_ANSWERED = 58
    AVATAR_CALL_CANCELLED = 59
    AVATAR_CALL_DECLINED = 60
    DELETED = 100
    MEMBER_JOIN = 101
    MEMBER_LEFT = 102
    CHAT_CREATED = 103
    BACKGROUND_CHANGE = 104
    TITLE_CHANGE = 105
    ICON_CHANGE = 106
    VOICE_CALL_START = 107
    VIDEO_CALL_START = 108
    AVATAR_CALL_START = 109
    VOICE_CALL_END = 110
    VIDEO_CALL_END = 111
    AVATAR_CALL_END = 112
    CONTENT_CHANGE = 113
    SCREENING_ROOM_START = 114
    SCREENING_ROOM_END = 115
    HOST_TRANSFERRED = 116
    FORCED_DELETED = 117
    CHAT_REMOVED = 118
    DELETED_BY_MOD = 119
    TIPPING = 120
    PIN_ANNOUNCEMENT = 121
    VOICE_PERMISSION_OPEN_TO_EVERYONE = 122
    VOICE_PERMISSION_APPROVAL_REQUIRED = 123
    VOICE_PERMISSION_INVITE_ONLY = 124
    ENABLE_VIEW_ONLY = 125
    DISABLE_VIEW_ONLY = 126
    UNPIN_ANNOUNCEMENT = 127
    ENABLE_TIP_PERMISSION = 128
    DISABLE_TIP_PERMISSION = 129
    TIMESTAMP = 65281
    WELCOME_MESSAGE = 65282
    INVITE_MESSAGE = 65283


class NotificationPicType(int, enum.Enum):
    NORMAL = 0
    USER_PROFILE_ICON = 1
    COMMUNITY_ICON = 2


class NotificationType(int, enum.Enum):
    RESERVED = 0
    USER_MEMBERSHIP = 1
    USER_MEMBERSHIP_INVITATION = 2
    COMMENT = 3
    COMMENT_QUOTED = 4
    TOPIC_MEMBERSHIP = 5
    TOPIC_MEMBERSHIP_INVITATION = 6
    REPLY = 7
    REPLY_QUOTED = 8
    VOTE_UP = 9
    VOTE_DOWN = 10
    REPOST = 11
    POLL_OPTION_ADDED = 12
    POLL_OPTION_APPROVED = 13
    POLL_OPTION_VOTED_UP = 14
    POLL_ENDED_GENERAL = 15
    POLL_ENDED_OWNER = 16
    POLL_ENDED_CONTESTANT = 17
    CHAT_MESSAGE_RECEIVED = 18
    CHAT_MESSAGE_TYPING = 19
    CHAT_THREAD_USER_OBSERVING = 20
    CHAT_THREAD_INVITE_RECEIVED = 21
    CHAT_THREAD_JOIN_REQUEST_RECEIVED = 22
    CHAT_THREAD_JOIN_REQUEST_APPROVED = 23

    INVITE_AUDIO_CHAT = 29
    INVITE_VIDEO_CHAT = 30
    CREATE_AUDIO_CHAT = 31
    CREATE_VIDEO_CHAT = 32
    INVITE_AVATAR_CHAT = 34
    CREATE_AVATAR_CHAT = 35

    INVITE_SCREENING_ROOM = 37
    CREATE_SCREENING_ROOM = 38
    CANCEL_VV_CHAT = 39

    P2A_TASK_FINISHED = 50
    GET_COINS_BY_WATCHING_ADS = 51
    TRANSFER_HOST_REQUEST_RECEIVED = 53
    TRANSFER_HOST_REQUEST_ACCEPTED = 54
    VV_CHAT_PRESENTER_INVITE = 66
    ADD_CHAT_CO_HOST = 67
    REMOVE_CHAT_CO_HOST = 68


class NoticeType(int, enum.Enum):
    NONE = 0
    PROMOTE_LEADER = 1
    PROMOTE_CURATOR = 2
    TRANSFER_AGENT = 3
    STRIKE_USER = 4
    COPYRIGHT_TAKE_DOWN = 5
    NOTICE_USER = 6
    WARN_USER = 7
    GLOBAL_NOTICE_USER = 8
    GLOBAL_WARN_USER = 9
    GLOBAL_STRIKE_USER = 10
    GLOBAL_SYSTEM_MESSAGE = 11


class NoticeAction(int, enum.Enum):
    YES = 1
    NO = 2


class NoticePenaltyType(int, enum.Enum):
    NONE = 0
    MUTE = 1


class ObjectType(int, enum.Enum):
    USER = 0
    BLOG = 1
    WIKI = 2
    COMMENT = 3
    BLOG_CATEGORY = 4
    BLOG_CATEGORY_ITEM_TAG = 5
    FEATURED_WIKI = 6
    CHAT_MESSAGE = 7
    REPUTATION_LOG = 10
    POLL_OPTION = 11
    CHAT = 12
    WIKI_CATEGORY = 13
    WIKI_CATEGORY_ITEM_TAG = 14
    WIKI_SUBMISSION = 15
    COMMUNITY = 16
    COMMUNITY_COLLECTION = 17
    COMMUNITY_INVITATION = 18
    COMMUNITY_JOIN_REQUEST = 19
    BOOKMARK = 20
    COMMUNITY_REVIEW_REQUEST = 21
    QUIZ_QUESTION = 23
    EXTERNAL_ORIGINAL_POST = 29
    # 32 mimeType="video/mp4v-es"
    # 33 mimeType="video/avc"
    # 35 mimeType="video/hevc"
    # 64 mimeType="audio/mp4a-latm"
    IMAGE = 100
    SOUND = 101  # mimeType="video/mpeg2"
    VIDEO = 102
    YOUTUBE_VIDEO = 103
    # 104 # mimeType="audio/mp4a-latm"
    SHARED_FOLDER = 106  # mimeType="video/mpeg"
    # 107 # mimeType="audio/mpeg"
    SHARED_FILE = 109
    AUDIO = 110
    MODERATION_TASK = 111
    SCREENSHOT = 112
    STICKER = 113
    STICKER_COLLECTION = 114
    PROP = 115
    CHAT_BUBBLE = 116
    VIDEO_FILTER = 117
    ORDER = 118
    SHARE_REQUEST = 119
    VV_CHAT = 120
    P2A = 121
    AVATAR_FRAME = 122
    AMINO_VIDEO = 123
    INTEREST_DATA = 126
    STORY_TOPIC = 128
    ANNOUNCEMENT = 131
    CAPTION_FONT = 133
    CAPTION_ANIMATION = 134
    # 163 mimeType="video/wvc1"
    # 165 mimeType="audio/ac3"
    # 166 mimeType="audio/eac3"
    # 171 mimeType="audio/vnd.dts.hd"
    # STREAM = 172  mimeType="audio/vnd.dts"
    # 173 mimeType="audio/opus"
    # 174 mimeType="audio/ac4"
    # 177 mimeType="video/x-vnd.on2.vp9"
    SEARCH_KEY_PREDICTION = 901


class SoundType(int, enum.Enum):
    MUSIC = 1
    SFX = 2


class StoreItemStatus(int, enum.Enum):
    IDLE = 0
    LOADING = 1
    DOWNLOADING = 2
    DOWNLOAD_ERROR = 3
    OWNED = 4
    ACTIVATED = 5
    SET = 6
    ADDED = 7
    UNAVAILABLE = 8


class StoryType(int, enum.Enum):
    DISCOVER = 0
    INVALID = -1


class StoryReqType(str, enum.Enum):
    DISCOVER_LIST = "discover-list"
    TOPIC_LIST = "topic-list"


class StoryCategoryKey(str, enum.Enum):
    LATEST = "latest"
    POPULAR = "popular"
    RECOMMENDATION = "recommendation"


class StoryPlayer(str, enum.Enum):
    COMMUNITY = "community-player"
    DISCOVER = "discover-player"
    GLOBAL_SEARCH = "global-search-player"
    TOPIC = "topic-player"
    TRENDING = "trending-player"
    USER_PROFILE = "user-player"


class UsersReqType(str, enum.Enum):
    ONLINE = "online"


class WsErrorType(int, enum.Enum):
    INTERNAL_SERVER_EXCEPTION = 1
    THREAD_NOT_AVAILABLE = 101
    THREAD_MEMBERSHIP_NOT_ACTIVE = 102
    USER_PROFILE_NOT_AVAILABLE = 103
    TOO_MANY_PRESENTERS = 105
    CHANGE_CHANNEL_TYPE_NOT_MATCH = 106
    CHANGE_CHANNEL_TYPE_NO_PERMISSION = 107
    CHANGE_CHANNEL_JOIN_ROLE_NOT_MATCH = 108
    NO_PRESENTERS = 109
    THREAD_MEMBERSHIP_NO_PERMISSION = 110
    CHANNEL_USER_BUSY = 111
    CHANNEL_USER_NOT_ACTIVE = 112
    INVALID_LIVE_STREAM_TOPIC = 113
    INVALID_LIVE_STREAM_ACTION = 114
    UPDATE_PLAY_LIST_NO_PERMISSION = 115
    TOO_MANY_PRESENTERS_IN_SCREENING_ROOM = 116
    VV_CHAT_CLOSED = 117


class WsMessageType(int, enum.Enum):
    ERROR_MESSAGE = 1
    CHANNEL_ORGANIZER_LEFT = 2
    CHANNEL_NOT_AVAILABLE = 3
    USER_PROFILE_BANNED = 4
    CHANNEL_MEMBERSHIP_BANNED = 5
    CHANNEL_NO_PRESENTER = 6

    PUSH_NOTIFICATION_DTO = 10

    CHANNEL_PRIVATE_NOT_ACCEPT = 99
    CHANNEL_JOIN_REQUEST = 100
    CHANNEL_JOIN_RESPONSE = 101
    CHANNEL_USER_LIST_RESPONSE = 102
    CHANNEL_LEAVE_REQUEST = 103
    CHANNEL_LEAVE_RESPONSE = 104
    CHANNEL_USER_LIST_REQUEST = 105
    CHANNEL_USER_JOINED_MESSAGE = 106
    CHANNEL_USER_LEFT_MESSAGE = 107
    CHANNEL_UPDATE_REQUEST = 108
    CHANNEL_UPDATE_RESPONSE = 109

    CHANNEL_STATUS_CHANGED_MESSAGE = 111  # CHANNEL_UPDATE_MESSAGE ?
    CHANNEL_UPDATE_JOIN_ROLE_REQUEST = 112
    CHANNEL_UPDATE_JOIN_ROLE_RESPONSE = 113
    CHANNEL_USER_STATUS_CHANGED_MESSAGE = 114
    CHANNEL_FORCE_QUIT_MESSAGE = 115
    CHANNEL_USER_PING_REQUEST = 116
    CHANNEL_USER_PING_RESPONSE = 117
    MULTI_DEVICE_ERROR = 118
    SCREEN_ROOM_PLAY_LIST_RESPONSE = 119
    SCREEN_ROOM_PLAY_LIST_UPDATE_REQUEST = 120
    SCREEN_ROOM_PLAY_LIST_UPDATE_RESPONSE = 121
    SCREEN_ROOM_PLAY_LIST_REQUEST = 122

    CHANNEL_FORCE_UPDATE_USER_ROLE_REQUEST = 126
    CHANNEL_FORCE_UPDATE_USER_ROLE_RESPONSE = 127
    CHANNEL_FORCE_UPDATE_USER_ROLE_MESSAGE = 128

    CHANNEL_WAIT_LIST_APPROVE_MESSAGE = 130
    CHANNEL_WAIT_LIST_CHANGED_MESSAGE = 131
    CHANNEL_WAIT_LIST_CLEAN_REQUEST = 132
    CHANNEL_WAIT_LIST_CLEAN_RESPONSE = 133
    CHANNEL_WAIT_LIST_JOIN_APPROVE_REQUEST = 134
    CHANNEL_WAIT_LIST_JOIN_APPROVE_RESPONSE = 135
    CHANNEL_WAIT_LIST_JOIN_CANCEL_REQUEST = 136
    CHANNEL_WAIT_LIST_JOIN_CANCEL_RESPONSE = 137
    CHANNEL_WAIT_LIST_JOIN_REQUEST = 138
    CHANNEL_WAIT_LIST_JOIN_RESPONSE = 139

    AGORA_TOKEN_REQUEST = 200
    AGORA_TOKEN_RESPONSE = 201

    LIVE_LAYER_SUBSCRIBE_REQUEST = 300
    LIVE_LAYER_SUBSCRIBE_RESPONSE = 301
    LIVE_LAYER_UNSUBSCRIBE_REQUEST = 302
    LIVE_LAYER_UNSUBSCRIBE_RESPONSE = 303
    LIVE_LAYER_REPORT_ACTIVE_REQUEST = 304
    LIVE_LAYER_REPORT_ACTIVE_RESPONSE = 305
    LIVE_LAYER_REPORT_INACTIVE_REQUEST = 306
    LIVE_LAYER_REPORT_INACTIVE_RESPONSE = 307

    LIVE_LAYER_USER_JOINED_EVENT = 400
    LIVE_LAYER_USER_LEFT_EVENT = 401

    CHAT_MESSAGE_DTO = 1000
    CHAT_MESSAGE_ACK_DTO = 1001


class RankingType(int, enum.Enum):
    NONE = 0
    TIME_SPENT_OF_LAST_24_HOURS = 1
    TIME_SPENT_OF_LAST_7_DAYS = 2
    REPUTATION_OF_ALL_TIME = 3
    CHECKIN = 4
    QUIZ_SCORE_ALL_TIME = 5


class Role(int, enum.Enum):
    MEMBER = 0
    LEADER = 100
    CURATOR = 101
    LEADER_AGENT = 102
    MODERATOR = 200
    ADMIN = 201
    NEWS_FEED = 253
    SYSTEM = 254


class ValidationType(int, enum.Enum):
    EMAIL = 1
    DIGITS = 3
    GLOBAL_SMS = 8


class ValidationLevel(int, enum.Enum):
    IDENTITY = 1  # email & phoneNumber
    SECRET = 2  # password


class CouponStatus(int, enum.Enum):
    NOT_AVAILABLE = 1
    TO_CLAIM = 2
    AVAILABLE = 3


class CommunityStatus(int, enum.Enum):
    OK = 0


class JoinRequestStatus(int, enum.Enum):
    NONE = 0
    APPROVED = 2
    PENDING = 1
    REJECTED = 3


class FollowNotification(int, enum.Enum):
    OFF = 0
    ON = 1


class FollowingStatus(int, enum.Enum):
    NOT_FOLLOWING = 0
    FOLLOWING = 1


class PaymentType(int, enum.Enum):
    COIN = 1
    IOS_PURCHASE = 2
    IOS_SUBSCRIPTION = 3  # AppStore IN AP
    ANDROID_PURCHASE = 4
    ANDROID_SUBSCRIPTION = 5  # GooglePlay IN AP


class PlayStatus(int, enum.Enum):
    READY = 1
    PLAYING = 2
    PAUSE = 3


class ProductDiscountStatus(int, enum.Enum):
    OFF = 0
    AMINO_PLUS = 1


class ProductRestrictType(int, enum.Enum):
    NONE = 0
    FREE = 1
    AMINO_MEMBERSHIP = 2
    NO_RESTRICTION = 3
    COIN = 4


class AccountMembership(int, enum.Enum):
    NONE = 0
    AMINO_PLUS = 1


class MediaType(int, enum.Enum):
    NONE = 0
    IMAGE = 100
    VIDEO = 102
    YOUTUBE = 103
    AUDIO = 110
    STICKER = 113
    AMINO_VIDEO = 123


class MembershipStatus(int, enum.Enum):
    NONE = 0
    FORWARD = 1
    BACKWARD = 2
    MUTUAL = 3


class MimeType(str, enum.Enum):
    AUDIO_AC3 = "audio/ac3"
    AUDIO_AC4 = "audio/ac4"
    AUDIO_ACC = "audio/mp4a-latm"
    AUDIO_E_AC3 = "audio/eac3"
    AUDIO_DTS = "audio/vnd.dts"
    AUDIO_DTS_HD = "audio/vnd.dts.hd"
    AUDIO_OPUS = "audio/opus"
    VIDEO_H265 = "video/hevc"
    VIDEO_MP4V = "video/mp4v-es"
    AUDIO_MPEG = "audio/mpeg"
    VIDEO_MPEG = "video/mpeg"
    VIDEO_MPEG2 = "video/mpeg2"
    VIDEO_VC1 = "video/wvc1"
    VIDEO_VP9 = "video/x-vnd.on2.vp9"


class NoticeStatus(int, enum.Enum):
    PENDING = 1
    ACCEPTED = 2
    DECLINED = 3


class Status(int, enum.Enum):
    OK = 0
    CLOSED = 3
    PENDING = 5
    DISABLED = 9
    DELETED = 10


class TrackType(int, enum.Enum):
    AUDIO = 1
    VIDEO = 2
    CLOSED_CAPTION = 3
    MEDIA_METADATA = 4
    CAMERA_MOTION = 5
