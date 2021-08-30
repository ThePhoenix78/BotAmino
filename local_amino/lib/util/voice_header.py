from amino.lib.util import device


class Headers:
    def __init__(self, data = None):
        headers = {
            "Accept-Language": "en-US",
            "Content-Type": "application/json",
            "User-Agent": "Amino/45725 CFNetwork/1126 Darwin/19.5.0",
            "Host": "rt.applovin.com",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "Keep-Alive",
            "Accept": "*/*"
        }

        if data: headers["Content-Length"] = str(len(data))
        self.headers = headers
