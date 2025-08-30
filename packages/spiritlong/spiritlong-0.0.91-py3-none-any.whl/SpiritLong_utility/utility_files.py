#!/usr/bin/python3
# coding=utf-8
###################################################################
#           ____     _     _ __  __                 
#          / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#         _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#        /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#           /_/                              /___/  
# Copyright (c) 2024 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.  
# @author	arthuryang
# @brief	文件工具集
#
###################################################################  

import os

## 返回指定目录下（包括子目录）指定扩展名（列表）的文件列表
#	extensions	多个扩展名列表，空表示全部扩展名
# 返回的列表中，每个元素是一个文件名和扩展名的列表，以便后继处理
def walk_for_files(directory, extensions=[]):
	if isinstance(extensions, str):
		extensions	= [extensions]

	file_list	= []
	for home, dirs, files in os.walk(directory):
		for f in files:
			# 完整路径名称
			filename	= os.path.join(home, f)
			name, extension	= os.path.splitext(filename)
			if not extensions or extension in extensions :
				file_list.append([name, extension])
	return file_list

# 测试
if __name__ == "__main__":
	result	= walk_for_files(r"C:\Users\yangs\Documents\SVN\SVN2024_SPIRITLONG\财务\数据\2024\原始数据\代发薪酬")
	for r in result:
		print(r)
