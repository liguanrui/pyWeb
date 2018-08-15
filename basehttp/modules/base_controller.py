
class BaseController():
 
    def __init__(self, urlInfo, postData):
        
        self.urlInfo = urlInfo
        self.postData = postData

    def echoError(self, code, msg):
        return {
            "ret": code,
            "msg": msg,
        }

    def echoSuc(self, msg, data):
        return {
            "ret": 0,
            "msg": msg,
            "data": data
        }
