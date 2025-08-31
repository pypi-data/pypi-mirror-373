import json
import os
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from requests_toolbelt import MultipartEncoder
import requests


def create_text(text: str):
    return {"tag": "text", "text": text}


def create_image(image_key: str):
    return {"tag": "img", "image_key": image_key}


def create_link(text: str, href: str):
    return {"tag": "a", "href": href, "text": text}
def create_at(user_id: str):
    return {"tag": "at", "user_id": user_id}

class FeishuBot:
    def __init__(self, receive_id_type='email', receive_id='3306601284@qq.com'):
        self.app_id = os.environ.get('FEISHU_APP_ID')
        self.app_secret = os.environ.get('FEISHU_APP_SECRET')
        self.receive_id_type = receive_id_type  # 接受者id类型
        self.receive_id = receive_id  # 接受者id
        if not self.app_id or not self.app_secret:
            raise ValueError('FEISHU_APP_ID and FEISHU_APP_SECRET must be set')
        # 创建client
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

    def _get_tenant_access_token(self):
        """
        获取tenant_access_token
        :return:
        """
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        if response_data.get("code") == 0:
            return response_data.get("tenant_access_token")
        else:
            raise Exception(f"Failed to get tenant_access_token: {response_data}")

    def upload_image(self, image_path: str, image_type: str = "message"):
        """
        上传图片
        :param image_path: 图片路径
        :param image_type: 图片类型，message表示用于消息中的图片资源，avatar表示用于头像的图片资源
        :return: image_key
        """
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        tenant_access_token = self._get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {tenant_access_token}"
        }
        form = {
            "image_type": image_type,
            "image": (open(image_path, "rb"))
        }
        multi_form = MultipartEncoder(form)
        headers["Content-Type"] = multi_form.content_type
        response = requests.post(url, headers=headers, data=multi_form)
        response_data = response.json()
        if response_data.get("code") == 0:
            return response_data.get("data").get("image_key")
        else:
            raise Exception(f"Failed to upload image: {response_data}")

    def upload_file(self, file_path: str, file_type: str = "stream"):
        """
        上传文件
        :param file_path: 文件路径
        :param file_type: 文件类型
        :return: file_key
        """
        url = "https://open.feishu.cn/open-apis/im/v1/files"
        tenant_access_token = self._get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {tenant_access_token}"
        }
        form = {
            "file_type": file_type,
            "file": (open(file_path, "rb"))
        }
        multi_form = MultipartEncoder(form)
        headers["Content-Type"] = multi_form.content_type
        response = requests.post(url, headers=headers, data=multi_form)
        response_data = response.json()
        if response_data.get("code") == 0:
            return response_data.get("data").get("file_key")
        else:
            raise Exception(f"Failed to upload file: {response_data}")

    def send_text(self, text: str):
        """
        发送文本消息
        :param text: 文本内容
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("text")
                          .content(json.dumps({"text": text}))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        return response

    def send_post(self, post_title: str, post_content: list):
        """
        发送富文本消息
        :param post_title: 富文本标题
        :param post_content: 富文本内容
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("post")
                          .content(json.dumps({
            "zh_cn": {
                "title": post_title,
                "content": post_content
            }
        }))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        return response

    def send_image(self, image_key: str):
        """
        发送图片消息
        :param image_key: 图片key
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("image")
                          .content(json.dumps({"image_key": image_key}))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        return response

    def send_file(self, file_key: str):
        """
        发送文件消息
        :param file_key: 文件key
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("file")
                          .content(json.dumps({"file_key": file_key}))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        return response

    def send_interactive_card(self, card_content: dict):
        """
        发送交互式卡片消息
        :param card_content: 卡片内容
        :return:
        """
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(self.receive_id_type) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(self.receive_id)
                          .msg_type("interactive")
                          .content(json.dumps(card_content))
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        return response


if __name__ == "__main__":
    fbot = FeishuBot()
    # 发送文本消息
    # fbot.send_text("Hello, World!")

    # 发送富文本消息
    image_key = fbot.upload_image(r"C:\Users\Arc\Downloads\20210208142819.png")
    post_content = [
        [create_text("第一行文本 "), create_link("超链接", "http://www.feishu.cn")],
        [create_text("第二行文本 "), create_image(image_key)],
    ]
    fbot.send_post("测试", post_content)


    # 上传并发送文件
    # file_key = fbot.upload_file("path/to/file.pdf")
    # fbot.send_file(file_key)
