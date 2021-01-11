import requests
from multiprocessing import Pool, Lock, Manager

headers = {
    'Accept': "text/html,*/*;q=0.01",
    'Accept-Encoding': "gzip, deflate",
    'Accept-Language': "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    'Connection': "keep-alive",
    'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
    'HOST': "www.acadsoc.com.cn",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0",
    'X-Requested-With': "XMLHttpRequest",
}


def check_ip(i, ip_list, lock):
    session = requests.session()
    response = session.get(url="http://icanhazip.com/", timeout=10)
    ip_list.append(response.text)

    print(i, response.text)


if __name__ == '__main__':
    manager = Manager()
    lock = manager.Lock()
    pool = Pool(10)
    ip_list = Manager().list()  # 主进程与子进程共享这个List

    for item in range(1, 10):
        pool.apply(check_ip, (item, ip_list, lock))

    print(ip_list)

    pool.close()
    pool.join()

# from fake_useragent import UserAgent
# ua = UserAgent()
# for i in range(0,10):
#     print(ua.chrome)
#     print(ua.random)