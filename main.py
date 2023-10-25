
from os import path

import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter

nonebot.init()

app = nonebot.get_asgi()
driver = nonebot.get_driver()
driver.register_adapter(OneBotV11Adapter)

config = driver.config
nonebot.load_plugins("src/mimi")
#if modules := config.enable_modules:
#    for module in modules:
#        module = path.join(path.dirname(__file__), "src", "mimi", module)
#        nonebot.load_plugins(module)

if __name__ == "__main__":
    nonebot.run()

