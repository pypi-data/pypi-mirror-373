import pathlib,sys,os

__all__=["c_配置","剩余空间"]

class c_配置(object):
    def __init__(self,配置文件):
        if len(sys.argv)>1:
            配置文件=sys.argv[1]
        if not os.path.isfile(配置文件):
            模板=pathlib.Path.joinpath(pathlib.Path(__file__).parent,"datafile",配置文件)
            print(f"需要一个配置文件，不在命令行指定的话默认是{配置文件}，格式请参考{模板}")
            sys.exit(-1)
        f=open(配置文件,encoding="utf8")
        self.配置内容=f.readlines()
        f.close()
    def 单行(self,表={}):   #解析成单行
        for i in self.配置内容:
            c=i.split("=")
            if len(c)!=2:
                continue
            表[c[0].strip()]=c[1].strip()
        return 表

def 剩余空间(目录):
    a=os.statvfs(目录)
    return a.f_bsize*a.f_bfree
