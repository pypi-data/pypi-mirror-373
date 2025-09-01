import random
import sys
import requests
import json
from mignonFramework import ConfigManager, Logger, inject, QueueIter, target
import datetime
import time

config = ConfigManager()
log = Logger(True)

# ======================Config============================
que = QueueIter(config)


# Dl注入类, 需自己配置
@target(que, "pageNo", 1)
@inject(config)
class Data:
    token: str
    pageNo: int
    pageSize: int


data = config.getInstance(Data)

# ======================Request============================
# 请求头
header = {
    "Authorization": data.token,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
}

# 请求体
json_data = {
    "useScroll": True,
    "newValue": False
}

urls = "https://xxxx/.com"

# ==========================================================


# 预检请求, 可以请求第0页拿total
@log
def preCheckRequest(searchStatement):
    global header, json_data, urls
    headers = header.copy()
    json_datas = json_data.copy()
    response = requests.post(
        urls,
        headers=headers,
        json=json_datas
    )
    if response.status_code == 200:
        res = response
        total = 0
        return total
    raise Exception(f"返回内容不正确:  {response}: {response.text}")

def callBack(que: QueueIter):
    global data
    data.pageNo = que.get_current_index() + 1


# 正式请求, 需获取pageSize, pageNo等
@log
def requestTo():
    global header, json_data, urls, data
    headers = header.copy()
    json_datas = json_data.copy()
    status = 0
    while True:
        try:
            response = None
            response = requests.post(
                urls,
                headers=headers,
                json=json_datas
            )
            if response.status_code == 200:
                res = response
                return True
        except Exception as e:
            status += 1
            time.sleep(status * 0.4)
            print(response)
            if status >= 17:
                raise e

# 主控制服务
@log
def masterControlService():
    global data, que, que2
    total = preCheckRequest()
    # 逻辑控制器
    que.pages = range(0, 1)
    que2.pages = range(0, 1)
    while que2.hasNext():
        que2Next = next(que2)
        while que.hasNext():
            nowPage = next(que)
            if requestTo():
                que.call()
        que2.call()


