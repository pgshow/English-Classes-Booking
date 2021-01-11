import requests
import time
import datetime
import json
import re
import copy
import operator
from msg import Msg
from multiprocessing import Pool, Manager
from fake_useragent import UserAgent

ua = UserAgent(path="fake_useragent_0.1.11")

INTERVAL = 30  # 通知间隔时间，单位秒
UID = "1035185"  # 用户ID
COID = "1003468"  # 套餐ID

# 老师数据初始化
TEACHERS = {
    # "37459": "Princess.DG",
    "49967": "test",
    # "58507": "Joyces",
    # "34180": "Ray.M",
    # "5918": "Candie",
    # "23143": "Rachel.T",
    # "24180": "Aly",
}

# 新版我的空闲时间，时间+星期几范围
MY_TIMES = {
    "15:00": [1, 2, 3, 4, 5, 6, 0],
    "15:30": [1, 2, 3, 4, 5, 6, 0],
    "16:00": [1, 2, 3, 4, 5, 6, 0],
    "16:30": [1, 2, 3, 4, 5, 6, 0],
    "17:00": [1, 2, 3, 4, 5, 6, 0],
    # "17:30": [1, 2, 3, 4, 5, 6, 0],
    # "18:00": [1, 2, 3, 4, 5, 6, 0],
    # "21:30": [1, 2, 3, 4, 5, 6, 0],
    # "22:00": [1, 2, 3, 4, 5, 6, 0],
    # "22:30": [1, 2, 3, 4, 5, 6, 0],
    # "23:00": [1, 2, 3, 4, 5, 6, 0],
    # "23:30": [1, 2, 3, 4, 5, 6, 0],
}


