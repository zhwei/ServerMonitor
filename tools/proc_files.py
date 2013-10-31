#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
from collections import namedtuple

from human import human_read

class Proc:

    def __init__(self):
        self.proc_file = dict(
            PROC = '/proc',
            MEM_INFO = "/proc/meminfo", # 内存使用
            CPU_INFO = '/proc/cpuinfo',
            CPU_STAT = '/proc/stat',    # cpu占用率
            LOAD_AVG = '/proc/loadavg', #  cpu负载
            UP_TIME = '/proc/uptime',
            NET_STAT = '/proc/net/dev'  #网卡
        )

    def __read_file(self, fi):
        """
        dict of data from proc files (str:int).
        Values are in kilobytes.
        From:
        http://forrst.com/posts/python_function_to_read_proc_meminfo-gRj
        """
        re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
        result = dict()
        with open(fi) as fil:
            for line in fil:
                match = re_parser.match(line)
                if not match:
                    continue # skip lines that don't parse
                key, value = match.groups(['key', 'value'])
                result[key] = float(value)
        return result

    def __meminfo(self):
        """
        read /proc/meminfo
        """
        return self.__read_file(self.proc_file['MEM_INFO'])

    def mem_info(self):
        """
        get mem from __meminfo()
        result: KB
        """
        dic = self.__meminfo()
        mem_total = dic['MemTotal']
        mem_used =  mem_total - dic['MemFree'] - dic['Buffers'] - dic['Cached']
        return dict(mem_total=mem_total, mem_used=mem_used)

    def __cpu_info(self):
        """
        read /proc/cpuinfo
        """
        with open(self.proc_file['CPU_INFO']) as f:
            model = list()
            for line in f:
                # Ignore the blank line separating the information between
                # details about two processing units
                if line.strip():
                    if line.rstrip('\n').startswith('model name'):
                        model_name = line.rstrip('\n').split(':')[1]
                        model.append(model_name)

        return model

    def cpu_info(self):
        '''
        每个处理器单元的模式名
        '''
        return self.__cpu_info()

    def __read_cpu_str(self):
        """
        Read the current system cpu usage from /proc/stat.
        """
        with open(self.proc_file['CPU_STAT']) as fi:
            for line in fi:
                l = line.split()
                if len(l) < 5:
                    continue
                if l[0].startswith('cpu'):
                    return l
        return []

    def __read_cpu_usage(self):
        """
        get cpu usage info from str
        """
        cpustr=self.__read_cpu_str()
        usni=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])+long(cpustr[5])+long(cpustr[6])+long(cpustr[7])+long(cpustr[4])
        usn=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])

        return float(usn), float(usni)

    def cpu_usage(self):
        """
        get cpu avg used by percent
        And the __read_cpu_usage()
        From:
        http://outofmemory.cn/code-snippet/3428/python-jiankong-linux-cpu-usage-lv
        """
        usn1, usni1 = self.__read_cpu_usage()
        time.sleep(2)
        usn2, usni2 = self.__read_cpu_usage()
        cpuper=(usn2-usn1)/(usni2-usni1)
        return cpuper

    def __load_stat(self):
        """
        ** 系统平均负载
        前三个数字是1、5、15分钟内的平均进程数。
        第四个值的分子是正在运行的进程数，分母是进程总数
        最后一个是最近运行的进程ID号
        """
        with open(self.proc_file['LOAD_AVG']) as fi:
            con = fi.read().split()
        loadavg = dict(
            lavg_1 = con[0],
            lavg_5 = con[1],
            lavg_15 = con[2],
            nr = con[3],
            last_pid = con[4],
        )
        return loadavg

    def load_avg(self):
        """
        系统平均负载
        """
        return self.__load_stat()

    def net_stat(self):
        """
        获取网卡流量信息 /proc/net/dev
        返回dict,单位byte
        """
        with open(self.proc_file['NET_STAT']) as fi:
            net_dump = fi.readlines()

        device_data={}
        data = namedtuple('data',['rx','tx'])
        for line in net_dump[2:]:
            line = line.split(':')
            if line[0].strip() != 'lo':
                device_data[line[0].strip()] = data(float(line[1].split()[0])/(1024.0*1024.0),
                                                    float(line[1].split()[8])/(1024.0*1024.0))

        return device_data

    def uptime_stat(self):
        """
        查看开机时间
        From:
        http://wangwei007.blog.51cto.com/68019/1047061
        """
        uptime = dict()
        with open(self.proc_file['UP_TIME']) as fi:
            con = fi.read().split()
        all_sec = float(con[0])
        MINUTE,HOUR,DAY = 60,3600,86400
        uptime['day'] = int(all_sec / DAY )
        uptime['hour'] = int((all_sec % DAY) / HOUR)
        uptime['minute'] = int((all_sec % HOUR) / MINUTE)
        uptime['second'] = int(all_sec % MINUTE)
        uptime['Free rate'] = float(con[1]) / float(con[0])
        return uptime

    def disk_stat(self):
        hd={}
        disk = os.statvfs("/")
        hd['available'] = disk.f_bsize * disk.f_bavail
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = disk.f_bsize * disk.f_bfree
        return hd

    def process_num(self):
        """
        进程数目
        """
        num = 0
        for subdir in os.listdir(self.proc_file['PROC']):
            if subdir.isdigit():
                num += 1
        return num

p = Proc()
#print(m.mem())
#print m.cpu_usage()
#print(m.load_avg())
#print(m.uptime_stat())
#print(m.net_stat()['ens33'].tx)
#print(m.disk_stat())
#print(m.cpu_info())
#for i in m.net_stat():
#    print m.net_stat()[i].rx, m.net_stat()[i].tx
#print m.process_num()

dic = {
    'mem_info': p.mem_info(),
    'cpu_usage': p.cpu_usage(),
    'load_avg': p.load_avg(),
    'net_stat': p.net_stat(),
    'disk_stat': p.disk_stat(),
    'up_time': p.uptime_stat(),
}

print(dic)