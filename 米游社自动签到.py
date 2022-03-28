# -*- coding: utf-8 -*-
import json
import requests
import time
import hashlib
import string
import random
import logging

#根据抓包信息修改以下变量的值，这些变量用于构建请求头
#app_version不能照着抓包信息填写 因为和计算DS码的函数挂钩 
app_version = "2.3.0"

act_id = "e202009291139501"
region = "cn_gf01"
uid = "你的原神游戏UID"
cookie = "你的米游社账号cookie"
device_id = "E92C2F3D-FF25-4BCD-A6E6-BFB9CA949284"
User_Agent = "Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.21.2"

#创建一个字典对象，用于构建请求头
headers = {}

# 设置logging对象
logging.basicConfig(filename='./自动签到日志.log',format='[%(filename)s-%(levelname)s:%(message)s]', level = logging.INFO,filemode='a',datefmt='%I:%M:%S %p')
 
def main_handler():
    # 设置请求头
    buildHearders()
    # 签到
    signResult = sign()
    # 游戏信息
    # totalSignDay = getTotalSignDay()["data"]["total_sign_day"]
    # gameInfo = getGameInfo()["data"]["list"][0]
    # signInfo = getSignInfo()["data"]
    # award = signInfo["awards"][totalSignDay - 1]
#     # 推送消息
#     message = '''>{} 
# ##### 游戏昵称：{} 
# ##### 冒险等级：{} 
# ##### 签到结果：{} 
# ##### 签到奖励：{} x {}
# ##### {}月累计签到：**{}** 天'''.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()+28800)), gameInfo["nickname"],
#                                  gameInfo["level"],
#                                  signResult['message'], award['name'], award['cnt'], signInfo["month"],
#                                  totalSignDay)
#     return notify(message)
 
# 构建请求头
def buildHearders():
    #对照着抓到的包进行设置
    headers["Host"] = "api-takumi.mihoyo.com"
    headers["Accept"] = "application/json, text/plain, */*"
    headers["x-rpc-device_id"] = device_id
    headers["x-rpc-client_type"] = "5"
    headers["Accept-Language"] = "zh-cn"
    headers["Accept-Encoding"] = "gzip, deflate, br"
    headers["Content-type"] = "application/json;charset=utf-8" 
    headers["Origin"] = "https://webstatic.mihoyo.com"
    headers["Referer"] = "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id={}&utm_source=bbs&utm_medium=mys&utm_campaign=icon".format(act_id)
    headers["User-Agent"] = User_Agent
    headers["x-rpc-app_version"] = app_version
    #请求头需要DS码，这个东西不是固定的，有一个算法，这里直接用别人给的算法构建出计算DS码的函数并调用
    headers["DS"] = getDS()
    headers["Cookie"] = cookie
    
# 用于构建DS码
def md5(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()
 
 #构建DS码的函数
def getDS():
    # n = 'cx2y9z9a29tfqvr1qsq6c7yz99b5jsqt' # v2.2.0 @Womsxd    
    n = 'h8w582wxwgqvahcdkpvdhbh2w9casgfl' # v2.3.0 web @povsister & @journey-ad    
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5("salt=" + n + "&t=" + i + "&r=" + r)
    return "{},{},{}".format(i, r, c)
 
# 显示日期
def getTime():
    year = time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    day = time.strftime("%d", time.localtime())
    logging.info("{}年{}月{}日".format(year,month,day))
    # print("{}年{}月{}日".format(year,month,day))

# 签到
def sign():
    #指定url
    signUrl = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign"
    #构建请求体
    param = {"act_id": act_id, "region": region, "uid": uid}
    #根据抓包信息知道 要用post请求 带上请求头和请求体
    result = requests.request("POST", signUrl, headers=headers, data=json.dumps(param))
    # 显示日期
    getTime()
    #将发送签到后得到的响应信息取出并从json格式转回字典
    # print(result.content.decode("utf-8"))
    logging.info(result.content.decode("utf-8"))
    return json.loads(result.content)
 
# 微信推送
def notify(message):
    snedKey = "替换方糖通知key，百度搜索：server酱"
    notifyUrl = "http://sc.ftqq.com/{}.send"
    param = {'text': '米游社签到',
             'desp': message}
    notifyResult = requests.request("POST", notifyUrl.format(snedKey), headers={}, data=param, files=[])
    return json.loads(notifyResult.text)

# 获取签到信息
def getSignInfo():
    url = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id={}"
    userInfoResult = requests.get(url.format(act_id), headers=headers)
    return json.loads(userInfoResult.content)
 
 
# 获取签到天数
def getTotalSignDay():
    url = "https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={}&act_id={}&uid={}"
    userInfoResult = requests.get(url.format(region, act_id, uid), headers=headers)
    return json.loads(userInfoResult.content)
 
 
# 获取游戏信息
def getGameInfo():
    url = "https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn"
    userInfoResult = requests.get(url, headers=headers)
    return json.loads(userInfoResult.content)

# 用死循环实现定时任务
if __name__ == "__main__":
    # 第一次运行
    # main_handler()  
    while True:
        now_localtime = time.strftime("%H:%M", time.localtime())
        time.sleep(10)
        if now_localtime == "00:00":
            main_handler()
            time.sleep(61)