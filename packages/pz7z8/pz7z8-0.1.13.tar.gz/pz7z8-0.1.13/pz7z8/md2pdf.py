#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#把md用pandoc转成pdf

import os,sys,re,pathlib,time

配置文件=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile","md2pdf.yaml")
头文件=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile","md2pdf.tex")
系统配置目录=os.path.join(os.path.dirname(__file__),"datafile")

def filemtime(wj):
    if not os.path.isfile(wj):
        return 0
    return os.stat(wj).st_mtime

class cfgfile(object):    #处理两个配置文件
    def __init__(self,fmd):
        self.目录=os.path.dirname(fmd)
        文件名,_=os.path.splitext(os.path.basename(fmd))
        createtime=time.strftime('%Y-%m-%d %H:%M:%S')
        self.data={"filename":文件名,"createtime":createtime,"createdate":createtime[:10],"md":fmd}
        self.data["pdf"]=os.path.splitext(fmd)[0]+".pdf"
        self.getcfgfile(fmd,"yaml")
        self.getcfgfile(fmd,"tex")
    def getcfgfile(self,fmd,ext):
        cfgname=os.path.join(self.目录,f"md2pdf.{ext}")
        if not os.path.exists(cfgname):  #没有本地配置文件则取全局的配置文件
            cfgname=os.path.join(系统配置目录,f"md2pdf.{ext}")
        if ext=="tex":
            self.data[ext]=cfgname
            return
        f=open(cfgname,"r",encoding="utf8")
        t=f.read()
        f.close()
        t2=t.format(**self.data)
        if t==t2:   #配置未改变，使用原始文件
            self.data[ext]=cfgname
        else:
            ftmpname=os.path.join("/tmp",f"{self.data['filename']}_md2pdf.{ext}")
            f=open(ftmpname,"w")
            f.write(t2)
            f.close()
            self.data[ext]=ftmpname

def pandoc(md):
    if os.path.isdir(md):
        for f in os.listdir(md):
            if not f.endswith(".md"):continue
            pandoc(os.path.join(md,f))
        return
    cfg=cfgfile(md)
    if filemtime(md)>filemtime(cfg.data["pdf"]):
        配置文件2=os.path.join(os.path.split(md)[0],"md2pdf.yaml")
        if not os.path.isfile(配置文件2):
            配置文件2=""
        头文件2=os.path.join(os.path.split(md)[0],"md2pdf.tex")
        if not os.path.isfile(头文件2):
            头文件2=""
        cmd="pandoc -s -N --pdf-engine=xelatex -H {tex} -o {pdf} {yaml} {md}".format(**cfg.data)
        print(cmd)
        os.system(cmd)

def main():
    if len(sys.argv)<2:
        print("无参数,处理当前目录下所有*.md")
        pandoc(".")
    for i in range(1,len(sys.argv)):
        pandoc(sys.argv[i])

if __name__ == "__main__":
    main()
