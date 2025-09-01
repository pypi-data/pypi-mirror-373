import requests


class WeChatWorkSender:
    def __init__(self, corpid, corpsecret, agentid):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = self.get_access_token()

    def get_access_token(self):
        """获取企业微信的 access_token"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        response = requests.get(url)
        result = response.json()
        if 'access_token' in result:
            return result['access_token']
        else:
            raise Exception(f"Failed to get access token: {result}")

    def upload_media(self, media_type, media_path):
        """上传文件或图片，获取 media_id"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type={media_type}"
        files = {'media': open(media_path, 'rb')}
        response = requests.post(url, files=files)
        result = response.json()
        if 'media_id' in result:
            return result['media_id']
        else:
            raise Exception(f"Failed to upload media: {result}")

    def send_text(self, user_ids, content):
        """发送文本消息（返回完整响应，包含msgid）"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": "|".join(user_ids),
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {"content": content}
        }
        response = requests.post(url, json=data)
        return response.json()  # 包含msgid的完整响应

    def send_image(self, user_ids, image_path):
        """发送图片消息（返回完整响应，包含msgid）"""
        media_id = self.upload_media('image', image_path)
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": "|".join(user_ids),
            "msgtype": "image",
            "agentid": self.agentid,
            "image": {"media_id": media_id}
        }
        response = requests.post(url, json=data)
        return response.json()  # 包含msgid的完整响应

    def send_file(self, user_ids, file_path):
        """发送文件消息（返回完整响应，包含msgid）"""
        media_id = self.upload_media('file', file_path)
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token}"
        data = {
            "touser": "|".join(user_ids),
            "msgtype": "file",
            "agentid": self.agentid,
            "file": {"media_id": media_id}
        }
        response = requests.post(url, json=data)
        return response.json()  # 包含msgid的完整响应

    def upload_file(self, webhook_url, excel_file_path):
        """向群聊上传文件，获取 media_id"""
        webhook_key = webhook_url.split("key=")[1]
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={webhook_key}&type=file"
        with open(excel_file_path, "rb") as file:
            files = {"media": file}
            response = requests.post(url, files=files)
        data = response.json()
        if data["errcode"] == 0:
            return data["media_id"]
        else:
            raise Exception(f"Failed to upload file to group: {data}")

    def send_text_to_group(self, webhook_url, text_message, mentioned_list=None):
        """发送群聊文本消息（返回完整响应，包含msgid）"""
        if mentioned_list is None:
            mentioned_list = ["@all"]
        text_message_dict = {
            "msgtype": "text",
            "text": {
                "content": text_message,
                "mentioned_list": mentioned_list
            }
        }
        response = requests.post(webhook_url, json=text_message_dict)
        return response.json()  # 包含msgid的完整响应

    def send_file_to_group(self, webhook_url, file_path):
        """发送群聊文件消息（返回完整响应，包含msgid）"""
        media_id = self.upload_file(webhook_url, file_path)
        file_message = {
            "msgtype": "file",
            "file": {"media_id": media_id}
        }
        response = requests.post(webhook_url, json=file_message)
        return response.json()  # 包含msgid的完整响应

    def recall_message(self, msgid):
        """
        撤回企业微信应用消息
        :param msgid: 要撤回的消息ID，从发送消息接口获取
        :return: 接口返回结果
        """
        if not msgid:
            raise ValueError("消息ID(msgid)不能为空")

        # 确保access_token有效（如果需要可以添加过期检查和刷新逻辑）
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/recall?access_token={self.access_token}"

        # 构建请求体
        data = {
            "msgid": msgid
        }

        try:
            response = requests.post(url, json=data)
            result = response.json()

            # 检查接口调用结果
            if result.get('errcode') == 0:
                print(f"消息撤回成功，msgid: {msgid}")
            else:
                print(f"消息撤回失败，错误码: {result.get('errcode')}, 错误信息: {result.get('errmsg')}")

            return result
        except Exception as e:
            raise Exception(f"撤回消息时发生错误: {str(e)}")