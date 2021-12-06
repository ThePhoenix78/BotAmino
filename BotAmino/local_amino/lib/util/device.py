class DeviceGenerator:
    def __init__(self, deviceId=None):
        if deviceId:
            self.device_id = deviceId
        else:
            self.device_id = "17CDC1AC5D08AC01AD9FF9C9FE7B56030C20A760FCE9FBCC68E6CF2C35E469850923E87133407BC3B0"

        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
