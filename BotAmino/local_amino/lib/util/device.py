class DeviceGenerator:
    def __init__(self, deviceId=None):
        if deviceId:
            self.device_id = deviceId
        else:
            self.device_id = "420698494B7D696610BAE8F654041DCAFE1EB92AC77D2478450774731789ABB3F0DDD5446FBFEDBF9C"

        self.user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)"
