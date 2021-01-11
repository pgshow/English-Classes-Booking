import requests
import markdown2
import json
from mail import Email


class Msg:
    """信息通知类"""
    def __init__(self):
        self.email = Email()

    def send(self, title, content):
        """发送通知"""
        self.send_by_email(title, content)

    def send_by_wechat(self, title, content):
        """通过Server酱的接口发送通知"""
        post_data = {
            'sendkey': '12379-3163e9a45e9bf0cacc21955f9622b3e7',
            'text':	title,
            'desp': content,
        }

        try:
            # 方糖通知
            response = requests.post("https://pushbear.ftqq.com/sub", data=post_data, timeout=30)
            response_json = json.loads(response.text)

            print("微信通知：", response_json["data"], "\n")

            if "成功" in response_json["data"]:
                return True

        except Exception as e:
            print("微信通知时发生错误", e, "\n")

    def send_by_email(self, title, content):
        """邮件通知"""
        try:
            html = markdown2.markdown(content)
            self.email.sent_email(title, html)
            return True
        except Exception as e:
            print("邮件通知时发生错误", e, "\n")
