# -*- coding: utf-8 -*-
import time
import web
import book
import threading

render = web.template.render('templates/')
urls = (
    '/(.*)', 'lesson'
)
app = web.application(urls, globals())

monitor = book.Book()

if __name__ == '__main__':
    # 启动保持登陆的线程
    keep_login_thread = threading.Thread(target=monitor.keep_login)  # 记住调用的函数不带括号
    keep_login_thread.start()

    time.sleep(5)

    # 启动web服务
    try:
        app.run()
    except Exception as e:
        print(e)


class lesson:
    """Webpy的架构函数"""
    def GET(self, name):
        web.header('Content-Type', 'text/html; charset=utf-8', unique=True)
        try:
            if not name:
                # 只有 lesson 才做出反应，否则输出一个乱编的错误信息
                return "Error 1025"

            elif name == "lesson":
                # 获取传递的数据
                action = web.input().get('action', '')
                teacher_id = web.input().get('tid', '')
                teacher_name = web.input().get('teacher_name', '')
                free_time = web.input().get('time', '')
                tool_no = web.input().get('tool_no', '')
                confirm = web.input().get('confirm', '')

                if teacher_id == "" and free_time == "":
                    return

                if action == "book":
                    """预定老师"""
                    if confirm != "yes":
                        # 显示确定预定信息
                        return render.book(teacher_id, teacher_name, free_time)  # 调用html模板并传送参数
                    else:
                        # 开始预定流程
                        msg = monitor.book_class(teacher_id, teacher_name, free_time, tool_no)  # 调用静态函数预定课程
                        return render.book_success(teacher_name, free_time, msg)

                elif action == "cancel":
                    """取消预定"""
                    return render.cancel(name)

        except Exception as e:
            print(e)
            return render.error(e)
