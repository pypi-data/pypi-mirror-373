import requests
import json

class CKQuery():
    def __init__(self,url,token):
        self.url = url
        self.token = token
        self.header = {
            'ezr-sys-code': 'ezr_log_stats',
            'ezr-ck-token': token,
            'Content-Type': 'application/json'
        }
    def query(self,sql):
        response = requests.request("POST", self.url, headers=self.header, data=sql)
        return response