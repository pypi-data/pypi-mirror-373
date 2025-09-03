#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#调整setup.py中的版本信息并自动上传到pypi

import os,sys,re,difflib,shutil

cfg={}

def 读入配置():
    配置文件=["chgver.ini",]
    cfg["file"]="setup.py"
    cfg["backup"]="setup.py.bak"

def 调整版本():
    os.system("./setup.py sdist")
    f=open("{file}".format(**cfg),"rb")
    data=f.readlines()
    f.close()
    shutil.copy2("{file}".format(**cfg),"{backup}".format(**cfg))
    f=open("{file}".format(**cfg),"wb")
    for i in data:
        if re.search(b'''version\s*=\s*['"](.*)['"]''',i):
            jg=re.search(b'\d+\.\d+\.\d+',i)
            if jg:
                oldver=jg.group()
                s=oldver.decode("utf8").split(".")
                i=i.decode("utf8").replace("%s.%s.%s" %(s[0],s[1],s[2]),"%s.%s.%d" %(s[0],s[1],int(s[2])+1))
                i=bytes(i,encoding="utf8")
                cmd="twine upload dist/*-%s.%s.%s.tar.gz" %(s[0],s[1],s[2])
        f.write(i)
    f.close()
    os.system(cmd)

def main():
    读入配置()
    调整版本()

if __name__ == "__main__":
    main()
