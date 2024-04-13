import uuid
import time

from .helpers import signature

__all__ = (
    "ApisHeaders",
    "Tapjoy"
)

class ApisHeaders:
    def __init__(self, deviceId, user_agent, auid=None, sid=None, data=None, type=None, sig=None):
        headers = {
            "NDCDEVICEID": deviceId,
            "NDCLANG": "en",
            "Accept-Language": "en-US",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": user_agent,
            "Host": "service.aminoapps.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "Keep-Alive"
        }
        if data:
            headers["Content-Length"] = str(len(data))
            headers["NDC-MSG-SIG"] = signature(data)
        if auid:
            headers["AUID"] = auid
        if sid:
            headers["NDCAUTH"] = f"sid={sid}"
        if type:
            headers["Content-Type"] = type
        if sig:
            headers["NDC-MSG-SIG"] = sig
        self.headers = headers

class Tapjoy:
    def __init__(self, userId):
        self.data = {
            "reward": {
                "ad_unit_id": "t00_tapjoy_android_master_checkinwallet_rewardedvideo_322",
                "credentials_type": "publisher",
                "custom_json": {
                    "hashed_user_id": userId
                },
                "demand_type": "sdk_bidding",
                "event_id": str(uuid.uuid4()),
                "network": "tapjoy",
                "placement_tag": "default",
                "reward_name": "Amino Coin",
                "reward_valid": True,
                "reward_value": 2,
                "shared_id": "4d7cc3d9-8c8a-4036-965c-60c091e90e7b",
                "version_id": "1569147951493",
                "waterfall_id": "4d7cc3d9-8c8a-4036-965c-60c091e90e7b"
            },
            "app": {
                "bundle_id": "com.narvii.amino.master",
                "current_orientation": "portrait",
                "release_version": "3.4.33585",
                "user_agent": "Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 9 Pro Build/QQ3A.200805.001; com.narvii.amino.master/3.4.33585)"
            },
            "device_user": {
                "country": "US",
                "device": {
                    "architecture": "aarch64",
                    "carrier": {
                        "country_code": 255,
                        "name": "Vodafone",
                        "network_code": 0
                    },
                    "is_phone": True,
                    "model": "GT-S5360",
                    "model_type": "Samsung",
                    "operating_system": "android",
                    "operating_system_version": "29",
                    "screen_size": {
                        "height": 2300,
                        "resolution": 2.625,
                        "width": 1080
                    }
                },
                "do_not_track": False,
                "idfa": "0c26b7c3-4801-4815-a155-50e0e6c27eeb",
                "ip_address": "",
                "locale": "en",
                "timezone": {
                    "location": "Asia/Seoul",
                    "offset": "GMT+02:00"
                },
                "volume_enabled": True
            },
            "session_id": "7fe1956a-6184-4b59-8682-04ff31e24bc0",
            "date_created": time.time()
        }

    @property
    def headers(self):
        return {
            "cookies": "__cfduid=d0c98f07df2594b5f4aad802942cae1f01619569096",
            "authorization": "Basic NWJiNTM0OWUxYzlkNDQwMDA2NzUwNjgwOmM0ZDJmYmIxLTVlYjItNDM5MC05MDk3LTkxZjlmMjQ5NDI4OA==",
            "X-Tapdaq-SDK-Version": "android-sdk_7.1.1",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 9 Pro Build/QQ3A.200805.001; com.narvii.amino.master/3.4.33585)"
        }
