class DeviceGenerator:
    def __init__(self, deviceId=None):
        if deviceId:
            self.device_id = deviceId
        else:
            self.device_id = "32255726EEA11E60ACD268CA4DD36C8E6517144FCD24D7A53B144DE77B57980B26386188009D2BDEDE"

        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
