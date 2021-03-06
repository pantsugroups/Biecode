# -*- coding: utf-8 -*-
import importlib
import json
import os
import sys

import telegram
from * import config
from coolq import CoolQHttpAPI
from flask import Flask, request

app = Flask(__name__)
api = CoolQHttpAPI(COOLQ_PUAH_URL, access_token=ASSESS_TOKEN)
bot = telegram.Bot(token=TG_TOKEN)
sys.path.append('plugin')
PLUGIN_CENTER = {}
Initialization = False
class PluginException(Exception):
    def __init__(self,err='插件错误'):
        print("%s\n",err)
        Exception.__init__(self,err)

def Plugin_Load():
    if not os.path.isdir("plugin/"):
        os.mkdir("plugin/")
    files = os.listdir("plugin/")
    for i in files:
        if i[i.rfind("."):] == ".py":
            register,plugins = importlib.import_module(i.replace(".py","")).Initialization()

            if type(plugins) != dict:
                raise PluginException("初始化插件失败")
            if "name" not in plugins or "register_trigger" not in plugins or "register_type" not in plugins or "callback" not in plugins:
                raise PluginException("初始化插件失败")
            PLUGIN_CENTER[register] = plugins
    Initialization = True
            
@app.route("/"+TG_TOKEN, methods=["POST"])
def tg_event():

    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message is None:
        return "Show me your TOKEN please!"
    if Initialization:
        data = update.message.to_dict()
        COMMAND = data["text"].split(" ")[0] 
        if "text" in data and COMMAND in PLUGIN_CENTER:
            if PLUGIN_CENTER["register_type"] == "tg" and PLUGIN_CENTER[COMMAND]["register_trigger"] != "":
                if data["chat"]["type"] == "group":
                    if ["chat"]["id"] in PLUGIN_CENTER[COMMAND]["register_target"]["tg"]["groups"] or PLUGIN_CENTER[COMMAND]["register_target"]["tg"]["groups"] == "all":
                        PLUGIN_CENTER[COMMAND][callback]["qq"](qq_handle=api,tg_handle=bot,data=data)
                else:
                    #处理成员消息
                    pass

    return ""

@app.route(COOLQ_RECVER_URL[COOLQ_RECVER_URL.rfind("/"):], methods=["POST"])
def qq_event():
    if Initialization:
        data = json.loads(request.data.decode("utf-8"))
        # 遍历插件加载消息
        for i in PLUGIN_CENTER["register_trigger"]:
            if PLUGIN_CENTER["register_trigger"] == "":
                PLUGIN_CENTER[COMMAND][callback]["qq"](qq_handle=api,tg_handle=bot,data=data)

        COMMAND = data["message"].split(" ")[0]
        if COMMAND in PLUGIN_CENTER:
            if PLUGIN_CENTER[COMMAND]["register_type"] == "qq" and PLUGIN_CENTER[COMMAND]["register_trigger"] != "":
                if data["message_type"] == "group":
                    if PLUGIN_CENTER[COMMAND]["register_target"]["qq"]["group"] == "all" or data["group_id"] in PLUGIN_CENTER[COMMAND]["register_target"]["qq"]["group"]:
                        PLUGIN_CENTER[COMMAND][callback]["qq"](qq_handle=api,tg_handle=bot,data=data)
                        
                else:
                    # if data["qq_id"] in COMMAND["register_target"]["qq"]["member"]:
                    # 我没看过成员字段是啥，先放着
                    pass
    return ""

@app.route("/control")
def control():
    if request.args.get("status") == "start":
        bot.set_webhook(TG_WEBHOOK)
        Plugin_Load()
        return ""
    elif request.args.get("status") == "stop":
        # 停止bot
        return ""

    # 返回状态
    return ""

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8088)
