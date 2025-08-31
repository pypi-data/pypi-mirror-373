import logging

from kxy.framework.base_config import BaseConfig
class Config(BaseConfig):
    AppName = 'kxy.sso.api'
    AppSign = 'sso'
    SystemCode = 'CRM'
    LOG_LEVEL = logging.INFO
    ENV_NAME = 'test'
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT=6379
    REDIS_PASSWORD=None
    # 假设JWT的密钥和算法
    JWT_SECRET_KEY = ""
    JWT_ALGORITHM = "xxx"
    wx_appid=''
    wx_secret=''
    AUTH_URL=''
    AutoAddModel = False
    ignor_auth=1
    WXTOKEN_ASYNC_URL = ''
    UPLOAD_FILEPATH='uploadfiles'
    BussinessLog = False
    SSO_URL=''
    

class DevConfig(Config):
    mysql_url = 'mysql+aiomysql://myfriend:123456@192.168.15.172:3306/kxy-open?autocommit=False'
    # normal_mysql_url = 'mysql+pymysql://myfriend:123456@192.168.15.172:3306/ant_demo?autocommit=True'
    AUTH_URL = ''
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT=6379
    REDIS_PASSWORD=None
    LOG_LEVEL = logging.DEBUG
    ENV_NAME = 'dev'
    WXTOKEN_ASYNC_URL=''
    AutoAddModel = True
    
config = DevConfig()