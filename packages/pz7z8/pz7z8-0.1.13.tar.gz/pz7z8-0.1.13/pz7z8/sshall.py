#!/usr/bin/python3

import hashlib
import os
import re
import sys
import curses,traceback
import shutil
import time
import json,pathlib

class c_slist(object):  #列出各服务器并依次处理
    def __init__(self):
        self.preinit()
        for data in readcfg():
            self.run(data)
    def preinit(self):
        pass
    def run(self,data):
        print(data)

class c_配置(object):
    def __init__(self):
        self.个人配置文件=pathlib.Path.joinpath(pathlib.Path.home(),".sshall.json")
        if not pathlib.Path.is_file(self.个人配置文件):
            模板文件=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile",".sshall.json")
            print(f"需要个人配置文件:{self.个人配置文件}，格式可参考模板文件:{模板文件}")
            sys.exit(0)
    def read(self): #读取配置数据
        with open(self.个人配置文件,'r',encoding="utf8") as f:
            data=json.load(f)
        data.sort(key=lambda k:k["class"]+k["name"])
        t=[]
        for d in data:
            if d["name"] in t:
                print("有重复的key:%s" %(d["name"]))
                sys.exit(0)
            t.append(d["name"])
        return data

class ccurse(object):   #curse模板，需要使用curse的继承这个
    def initcurse(self):
        global stdscr
        try:
            if "TERM" not in os.environ:
                os.environ["TERM"]="linux"
            stdscr=curses.initscr()
            curses.noecho()     #关闭回显
            curses.cbreak()     #不需要回车即可实时读取键盘等输入
            stdscr.keypad(1)
            curses.mousemask(2**16-1)
        except:
            print("初始化失败")
            traceback.print_exc()
            self.endcurse()
    def endcurse(self):
        try:
            stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
        except:
            pass
    def __del__(self):
        self.endcurse()

class main(ccurse):
    '''主程序'''
    def __init__(self):
        self.initcurse()
        try:
            self.main()
        except:
            self.endcurse()
            traceback.print_exc()
    def main(self):
        self.fz=u"其它服务" #分组
        self.stinfo=""  #显示状态
        print("\x1b]2;@%s\x07" %(os.uname()[1]))
        while True:
            self.data=配置.read()
            self.freshall() #重画全屏幕
            c=self.getkey()
            if c>255:continue
            if c==0x1b:
                return
            if chr(c)>='0' and chr(c)<='9' and c-ord('0')<len(self.fzsj):
                self.fz=self.fzsj[c-ord('0')]
            if chr(c)>='a' and chr(c)<='z' and chr(c) in self.fwq:
                f=self.fwq[chr(c)]
                self.endcurse()
                s="ssh -A -p %s %s" %(f["port"],f["host"])
                print("\x1b]2;%s\x07" %(f["name"]))
                os.system(s)
                print("\x1b]2;@%s\x07" %(os.uname()[1]))
                self.initcurse()
    def freshall(self): #重画全屏幕。需要知道当前选择的分类，未选择默认为“开发测试”
        stdscr.clear()
        self.fzsj=[]    #取分组数据
        for i in self.data:
            if i["class"] not in self.fzsj:
                self.fzsj.append(i["class"])
        self.fzsj.sort()
        maxy,maxx=stdscr.getmaxyx()
        bq="abcdefghijklmnopqrstuvwxyz"
        for i in range(len(self.fzsj)):
            if self.fzsj[i]==self.fz:
                stdscr.addstr(i+1,0,"%d  %s" %(i,self.fzsj[i]),curses.A_UNDERLINE)
            else:
                stdscr.addstr(i+1,0,"%d  %s" %(i,self.fzsj[i]))
#       jg=self.c.find({"class":self.fz}).sort("info")
        jg=[]
        for i in self.data:
            if i["class"]==self.fz:jg.append(i)
        self.fwq={}
        for i in range(min(maxy-2,len(bq),len(jg))):
            stdscr.addstr(i+1,20,"%s  %s" %(bq[i],jg[i]["info"]))
            self.fwq[bq[i]]=jg[i]
        stdscr.addstr(0,0,self.stinfo)
        stdscr.refresh()
    def getkey(self):   #取输入命令，鼠标也转换成键盘的形式
        c=stdscr.getch()
        if c==curses.KEY_MOUSE:
            try:    #非当前窗口时突然点进来，getmouse会报错导致程序退出
                i,x,y,z,e=curses.getmouse()
            except:
                return 0
            if x<20 and y<10:
                return ord('0')+y-1
            if x>20 and y<26:
                return ord('a')+y-1
            return 0
        else:
            return c

def px():
    '''对server.json进行排序'''
    shutil.copy("/root/work/config/server.json","/root/work/config/server2.json")
    data=readcfg()
    s=json.dumps(data,ensure_ascii=False,indent=4)
    print(s)
    with open("/root/work/config/server.json",'w') as f:
        f.write(s)

配置=c_配置()
