#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time : 2023/11/17 13:55 
# @Author : JY
"""
向飞书机器人发送消息
https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot#355ec8c0
"""
import requests
import json
from jyhelper import common,timeHelper


class feishuRobot:
    def __init__(self, webhook):
        self.webhook = webhook

    # 发送文本消息
    def sendTextMessage(self, msg, atAll=False):
        msg = str(msg)
        # 发送文本
        if atAll:
            msg += '<at user_id="all">所有人</at>'
        data = {"msg_type": "text", "content": {"text": msg}}
        return self._doSend(data)

    # 发送富文本消息
    # 富文本消息是指包含文本、超链接、图标等多种文本样式的复合文本信息。
    """
    msgContent格式一：(text 默认可以不用写)
    [
        ['text 执行成功1：', 'a 请查看1 www.xxx.com', 'img xxxxxx'],
        ['text 执行成功2：', 'a 请查看2 www.xxx.com', 'img xxxxxx']
    ]
    msgContent格式二：
    ['text 执行成功2：', 'a 请查看2 www.xxx.com', 'img xxxxxx']
    msgContent格式三个：
    ['aaaa','bbbb']
    img后面跟的是图片Key。可通过 上传图片 接口获取 image_key
    """

    def sendPostMessage(self, msgTitle=None, msgContent=None, atAll=False):
        """
        msgContent = [
                        {
                            "tag": "text",
                            "text": "项目有更新: "
                        },{
                            "tag": "a",
                            "text": "请查看",
                            "href": "http://www.example.com/"
                        },{
                            "tag": "img",
                            "image_key": "d640eeea-4d2f-4cb3-88d8-c96fa5****"
                        },
                    ]
        """
        # 只能是list格式的数据
        if not isinstance(msgContent, list):
            return False
        if msgContent.__len__() == 0:
            return False
        # msgContent = [['text 执行成功：','a 请查看 www.xxx.com','img xxxxxx']]
        for i in range(msgContent.__len__()):
            if not isinstance(msgContent[i], list):
                msgContent[i] = [msgContent[i]]
            for j in range(msgContent[i].__len__()):
                org = str(msgContent[i][j])
                if org[:5] == 'text ':
                    org = org[5:]
                    new = {
                        "tag": "text",
                        "text": org
                    }
                elif org[:4] == 'img ':
                    org = org[4:]
                    new = {
                        "tag": "img",
                        "image_key": org
                    }
                elif org[:2] == 'a ':
                    org = org[2:]
                    orgList = org.split(' ')
                    new = {
                        "tag": "a",
                        "text": org.replace(' ' + orgList[-1], ''),
                        "href": orgList[-1]
                    }
                else:
                    # 啥标签都没有，默认认为是text
                    new = {
                        "tag": "text",
                        "text": org
                    }
                msgContent[i][j] = new

        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": str(msgTitle) if msgTitle is not None else "",
                        "content": msgContent
                        # [
                        #     [
                        #         {
                        #             "tag": "text",
                        #             "text": "项目有更新: "
                        #         }, {
                        #             "tag": "a",
                        #             "text": "请查看",
                        #             "href": "http://www.example.com/"
                        #         }
                        #     ]
                        # ]
                    }
                }
            }
        }
        if atAll:
            data['content']['post']['zh_cn']['content'].append([{"tag": "at", "user_id": "all"}])

        return self._doSend(data)

    def _doSend(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        result = requests.post(url=self.webhook, headers=headers, json=data)
        result_text = json.loads(result.text)
        if result.status_code == 200 and result_text['code'] == 0:
            common.print('飞书消息',result_text['msg'])
            return True
        else:
            # 如果因为 飞书消息 error status_code 400 text {"code":9499,"msg":"too many request","data":{}}重新发送一次
            if result.status_code == 400 and result_text['code'] == 9499:
                # 等待几秒后重发
                timeHelper.sleep(common.getRandomInt(1,10))
                nextResult = requests.post(url=self.webhook, headers=headers, json=data)
                nextResult_text = json.loads(nextResult.text)
                if nextResult.status_code == 200 and nextResult_text['code'] == 0:
                    common.print('飞书消息', nextResult_text['msg'],'重发后的结果')
                    return True
                else:
                    common.print('飞书消息', 'error', 'status_code', nextResult.status_code, 'text', nextResult.text,'重发后的结果')
                    return False

            common.print('飞书消息','error', 'status_code', result.status_code, 'text', result.text)
            return False


if __name__ == '__main__':
    robotIns = feishuRobot(webhook='xxx')
    # robotIns.sendTextMessage('执行成功',atAll=True)
    # robotIns.sendPostMessage('预警通知', msgContent=[
    #     ['text 执行成功1：', 'a 请查看1 www.xxx.com'],
    #     ['text 执行成功2：', 'a 请查看2 www.xxx.com','text  结束']
    # ], atAll=False)
