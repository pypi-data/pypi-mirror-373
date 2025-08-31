import httpx
from kxy.framework.context import trace_id, session_id, user_id, access_token

class HttpClient:
    @staticmethod
    def get_default_headers():
        return {
            'X-Trace-ID': trace_id.get(),
            'Authorization': f'Bearer {access_token.get()}'
        }
    
    @classmethod
    async def request(cls, method, url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers.update(cls.get_default_headers())
        
        async with httpx.AsyncClient() as client:
            return await client.request(method, url, headers=headers, **kwargs)
    
    @classmethod
    async def get(cls, url, **kwargs):
        return await cls.request('GET', url, **kwargs)
    
    @classmethod
    async def post(cls, url, **kwargs):
        return await cls.request('POST', url, **kwargs)