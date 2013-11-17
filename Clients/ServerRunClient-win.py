# -*- coding: GBK -*-

import os
import sys
import wmi
import time
import platform
import threading
import SimpleXMLRPCServer

import winerror
import win32event
import win32service
import win32evtlogutil
import win32serviceutil
import servicemanager
import pythoncom

IP="0.0.0.0"
PORT=1234

class WmiObj:

    def __init__(self):
        pythoncom.CoInitialize()
        self._w = wmi.WMI()

    def mem_info(self):
        """获取内存信息
        Out: {'mem_total': float, 'mem_used': float}
        """
        for i in self._w.Win32_ComputerSystem():
            mem_total = float(i.TotalPhysicalMemory)
        for i in self._w.Win32_OperatingSystem():
            mem_free = float(i.FreePhysicalMemory)
        return dict(mem_total=mem_total,mem_used=mem_total-mem_free)

    def cpu_info(self):
        """cpu信息
        包括cpu型号，核心数目，线程数目
        Out: {'name':str,'num_of_cores': int, 'num_of_processors': int}
        """
        res = dict()
        for cpu in self._w.Win32_Processor():
             res["name"] = cpu.Name
             res['num_of_processors'] = cpu.NumberOfLogicalProcessors
             try:
                     res["num_of_cores"] = cpu.NumberOfCores
             except:
                     res["num_of_cores"] += 1
        return res

    def __read_cpu_usage(self):
        """ once load
        """
        for cpu in self._w.Win32_Processor():
            return float(cpu.LoadPercentage)

    def cpu_usage(self):
        """cpu usage
         Out: float(not percent)
        """
        cpustr1 = self.__read_cpu_usage()
        if not cpustr1:
             return 0
        time.sleep(2)
        cpustr2 = self.__read_cpu_usage()
        if not cpustr2:
             return 0
        cpuper = (cpustr1+cpustr2)/2
        return cpuper

    def load_avg(self):
        """系统平均负载
        """
        return 0

    def net_stat(self):
        """
        获取网卡流量信息 /proc/net/dev
        返回dict,单位byte
        """
        return 0

    def uptime_stat(self):
        """待机时间
        """
        return 0

    def disk_stat(self):
        """磁盘信息
        Out: {'caption': str, 'size': float}
        """
        dic=dict()
        for d in self._w.Win32_DiskDrive():
            dic['caption'] = d.Caption
            dic['size'] = float(d.Size)
        return dic

    def process_num(self):
        """进程数目
        """
        for sys in self._w.Win32_OperatingSystem():
            return sys.NumberOfProcesses


    def partition(self) :
         """
         获取文件系统信息。
         包含分区的大小、可用量、挂载点信息。
         Out: {u'C:': {'total': float, 'free': float},...
         """
         res = dict()
         for physical_disk in self._w.Win32_DiskDrive ():
                 for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"):
                         for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
                                 res[logical_disk.Caption] = {
                                     'total':float(logical_disk.Size),
                                     'free':float(logical_disk.FreeSpace),
                                 }
         return res

    def network(self):
        """Get network information
        Out: {'ip': str, 'mac': str, 'caption': str}
        """
        res = dict()
        for interface in self._w.Win32_NetworkAdapterConfiguration (IPEnabled=1):
            res['mac'] = interface.MACAddress
            res['ip'] = interface.IPAddress[0]
            res['caption'] = interface.Caption
        return res

    def set_up(self):
        """  获取自启动程序的位置
        Out: {'caption':
                {'location': str, 'command': str}
            }
        """
        res = dict()
        for s in self._w.Win32_StartupCommand():
            # print s.Location, s.Caption, s.Command
            res[s.Caption] = {
                'location': s.Location,
                'command': s.Command,
            }
        return res

    def get_platform(self):
        """Out:  'Windows-8-6.2.9200'
        """
        return platform.platform()

    def get_uname(self):
        """
        system uname
        eg:
        ('Linux', 'fedora.echorand', '3.7.4-204.fc18.x86_64',
        '#1 SMP Wed Jan 23 16:44:29 UTC 2013', 'x86_64')
        """
        return platform.uname()

    def get_system(self):
        '''
        get system platform eg: linux or windows
        '''
        return platform.system()

    def get_release(self):
        """
        get release version num
        """
        return platform.release()

    def get_linux_distribution(self):
        '''
        get info about linux distribution
        '''
        return platform.linux_distribution()

    def get_architecture(self):
        """
        return 64bit or 32bit
        """
        return platform.architecture()[0]

    def get_node(self):
        """
        return node name
        hostname
        """
        return platform.node()

    def get_machine(self):
        """Out: AMD64
        """
        return platform.machine()



class RpcServerThread(threading.Thread):
    """ SimpleXMLRPCServer
    func run and stop
    """
    running=True
    def run(self):
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer((IP, PORT))
        obj = WmiObj()
        self.server.register_instance(obj)
        self._set_daemon()
        while self.running:
            self.server.handle_request()

    def stop(self):
        self.running = False
        self.server.server_close()


class aservice(win32serviceutil.ServiceFramework):
    _svc_name_ = "ServerMonitorWindowsClient"
    _svc_display_name_ = "JWCH Server Monitor windows client"
    _svc_description_ = "教务处服务监控的windows客户端"
    _svc_deps_ = ["EventLog"]

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop=win32event.CreateEvent(None, 0, 0, None)
        self.isAlive=True
        self.rpc_server = RpcServerThread()

    def SvcStop(self):

        # tell Service Manager we are trying to stop (required)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # write a message in the SM (optional)
        # import servicemanager
        # servicemanager.LogInfoMsg("aservice - Recieved stop signal")

        # set the event to call
        win32event.SetEvent(self.hWaitStop)
        self.isAlive=False

        self.rpc_server.running=False # how to stop

    def SvcDoRun(self):
        import servicemanager
        # Write a 'started' event to the event log... (not required)
        #
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STARTED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))

        # methode 1: wait for beeing stopped ...
        # win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        # methode 2: wait for beeing stopped ...
        self.timeout=1000  # In milliseconds (update every second)

        self.rpc_server.start() # what you want to do

        while self.isAlive:
            # wait for service stop signal, if timeout, loop again
            rc=win32event.WaitForSingleObject(self.hWaitStop, self.timeout)


        # and write a 'stopped' event to the event log (not required)
        #
        win32evtlogutil.ReportEvent(self._svc_name_,servicemanager.PYS_SERVICE_STOPPED, 0,
                                    servicemanager.EVENTLOG_INFORMATION_TYPE,(self._svc_name_, ''))
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        return


if __name__ == '__main__':

    # if called without argvs, let's run !

    if len(sys.argv) == 1:
        try:
            evtsrc_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(aservice)
            servicemanager.Initialize('aservice', evtsrc_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error, details:
            if details[0] == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        win32serviceutil.HandleCommandLine(aservice)