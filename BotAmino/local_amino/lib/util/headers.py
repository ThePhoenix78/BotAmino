from .device import DeviceGenerator

sid = None
web = None

class Headers:
    def __init__(self, data = None, type = None, deviceId: str = "2271017D5F917B37DAC9C325B10542BC9B63109292D882729D1813D5355404380E2F1A699A34629C10", sig: str = None):
        if deviceId:
            dev = DeviceGenerator(deviceId=deviceId)
        else:
            dev = DeviceGenerator()
        headers = {
            "NDCDEVICEID": dev.device_id,
            "NDC-MSG-SIG": dev.device_id_sig,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": dev.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        s_headers = {"NDCDEVICEID": dev.device_id}

        web_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "x-requested-with": "xmlhttprequest"
        }

        if data: headers["Content-Length"] = str(len(data))
        if sid:
            headers["NDCAUTH"] = f"sid={sid}"
            web_headers["cookie"] = f"sid={sid}"
            s_headers["NDCAUTH"] = f"sid={sid}"
        if type: headers["Content-Type"] = type
        #if sig: headers["NDC-MSG-SIG"] = sig
        self.headers = headers
        self.s_headers = s_headers
        self.web_headers = web_headers
        #print(sid)
