import time
import filter
import re

scan = filter.Filter()

if __name__ == '__main__':
    while True:
        print("""
1.直接预约课程
2.添加老师到关注列表
3.扫描全部老师
4.快速扫描数据库里优秀老师的课程表""")
        action = input("\n输入你要做的事情：")

        if action == '1':
            try:
                tid, date = input("输入老师的ID和日期（格式 1047, 2019-06-05）：").split(',')
                date = date.strip()

                if not re.match(r'^\d+$', tid):
                    print('老师ID格式不正确，请重新输入')
                    continue
            except:
                print('格式不正确，请重新输入')
                continue

            free_lesson = scan.get_times(tid, date)
            time.sleep(3)

            i = 0
            lesson_list = []  # 字典转成列表格式
            for lesson in free_lesson:
                print(i, lesson)
                lesson_list.append(lesson)
                i += 1

            lesson_no = int(input("输入课程编号约课："))

            booking_time = lesson_list[lesson_no]

            scan.book_class(tid, "手动定课", booking_time)

        elif action == '2':
            tid = input("输入老师的ID：")

            if not tid:
                continue

            print(scan.follow_teacher(tid))

        elif action == '3':
            print("开始扫描所有老师……")
            scan.running()

        elif action == '4':
            date = input("\n输入你要查询的日期（格式 2019-01-09）：")
            print("快速扫描已有的优秀老师……")
            scan.running(date)

        else:
            print("输入错误，请重新输入")
            time.sleep(1)
