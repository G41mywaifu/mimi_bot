import httpx
import aiofiles
import hashlib
from nonebot import get_driver

#driver = get_driver()

#http_proxy = driver.config.http_proxy
http_proxy=None
class AioRequst:
    proxy=http_proxy
    
    @classmethod
    async def get(
        cls,
        url:str,
        *,
        data_=None,
        header=None,
        timeout_=20,
        params=None,
        verify_=False,
        **kwargs,
    ):
        async with httpx.AsyncClient(proxies=cls.proxy, verify=verify_) as client:
            return await client.get(
                url,
                #data=data_,
                headers=header,
                params=params,
                timeout=timeout_,
                **kwargs,
                )


    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data= None,
        files = None,
        verify = True,
        proxy = None,
        json = None,
        headers= None,
        params=None,
        timeout = 20,
        **kwargs,
    ):
        async with httpx.AsyncClient(proxies=proxy, verify=verify) as client:
            return await client.post(
                url,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs
            )

    @classmethod   
    async  def download_img(vls,url):
        try:
            async with httpx.AsyncClient() as client:
                response=await client.get(url)
                fileName = hashlib.sha256(url.encode('utf-8')).hexdigest()+'.jpg'
                async with aiofiles.open(fileName, 'wb') as afp:
                    await afp.write(response.content)
        except:
            return '下载失败'
        return fileName

    