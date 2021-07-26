import json
from .helpers import generate_device_info

class DeviceGenerator:
    def __init__(self):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["device_id"]
                self.device_id_sig = data["device_id_sig"]

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = generate_device_info()
            with open("device.json", "w") as stream:
                json.dump(device, stream, indent=4)

            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]
                self.device_id = data["device_id"]
                self.device_id_sig = data["device_id_sig"]
