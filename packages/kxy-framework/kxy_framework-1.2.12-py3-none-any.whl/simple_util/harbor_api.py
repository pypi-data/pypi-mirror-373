import requests
import base64

class HarborApi():
    def __init__(self,host,username,password):
        # 构建Basic Auth字符串
        auth = username + ":" + password
        encoded = base64.b64encode(auth.encode('utf8'))
        auth = f"Basic {encoded.decode()}"
        
        self.host=host
        self.cookie=self.get_cookie()
        # 设置Header
        self.headers = {
            'accept': 'application/json',
            "authorization": auth,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            # 'Accept':"*"            
            # "X-Harbor-CSRF-Token": "aT4anP6upD4ozdzlT9JdKt9PBOfbLrEk9Be5MnogwUzBml7ufDpgLwVIlbeLPveRDLk3AgfXcApsQHicIyUgYg=="
        }
        
        
        self.token=self.get_token()
        self.headers['X-Harbor-CSRF-Token']=self.token

        self.host_api=f'https://{host}/api/v2.0'
    def get_cookie(self):
        response = requests.get(f"https://{self.host}/c/login")
        csrf_cookie = response.cookies.get_dict()
        # headers = {'X-Harbor-CSRF-Token': csrf_cookie['_gorilla_csrf']}
        return csrf_cookie
    
    def get_token(self):
        url=f'https://{self.host}/c/api/v2.0/token'
        response = requests.get(url, headers=self.headers,cookies=self.cookie)
        return response.headers['X-Harbor-Csrf-Token']
        
    def exist_porject(self,projectName):
        url=f'{self.host_api}/projects/{projectName}'
        response = requests.get(url, headers=self.headers)
        return response.json()
        
    def create_porject(self,projectName):
        if self.exist_porject(projectName).get('errors',None) is None:
            return
        url=f'{self.host_api}/projects'
        # Harbor API URL
        
        # 命名空间信息
        project = {
            "project_name": projectName, 
            "metadata": {
                "public": "false"
            }
        }
        # 发送GET请求查询命名空间
        response = requests.post(url, headers=self.headers,json=project)
        if response.reason=='Created':
            return True
        return False
    def delete_image(self,project,imagename,tag):
        url=f'{self.host_api}/projects/{project}/repositories/{imagename}/artifacts/{tag}'
        response = requests.delete(url, headers=self.headers)
        return response.reason
        