import httpx
from kxy.framework.context import trace_id, session_id, user_id, access_token
from kxy.framework.base_config import BaseConfig
class HttpClient:
    @staticmethod
    def get_default_headers():
        headers = {
            'x-trace-id': trace_id.get(),
        }
        
        # 只有当access_token存在且非空时才添加Authorization头部
        token = access_token.get()
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return headers
        
    
    @classmethod
    async def request(cls, method, url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers.update(cls.get_default_headers())
        BaseConfig.AppLogger.refresh_time()
        try:
            async with httpx.AsyncClient() as client:
                result = await client.request(method, url, headers=headers, **kwargs)
                BaseConfig.AppLogger.info(f'{method} {url} success {result.status_code}','http')
                return result
        except Exception as ex:
            BaseConfig.AppLogger.error(f'{method} {url} error:{ex}','http')
            raise ex
            
            
    
    @classmethod
    async def get(cls, url, **kwargs):
        return await cls.request('GET', url, **kwargs)
    
    @classmethod
    async def post(cls, url, **kwargs):
        return await cls.request('POST', url, **kwargs)
    
    @classmethod
    async def put(cls, url, **kwargs):
        return await cls.request('PUT', url, **kwargs)
    
    @classmethod
    async def delete(cls, url, **kwargs):
        return await cls.request('DELETE', url, **kwargs)
    