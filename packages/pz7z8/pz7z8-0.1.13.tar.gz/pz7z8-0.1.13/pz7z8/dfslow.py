#!/usr/bin/python3
#Copyright by Chen Chuan (kcchen@139.com)

import os,time

def dfslow():   #检查比较慢的映射
    mtab=open("/etc/mtab","rt")
    for 文件内容 in mtab.readlines():
        文件内容=文件内容.split()
        挂载目标=文件内容[0]
        挂载目录=文件内容[1]
        开始时间=time.time()
        os.system("df "+挂载目录+">/dev/null")
        if time.time()-开始时间>1:
            print(挂载目标,挂载目录,time.time()-开始时间)

if __name__ == "__main__":
    dfslow()
