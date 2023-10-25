

from src.utils.http_request import AioRequests
import aiofiles
import httpx
import hashlib
import aiohttp
import os

from typing import Any, Iterable, Optional

from aiohttp import FormData as BaseFormData
from aiohttp.multipart import MultipartWriter






description = "搜索galgame作品!" + "\n" "支持的指令:" + "\n" " - 搜gal <图片>"

sv = Service("gal_search", description, enable_default=True)
galgame = sv.on_command("搜gal", aliases={"gal搜索"}, only_group=False)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
}
async  def download_img(url):
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            fileName = hashlib.sha256(url.encode('utf-8')).hexdigest()+'.jpg'
            async with aiofiles.open(fileName, 'wb') as afp:
                await afp.write(await response.content.read())
                
                return fileName

async def get_gal_result(image_url):

    files = {
        'image': open(await download_img(image_url), 'rb')
    }

    url="https://aiapiv2.animedb.cn/ai/api/detect?model=game_model_kirakira&force_one={1}"
    #async with aiohttp.ClientSession() as session:
    async with httpx.AsyncClient() as client: 
        gallist=await client.post(url,data=None, files=files)
        
    return  gallist

@galgame.handle()
async def _(event: MessageEvent, state: T_State):
    if event.get_message(state) or event.reply is not None:
        state["image_urls"] = event.message or event.reply.message

@galgame.got("image_urls", prompt="请发送图片")
async def _(event: MessageEvent):
    image_urls = extract_image_url(event)
    if not image_urls:
        await galgame.finish("没有找到图, 请检查图片是否成功发送~")
    print(image_urls)
    for url in image_urls:
        gallist=await get_gal_result(url)
        gallist=eval(gallist._content)

        if gallist['data']==[] or gallist['code']==-1:
            await galgame.send('未找到gal')
        else:
            gallist=gallist['data'][0]['char']
            msg=""
            for i in range(len(gallist)):
                gal=gallist[i]
                if i>2:
                    break
                msg+=f"角色：{gal['name']}   作品:{gal['cartoonname']} 评分: {gal['acc']} \n"
            await galgame.send(f"搜到以下结果：\n{msg}")
           