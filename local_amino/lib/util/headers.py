from amino.lib.util import device

sid = None

class Headers:
    def __init__(self, data = None, type = None, deviceId: str = "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10", sig: str = None):
        if deviceId:
            dev = device.DeviceGenerator(deviceId=deviceId)
        else:
            dev = device.DeviceGenerator()

        headers = {
            "NDCDEVICEID": "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10",
            "NDC-MSG-SIG": dev.device_id_sig,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid: headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        #if sig: headers["NDC-MSG-SIG"] = sig
        self.headers = headers
