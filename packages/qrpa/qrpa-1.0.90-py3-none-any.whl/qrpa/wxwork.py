# -*- coding: utf-8 -*-
"""
-------------------------------------------------
@version    : v1.0
@author     : qsir
@contact    : qsir@vxnote.com
@software   : PyCharm
@filename   : wxwork.py
@create time: 2025/08/03 
@modify time: 2025/08/03 
@describe   : 
-------------------------------------------------
"""
import json
import os
import hashlib
import base64
import requests
from requests_toolbelt import MultipartEncoder
from datetime import datetime

# 通过企微群机器人发送消息
class WxWorkBot:
    def __init__(self, key):
        self.key = key

    def upload_media(self, filepath):
        """
        上传临时素材，给企微群里发文件消息时需要先将文件上传至企微临时素材中
        :param filepath:
        :return: 临时素材的media_id
        """
        try:
            headers = {
                'Content-Type': 'multipart/form-data',
            }
            with open(filepath, 'rb') as f:
                files = {
                    'media': (os.path.basename(filepath), f.read())
                }
                response = requests.post(
                    f'https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={self.key}&type=file',
                    headers=headers, files=files)
                response_text = json.loads(response.text)
                if str(response_text.get('errcode')) != '0':
                    raise Exception(response_text)
                if response.status_code == 200:
                    result = json.loads(response.text)
                    return result['media_id']
                else:
                    print("HTTP Error:", response.status_code)
                    return None
        except Exception as err:
            raise Exception("upload_media error", err)

    def send_file(self, file_path):
        if not os.path.exists(file_path):
            print('文件不存在: ', file_path)
            return
        """
        发送文件到群里
        :param file_path:
        :return:
        """
        media_id = self.upload_media(file_path)
        data = {
            "msgtype": "file",
            "file"   : {
                "media_id": media_id
            }
        }
        return self.send_msg(data)

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        """
        发送文本消息
        :param content:
        :param mentioned_list: 需要@的人userid
        :param mentioned_mobile_list: 需要@的人手机号
        :return:
        """
        data = {
            "msgtype": "text",
            "text"   : {
                "content": content
            }
        }
        if mentioned_list is not None and mentioned_list:
            data['text'].update({"mentioned_list": mentioned_list})
        if mentioned_mobile_list is not None and mentioned_mobile_list:
            data['text'].update({"mentioned_mobile_list": mentioned_mobile_list})

        self.send_msg(data)

    def send_markdown(self, content):
        """
        发送Markdown消息
        :param content:
        :return:
        """
        data = {
            "msgtype" : "markdown",
            "markdown": {
                "content": content
            }
        }
        self.send_msg(data)

    def send_notify(self, title, sub_title_list, data_list):
        """
        发送Markdown消息
        :param content:
        :return:
        """

        current_date = datetime.now().strftime("%Y-%m-%d")
        header = f"{current_date} {title}\n\n"

        arr_color = ['warning', 'info', 'warning']
        arr_sub_header = [f"<font color='{arr_color[index]}'>{title}</font>" for index, title in enumerate(sub_title_list)]
        sub_header = "\t".join(arr_sub_header) + "\n\n"

        # 获取每个元素的行索引和列索引
        arr_content = [
            [
                f'{value}' if col_idx == 0 else f"<font color='{arr_color[col_idx - 1]}'>{value}</font>"
                for col_idx, value in enumerate(row)
            ]  # 每行的元素组成一个子列表
            for row_idx, row in enumerate(data_list)  # 外层循环控制行
        ]
        # 将二维数组转换为字符串
        content = "\n".join(
            # 对每行的元素列表使用 join()，用 \t 连接
            "\t".join(row) for row in arr_content
        )

        data = {
            "msgtype" : "markdown",
            "markdown": {
                "content": header + sub_header + content
            }
        }
        self.send_msg(data)

    def send_img(self, img_path):
        """
        发送图片消息
        图片（base64编码前）最大不能超过2M，支持JPG,PNG格式
        :param img_path:
        :return:
        """
        data = {
            "msgtype": "image",
            "image"  : {
                "base64": self.img_to_base64(img_path),
                "md5"   : self.img_to_md5(img_path)
            }
        }
        self.send_msg(data)

    def send_news(self, title, description, url, picurl):
        """
        发送图文消息
        :param title: 标题
        :param description: 描述
        :param url: 跳转URL
        :param picurl: 图文图片地址
        :return:
        """
        data = {
            "msgtype": "news",
            "news"   : {
                "articles": [
                    {
                        "title"      : title,
                        "description": description,
                        "url"        : url,
                        "picurl"     : picurl
                    }
                ]
            }
        }
        self.send_msg(data)

    def send_msg(self, data):
        """
        发送机器人通用消息到企微群
        :param data: 消息内容json数据
        :return:
        """
        try:
            header = {
                "Content-Type": "application/json"
            }
            response = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.key}", headers=header, data=json.dumps(data))
            response_text = json.loads(response.text)
            if str(response_text.get('errcode')) != '0':
                raise Exception(response_text)
            if response.status_code == 200:
                result = json.loads(response.text)
                return result
            else:
                print("HTTP Error:", response.status_code)
                return None
        except Exception as err:
            raise Exception("Send Chat Message error", err)

    def img_to_md5(self, img_path):
        # 读取图片文件并计算MD5值
        with open(img_path, 'rb') as image_file:
            image_data = image_file.read()
            return hashlib.md5(image_data).hexdigest()

    def img_to_base64(self, img_path):
        # 读取图片文件并转换为Base64编码
        with open(img_path, 'rb') as image_file:
            image_data = image_file.read()
            return base64.b64encode(image_data).decode('utf-8')

