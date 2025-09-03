import os,random,datetime,math,sys,shutil,hashlib,pathlib

def filemd5(filename,编码):#获取文件的md5值
    if not os.path.isfile(filename):return ""
    m = hashlib.md5()
    with open(filename,'rb') as f:
        if 编码!="utf8":
            m.update(f.read().decode(编码).encode("utf8"))
        else:
            m.update(f.read())
    return m.hexdigest()

def filetime(filename): #获取文件的修改时间
    if not os.path.exists(filename):
        return 0
    return os.stat(filename).st_mtime

def 带编码复制文件(源,源编码,目标,目标编码):
    if 源编码==目标编码:
        shutil.copy2(源,目标)
    else:
        with open(源,'rb') as f:
            data=f.read().decode(源编码).encode(目标编码)
            ft=open(目标,'wb')
            ft.write(data)
            ft.close()
            os.system(f"touch {目标} -r {源}")

def 同步文件(文件1,编码1,文件2,编码2):
    修改时间1=filetime(文件1)
    修改时间2=filetime(文件2)
    if 修改时间1>修改时间2:
        print("%s  ==>  %s" %(文件1,文件2))
        带编码复制文件(文件1,编码1,文件2,编码2)
    if 修改时间1<修改时间2:
        print("%s  ==>  %s" %(文件2,文件1))
        带编码复制文件(文件2,编码2,文件1,编码1)
    if 修改时间1==修改时间2:
        print("%s & %s has same change time!" %(文件1,文件2))

def 检查文件(文件1,编码1,文件2,编码2):
    if os.path.exists(文件1) and not os.path.isfile(文件1):
        return False
    if os.path.exists(文件2) and not os.path.isfile(文件2):
        return False
    if not os.path.isfile(文件1) and not os.path.isfile(文件2):
        print("%s & %s not exists!" %(文件1,文件2))
        return False
    if not os.path.isfile(文件1) or not os.path.isfile(文件2):
        return True
    if filemd5(文件1,编码1)!=filemd5(文件2,编码2):
        return True

def dsync():    #双向同步
    目录1=""
    目录2=""
    编码1="utf8"
    编码2="utf8"
    分隔符="|"
    if len(sys.argv)>1:
        配置文件=sys.argv[1]
    else:
        配置文件="dsync.conf"
    if not os.path.isfile(配置文件):
        模板=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile","dsync.conf")
        print(f"需要一个配置文件，不在命令行指定的话默认是{配置文件}，格式请参考{模板}")
        return
    f=open(配置文件)
    配置内容=f.readlines()
    f.close()
    for conf in 配置内容:
        conf=conf.strip().split("=")
        if len(conf)!=2:continue
        i,v=conf
        if i.lower()=="d1":目录1=v
        if i.lower()=="d2":目录2=v
        if i.lower()=="c1":编码1=v
        if i.lower()=="c2":编码2=v
        if i.lower()=="sp":分隔符=v
        if i.lower()=="f":
            文件=v.split(分隔符)
            if len(文件)==2:
                v1,v2=文件
                文件1=os.path.join(目录1,v1)
                文件2=os.path.join(目录2,v2)
            else:
                文件1=os.path.join(目录1,v)
                文件2=os.path.join(目录2,v)
            if 检查文件(文件1,编码1,文件2,编码2):
                同步文件(文件1,编码1,文件2,编码2)

if __name__ == "__main__":
    dsync()
