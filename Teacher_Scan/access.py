import pypyodbc

DB_NAME = "access.mdb"
TABLE_NAME = "teachers"


# teachi = {
#     "id": 567,
#     "name": "Hanna.N",
#     "mp3": "Mcgel---",
#     "schedule": "2018-45-55",
#     "description": "Hello every one",
#  }


class DB:
    """数据库操作类"""
    def __init__(self):
        self.path = "access.mdb"
        self.conn = self.mdb_conn()
        self.cur = self.conn.cursor()

    def mdb_conn(self):
        """创建数据库连接"""
        str = 'Driver={Microsoft Access Driver (*.mdb)};DBQ=' + DB_NAME
        conn = pypyodbc.win_connect_mdb(str)

        return conn

    def add(self, dict):
        """添加老师"""
        sql = "Insert Into " + TABLE_NAME + " Values ({id}, \'{name}\', \'{full_day}\', \'{schedule}\', \'{mp3}\', \'{description}\', \'\')".format(**dict)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True

    def update(self, dict):
        """更新老师"""
        sql = "Update " + TABLE_NAME + " Set full_day = \'{full_day}\', schedule = \'{schedule}\', mp3 = \'{mp3}\', description = \'{description}\' where ID = {id}".format(**dict)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True

    def select(self, dict):
        """查询老师"""
        sql = "Select * from " + TABLE_NAME + " Where ID = {id}".format(**dict)

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except Exception as e:
            print(e)
            return

        if result:
            return True

    def select_teachers(self):
        """查询所有老师的ID和名字"""
        sql = "Select id, name from " + TABLE_NAME

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except Exception as e:
            print(e)
            return

        if result:
            teachers = []
            # 转换下格式和数据类型
            for item in result:
                teachers.append({'id': item[0], 'name': item[1]})

            return teachers

    def save(self, dict):
        """保存老师"""
        if self.select(dict):
            return self.update(dict)
        else:
            return self.add(dict)

    def save_times(self, tid, times):
        """保存搜索日期的课程表"""
        sql = "Update " + TABLE_NAME + " Set tmp_times = \'{}\' where ID = {}".format(times, tid)

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(e)
            return

        return True








# db = DB()
# db.update(teachi)