# 通过企微应用发送消息
class WxWorkAppBot:
    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = self._getToken()

    def _getToken(self):
        try:
            if all([self.corpid, self.corpsecret]):
                url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                    corpid=self.corpid, corpsecret=self.corpsecret)
                response = requests.get(url)
                if response.status_code == 200:
                    result = json.loads(response.text)
                    return result['access_token']
                else:
                    print("HTTP Error:", response.status_code)
                    return None
        except Exception as err:
            raise Exception("get WeChat access Token error", err)

    def _send_msg(self, data):
        self._check_token()
        try:
            send_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
                access_token=self.access_token)
            response = requests.post(send_url, json.dumps(data))
            if response.status_code == 200:
                result = json.loads(response.text)
                return result
            else:
                print("HTTP Error:", response.status_code)
                return None
        except Exception as err:
            raise Exception("send WeChat Message error", err)

    def _check_token(self):
        if self.access_token is None:
            self._getToken()

    def send_msg(self, data):
        return self._send_msg(data)

    def upload_media(self, filetype, filepath, filename):
        """
        上传临时素材到企微并获取media_id
        :param filetype: 图片（image）、语音（voice）、视频（video），普通文件（file）
        :param filepath:
        :param filename:
        :return: media_id
        """
        try:
            self._check_token()
            post_file_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type={filetype}".format(
                filetype=filetype,
                access_token=self.access_token)

            m = MultipartEncoder(
                fields={filename: (filename, open(filepath + filename, 'rb'), 'text/plain')},
            )
            response = requests.post(url=post_file_url, data=m, headers={'Content-Type': m.content_type})
            if response.status_code == 200:
                result = json.loads(response.text)
                return result['media_id']
            else:
                print("HTTP Error:", response.status_code)
                return None
        except Exception as err:
            raise Exception("upload media error", err)

    def get_media(self, media_id):
        """
        获取临时素材
        :param media_id:
        :return: 返回二进制形式
        """
        try:
            self._check_token()
            url = "https://qyapi.weixin.qq.com/cgi-bin/media/get"
            params = {
                "access_token": self.access_token,
                "media_id"    : media_id
            }
            response = requests.get(url=url, params=params)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type')
                if content_type == 'application/json':
                    response_data = json.loads(response.text)
                    print("Error:", response_data.get("errmsg"))
                    return None
                else:
                    return response.content
            else:
                print("HTTP Error:", response.status_code)
                return None
        except Exception as err:
            raise Exception("get media error", err)
