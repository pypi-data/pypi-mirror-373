#!/usr/bin/python3
# coding=utf-8
##################################################################
#              ____     _     _ __  __                 
#             / __/__  (_)___(_) /_/ /  ___  ___  ___ _
#            _\ \/ _ \/ / __/ / __/ /__/ _ \/ _ \/ _ `/
#           /___/ .__/_/_/ /_/\__/____/\___/_//_/\_, / 
#              /_/                              /___/  
# 
# Copyright (c) 2025 Chongqing Spiritlong Technology Co., Ltd.
# All rights reserved.
# @author	arthuryang
# @brief	生成webframe后端框架python版
##################################################################

import	os
import	webframe_python_routes_py
import	webframe_python_webframe_py
import	SpiritLong_utility

## 准备webframe_python基本框架
def generate_basic_frame(path, project_name='webframe'):
	# 创建基本目录
	os.makedirs(f"{path}/frontend", 	exist_ok=True)
	os.makedirs(f"{path}/application",	exist_ok=True)
	os.makedirs(f"{path}/config/",		exist_ok=True)
	os.makedirs(f"{path}/service/",		exist_ok=True)
	os.makedirs(f"{path}/script/",		exist_ok=True)
	os.makedirs(f"{path}/runtime/",		exist_ok=True)

	# 基本框架：routes.py	
	with open(f"{path}/routes.py", 'w') as f:
		f.write(webframe_python_routes_py.content)

	# 基本框架：webframe.py
	with open(f"{path}/webframe.py", 'w') as f:
		f.write(webframe_python_webframe_py.content)


# 脚本执行
if __name__ == '__main__':
	# # 给文件增加版权说明
	# SpiritLong_utility.copyright(__file__, author='arthuryang')
	
	generate_basic_frame('backend')