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
# @brief	数学和数值相关工具
#
###################################################################  

import	decimal
import	re
import	os

## 将浮点数或者字符串转换成两位小数的decimal类型
def decimal2(k):
	try:
		value	= decimal.Decimal(k).quantize(decimal.Decimal('0.00'), decimal.ROUND_HALF_UP)
		return value
	except:
		return 0	

# 调试/测试代码
if __name__ == '__main__':
	pass

