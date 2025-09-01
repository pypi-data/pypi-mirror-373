#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import platform
import socket
import subprocess
import sys
import shutil
from datetime import datetime

def main():

    print("Pyhton解释器的版本信息")
    print(sys.version)
    print("")

    def getLocalIp():
        try:
            # ip=socket.gethostbyname(socket.gethostname())
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print("occor error!")
        return ""


    inner_ip = getLocalIp()
    # outer_ip = requests.get('https:li//api.hohode.com/ip', timeout=1).text.strip()
    proc = subprocess.Popen(["curl -s ipinfo.io"], stdout=subprocess.PIPE, shell=True)
    (outer_ip, err) = proc.communicate()
    if isinstance(outer_ip,bytes):
        outer_ip = outer_ip.decode("utf8")

    print("内网ip：{}".format(inner_ip))
    print("外网ip：{}".format(outer_ip))
    print("")
    print("系统的版本号")
    system = platform.system()
    if system == "Darwin":
        print('这是苹果电脑，请查看"关于本机"')
    elif "ubuntu" in platform.platform().lower():
        print(platform.platform())
        os.system("lsb_release -a")
    else:
        os.system("cat /etc/redhat-release")
    print("")

    print("操作系统位数")
    if system == "Darwin":
        print(platform.mac_ver()[2])
    else:
        os.system("uname -m")
    print("")

    print("硬盘资源使用情况")
    os.system("df -h")
    print("")

    print("内存资源使用情况")
    if system == "Darwin":
        os.system("top -l 1 | head -n 10 | grep PhysMem")
    else:
        os.system("free -h")
    print("")

    print("查看CPU型号信息")
    if system == "Darwin":
        os.system("sysctl -n machdep.cpu.brand_string.")
    else:
        os.system("cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq")
    print("")

    print("查看CPU利用率")
    os.system("""top -b -n1 | grep "Cpu(s)" | awk '{print $2}'""")
    print("")


    print("物理CPU个数")
    if system == "Darwin":
        print('详细信息请查看 关于本机 -> 系统报告')
    else:
        os.system('cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l')
    print("")

    print("每个物理CPU的核数")
    if system == "Darwin":
        os.system("sysctl -n machdep.cpu.core_count")
    else:
        os.system("""cat /proc/cpuinfo| grep "cpu cores"| uniq | cut -d : -f 2 | awk '$1=$1'""")
    print("")

    print("逻辑CPU的总个数")
    if system == "Darwin":
        # os.system("sysctl -n machdep.cpu.core_count")
        print('详细信息请查看 关于本机 -> 系统报告')
    else:
        os.system('cat /proc/cpuinfo| grep "processor"| wc -l')
    print("")

if __name__ == "__main__":
    main()