class Acadsoc:
    """阿卡索管理类"""
    def __init__(self):
        self.msg = Msg()
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
        self.last_mention_time = datetime.datetime.now()  # 上次发送消息时间
        self.last_lesson_records = {t: "" for t in TEACHERS.keys()}  # 过去课表记录

    def running(self):
        """开始任务"""
        # 进程池
        pool = Pool(3)

        while True:

            try:
                now_lesson_records = {t: "" for t in TEACHERS.keys()}  # 现在的课表记录

                the_titles = "老师："
                the_contents = "` 今天是 " + datetime.datetime.now().strftime('%m-%d %A') + " `\r\n\r\n"

                for tid, name in TEACHERS.items():
                    # 获取空闲日期表
                    free_date = Manager().list()  # 主进程与子进程共享这个List
                    pool.apply(self.teacher_date, (tid, free_date))

                    # 日期表为空就不继续获取时间表
                    if not free_date:
                        print("%s 老师没有空闲日期\n" % name)
                        time.sleep(2)
                        continue

                    time.sleep(1)

                    # 获取老师空闲时间
                    free_times = Manager().list()
                    for date in free_date:
                        pool.apply(self.teacher_time, (tid, date, free_times))  # 子进程访问
                        time.sleep(1)

                    if not free_times:
                        print("%s 老师的空闲时间被人订走啦\n" % name)
                        time.sleep(2)
                        continue

                    fit_time = self.match_my_time(free_times)

                    if not fit_time:
                        print("%s 老师的时间与你不匹配\n" % name)
                        time.sleep(2)
                        continue

                    # 列表转换为字符串
                    fit_time.sort()
                    fit_time_str = "  ".join(fit_time)
                    fit_time_str = fit_time_str.replace("T", " ")

                    # 记录老师课表的变化
                    now_lesson_records[tid] = fit_time_str

                    # 输出老师匹配时间
                    print("%s 老师匹配时间：%s\n" % (name, fit_time_str))

                    # 微信消息标题，多个老师的名字相加
                    the_titles = the_titles + name + "， "

                    # 微信消息内容，多个老师的相加，使用了 Markdown 语法
                    fit_time_str = fit_time_str.replace("  ", "\r\n\r\n")  # 微信通知需要两个换行符才能实现在Server酱换行
                    fit_time_str = self.add_link(tid, name, fit_time_str)  # 给日期加上超链接
                    the_contents = the_contents + "####" + name + " 老师的课表：\r\n\r\n" + fit_time_str + "\r\n\r\n***\r\n\r\n"

                # 课程不变不提醒
                if operator.eq(now_lesson_records, self.last_lesson_records):
                    continue

                # 一分钟提醒间隔
                now = datetime.datetime.now()
                if (now - self.last_mention_time).seconds < INTERVAL:
                    continue

                time.sleep(1)

                # 获取我有预定的时间
                my_booked_times = Manager().list()
                pool.apply(self.my_booked_date, (my_booked_times, ))  # 子进程访问

                if my_booked_times:
                    the_contents = self.light_my_booked_date(my_booked_times, the_contents)  # 从内容里高亮我预定的日期

                # 发送并记录提示的状态
                result = self.msg.send(the_titles, the_contents)
                # if result:
                self.last_lesson_records = copy.deepcopy(now_lesson_records)
                self.last_mention_time = now

            except Exception as e:
                print(e)

            time.sleep(5)

        pool.close()
        pool.join()

    def teacher_date(self, tid, free_date):
        """获取老师的日期表"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=GetTutorTime"

        post_data = {
            '__': "GetTutorTime",
            'COID': COID,
            'TUID': tid,
        }

        header = {
            'User-Agent': ua.random,
        }

        response = requests.post(url, data=post_data, headers=header, timeout=5)
        response_json = json.loads(response.text)
        response.close()

        # 只返回空闲的日期
        for item in response_json["value"]:
            if item["isfull"] == 0:
                free_date.append(item["time"])

    def teacher_time(self, tid, date, free_times):
        """获取老师的空闲时间表"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=GetTargetTimeAvaDuration"

        post_data = {
            '__': "GetTargetTimeAvaDuration",
            'COID': COID,
            'TargetTime': "\"" + date + "\"",
            'TUID': tid,
        }

        header = {
            'User-Agent': ua.random,
        }

        response = requests.post(url, data=post_data, headers=header, timeout=5)
        response_json = json.loads(response.text)
        response.close()

        free_times += response_json["value"]

    def match_my_time(self, free_time):
        """挑选合适时间"""
        fit_time = []
        for time in free_time:
            tmp = re.search(r'(\d{4}/\d{1,2}/\d{1,2})T(\d{1,2}:\d{1,2})', time)
            week = int(datetime.datetime.strptime('{} 00:00:00'.format(tmp.group(1)), '%Y/%m/%d %H:%M:%S').strftime("%w"))  # 获取课程当天周几
            time_str = tmp.group(2)  # 获取课程时间

            try:
                # 按星期几匹配课程时间
                limit_day = MY_TIMES[time_str]

                if week in limit_day:
                    fit_time.append(time)
            except:
                pass

        return fit_time

    def my_booked_date(self, my_booked_times):
        """我已经预定的日期"""
        url1 = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.User.aspx?method=GetUserLessonsByCOID"

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        in_7day = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d')

        # 获取这几天我约的课的日期
        post_data1 = {
            '__': "GetUserLessonsByCOID",
            'COID': COID,
            'start': "\"" + today + "\"",
            'end': "\"" + in_7day + "\""
        }

        header = {
            'User-Agent': ua.random,
        }

        response1 = requests.post(url1, data=post_data1, headers=header, timeout=5)
        response_json = json.loads(response1.text)
        response1.close()

        # 获取我有预订课程的日期
        for day in response_json["value"]:
            my_booked_times.append(day['start'][:-9].replace("-0", "/").replace("-", "/"))

    def add_link(self, teacher_id, teacher_name, content):
        """给日期加上超链接"""
        content = re.sub(r'(\d+/\d+/\d+) (\d+:\d+)', r'[\1 \2](http://xxx.xxx.xxx.xxx:8080/lesson?time=\1+\2&tid=' + teacher_id + '&teacher_name=' + teacher_name + '&action=book)', content)  # 用了 MakeDown 的超链接语法
        return content

    def light_my_booked_date(self, booked_times, content):
        """标记我预约过的日期"""
        for t in booked_times:
            # content = re.sub(r'\[(' + t + ' \d+:\d+)\](.+)=book', r'[` \1 `]\2=cancel', content)  # 用了 MakeDown 底纹代码语法，action 改成取消
            content = re.sub(r'\[(' + t + ' \d+:\d+)\]', r'[` \1 `]', content)  # 用了 MakeDown 底纹代码语法，action 改成取消

        return content

