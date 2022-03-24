class DeviceGenerator:
    def __init__(self, deviceId=None):
        if deviceId:
            self.device_id = deviceId
        else:
            self.device_id = "42953964987F7797F3664DEC074951F8DCE0E0789881766A1D073CD4D85FE31BC52D9E6C28216B512D"

        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
