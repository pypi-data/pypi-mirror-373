#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 扫描 模板目录（默认是当前目录）下的模板文件 *.htm *.html
# 扫描 目标目录 (默认是web/static) 下的目标文件 *.htm *.html
# 如果目标文件中有 <!-- updatehtm xxxx.htm start --> 或者是 <!-- updatehtm xxxx.htm end -->  这样的行，则认为是需要用相应模板中的内容替换
# 替换后如果内容有变化，则更新文件，如果没有变化，则不更新文件

import os,sys,re,difflib

def 判断头尾(行):
    m=re.match(r"<!-- updatehtm (.*) (.*) -->",行)
    if m==None:
        return "",""
    return m.group(1),m.group(2)

def updatefile(模板文件,文件):
    fs=open(文件,"r")
    文件内容=fs.readlines()
    print("文件%s有%d行" %(文件,len(文件内容)))
    fs.close()
    新内容=[]
    当前模板=""
    for 行 in 文件内容:
        模板文件名,头尾=判断头尾(行)
        if 模板文件名 not in 模板文件 or 头尾 not in ["start","end"]:
            if 当前模板=="":
                新内容.append(行)
            continue
        if 头尾=="start":
            if 当前模板!="":
                print("文件%s错误：模板%s没有结束，又定义了新模板" %(文件,当前模板,模板文件名))
                sys.exti(-1)
            当前模板=模板文件名
        if 头尾=="end":
            if 当前模板=="":
                新内容=[]
                for 行2 in 模板文件[模板文件名]:
                    新内容.append(行2)
            else:
                for 行2 in 模板文件[当前模板]:
                    新内容.append(行2)
            当前模板=""
        新内容.append(行)
    if 当前模板!="":
        for 行2 in 模板文件[当前模板]:
            新内容.append(行2)
    if 新内容==文件内容:return
    print("%s 有变化" %(文件))
#   print(''.join(difflib.Differ().compare(新内容,文件内容)))
    fs=open(文件,"w")
    fs.writelines(新内容)
    fs.close()
        
def main():
    if len(sys.argv)==1:
        源目录="."
        目标目录="web/static"
    if len(sys.argv)==2:
        源目录="."
        目标目录=sys.argv[1]
    if len(sys.argv)==3:
        源目录=sys.argv[1]
        目标目录=sys.argv[2]
    模板文件={}
    for f in os.listdir(源目录):
        _,fext=(os.path.splitext(f))
        if fext.lower() in [".html",".htm"]:
            ff=os.path.join(源目录,f)
            with open(ff,'r') as fs:
                print("读入"+ff)
                模板文件[f]=fs.readlines()
    for f in os.listdir(目标目录):
        _,fext=(os.path.splitext(f))
        if fext.lower() in [".html",".htm"]:
            updatefile(模板文件,os.path.join(目标目录,f))

if __name__ == "__main__":
    main()
