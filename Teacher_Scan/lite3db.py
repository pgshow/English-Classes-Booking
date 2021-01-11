import sqlite3

FILE_NAME = "sqlite3.db"


# teachi = {
#     "id": 100000,
#     "teacher_name": "Sara",
#     "full_day": 100,
#     "mp3": "Mcgel---",
#     "schedule": "2018-45-55",
#     "description": "Hello every one",
#  }


class DB:
    """数据库操作类"""
    def __init__(self):
        self.conn = sqlite3.connect(FILE_NAME)
        self.cursor = self.conn.cursor()

    def add(self, dict):
        """添加老师"""
        sql = '''INSERT INTO TEACHERS(id, teacher_name, full_day, schedule, mp3, description) VALUES (?, ?, ?, ?, ?, ?)'''

        try:
            param = tuple(dict.values())
            self.conn.execute(sql, param)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True

    def update(self, dict):
        """更新老师"""
        sql = "UPDATE TEACHERS SET full_day = \'{full_day}\', schedule = \'{schedule}\', mp3 = \'{mp3}\', description = \'{description}\' where ID = {id}".format(**dict)

        try:
            self.conn.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True

    def save(self, dict):
        """保存老师"""
        if self.select(dict):
            return self.update(dict)
        else:
            return self.add(dict)

    def save_times(self, tid, times):
        """保存搜索日期的课程表"""
        sql = "UPDATE TEACHERS SET tmp_times = \'{}\' where ID = {}".format(times, tid)

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True

    def select(self, dict):
        """查询某个老师"""
        sql = "SELECT * from TEACHERS Where ID = {id}".format(**dict)

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
        except Exception as e:
            print(e)
            return

        if result:
            return True

    def all_teachers(self):
        """查询所有老师的ID和名字"""
        sql = "SELECT id, teacher_name from TEACHERS"

        try:
            result = self.conn.execute(sql)
        except Exception as e:
            print(e)
            return

        if result:
            teachers = []
            # 转换下格式和数据类型
            for item in result:
                teachers.append({'id': item[0], 'teacher_name': item[1]})

            return teachers

# db = DB()
# db.save(teachi)