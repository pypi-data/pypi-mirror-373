#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pathlib

def main():
    文档路径=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile","usermenual.md")
    print(f'''
pz7z8包有以下脚本

chgver           调用twine发布pypi包，并修改setup.py里的版本号到下一个版本
dfslow           找出速度比较慢的挂载盘
dsync            双向的文件同步工具
filenum          统计目录下的文件数量
md2pdf           把markdown文件编译成pdf
pz7z8            就是这个可以显示pz7z8包大致内容的脚本
smod             根据模板调整源代码
sshall           使用ssh跳转到预先设置好的目标机器
wjzl             文件整理。备份、归档、删除清理等

详细情况，可以参考{文档路径}

''')

if __name__ == "__main__":
    main()
