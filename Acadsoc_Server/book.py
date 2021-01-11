# -*- coding: utf-8 -*-
import requests
import time
import datetime
import json
import http.cookiejar

USERNAME = "18008769096"
PASSWORD = "qwerty"
UID = "1830185"  # 用户ID
COID = "1003468"  # 套餐ID


class Book:
    """阿卡索管理类"""
    def __init__(self):
        self.session = requests.session()
        self.header = {
            'Accept': "text/html,*/*;q=0.01",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            'Connection': "keep-alive",
            'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
            'HOST': "www.acadsoc.com.cn",
            'Referer': "https://www.acadsoc.com.cn/webnew/Login/?ReturnUrl=%2fWebNew%2fuser%2findex.aspx",
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
            'X-Requested-With': "XMLHttpRequest",
        }

        # 状态记录
        self.last_sign_time = datetime.datetime.now()  # 上次签到时间

    def keep_login(self):
        """保持登陆的线程"""
        while True:
            try:
                if not self.is_login():

                    time.sleep(10)
                    result = self.login()
                    if "登陆成功" in result:
                        print(result)
                    else:
                        print(result)
                        continue
                else:
                    print("仍然登录状态")
            except requests.exceptions.ReadTimeout:
                self.session.close()
                time.sleep(10)
            time.sleep(300)

    def login(self):
        """登陆阿卡索"""
        # 不知道阿卡索怎么写的，账号密码非要用双引号括起来，否则提示异常
        post_data = {
            'phone': "\"" + USERNAME + "\"",
            'password': "\"" + PASSWORD + "\"",
            '__': "NewLogin",
        }

        login_url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.User.aspx?method=NewLogin"

        self.session.cookies = http.cookiejar.LWPCookieJar(filename='{}_cookies'.format(USERNAME))

        response_text = self.session.post(login_url, data=post_data, headers=self.header, timeout=30)

        if response_text.text == "1":
            # self.sign_today()  # 签到
            # 每次登录保存为全局变量，会用在 web服务器的调用里
            # global GLOBAL_ACS
            # GLOBAL_ACS = self

            # 保存cookie到文件
            self.session.cookies.save()

            return "登陆成功"
        else:
            return response_text.text

    def is_login(self):
        """判断登陆状态"""
        self.session.cookies = http.cookiejar.LWPCookieJar(filename='{}_cookies'.format(USERNAME))
        try:
            self.session.cookies.load(ignore_discard=True)
            print('载入cookies文件')
        except:
            print('未找到cookies文件')

        home_url = "https://www.acadsoc.com.cn/WebNew/newuser/index2.aspx"
        response = self.session.head(home_url, headers=self.header, allow_redirects=False, timeout=30)
        if response.status_code == 200:
            return True

    def sign_today(self):
        """自动签到"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.NewUser.aspx"
        post_data = {
            '__': "UpdateStudentAcCount",
        }

        # 每隔12小时尝试一次签到
        now = datetime.datetime.now()
        if (now - self.last_sign_time).seconds < 12*60*60:
            return

        time.sleep(3)
        self.session.post(url, data=post_data, headers=self.header, timeout=30)
        self.last_sign_time = now
        print("签到领A豆")

    def book_class(self, tid, teacher_name, the_time, tool_no):
        """预定课程"""
        self.session.cookies = http.cookiejar.LWPCookieJar(filename='{}_cookies'.format(USERNAME))
        
        if not self.is_login():
            login_result = self.login()
            return "登陆失效，已经【{}】，请重试一次！".format(login_result)

        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=AppointClass"

        the_time = the_time.replace("/", "-")  # 格式转换

        post_data = {
            'TUID': tid,
            'bookingWay': "3",
            'COID': COID,
            'UID': UID,
            'targetTime': "\"" + the_time + "\"",
            'classtool': tool_no,
            'IsNew': "0",
            '__': "AppointClass",
        }

        response = self.session.post(url, data=post_data, headers=self.header, timeout=30)
        response_json = json.loads(response.text)

        print(teacher_name, the_time, response_json["value"]["msg"])
        return response_json["value"]["msg"]
