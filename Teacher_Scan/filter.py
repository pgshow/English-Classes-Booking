import requests
import time
import gc
import re
import system_function as sf
from lite3db import DB
from retrying import retry
from fake_useragent import UserAgent
from multiprocessing import Pool, Manager
from multiprocessing import Value

ua = UserAgent(path="fake_useragent_0.1.11")

USERNAME = "18008069796"
PASSWORD = "password"
UID = "100085"  # 用户ID
COID = "1003468"  # 套餐ID
POPULAR_COUNT = 4  # 订满大于此天数才算受欢迎老师


class Filter:
    """阿卡索管理类"""
    def __init__(self):
        self.session = requests.session()

    def running(self, search_date=""):
        """开始抓取任务"""
        lock = Manager().Lock()
        pool = Pool(1)

        if not search_date:
            # 扫描全部老师
            ids = range(22042, 100000)

            not_exist_num = Manager().dict()  # 多少次没有搜到老师说明超出数据范围了
            not_exist_num['i'] = 0

            for tid in ids:
                pool.apply(self.scan_all_teacher, (tid, not_exist_num, lock))  # 子进程访问
                if not_exist_num['i'] > 50:
                    print("老师已经搜索完成")
                    return

        else:
            if not re.match(r'\d{4}-\d{2}-\d{2}', search_date):
                print('日期格式不正确')
                return

            # 快速扫描数据库内的优秀老师
            db = DB()
            teachers = db.all_teachers()

            del db
            gc.collect()

            if not teachers:
                print("快速扫描优秀老师任务启动失败")
                return

            for item in teachers:
                pool.apply(self.fast_scan_teacher, (item, search_date, lock))  # 子进程访问

        pool.close()
        pool.join()

    def fast_scan_teacher(self, teacher, search_date, lock):
        """快速扫描老师空闲时间"""
        try:
            print("ID:", teacher['id'], teacher['teacher_name'])

            teacher_schedule = self.get_schedule(teacher['id'])

            if not teacher_schedule:
                print("老师没教了")
                return

            good_teacher = self.popular(teacher_schedule)

            the_schedule = good_teacher[1]  # 课程表情况

            # 显示搜索日期的课表情况
            if search_date and search_date + "  未满" in the_schedule:
                time.sleep(2)
                times = self.get_times(teacher['id'], search_date)
                times_str = "  ".join(times)  # 时间列表转换成字符串

                db = DB()
                lock.acquire()
                db.save_times(teacher['id'], times_str)  # 保存课程表到数据库
                lock.release()

                del db
                gc.collect()

                print("---- " + times_str)

        except Exception as e:
            print(e)

        time.sleep(1)

    def scan_all_teacher(self, tid, not_exist_num, lock):
        """扫描所有老师"""
        try:
            print("ID:" + str(tid))

            teach_info = self.teach_info(tid)

            if not teach_info:
                print("老师不存在")
                not_exist_num['i'] += 1
                time.sleep(2)
                return

            not_exist_num['i'] = 0  # 后面有老师的情况，要清空无效老师计数器
            time.sleep(2)
            teacher_schedule = self.get_schedule(tid)

            if not teacher_schedule:
                print("老师没教了")
                time.sleep(2)
                return

            good_teacher = self.popular(teacher_schedule)

            if not good_teacher:
                # 并不是高分老师
                print("不是高分老师")
                time.sleep(2)
                return

            full_day = good_teacher[0]  # 满的天数
            the_schedule = good_teacher[1]  # 课程表情况

            lock.acquire()
            self.save_teacher(teach_info, full_day, the_schedule)
            lock.release()

        except Exception as e:
            time.sleep(2)
            print(e)

    # @retry(wait_exponential_multiplier=1000, wait_exponential_max=30000)
    def teach_info(self, tid):
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.User.aspx?method=GetTutorTableListByTUIDAndCOrder"

        header = {
            'User-Agent': ua.random,
        }

        """获取老师信息"""
        post_data = {
            '__': "GetTutorTableListByTUIDAndCOrder",
            'TUID': tid,
            'COID': COID,
        }

        response = self.session.post(url, data=post_data, headers=header, timeout=30)

        the_json = response.json()

        if the_json["value"]:
            return the_json["value"][0]

    # @retry(wait_exponential_multiplier=1000, wait_exponential_max=30000)
    def get_schedule(self, tid):
        """获取老师日程"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=GetTutorTime"

        header = {
            'User-Agent': ua.random,
        }

        post_data = {
            '__': "GetTutorTime",
            'COID': COID,
            'TUID': tid,
        }

        response = self.session.post(url, data=post_data, headers=header, timeout=30)

        the_json = response.json()

        return the_json["value"]

    # @retry(wait_exponential_multiplier=1000, wait_exponential_max=30000)
    def get_times(self, tid, date):
        """获取当天时间表"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=GetTargetTimeAvaDuration"

        header = {
            'User-Agent': ua.random,
        }

        post_data = {
            '__': "GetTargetTimeAvaDuration",
            'COID': COID,
            'TargetTime': "\"" + date + "\"",
            'TUID': tid,
        }

        response = self.session.post(url, data=post_data, headers=header, timeout=30)

        json = response.json()

        return json["value"]

    def popular(self, schedule):
        """判断老师受欢迎程度"""
        count = 0
        new_schedule = []
        for item in schedule:
            if item["isfull"]:
                new_schedule.append(item["time"] + "  订满")
                count += 1
            else:
                new_schedule.append(item["time"] + "  未满")

        # 大于一定天数才算受欢迎老师
        if count >= POPULAR_COUNT:
            return count, new_schedule
        else:
            return

    def format_info(self, teacher_info, full_day, the_schedule):
        """格式化老师信息成字典"""

        data = {
            'id': teacher_info['TUID'],
            'teacher_name': teacher_info['FullName'],
            'full_day': full_day,
            'schedule': ' , '.join(the_schedule),
            'mp3': teacher_info['mp3file'],
            'description': sf.filter_s(teacher_info['Profile']),  # 需要过滤掉特殊符号才能数据库操作
        }

        return data

    def save_teacher(self, teacher_info, full_day, schedule):
        """保存老师信息"""
        teacher_dict = self.format_info(teacher_info, full_day, schedule)  # 先把老师信息做成字典

        db = DB()

        if db.save(teacher_dict):
            print("老师 %s ，满 %d 天， 日程：[ %s ]" % (teacher_info["FullName"], full_day, ' , '.join(schedule)))

        del db
        gc.collect()

    def follow_teacher(self, tid):
        """添加老师到关注"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.User.aspx?method=FocusTeacher"

        header = {
            'User-Agent': ua.random,
        }

        # 先登陆阿卡索
        login_result = self.login()

        print(login_result)

        if login_result != "登陆成功":
            return

        # 开始添加老师到关注
        time.sleep(10)
        post_data = {
            '__': "FocusTeacher",
            'coid': COID,
            'tuid': tid,
        }

        response = self.session.post(url, data=post_data, headers=header, timeout=30)

        json = response.json()

        return json["value"]["msg"]

    def login(self):
        """登陆阿卡索"""
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.User.aspx?method=NewLogin"

        header = {
            'User-Agent': ua.random,
        }

        # 不知道阿卡索怎么写的，账号密码非要用双引号括起来，否则提示异常
        post_data = {
            'phone': "\"" + USERNAME + "\"",
            'password': "\"" + PASSWORD + "\"",
            '__': "NewLogin",
        }

        response_text = self.session.post(url, data=post_data, headers=header, timeout=30)

        if response_text.text == "1":
            return "登陆成功"
        else:
            return response_text.text

    def book_class(self, tid, teacher_name, the_time):
        """预定课程"""
        # 先登陆阿卡索
        login_result = self.login()

        print(login_result)

        if login_result != "登陆成功":
            return

        time.sleep(2)
        url = "https://www.acadsoc.com.cn/Ajax/Web.UI.Fun.Course.aspx?method=AppointClass"

        the_time = the_time.replace("/", "-")  # 格式转换
        the_time = the_time.replace("T", " ")

        header = {
            'User-Agent': ua.random,
        }

        post_data = {
            'TUID': tid,
            'bookingWay': "3",
            'COID': COID,
            'UID': UID,
            'targetTime': "\"" + the_time + "\"",
            'classtool': "7",
            'IsNew': "0",
            '__': "AppointClass",
        }

        response = self.session.post(url, data=post_data, headers=header, timeout=30)
        response_json = response.json()

        print(teacher_name, the_time, response_json["value"]["msg"])


# a = Acadsoc()
# a.running()
