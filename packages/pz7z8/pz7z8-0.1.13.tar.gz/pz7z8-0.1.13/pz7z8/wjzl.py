#!/usr/bin/python3

import pathlib,os,shutil
from .util import *

class c_slist(object):  #列出各服务器并依次处理
    def __init__(self):
        self.preinit()
        for data in readcfg():
            self.run(data)
    def preinit(self):
        pass
    def run(self,data):
        print(data)

class main(object):
    def __init__(self):
        配置=c_配置("wjzl.cfg")
        参数=配置.单行({'leftspace': '0','leftnum':'0','sort':'time'})
        if 参数["method"]=="del":
            self.fdel(参数)
    def fdel(self,参数):
        if not 参数["dir"]:return
        文件=[]
        for f in os.listdir(参数["dir"]):
            fn=os.path.join(参数["dir"],f)
            文件.append({"name":fn,"time":os.stat(fn).st_mtime})
        文件.sort(key=lambda x:x[参数["sort"]])
        while (参数["leftspace"]!="0" and 剩余空间(参数["dir"])<int(参数["leftspace"])*1024) or (参数["leftnum"]!="0" and len(文件)>int(参数["leftnum"])):
            print(f"删除{文件[0]}")
            if os.path.isdir(文件[0]["name"]):
                shutil.rmtree(文件[0]["name"])
            else:
                os.unlink(文件[0]["name"])
            文件.pop(0)

if __name__ == "__main__":
    main()
