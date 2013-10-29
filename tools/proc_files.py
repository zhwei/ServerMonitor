#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
from human import human_read

class Proc:

    def __init__(self):
        self.proc_file = dict(
            MEM_INFO = "/proc/meminfo", # 内存使用
            CPU_INFO = '/proc/cpuinfo',
            CPU_STAT = '/proc/stat',    # cpu占用率
            LOAD_AVG = '/proc/loadavg', #  cpu负载
            UP_TIME = '/proc/uptime',
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
                result[key] = int(value)
        return result

    def __meminfo(self):
        """
        read /proc/meminfo
        """
        return self.__read_file(self.proc_file['MEM_INFO'])

    def __cpu_info(self):
        """
        read /proc/cpuinfo
        """
        pass

    def __read_cpu_usage(self):
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
    def net_stat(self):
        net = []
        f = open("/proc/net/dev")
        lines = f.readlines()
        f.close()
        for line in lines[2:]:
            con = line.split()
            intf = {}
            intf['interface'] = con[0].lstrip(":")
            intf['ReceiveBytes'] = int(con[1])
            intf['ReceivePackets'] = int(con[2])
            intf['ReceiveErrs'] = int(con[3])
            intf['ReceiveDrop'] = int(con[4])
            intf['ReceiveFifo'] = int(con[5])
            intf['ReceiveFrames'] = int(con[6])
            intf['ReceiveCompressed'] = int(con[7])
            intf['ReceiveMulticast'] = int(con[8])
            intf['TransmitBytes'] = int(con[9])
            intf['TransmitPackets'] = int(con[10])
            intf['TransmitErrs'] = int(con[11])
            intf['TransmitDrop'] = int(con[12])
            intf['TransmitFifo'] = int(con[13])
            intf['TransmitFrames'] = int(con[14])
            intf['TransmitCompressed'] = int(con[15])
            intf['TransmitMulticast'] = int(con[16])
            intf = dict(
                zip(
                    ( 'interface','ReceiveBytes','ReceivePackets',
                      'ReceiveErrs','ReceiveDrop','ReceiveFifo',
                      'ReceiveFrames','ReceiveCompressed','ReceiveMulticast',
                      'TransmitBytes','TransmitPackets','TransmitErrs',
                      'TransmitDrop', 'TransmitFifo','TransmitFrames',
                      'TransmitCompressed','TransmitMulticast' ),
                    ( con[0].rstrip(":"),int(con[1]),int(con[2]),
                      int(con[3]),int(con[4]),int(con[5]),
                      int(con[6]),int(con[7]),int(con[8]),
                      int(con[9]),int(con[10]),int(con[11]),
                      int(con[12]),int(con[13]),int(con[14]),
                      int(con[15]),int(con[16]), )
                )
            )

            net.append(intf)
        return net

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

    def get_cpu_usage(self):
        """
        get cpu avg used by percent
        And the __read_cpu_usage()
        From:
        http://outofmemory.cn/code-snippet/3428/python-jiankong-linux-cpu-usage-lv
        """
        cpustr=self.__read_cpu_usage()
        if not cpustr:
            return 0
        usni1=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])+long(cpustr[5])+long(cpustr[6])+long(cpustr[7])+long(cpustr[4])
        usn1=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])
        time.sleep(2)
        cpustr=self.__read_cpu_usage()
        if not cpustr:
            return 0
        usni2=long(cpustr[1])+long(cpustr[2])+float(cpustr[3])+long(cpustr[5])+long(cpustr[6])+long(cpustr[7])+long(cpustr[4])
        usn2=long(cpustr[1])+long(cpustr[2])+long(cpustr[3])
        cpuper=(usn2-usn1)/(usni2-usni1)
        return cpuper

    def get_mem(self):
        """
        get mem from __meminfo()
        result: KB
        """
        dic = self.__meminfo()
        mem_total = dic['MemTotal']
        mem_used =  mem_total - dic['MemFree'] - dic['Buffers'] - dic['Cached']
        return dict(mem_total=mem_total, mem_used=mem_used)

    def load_avg(self):
        """
        系统平均负载
        """
        return self.__load_stat()
    def disk_stat(self):
        hd={}
        disk = os.statvfs("/")
        hd['available'] = disk.f_bsize * disk.f_bavail
        hd['capacity'] = disk.f_bsize * disk.f_blocks
        hd['used'] = disk.f_bsize * disk.f_bfree
        return hd

m = Proc()
print(m.get_mem())
#print m.get_cpu_usage()
print(m.load_avg())
print(m.uptime_stat())
print(m.net_stat())
print(m.disk_stat())