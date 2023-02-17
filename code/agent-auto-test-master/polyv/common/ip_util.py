import socket
from os import getcwd
from multiprocessing import Process
from urllib.request import urlopen

import psutil, time


def get_ip():
    ip = "localhost"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        # return ip
    except Exception as err:
        print(err)

    # 尝试获取外网ip，以外网ip优先返回
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1':
                if "10.10" in item[1]:
                    netcard_info.append(item[1])
    print(netcard_info)
    return netcard_info[0] if netcard_info else ip


class IP(object):
    pass


class NetWorkCalc:
    def get_net_name(self):
        target_lines = ['以太网', 'WLAN']
        find_turned_on_lines = []
        for net_name, info in psutil.net_if_stats().items():  # snicstats class
            if info.isup == True:
                find_turned_on_lines.append(net_name)
        avaliable_line = list(set(find_turned_on_lines) & set(target_lines))
        # 若网线和WiFi同时连上，Win10系统会优先跑网线
        if '以太网' in avaliable_line:
            return '以太网'
        elif 'WLAN' in avaliable_line:
            return 'WLAN'
        elif len(avaliable_line) != 0:
            return 0
        else:
            return -1

    def get_net_io(self, Networked_Line, Step_Time=1.0):
        before_io = psutil.net_io_counters(pernic=True)[Networked_Line].bytes_recv
        time.sleep(Step_Time)
        after_io = psutil.net_io_counters(pernic=True)[Networked_Line].bytes_recv
        speed = (after_io - before_io) / 1024
        return "%.2f K/s" % speed

    def check(self, Step_Time=1.0):
        net_name = self.get_net_name()
        if isinstance(net_name, str):
            # print(psutil.net_io_counters(pernic=True)[net_name]) # snetio class
            return self.get_net_io(Networked_Line=net_name, Step_Time=Step_Time), True
        else:
            time.sleep(Step_Time)
            if net_name == -1:
                return "Error, No available Network card detected", False
            elif net_name == 0:
                return "Error, Check whether '以太网' or 'WLAN' are Turned ON", False
            else:
                return "Unknown Error", False


class Monitor(Process):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def loops_work(self):
        nwc = NetWorkCalc()
        get_now_timestamp = lambda: int(time.time())
        start_time = get_now_timestamp()
        run_times = 7 * 86400
        log_path = getcwd() + '/monitor_network_log.txt'
        while 1:
            now_time = get_now_timestamp()
            if (now_time - start_time) % run_times == 0:
                # 清空日志文件
                with open(log_path, 'w', encoding='utf8') as f:
                    f.write('')
            else:
                with open(log_path, 'a', encoding='utf8') as f:
                    result = nwc.check()
                    # print(str(result))
                    f.write(time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now_time)) + str(result) + '\n')

    def run(self):
        self.loops_work()


if __name__ == '__main__':
    print(get_ip())
