#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys

def filenum(dirname):
	fcount=1
	if os.path.isdir(dirname):
		for f in os.listdir(dirname):
			ff=os.path.join(dirname,f)
			if os.path.isdir(ff):
				fcount=fcount+filenum(ff)
			else:
				fcount=fcount+1
	print("%d   %s" %(fcount,dirname))
	return fcount

def main():
	if len(sys.argv)==1:
		filenum(os.getcwd())
	else:
		filenum(sys.argv[1])

if __name__ == "__main__":
	main()
